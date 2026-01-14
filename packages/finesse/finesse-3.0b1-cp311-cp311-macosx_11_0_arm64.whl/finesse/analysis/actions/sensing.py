"""Collection of Actions that deal with sensing tasks such as computing sensing
matrices, optimising RF readouts, etc."""

import logging

import numpy as np

from finesse.components import DegreeOfFreedom
from finesse.components.readout import ReadoutDetectorOutput, ReadoutRF
from finesse.exceptions import FinesseException
from finesse.parameter import Parameter, ParameterRef
from finesse.utilities.misc import deprecation_warning

from ...parameter import deref
from ...solutions import BaseSolution
from ...utilities.tables import NumberTable
from ...simulations.sparse.simulation import SparseMatrixSimulation
from . import elements_to_name
from .base import Action
from .lti import FrequencyResponse
from finesse.utilities import OrderedSet

LOGGER = logging.getLogger(__name__)


def get_readout_workspace(readouts, output, readout_workspaces):
    """Return the readout workspaces for a particular readout's quadrature outputs.

    Parameters
    ----------
    readouts : iterable
        :class:`.ReadoutRF` elements
    output : str
        Quadrature output to try and select, 'I', 'Q', 'DC'
    readout_workspaces : dict
        Workspaces of the readouts in the simulation
    """
    return tuple(readout_workspaces[rd.name + "_" + output] for rd in readouts)


class OptimiseRFReadoutPhaseDCSolution(BaseSolution):
    pass


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class OptimiseRFReadoutPhaseDC(Action):
    """This optimises the demodulation phase of :class:`.ReadoutRF` elements relative to
    some :class:`.DegreeOfFreedom` or driven :class:`.Parameter` in the model. The
    phases are optimised by calculating the DC response of the readouts. This
    :class:`.Action` changes the state of the model by varying the readout demodulation
    phases. If no arguments are given it will try to automatically optimise any lock
    element in the model that is using an RF readout with respect to the lock feedback
    parameter.

    Parameters
    ----------
    args
        Pairs of :class:`.DegreeOfFreedom` or :class:`.Parameter` and :class:`.ReadoutRF` elements, or pairs
        of their names. If none are provided `OptimiseRFReadoutPhaseDC` will
        automatically search for :class:`.Lock` elements which have :class:`.ReadoutRF`
        error signal and optimise them.
    d_dof : float, optional
        A small offset applied to the DOFs to compute the gradients of the error
        signals

    Examples
    --------
    Take a typicaly Pound-Drever-Hall lock of a cavity. Here is some KatScript
    to setup such a model:

    >>> import finesse
    >>> from finesse.analysis.actions import OptimiseRFReadoutPhaseDC
    >>>
    >>> model = finesse.Model()
    >>> model.parse('''
    >>> l l1
    >>> mod mod1 10M 0.1 mod_type=pm
    >>> readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    >>> m m1 R=0.99 T=0.01
    >>> m m2 R=1 T=0
    >>> link(l1, mod1, m1, 1, m2)
    >>> lock cav_lock PD_I m2.phi 0.01 1e-3
    >>> ''')

    We have defined a `lock` above using the I quadrature RF demodulation and
    feeding back to the `m2` mirror position. We can optimise this demodulation
    phase by running. Here we manually provied which drives and readouts to use:

    >>> sol = model.run(OptimiseRFReadoutPhaseDC("m2.phi", 'PD_I'))
    >>> print(sol.phases)
    {'PD': 181.3535303754581}
    >>> print(model.PD.phase)
    181.3535303754581

    Alternatively, `PD_Q` could also be optimised for above. You can also just
    optimise all locks that are using RF readouts by providing no arguments:

    >>> sol = model.run(OptimiseRFReadoutPhaseDC())
    >>> print(sol.phases)
    {'PD': 181.3535303754581}

    To tell what was optimised, see the `sol.phases` dictionary.
    """

    def __init__(self, *args, d_dof=1e-10, name="optimise_demod_phases_dc"):
        super().__init__(name)
        self.args = args
        self.d_dof = d_dof

    def _do(self, state):
        readout_outputs = [
            state.sim.model.elements[name] for name in self.readout_output_names
        ]
        readouts = [state.sim.model.elements[name] for name in self.readout_names]
        drives = []

        Idws = get_readout_workspace(readouts, "I", state.sim.workspace_name_map)
        Qdws = get_readout_workspace(readouts, "Q", state.sim.workspace_name_map)
        drives = tuple(state.model.get(drive) for drive in self.drive_names)

        assert len(drives) == len(readouts) == len(readout_outputs)

        N = len(drives)
        sol = OptimiseRFReadoutPhaseDCSolution(self.name)
        sol.Ivals = np.zeros((N, 2), dtype=complex)
        sol.Qvals = np.zeros((N, 2), dtype=complex)

        # Here we compute the gradient of the error signals
        # with respect to some DOF change
        for i in range(N):
            drives[i].value -= self.d_dof
            state.sim.run_carrier()
            sol.Ivals[i, 0] = Idws[i].get_output()
            sol.Qvals[i, 0] = Qdws[i].get_output()
            drives[i].value += 2 * self.d_dof
            state.sim.run_carrier()
            sol.Ivals[i, 1] = Idws[i].get_output()
            sol.Qvals[i, 1] = Qdws[i].get_output()
            # reset value
            drives[i].value -= self.d_dof

        # Compute the gradients in both I and Q
        sol.I_gradients = (sol.Ivals[:, 1] - sol.Ivals[:, 0]) / 2e-6
        sol.Q_gradients = (sol.Qvals[:, 1] - sol.Qvals[:, 0]) / 2e-6

        # We can use the complex angle to compute how much to change the
        # demod phase by to optimise it
        sol.add_degrees = np.angle(sol.I_gradients + 1j * sol.Q_gradients, deg=True)
        sol.phases = {}
        sol.previous_phases = {}

        for i in range(N):
            param = readouts[i].phase
            sol.previous_phases[self.readout_names[i]] = float(param.value)
            if self.readout_output_names[i].endswith("_Q"):
                param.value += sol.add_degrees[i] + 90
            else:
                param.value += sol.add_degrees[i]
            sol.phases[self.readout_names[i]] = float(param.value)

        return sol

    def _setup(self, model):
        if len(self.args) == 0:
            rf_locks = tuple(
                lock
                for lock in model.locks
                if isinstance(lock.error_signal, ReadoutDetectorOutput)
                and isinstance(lock.error_signal.readout, ReadoutRF)
            )
            self.drive_names = list(lock.feedback.full_name for lock in rf_locks)
            self.readout_output_names = list(
                lock.error_signal.name for lock in rf_locks
            )
        else:
            self.drive_names = list(elements_to_name(self.args[::2]))
            self.readout_output_names = list(elements_to_name(self.args[1::2]))

        self.readout_names = []

        for i, name in enumerate(self.drive_names):
            obj = model.get(name)
            if isinstance(obj, DegreeOfFreedom):
                self.drive_names[i] = obj.DC.full_name
            elif isinstance(obj, Parameter):
                self.drive_names[i] = obj.full_name
            elif isinstance(obj, ParameterRef):
                self.drive_names[i] = obj.parameter.full_name
            else:
                raise FinesseException(
                    f"OptimiseRFReadoutPhaseDC: cannot drive {repr(obj)}"
                )

        for i, name in enumerate(self.readout_output_names):
            obj = model.get(name)
            if isinstance(obj, ReadoutDetectorOutput):
                self.readout_names.append(obj.readout.name)
            elif isinstance(obj, ReadoutRF):
                # first output defined, usually I
                default = obj.outputs.I.name
                deprecation_warning(
                    f"OptimiseRFReadoutPhaseDC should now be given a ReadoutDetectorOutput not ReadoutRF '{obj}'. Defaulting to output '{default}'",
                    "3.0",
                )
                self.readout_output_names[i] = default
                self.readout_names.append(obj.name)
            else:
                raise FinesseException(
                    f"OptimiseRFReadoutPhaseDC: {repr(obj)} should be a ReadoutRF or a ReadoutDetectorOutput"
                )

        if len(self.drive_names) != len(self.readout_output_names):
            raise FinesseException(
                "OptimiseRFReadoutPhaseDC: matching pairs of drives and readouts should be provided"
            )

    def _requests(self, model, memo, first=True):
        self._setup(model)
        memo["changing_parameters"].extend(_ for _ in self.drive_names)
        memo["changing_parameters"].extend(_ + ".phase" for _ in self.readout_names)
        return memo


class SensingMatrixSolution(BaseSolution):
    """Sensing matrix solution.

    The raw sensing matrix information can be accessed using the
    `SensingMatrixSolution.out` member. This is a complex-valued array with dimensions
    (DOFs, Readouts), which are accessible via `SensingMatrixSolution.dofs` and
    `SensingMatrixSolution.readouts`.

    A table can be printed using :meth:`.SensingMatrixSolution.display`.

    Polar plot can be generated using :meth:`.SensingMatrixSolution.plot`

    Printing :class:`.SensingMatrixSolution` will show an ASCII table of the data.
    """

    def display(
        self,
        dofs=None,
        readouts=None,
        tablefmt="pandas",
        numfmt="{:.2G}",
        highlight=None,
        highlight_color="#808080",
    ):
        """Displays a HTML table of the sensing matrix, optionally highlighting the
        largest absolute value for each readout or dof.

        Notes
        -----
        Only works when called from an IPython environment with the
        `display` method available. Pandas is required for highlighting.

        Parameters
        ----------
        dofs : iterable[str], optional
            Names of degrees of freedom to show, defaults to all if None
        readouts : iterable[str], optional
            Names of readouts to show, defaults to all if None
        tablefmt : str, optional
            Either 'pandas' for pandas formatting, or anything else to
            use `finesse.utilities.tables.Table`. Defaults to 'pandas' if available.
        numfmt : str or func or array, optional
            Either a function to format numbers or a formatting string. The
            function must return a string. Can also be an array with one option per
            row, column or cell. Defaults to '{:.2G}'.
        highlight : str or None, optional
            Either 'dof' to highlight the readout that gives the largest
            output for each dof, or 'readout' to highlight the dof for
            which each readout gives the largest output. Defaults to
            None (no highlighting).
        highlight_color : str, optional
            Color to highlight the maximum values with. Pandas is
            required for this to have an effect. Defaults to pale
            orange.
        """
        from IPython.display import display

        B, dofs, readouts = self.matrix_data(dofs, readouts)

        if tablefmt == "pandas":
            try:
                import pandas as pd
            except ModuleNotFoundError:
                tablefmt = "html"

        if tablefmt == "pandas":

            def highlight_max(data):
                return np.where(
                    abs(data) == abs(data).max(),
                    f"background-color: {highlight_color}",
                    "",
                )

            B = pd.DataFrame(B, index=dofs, columns=readouts)

            if highlight == "dof":
                style = B.style.apply(highlight_max, axis=1)
            elif highlight == "readout":
                style = B.style.apply(highlight_max, axis=0)
            elif highlight is None:
                style = B.style
            else:
                raise ValueError(
                    "Argument 'highlight' must be one of 'dof', 'readout' or None."
                )

            display(style.format(numfmt))
        else:
            return NumberTable(
                B,
                colnames=readouts,
                rownames=dofs,
                numfmt=numfmt,
            )

    def __str__(self):
        B, dofs, readouts = self.matrix_data()
        return str(NumberTable(B, colnames=readouts, rownames=dofs, numfmt="{:.2G}"))

    def matrix_data(self, dofs=None, readouts=None):
        """Generates a sensing matrix table.

        Parameters
        ----------
        dofs : iterable[str], optional
            Names of degrees of freedom to show, defaults to all if None
        readouts : iterable[str], optional
            Names of readouts to show, defaults to all if None

        Returns
        -------
        matrix : 2D numpy array, complex
        dofs : list of :class:`str`
        readouts: list of :class:`str`
        """
        dofs = dofs or self.dofs
        if readouts is not None:
            readouts = readouts
            readouts_rf = [rd for rd in self.readouts_rf if rd in readouts]
            readouts_dc = [rd for rd in self.readouts_dc if rd in readouts]
            try:
                readout_indices = [self.readouts.index(rd) for rd in readouts]
                A = self.out[:, readout_indices]
            except Exception:
                print(
                    "ValueError: Some readouts provided "
                    "are not present in the sensing matrix."
                )
                raise
        else:
            readouts = self.readouts
            readouts_rf = self.readouts_rf
            readouts_dc = self.readouts_dc
            A = self.out

        hdrs = []
        for rd in readouts:
            if rd in readouts_rf:
                hdrs.append(rd + "_I")
                hdrs.append(rd + "_Q")
            else:
                hdrs.append(rd + "_DC")
        Nd = len(dofs)
        Nr_rf = len(readouts_rf)
        Nr_dc = len(readouts_dc)
        B = np.zeros((Nd, ((2 * Nr_rf) + Nr_dc)))
        col_num = 0
        for ind, rd in enumerate(readouts):
            if rd in readouts_rf:
                B[:, col_num] = A[:, ind].real
                B[:, col_num + 1] = A[:, ind].imag
                col_num += 2
            else:
                B[:, col_num] = A[:, ind].real
                col_num += 1
        return B, dofs, hdrs

    def plot(
        self, Nrows, Ncols, figsize=(6, 5), *, dofs=None, readouts=None, r_lims=None
    ):
        import matplotlib.pyplot as plt

        dofs = np.atleast_1d(dofs or self.dofs)
        readouts = np.atleast_1d(readouts or self.readouts)

        fig, axs = plt.subplots(
            Nrows,
            Ncols,
            figsize=figsize,
            subplot_kw={"projection": "polar"},
            squeeze=False,
        )
        axs = axs.flatten()
        for idx in range(len(readouts)):
            dof_idxs = tuple(self.dofs.index(_) for _ in dofs)
            _ax = axs[idx]
            A = self.out[dof_idxs, idx]

            _ax.set_theta_zero_location("E")
            if r_lims is None or (r_lims is not None and r_lims[idx] is None):
                r_lim = (np.log10(np.abs(A)).min() - 1, np.log10(np.abs(A)).max())
            else:
                r_lim = np.log10(r_lims[idx])

            _ax.set_ylim(r_lim[0], r_lim[1] + 1)
            _ax.set_yticklabels([])

            theta = np.angle(A)
            r = np.log10(np.abs(A))
            _ax.plot(
                (theta, theta),
                (r_lim[0] * np.ones_like(r), r),
                marker="D",
                markersize=5,
            )
            _ax.set_title(self.readouts[idx])
            _ax.set_ylim(r_lim[0], r_lim[1] + 1)

        _ax.legend(self.dofs, loc="best", bbox_to_anchor=(0.5, -0.3), fontsize=8)
        plt.tight_layout(pad=1.2)
        return fig, axs


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class SensingMatrixDC(Action):
    """Computes the sensing matrix elements for various degrees of freedom and readouts
    that should be present in the model. The solution object for this action then
    contains all the information on the sensing matrix. This can be plotted in polar
    coordinates, displayed in a table, or directly accessed.

    The sensing gain is computed by calculating the gradient of each readout
    signal, which means it is a DC measurement. This will not include any
    suspension or radiation pressure effects.

    This action does not modify the states model.

    Parameters
    ----------
    dofs : iterable[str]
        String names of degrees of freedom
    readouts : iterable[str]
        String names of readouts
    d_dof : float, optional
        Small step used to compute derivative
    """

    def __init__(self, dofs, readouts, d_dof=1e-9, name="sensing_matrix_dc"):
        super().__init__(name)
        # only store string names
        self.dofs = elements_to_name(dofs)
        self.readouts = elements_to_name(readouts)
        self.d_dof = d_dof

    def _do(self, state):
        self.readouts_rf = []
        self.readouts_dc = []
        Idws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_I", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        Qdws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_Q", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        DCws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_DC", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        dcs = tuple(state.model.get(f"{dof}.DC") for dof in self.dofs)
        Nd = len(self.dofs)
        Nr = len(self.readouts)

        sol = SensingMatrixSolution(self.name)
        sol.dofs = self.dofs
        sol.readouts = self.readouts
        sol.readouts_rf = []
        sol.readouts_dc = []
        sol.vals = np.zeros((Nd, Nr, 2), dtype=complex)
        sol.out = np.zeros((Nd, Nr), dtype=complex)
        # Here we compute the gradient of the error signals
        # with respect to some DOF change
        for i in range(Nd):
            dcs[i].value -= self.d_dof
            state.sim.run_carrier()
            for j in range(Nr):
                if Idws[j] is not None:
                    sol.vals[i, j, 0] += Idws[j].get_output()
                    sol.vals[i, j, 0] += 1j * Qdws[j].get_output()
                    if i == 0:
                        sol.readouts_rf.append(self.readouts[j])
                else:
                    sol.vals[i, j, 0] += DCws[j].get_output()
                    if i == 0:
                        sol.readouts_dc.append(self.readouts[j])
            dcs[i].value += 2 * self.d_dof
            state.sim.run_carrier()
            for j in range(Nr):
                if Idws[j] is not None:
                    sol.vals[i, j, 1] += Idws[j].get_output()
                    sol.vals[i, j, 1] += 1j * Qdws[j].get_output()
                else:
                    sol.vals[i, j, 1] += DCws[j].get_output()
            # reset value
            dcs[i].value -= self.d_dof

        # Compute the gradients
        sol.out = (sol.vals[:, :, 1] - sol.vals[:, :, 0]) / (2 * self.d_dof)
        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].extend((f"{_}.DC" for _ in self.dofs))
        return memo


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class SensingMatrixAC(Action):
    """Computes the sensing matrix elements for various degrees of freedom and readouts
    that should be present in the model. The solution object for this action then
    contains all the information on the sensing matrix. This can be plotted in polar
    coordinates, displayed in a table, or directly accessed.

    The sensing gain is computed by calculating the gradient of each readout
    signal, which means it is a DC measurement. This will not include any
    suspension or radiation pressure effects.

    This action does not modify the states model.

    Parameters
    ----------
    dofs : iterable[str]
        String names of degrees of freedom
    readouts : iterable[str]
        String names of readouts
    f : float
        Frequency to measure sensing matrix at
    """

    def __init__(self, dofs, readouts, f=1e-3, name="sensing_matrix_ac"):
        super().__init__(name)
        # only store string names
        self.dofs = elements_to_name(dofs)
        self.readouts = elements_to_name(readouts)
        self.f = f

        self.nodes = []
        self.nodes.extend([readout + ".I" for readout in self.readouts])
        self.nodes.extend([readout + ".Q" for readout in self.readouts])

    def _do(self, state):
        sol = SensingMatrixSolution(self.name)
        sol.dofs = self.dofs
        sol.readouts = self.readouts

        sol.freqresp = FrequencyResponse((self.f,), self.dofs, self.nodes)._do(state)

        sol.out = np.zeros((len(self.dofs), len(self.readouts)), dtype=np.complex128)
        for i, dof in enumerate(self.dofs):
            for j, readout in enumerate(self.readouts):
                sol.out[i, j] = np.real(sol.freqresp[dof, readout + ".I"])
                sol.out[i, j] += 1j * np.real(sol.freqresp[dof, readout + ".Q"])

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["input_nodes"].extend((dof, ("input",)) for dof in self.dofs)
        memo["output_nodes"].extend((node, ("output",)) for node in self.nodes)
        return memo


class CheckLinearitySolution(BaseSolution):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = None
        self.lock_names = ()


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class CheckLinearity(Action):
    """An action that shows the relationships between all DOFs and all error signals, to
    check whether they are related linearly. Plotted for DOFs starting at their initial
    values and up until their initial values + 2*gain*intial error signal.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each :class:`finesse.analysis.actions.locks.RunLocks`
        step. Acts like \\*locks parameter in
        :class:`finesse.analysis.actions.locks.RunLocks`: if not provided, all locks in
        model are used.

    num_points : int
        Number of points to plot in the DOF range.

    plot_results : boolean
        Whether or not to plot results (requires
        matplotlib)

    xlim : list or None
        Defines (half of) the range of DOF values
        over which to plot the error signals. If
        not specified, gains are used to find a
        useful range of DOF values to plot over.

    name : str
        Name of the action.
    """

    def __init__(
        self, *locks, num_points=10, plot_results=True, xlim=None, name="run locks"
    ):
        super().__init__(name)
        self.locks = elements_to_name(locks)
        # Round up to the nearest odd integer, so that the plot always
        # includes the current points.
        self.num_points = num_points + 1 if num_points % 2 == 0 else num_points
        self.xlim = xlim
        self.plot_results = plot_results

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, SparseMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = tuple(lck for lck in state.model.locks if lck.enabled)
        else:
            locks = tuple(
                state.model.elements[name]
                for name in self.locks
                if not state.model.elements[name].enabled
            )

        if self.xlim is not None:
            if len(self.xlim) != len(locks):
                raise Exception("Number of locks and xlim not equal.")
            # else:
            # xlim = self.xlim # Not used

        out_wss = OrderedSet(  # workspaces can be in both lists
            (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
        )

        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    out_wss,
                ),
                None,
            )
            for lock in locks
        )
        sol = CheckLinearitySolution(self.name)
        N = len(locks)
        # Store initial parameters in case of failure so we can reset the model
        initial_parameters = tuple(float(lock.feedback) for lock in locks)
        initial_errors = tuple(
            float(dw.get_output() - locks[dws.index(dw)].offset) for dw in dws
        )
        sol.results = np.zeros((N, N, 2, self.num_points))
        sol.lock_names = tuple(lock.name for lock in locks)

        err_sigs = [lck.error_signal for lck in locks]
        err_sig_names = [sig.name for sig in err_sigs]
        readout_names = [sig.readout.name for sig in err_sigs]
        lock_dof_names = [deref(lck.feedback).owner.name for lck in locks]

        sensing_matrix = state.apply(SensingMatrixDC(lock_dof_names, readout_names))
        gain_matrix = np.zeros((N, N))
        for dof_idx in range(N):
            for rd_idx in range(N):
                err_sig = err_sig_names[rd_idx]
                val = sensing_matrix.out[dof_idx, rd_idx]
                if "_Q" in err_sig:
                    gain = val.imag
                else:
                    gain = val.real
                gain_matrix[rd_idx, dof_idx] = gain

        # Index i runs over error signals
        for i in range(N):
            # Index j runs over DOFs
            initial_error = initial_errors[i]
            for j in range(N):
                initial_param = initial_parameters[j]

                if self.xlim is not None:
                    dof_list = np.linspace(
                        initial_param - self.xlim[j],
                        initial_param + self.xlim[j],
                        self.num_points,
                    )
                elif gain_matrix[i, j] == 0:
                    dof_list = np.linspace(
                        initial_param - 1, initial_param + 1, self.num_points
                    )
                else:
                    lock_gain = -1 / gain_matrix[i, j]
                    dof_list = np.linspace(
                        initial_param - 0 * lock_gain * initial_error,
                        initial_param + 2 * lock_gain * initial_error,
                        self.num_points,
                    )

                rel_dof_list = dof_list - initial_param
                sol.results[i, j, 0] = rel_dof_list
                for idx, dof_val in enumerate(dof_list):
                    deref(locks[j].feedback).value = dof_val
                    state.sim.run_carrier()
                    new_error = dws[i].get_output() - locks[i].offset
                    sol.results[i, j, 1, idx] = new_error
                deref(locks[j].feedback).value = initial_param

        if self.plot_results:
            import matplotlib.pyplot as plt

            plt.rcParams["figure.figsize"] = [1.5 * N, 1.5 * N]
            if N > 1:
                fig, axs = plt.subplots(N, N)
                for i in range(N):
                    for j in range(N):
                        axs[i][j].plot(
                            sol.results[i, j, 0, 0:], sol.results[i, j, 1, 0:], zorder=0
                        )
                        axs[i][j].ticklabel_format(
                            axis="y", style="sci", scilimits=(0, 0)
                        )
                for ax, name in zip(axs[-1], lock_dof_names):
                    ax.set_xlabel(name, labelpad=10, fontsize=14)
                for ax, name in zip(axs[:, 0], err_sig_names):
                    ax.set_ylabel(name, labelpad=10, fontsize=14)
                plt.tight_layout()
                plt.subplots_adjust(wspace=0.6, hspace=0.6)
            elif N == 1:
                plt.plot(sol.results[0, 0, 0, 0:], sol.results[0, 0, 1, 0:])
                plt.xlabel(lock_dof_names[0], fontsize=14)
                plt.ylabel(err_sig_names[0], fontsize=14)
            else:
                print("No existing locks to display.")

            plt.show()
        return sol

    def _requests(self, model, memo, first=True):
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
                    model.elements[name].feedback.parameter.full_name
                )
                rd_name = model.elements[name].error_signal.name
                if "_DC" not in rd_name:
                    memo["changing_parameters"].append(
                        model.elements[name].error_signal.readout.name + ".phase"
                    )


class GetErrorSignalsSolution(BaseSolution):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = None
        self.lock_names = ()


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class GetErrorSignals(Action):
    """An action that quickly calculates the current  error signals for all or a subset
    of locks in a model.

    Parameters
    ----------
    *locks : list, optional
        A list of lock names to compute the error signals for.
        If not provided, all locks in model are used.

    name : str
        Name of the action.
    """

    def __init__(self, *locks, name="get error signals"):
        super().__init__(name)
        self.locks = elements_to_name(locks)

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, SparseMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = state.model.locks
        else:
            locks = tuple(state.model.elements[lock] for lock in self.locks)

        out_wss = OrderedSet(  # workspaces can be in both lists so combine them
            (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
        )

        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    out_wss,
                ),
                None,
            )
            for lock in locks
        )

        state.sim.run_carrier()
        N = len(locks)
        sol = GetErrorSignalsSolution(self.name)
        sol.results = np.zeros(N)
        sol.lock_names = tuple(lock.name for lock in locks)
        for i in range(N):
            res = dws[i].get_output() - locks[i].offset
            sol.results[i] = res

        return sol

    def _requests(self, model, memo, first=True):
        pass
