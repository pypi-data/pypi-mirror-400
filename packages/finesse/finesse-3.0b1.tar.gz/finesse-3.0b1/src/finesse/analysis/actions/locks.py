"""Lock Actions."""

import logging

import numpy as np

import finesse.config

from ...env import is_interactive, warn
from ...parameter import Parameter, deref
from ...solutions import BaseSolution
from . import elements_to_name
from .base import Action, convert_str_to_parameter
from .random import Change
from .sensing import SensingMatrixDC, SensingMatrixSolution
from ...simulations.sparse.simulation import SparseMatrixSimulation
from tqdm.auto import tqdm
from finesse.utilities import OrderedSet

LOGGER = logging.getLogger(__name__)


class RunLocksSolution(BaseSolution):
    """Solution from applying the :class:`.RunLocks` action.

    Attributes
    ----------
    iters : int
        Number of steps lock has required

    max_iterations : int
        Maximum number of iterations this lock can do

    error_signals : array_like
        error signals during locking steps, shape [num_locks, max_iterations]

    control_signals : array_like
        Control signals during locking steps, shape [num_locks, max_iterations]

    lock_names : tuple[str]
        Names of locks being controlled, shape [num_locks]

    feedback_names : tuple[str]
        Names of feedback for each lock, shape [num_locks]

    feedback_names : tuple[str]
        Names of error signals for each lock, shape [num_locks]

    final : arrary_like
        Final control signals, shape [num_locks]

    sensing_matrix : SensingMatrixSolution, optional
        The sensing matrix used when running the locks with Newton's method.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iters = 0
        self.error_signals = None
        self.control_signals = None
        self.lock_names = ()
        self.feedback_names = ()
        self.error_signal_names = ()
        self.final = None
        self.max_iterations = 0
        self.num_locks = 0
        self.sensing_matrix = None

    def plot_error_signals(self, ax=None):
        """Plots how the error signals vary during this lock attempt.

        Parameters
        ----------
        ax : Matplotlib.Axes, optional
            Axes to plot on, if no current axis is set then a new one
            is generated
        """
        import matplotlib.pyplot as plt

        if ax is not None:
            plt.sca(ax)
        plt.semilogy(abs(self.error_signals.T[: self.iters, :]))
        plt.legend(
            tuple(f"{a}:{b}" for a, b in zip(self.lock_names, self.error_signal_names))
        )
        plt.xlabel("steps")
        plt.ylabel("Error signal [arb]")

    plot = plot_error_signals  # Default plot option

    def plot_control_signals(self, ax=None):
        """Plots how the controls signals vary during this lock attempt. If `0` gaps
        will be shown when no change has been made to that degree of freedom for that
        step (As it was within the locks accuracy setting).

        Parameters
        ----------
        ax : Matplotlib.Axes, optional
            Axes to plot on, if no current axis is set then a new one
            is generated
        """
        import matplotlib.pyplot as plt

        if ax is not None:
            plt.sca(ax)
        plt.semilogy(abs(self.control_signals.T[: self.iters, :]))
        plt.legend(
            tuple(f"{a}:{b}" for a, b in zip(self.lock_names, self.feedback_names))
        )
        plt.xlabel("steps")
        plt.ylabel("Control signal [arb]")


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class RunLocks(Action):
    """An action that iteratively moves the system to lock. Currently, lock error
    signals must be readouts, not detectors, for use in this action.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each RunLocks step.
        If not provided, all locks in model are used.

    method : str, either "newton" or "proportional"
        Which method to use in the locking iterations.

    scale_factor : float
        Factor by which to multiply all DOF changes. Should be set
        below 1 if it is desired to minimize overshooting.

    sensing_matrix : SensingMatrixSolution or None
        Sensing matrix of gains used in locking, of the type
        that would be returned by
        state.apply(SensingMatrixDC(lock_dof_names, readout_names)
        If None, the sensing matrix is recalculated. Recommended
        to be None except when locking multiple times in a row,
        e.g. with DragLocks.

    max_iterations : int
        The maximum number of locking steps in each execution
        of RunLocks.

    display_progress : boolean
        When true, displays the status of the error signals
        during locking iterations.

    optimize_phase : boolean
        Deprecated: Use an action like OptimiseRFReadoutPhaseDC instead.

    d_dof_phase : float
        Step size to use when optimizing the demodulation
        phase for each error signal/DOF pair.

    set_gains : boolean
        Only applies if method is "proportional". If true,
        sets the gains for each error signal/DOF pair.
        If false, uses pre-set gains.

    d_dof_gain : float
        Step size to use when calculating the gain
        for every pair of error signals and DOFs.

    exception_on_fail : boolean
        When true, raise exception if maximum iterations
        are surpassed.

    no_warning : boolean
        When true, don't even raise a warning if maximum
        iterations are reached. Recommended to be false
        unless repeatedly testing locking.

    pre_step : :class:`.Action`
        Action to apply on each step of the lock

    show_progress_bar : boolean
        Will enable the progress bar when true.

    name : str
        Name of the action.
    """

    def __init__(
        self,
        *locks,
        method="proportional",
        scale_factor=1,
        sensing_matrix=None,
        max_iterations=10000,
        display_progress=False,
        optimize_phase=None,
        d_dof_phase=1e-9,
        set_gains=True,
        d_dof_gain=1e-9,
        exception_on_fail=True,
        no_warning=False,
        pre_step=None,
        show_progress_bar=None,
        name="run locks",
    ):
        super().__init__(name)

        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        self.max_iterations = max_iterations
        self.method = method
        self.scale_factor = scale_factor
        self.sensing_matrix = sensing_matrix
        self.display_progress = display_progress
        self.optimize_phase = optimize_phase
        if optimize_phase is not None:
            finesse.utilities.misc.deprecation_warning(
                "DragLocks: `optimize_phase` is deprecated, consider using the :class:`.OptimiseRFReadoutPhaseDC` action before this one instead.",
                "3.0.0",
            )
        self.d_dof_phase = d_dof_phase
        self.set_gains = set_gains
        self.d_dof_gain = d_dof_gain
        self.exception_on_fail = exception_on_fail
        self.no_warning = no_warning
        self.pre_step = pre_step

        # use local flag if provided, otherwise default to global setting
        if show_progress_bar is not None:
            self.show_progress_bar = show_progress_bar
        else:
            self.show_progress_bar = finesse.config.show_progress_bars

        self.pbar = None

    def init_pbar(self, locks):
        # define template for lock status display
        lock_format = " ".join(
            [f"{lock.name} {{postfix[0][{lock.name}]}}" for lock in locks]
        )

        # create the progress bar
        self.pbar = tqdm(
            range(self.max_iterations),
            initial=self.max_iterations,
            desc="",
            bar_format=f"{lock_format} |{{bar}}| {{n_fmt}}/{{total_fmt}}",
            colour="red",
            dynamic_ncols=True,
            postfix=[dict((lock.name, "✗") for lock in locks), len(locks)],
            disable=not self.show_progress_bar,
        )

    def update_pbar(self):
        # decrement the counter
        self.pbar.update(-1)

    def update_pbar_lock(self, lock_name, is_locked):
        # update the lock's status
        if self.show_progress_bar:
            self.pbar.postfix[0][lock_name] = "✔" if is_locked else "✘"

    def complete_pbar(self):
        # runs when the progress bar is considered complete
        self.pbar.colour = "green"
        self.pbar.refresh()

    def _do(self, state):
        # we need a carrier signal simulation to run the locks
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, SparseMatrixSimulation):
            raise NotImplementedError()

        # gather locks from the model
        if len(self.locks) > 0:
            # use specified locks if they are enabled
            locks = tuple(state.model.elements[name] for name in self.locks)
        else:
            # otherwise use all enabled locks
            locks = tuple(lck for lck in state.model.locks if lck.enabled)

        # collect all lock related workspaces
        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    OrderedSet(
                        # workspaces can be in both lists
                        (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
                    ),
                ),
                None,
            )
            for lock in locks
        )

        # Store initial parameters in case of failure so we can reset the model
        initial_feedback = tuple(float(lock.feedback) for lock in locks)

        # initialize the solution
        sol = RunLocksSolution(self.name)
        sol.max_iterations = self.max_iterations
        sol.num_locks = len(locks)
        sol.iters = -1
        sol.error_signals = np.zeros((len(locks), self.max_iterations + 1))
        sol.control_signals = np.zeros((len(locks), self.max_iterations + 1))
        sol.lock_names = tuple(lock.name for lock in locks)
        sol.feedback_names = tuple(deref(lock.feedback).full_name for lock in locks)
        sol.error_signal_names = tuple(deref(lock.error_signal).name for lock in locks)

        # set up the progress bar using all enabled locks
        self.init_pbar(locks)

        if self.display_progress:
            GREEN = "\033[92m" if is_interactive() else ""
            RED = "\033[91m" if is_interactive() else ""
            # BOLD = "\033[1m" not used
            END = "\033[0m" if is_interactive() else ""
            print("Error Signal Residuals at Each Iteration (W):")
            print(format("", "23s"), end="")
            for lock in locks:
                print(format(lock.name, "^15s"), end="")

        # ----------------------------------------------------------------------
        # Proportional method
        # ----------------------------------------------------------------------
        if self.method in "proportional":
            # use the sensing matrix to set the gains?
            # TODO: allow this method to set gains from the sensing matrix
            # if self.set_gains:
            #     for idx, _ in enumerate(lock_dof_names):
            #         if "_Q" in err_sig_names[idx]:
            #             locks[idx].gain = -1 / sensing_matrix.out[idx, idx].imag
            #         else:
            #             locks[idx].gain = -1 / sensing_matrix.out[idx, idx].real

            # compute as needed or until max iterations have been reached
            recompute = True
            while recompute and sol.iters < self.max_iterations:
                sol.iters += 1

                if self.display_progress:
                    print(
                        format("\nIteration Number ", "<20s")
                        + format(sol.iters, "<3d"),
                        end="",
                    )

                # run the pre-step action
                if self.pre_step:
                    state.apply(self.pre_step)

                # calculate the readout values
                state.sim.run_carrier()

                # compute as needed or until max iterations have been reached
                recompute = False
                for i in range(len(locks)):
                    # read the error
                    err = dws[i].get_output() - locks[i].offset
                    sol.error_signals[i, sol.iters] = err

                    # recompute if the error is too large
                    acc = locks[i].accuracy
                    if abs(err) >= acc:
                        # adjust the feedback
                        feedback = float(locks[i].gain) * err * self.scale_factor
                        deref(locks[i].feedback).value += feedback

                        # store it
                        sol.control_signals[i, sol.iters] = feedback

                        # and go again
                        recompute = True

                    is_locked = abs(err) < acc

                    if self.display_progress:
                        str_color = GREEN if is_locked else RED
                        print(str_color + format(err, "^ 15.2e") + END, end="")

                    # update the lock status
                    self.update_pbar_lock(locks[i].name, is_locked)

                # update the bar status
                self.update_pbar()

        # ----------------------------------------------------------------------
        # Newton method
        # ----------------------------------------------------------------------
        elif self.method == "newton":
            # this method requires the use of readouts
            # TODO: make sure this can only be done with readouts (not pds)
            err_sigs = [lock.error_signal for lock in locks]
            err_sig_names = [sig.name for sig in err_sigs]
            readout_names = [sig.readout.name for sig in err_sigs]  # fails if pd
            lock_dof_names = [deref(lock.feedback).owner.name for lock in locks]

            if self.display_progress:
                print("\n" + format("", "23s"), end="")
                for idx in range(len(locks)):
                    print(format(err_sig_names[idx] + "1", "^15s"), end="")

            # a sensing matrix is required
            if self.sensing_matrix is not None:
                if isinstance(self.sensing_matrix, SensingMatrixSolution):
                    sensing_matrix = self.sensing_matrix
                else:
                    raise Exception(
                        "Locks failed: invalid type of sensing matrix specified"
                    )
            else:
                sensing_matrix = state.apply(
                    SensingMatrixDC(lock_dof_names, readout_names)
                )

            # store the sensing maxtrix
            sol.sensing_matrix = sensing_matrix

            # Matrix of gains only for readout phases that are actually used in
            # locks. Also transposes the sensing matrix, so that rows rather
            # than columns correspond to error signals.
            N = len(locks)
            gain_matrix = np.zeros((N, N))
            for dof_idx, _ in enumerate(lock_dof_names):
                for rd_idx, _ in enumerate(readout_names):
                    # get the sensing matrix value
                    val = sensing_matrix.out[dof_idx, rd_idx]

                    # take imag or real depending on the type of signal
                    if "_Q" in err_sig_names[rd_idx]:
                        gain_matrix[rd_idx, dof_idx] = val.imag
                    else:
                        gain_matrix[rd_idx, dof_idx] = val.real

            # Evaluate the inverse of the gain matrix/Jacobian. Assuming
            # that we stay in the linear region for all DOFs/readouts, we evaluate
            # the inverted Jacobian only once but use it in all iterations.
            jacobian_inv = np.linalg.inv(gain_matrix) * self.scale_factor

            # compute as needed or until max iterations have been reached
            recompute = True
            while recompute and sol.iters < self.max_iterations:
                # set up the run
                sol.iters += 1
                recompute = False

                if self.display_progress:
                    print()
                    print(
                        format("Iteration Number ", "<20s") + format(sol.iters, "<3d"),
                        end="",
                    )

                # run the pre-step action
                if self.pre_step:
                    state.apply(self.pre_step)

                # recalculate the readout values
                state.sim.run_carrier()

                # gather the accuracy from the locks and error from the readouts
                acc_vect = np.array([lock.accuracy for lock in locks])
                err_vect = np.array(
                    [dws[i].get_output() - locks[i].offset for i in range(N)]
                )

                # calculate the new feedbacks using the inverted jacobian
                feedback_vect = -1 * np.matmul(jacobian_inv, err_vect)

                # for each lock
                results = [None] * N
                for i in range(N):
                    # store the error
                    sol.error_signals[i, sol.iters] = err_vect[i]

                    # if any error is too high, we need to recompute
                    if any(np.greater(abs(err_vect), acc_vect)):
                        # store the feedback increment
                        sol.control_signals[i, sol.iters] = feedback_vect[i]

                        # adjust the feedback
                        deref(locks[i].feedback).value += feedback_vect[i]

                        # let's do it again
                        recompute = True

                    results[i] = f"{locks[i].name} {err_vect[i]:.2g}"

                    is_locked = abs(err_vect[i]) < acc_vect[i]

                    if self.display_progress:
                        str_color = GREEN if is_locked else RED
                        print(str_color + format(err_vect[i], "^ 15.2e") + END, end="")

                    # update the lock status
                    self.update_pbar_lock(locks[i].name, is_locked)

                # update the bar status
                self.update_pbar()

        # method not found!
        else:
            raise Exception("Locks failed: invalid method provided")

        # if the locks still need to be recomputed then we've failed...
        if recompute:
            # reset the locks
            for lock, value in zip(locks, initial_feedback):
                deref(lock.feedback).value = value

            # throw an exception?
            if self.exception_on_fail:
                raise finesse.exceptions.LostLock(
                    "Locks failed: max iterations reached"
                )

            # display a warning?
            if not self.no_warning:
                warn(
                    "Locks failed to converge, try increasing maximum iterations, check gains/error signals. See RunLocks exception_on_fail=False to inspect solution for locking problems."
                )
        else:
            # locks have successfully locked
            self.complete_pbar()

        # store the final feedback values in the solution
        sol.final = np.array(
            tuple(deref(lock.feedback).value for lock in locks), dtype=float
        )

        return sol

    def _requests(self, model, memo, first=True):
        # gather locks from the model
        if len(self.locks) > 0:
            # use specified locks if they are not enabled
            locks = tuple(model.elements[name] for name in self.locks)
        else:
            # otherwise use all enabled locks
            locks = tuple(lck for lck in model.locks if lck.enabled)

        for lock in locks:
            # the lock feedback values will be changing
            memo["changing_parameters"].append(deref(lock.feedback).full_name)

        if self.pre_step:
            self.pre_step._requests(model, memo)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class DragLocks(Action):
    """An action that incrementally changes model parameter values, reaching lock at
    each step, until lock is reached at the desired final parameter values.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each :class:`finesse.analysis.actions.locks.RunLocks`
        step. Acts like the \\*locks parameter in
        :class:`finesse.analysis.actions.locks.RunLocks`: if not provided, all locks in
        model are used.

    parameters : list
        A list of strings. Each element should correspond
        to a parameter in the model.

    stop_points : list
        The final parameter values that locks move
        towards incrementally.

    relative : boolean
        If true, stop_points are relative to the initial
        parameter values.

    max_recursions : int
        The number of times that the step size is allowed to decreased
        by a factor of ten when locks fail.

    method : str, either "newton" or "proportional"
        The method to use in each locking step.

    scale_factor : float
        Factor by which to multiply all DOF changes. Should be set
        below 1 if it is desired to minimize overshooting.

    num_steps : int
        Number of steps to calculate, starting at the initial point and ending
        at the stop point.

    never_optimize_phase : boolean
        Deprecated: When true, never optimize readout phases. When false,
        phases will be optimized anytime the previous step required
        more than 10 iterations.

    exception_on_fail : boolean
        When true, raise exception if max_recursions is surpassed.

    max_iterations : int
        The maximum number of locking steps in each execution
        of RunLocks. If surpassed, step size is decreased.

    display_progress : boolean
        When true, displays the status of the lock dragging.

    name : str
        Name of the action.
    """

    def __init__(
        self,
        *locks,
        parameters,
        stop_points,
        relative=False,
        method="proportional",
        scale_factor=1,
        num_steps=11,
        never_optimize_phase=None,
        exception_on_fail=True,
        max_recursions=5,
        max_iterations=1000,
        display_progress=False,
        show_progress_bar=False,
        name="drag locks",
    ):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        self.parameters = parameters
        self.stop_points = np.array(stop_points)
        if len(self.parameters) != len(self.stop_points):
            raise ValueError("Unequal number of parameters and stopping points")
        self.relative = relative
        self.max_recursions = max_recursions
        self.method = method
        self.scale_factor = scale_factor
        self.num_steps = num_steps
        self.exception_on_fail = exception_on_fail
        self.max_iterations = max_iterations
        self.show_progress_bar = show_progress_bar
        self.display_progress = display_progress

        if never_optimize_phase is not None:
            finesse.utilities.misc.deprecation_warning(
                "DragLocks: `never_optimize_phase` is deprecated, consider using the :class:`.OptimiseRFReadoutPhaseDC` action before this one instead.",
                "3.0.0",
            )

    def _do(self, state):
        def TryLocking(state, steps, recursion_num=0):
            sensing_matrix = None

            for step_ind, step_vals in enumerate(steps):
                # Change each parameter to its value at this step.
                for p_ind, param_val in enumerate(step_vals):
                    state.apply(Change({self.parameters[p_ind]: param_val}))

                # Run locks at this step.
                try:
                    step_vals_str = str([format(val, "4.3e") for val in step_vals])

                    if self.display_progress:
                        print(
                            "\t" * recursion_num
                            + f"Step {step_ind:2d} of {len(steps) - 1}: ",
                            end="",
                        )
                    sol = state.apply(
                        RunLocks(
                            method=self.method,
                            scale_factor=self.scale_factor,
                            sensing_matrix=sensing_matrix,
                            exception_on_fail=True,
                            max_iterations=self.max_iterations,
                            display_progress=False,
                            show_progress_bar=self.show_progress_bar,
                        )
                    )
                    # Print status of locking steps.
                    if self.display_progress:
                        print(
                            "Reached lock with",
                            self.parameters,
                            "= "
                            + step_vals_str
                            + " in "
                            + str(sol.iters)
                            + " iterations.",
                        )
                    # If the previous step converged very quickly, don't bother
                    # optimizing phases or recalculating the sensing matrix at
                    # the next step.
                    if sol.iters <= 10:
                        sensing_matrix = sol.sensing_matrix
                    else:
                        sensing_matrix = None
                        if self.display_progress:
                            print(
                                "\t" * recursion_num
                                + "Step required more than 10 iterations."
                                + " Recalculating sensing matrix in next step."
                            )
                except Exception:
                    recursion_num += 1
                    if self.display_progress:
                        print(
                            "Failed to lock with",
                            self.parameters,
                            "= " + step_vals_str + ". Decreasing step size.",
                        )
                    if recursion_num >= self.max_recursions:
                        raise Exception("Maximum recursion level exceeded.")
                    if step_ind == 0:
                        new_step_vals = np.linspace(
                            steps[step_ind], steps[step_ind + 1], self.num_steps
                        )
                    else:
                        new_step_vals = np.linspace(
                            steps[step_ind - 1], steps[step_ind], self.num_steps
                        )
                    TryLocking(state, new_step_vals, recursion_num=recursion_num)
                    recursion_num -= 1
            return sol

        # Find the model parameters corresponding to the strings provided
        p = [convert_str_to_parameter(state.model, param) for param in self.parameters]
        p_vals = np.array([param.value for param in p])
        # The parameter values that will be stepped through and locked to.
        if not self.relative:
            step_vals_list = np.linspace(p_vals, self.stop_points, self.num_steps)
        else:
            step_vals_list = np.linspace(
                p_vals, p_vals + self.stop_points, self.num_steps
            )

        sol = TryLocking(state, step_vals_list)

        return sol

    def _requests(self, model, memo, first=True):
        for param in self.parameters:
            p = convert_str_to_parameter(model, param)
            if isinstance(p, Parameter):
                memo["changing_parameters"].append(param)
        if len(self.locks) == 0:
            # If none given lock everything
            for lock in model.locks:
                memo["changing_parameters"].append(deref(lock.feedback).full_name)
                rd_name = lock.error_signal.name
                if "_DC" not in rd_name:
                    memo["changing_parameters"].append(
                        lock.error_signal.readout.name + ".phase"
                    )
        else:
            for name in self.locks:
                if name not in model.elements:
                    raise Exception(f"Model {model} does not have a lock called {name}")
                memo["changing_parameters"].append(
                    deref(model.elements[name].feedback).full_name
                )
                rd_name = model.elements[name].error_signal.name
                if "_DC" not in rd_name:
                    memo["changing_parameters"].append(
                        model.elements[name].error_signal.readout.name + ".phase"
                    )


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class SetLockGains(Action):
    """An action that computes the optimal lock gains using the sensing matrix found
    with :class:`.SensingMatrixDC`. This action computes the error signal gradient for
    each lock with respect to its drive and sets the gain as `-gain_scale/sensing`.

    Parameters
    ----------
    *locks : list, optional
        A list of locks for which to set the gain. If none provided, all enabled
        locks in model are used. Disabled locks that are explicitly listed will
        have their gains set.

    d_dof_gain : float, optional
        Step size to use when calculating the gain for each error signal/DOF pair.

    gain_scale : float, optional
        Extra gain scaling factor applied to the gain calculation: `-gain_scale/sensing`
        In multiple lock models where the locks are cross coupled using a `gain_scale` < 1
        can improve the stability of the locking algorithm to stop excessively large
        steps.

    optimize_phase : bool, optional,
        Deprecated feature: Use :class:`.OptimiseRFReadoutPhaseDC` instead

    name : str
        Name of the action.

    verbose : bool
        If True this will print the name of the enabled locks and their gains.
    """

    def __init__(
        self,
        *locks,
        d_dof_gain=1e-10,
        gain_scale=1,
        name="set gains",
        optimize_phase=None,
        verbose=False,
    ):
        super().__init__(name)
        self.locks = elements_to_name(locks)
        self.d_dof_gain = d_dof_gain
        self.gain_scale = gain_scale
        self.sensing_action = None
        self.optimize_phase = optimize_phase
        if optimize_phase is not None:
            finesse.utilities.misc.deprecation_warning(
                "SetLockGains: `optimize_phase` is deprecated, consider using the :class:`.OptimiseRFReadoutPhaseDC` action instead.",
                "3.0.0",
            )
        self.verbose = verbose

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, SparseMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = tuple(lck for lck in state.model.locks)
        else:
            locks = tuple(
                state.model.elements[lock.name] for lock in self.locks if lock.enabled
            )

        err_sigs = [lck.error_signal for lck in locks]
        err_sig_names = [sig.name for sig in err_sigs]

        gain_matrix = state.apply(self.sensing_action)

        for idx, lock in enumerate(locks):
            err_sig = err_sig_names[idx]
            val = gain_matrix.out[idx, idx]
            if "_Q" in err_sig:
                gain = val.imag
            else:
                gain = val.real

            if gain == 0:
                raise ZeroDivisionError(f"{lock.name} found a gain of zero")
            lock.gain = -self.gain_scale / gain
            if self.verbose:
                print(f"{lock.name}: {lock.gain}")

    def _requests(self, model, memo, first=True):
        if len(self.locks) == 0:
            self.locks = tuple(lck for lck in model.locks if lck.enabled)
        else:
            self.locks = tuple(model.get(name) for name in self.locks)

        self.sensing_action = SensingMatrixDC(
            [deref(lock.feedback).owner.name for lock in self.locks],
            [lock.error_signal.readout.name for lock in self.locks],
            d_dof=self.d_dof_gain,
        )
        self.sensing_action._requests(model, memo)
        for lock in self.locks:
            memo["changing_parameters"].append(lock.gain.full_name)
