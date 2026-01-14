import logging

from libc.stdlib cimport free, calloc

cimport cython

from finesse import BeamParam
from finesse.env import warn
from finesse.frequency cimport Frequency, FrequencyContainer
from finesse.cymath cimport complex_t
from finesse.cymath.math cimport float_eq
from finesse.cymath.complex cimport conj
from finesse.cymath.gaussbeam cimport beam_param, transform_q, inv_transform_q
from finesse.symbols import Constant
from finesse.exceptions import BeamTraceException, NotChangeableDuringSimulation
from finesse.components.modal.cavity cimport CavityWorkspace
from finesse.warnings import CavityUnstableWarning
from finesse.utilities.collections import OrderedSet
from finesse.utilities.cyomp cimport determine_nthreads_even
from finesse.parameter cimport Parameter

from finesse.simulations.workspace cimport ABCDWorkspace
from finesse.element_workspace cimport ElementWorkspace

LOGGER = logging.getLogger(__name__)


cdef class BaseSimulation:
    """This base level class should be inherited by others to perform the exact
    needs of a particular type of simulation. This BaseSimulation class contains
    the methods to store common settings as well as functionality for beam tracing
    through a model, and detecting which beam parameters will be changing.
    Developers should ensure that methods raising `NotImplementedError` are defined
    in any deriving classes.
    """
    def __init__(self, model, unicode name, dict simulation_options):
        self.model = model
        self.name = name
        self.initial_trace_sol = None
        self.trace = NULL
        self.changing_mismatch_couplings = ()
        self.contingent_trace_forests = {}
        self.needs_reflag_changing_q = False
        self.simulation_options = simulation_options
        self.workspace_name_map = {}

    def __dealloc__(self):
        if self.trace:
            free(self.trace)

    def build_carrier_solver(self, nodes, optical_frequencies):
        raise NotImplementedError()

    def build_signal_solver(self, nodes, optical_frequencies, signal_frequencies):
        raise NotImplementedError()

    def build(self):
        cf = self.carrier_frequencies_to_use
        self.carrier = self.build_carrier_solver(self.optical_nodes_to_use, cf)

        if self.compute_signals:
            osf, sf, =self.signal_optical_frequencies_to_use, self.signal_frequencies_to_use
            self.signal = self.build_signal_solver(self.optical_nodes_to_use + self.signal_nodes_to_use, osf, sf)

        self.setup_build()

    def setup_build(self):
        raise NotImplementedError()

    def pre_build(self):
        """
        Pre-build performs some common setup routine that should be applicable to
        any deriving simulation class. This method performs the following tasks:


            * Checks if the signal frequency (fsig) is changing and if its value
              is None. If so, it sets a default value of 1 Hz.
            * Creates a list of all the changing parameters in the simulation.
            * Creates a set of tunable parameters from the changing parameters.
            * Determines if signal computation is required based on the value of
              fsig.f. Sets self.compute_signals
            * Determines if the simulation is modal or not. Sets self.is_modal
            * Initializes the model settings
            * Initializes the simulation configuration data.
            * Generates carrier frequencies based on the model.
            * Initializes the trace forest if the simulation is modal.
            * Determines the changing beam parameters if the simulation is modal.

        """
        if self.model.fsig.f.is_changing and self.model.fsig.f.value is None:
            warn(
                "Signal frequency (fsig) was set to None but simulation needs it. "
                "Setting default value of 1 Hz"
            )
            self.model.fsig.f.value = 1

        self.changing_parameters = OrderedSet(
            (p for p in self.model.all_parameters if p.is_changing)
        )

        for p in self.changing_parameters:
            if not p.changeable_during_simulation:
                raise NotChangeableDuringSimulation(
                    f"Parameter {p} cannot be changed during a simulation. Loop over this parameter changed with a Python for loop instead."
                )

        self.tunable_parameters = OrderedSet(
            p for p in self.changing_parameters if p.is_tunable
        )
        self.compute_signals = self.model.fsig.f.value is not None
        self.is_modal = self.model.is_modal
        self.initialise_model_settings()
        self.initialise_sim_config_data()

        self.optical_nodes_to_use = self.model.optical_nodes
        self.carrier_frequencies_to_use = self.generate_carrier_frequencies()

        if self.compute_signals:
            self.signal_nodes_to_use = list(self.model.get_active_signal_nodes())
            self.signal_optical_frequencies_to_use, self.signal_frequencies_to_use = self.generate_signal_frequencies(
                self.optical_nodes_to_use + self.signal_nodes_to_use,
                self.carrier_frequencies_to_use
            )

        self.initialise_trace_forest(self.model.optical_nodes)

        for el in self.model.elements.values():
            el._setup_changing_params()


    def post_build(self):
        """Post build calls functions that should be called after everything else has been
        built. For example, detectors that might rely on components being set up.
        """
        if self.carrier is None:
            raise RuntimeError("No carrier simulation was made")
        if self.compute_signals and self.signal is None:
            raise RuntimeError("No carrier simulation was made")

        self.setup_output_workspaces()

    def unbuild(self):
        if self.carrier is not None:
            self.carrier.destruct()
        if self.signal is not None:
            self.signal.destruct()

        for p in self.changing_parameters:
            # Reset all changing parameters so their type can change again
            (<Parameter>p).__disable_state_type_change = False

        # Code below can be used in debug mode to determine if anyone is keeping any
        # references to this matrix object, meaning its memory can't be freed.
        # This takes ~20ms to do so makes a difference for quick models. Maybe we need
        # a debug mode

        #_ref = self._M
        #self._M = None

        # refs = gc.get_referrers(_ref)
        # Nref = len(refs)
        # if Nref > 0:
        #     warn(
        #         f"Something other than the Simulation object (N={Nref}) is keeping"
        #         f" a reference to the matrix object {repr(self._M)}."
        #         " Could lead to excessive memory usage if not released."
        #     )
        #     for _ in refs:
        #         warn(f" - {repr(_)}")
        #del _ref

    cpdef update_cavities(self):
        cdef CavityWorkspace ws
        for ws in self.cavity_workspaces.values():
            ws.update()

    cpdef update_map_data(self):
        """This will cycle through each map being used and if
        it is defined by a function it will be evaluated again.
        """
        cdef ABCDWorkspace ws
        # This could be made more efficient by just storing the
        # a list of those with changing maps
        for ws in self.to_scatter_matrix_compute:
            ws.update_map_data()

    cdef int set_gouy_phases(self) except -1:
        cdef ABCDWorkspace ws
        cdef int rtn

        for ws in self.gouy_phase_workspaces:
            if ws.fn_gouy_c is not None:
                rtn = ws.fn_gouy_c.func(ws)
            elif ws.fn_gouy_py is not None:
                rtn = ws.fn_gouy_py(ws)
            if rtn:
                return rtn

        return 0

    cpdef modal_update(self):
        """Updates HOM related dependencies / properties of the model.

        These updates are as follows:

         * Execute a beam trace on the changing trace trees
         * Computes the changing scattering matrices
         * Calculates the Gouy phase of Spaces and Laser power coefficients

        Returns
        -------
        validity : bool
            True if the modal update was successful, or False if an unstable
            cavity combination prevented a beam trace from being performed.
        """
        # Evaluate changing properties of cavity workspaces
        self.update_cavities()

        if self.retrace:
            if not self.trace_beam():
                return False

        # Update the changing Gouy phases at spaces
        # and TEM Gouy phases at lasers
        self.set_gouy_phases()

        return True


    cdef int _determine_changing_beam_params(
        self, TraceForest forest=None, bint set_tree_node_ids=True,
    ):
        if self.trace == NULL:
            raise RuntimeError("trace is NULL")

        cdef:
            Py_ssize_t i
            Py_ssize_t num_nodes = len(self.model.optical_nodes)
            ABCDWorkspace kws

        # Re-set all beam parameter changing flags to false initially
        for i in range(num_nodes):
            self.trace[i].is_fixed = True

        if self.retrace:
            LOGGER.info("Flagging changing beam parameters.")
            # Prepare the forest for simulation by setting all the node_id attributes
            # and flag the corresponding self.trace entries as changing
            self._setup_trace_forest(forest, set_tree_node_ids)

        # Now tell each knm workspace whether it is changing or not
        # so that only changing scattering matrices get recomputed
        # from here on
        if self.to_scatter_matrix_compute is not None:
            for kws in self.to_scatter_matrix_compute:
                kws.flag_changing_beam_parameters(self.changing_mismatch_edges)

        return 0

    def is_component_in_mismatch_couplings(self, comp):
        """Determines whether the connector `comp` is associated with any
        of the node couplings in the stored changing mismatch couplings.

        .. note::

            This method can be replaced if connectors eventually use more
            granular refill flags --- i.e. per coupling refill flags. Then
            the check for refilling that coupling can simply include the
            condition ``(from_node, to_node) in sim.changing_mismatch_couplings``.
        """
        return any(node.component is comp for node, _ in self.changing_mismatch_couplings)

    cdef _setup_trace_forest(self, TraceForest forest=None, bint set_tree_node_ids=True):
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

        if forest is None:
            forest = self.trace_forest

        for tree_idx in range(forest.size()):
            tree = forest.forest[tree_idx]
            self._setup_single_trace_tree(tree, set_tree_node_ids)

    cdef _setup_single_trace_tree(self, TraceTree tree, bint set_tree_node_ids=True):
        cdef:
            TraceTree ltree = tree.left
            TraceTree rtree = tree.right

        # Only ever need to do this once, so avoid repeating when reflagging
        # changing beam params after exiting unstable cavity regions
        if set_tree_node_ids:
            tree.node_id = self.trace_node_index[tree.node]
            tree.opp_node_id = self.trace_node_index[tree.node.opposite]

        self.trace[tree.node_id].is_fixed = False
        self.trace[tree.opp_node_id].is_fixed = False

        if ltree is not None:
            self._setup_single_trace_tree(ltree)
        if rtree is not None:
            self._setup_single_trace_tree(rtree)

    cdef tuple _find_new_unstable_cavities(self) :
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            CavityWorkspace cav_ws
            bint source_is_cav
            double gx, gy

            list ch_unstable_cavities = []

        for tree_idx in range(self.trace_forest.size()):
            tree = self.trace_forest.forest[tree_idx]

            if tree.is_source:
                cav_ws = self.cavity_workspaces.get(tree.dependency)
                source_is_cav = cav_ws is not None
                if source_is_cav: # Tree is an internal cavity tree
                    # The geometrically changing cavity has become unstable
                    # so inform that this is the case
                    if not cav_ws.is_stable:
                        ch_unstable_cavities.append(cav_ws.owner)

                        gx = cav_ws.gx
                        gy = cav_ws.gy
                        if float_eq(gx, gy):
                            warn(
                                f"Cavity {repr(tree.dependency.name)} is unstable with "
                                f"g = {gx}",
                                CavityUnstableWarning
                            )
                        else:
                            warn(
                                f"Cavity {repr(tree.dependency.name)} is unstable with "
                                f"gx = {gx}, gy = {gy}",
                                CavityUnstableWarning
                            )

        if not ch_unstable_cavities:
            return ()

        # Return tuple of the unstable cavities sorted by name so that
        # all permutations of the same combination of cavities give same
        # tuple --- important for look-ups in contingent_trace_forests dict
        return tuple(sorted(ch_unstable_cavities, key=lambda x: x.name))

    cdef TraceForest _initialise_contingent_forest(self, tuple unstable_cavities) :
        cdef TraceForest contingent_forest = TraceForest(self.model, self.trace_forest.symmetric)
        cdef TraceForest model_trace_forest = self.model.trace_forest
        cdef list order = model_trace_forest.dependencies.copy()
        for uc in unstable_cavities:
            order.remove(uc)

        # If there are no dependencies left after disabling the
        # unstable cavities then a beam trace cannot be performed
        # at this data point so no forest can be planted
        if not order:
            warn(
                "Cannot build a contingent trace forest as the simulation "
                "is in a regime with no stable cavities nor Gauss objects.",
                CavityUnstableWarning
            )
            return None

        contingent_forest.plant(order)

        if self._determine_changing_beam_params(contingent_forest):
            return None

        return contingent_forest

    @cython.initializedcheck(False)
    cdef void _propagate_trace(self, TraceTree tree, bint symmetric) noexcept:
        cdef:
            TraceTree ltree = tree.left
            TraceTree rtree = tree.right

            const NodeBeamParam* q1 = &self.trace[tree.node_id]
            complex_t qx1 = q1.qx.q
            complex_t qy1 = q1.qy.q
            complex_t qx2, qy2

        if ltree is not None:
            # For non-symmetric traces we have some special checks
            # to do on trees which couldn't be reached from the
            # other dependency trees. Note these are only performed
            # on the left tree; see TraceForest._add_backwards_nonsymm_trees
            # for details.
            if symmetric or (not tree.do_nonsymm_reverse and not tree.do_inv_transform):
                qx2 = transform_q(tree.left_abcd_x, qx1, tree.nr, ltree.nr)
                qy2 = transform_q(tree.left_abcd_y, qy1, tree.nr, ltree.nr)
            elif tree.do_inv_transform:
                # Can't reach tree directly but there is a coupling from ltree.node
                # to tree.node so apply the inverse abcd law to get correct q
                qx2 = inv_transform_q(tree.left_abcd_x, qx1, tree.nr, ltree.nr)
                qy2 = inv_transform_q(tree.left_abcd_y, qy1, tree.nr, ltree.nr)
            else:
                # Really is no way to get to the node (no coupling from ltree.node to
                # tree.node) so only option now is to reverse q for ltree node entry
                qx2 = -conj(qx1)
                qy2 = -conj(qy1)

            self.trace[ltree.node_id].qx.q = qx2
            self.trace[ltree.node_id].qy.q = qy2
            if symmetric:
                self.trace[ltree.opp_node_id].qx.q = -conj(qx2)
                self.trace[ltree.opp_node_id].qy.q = -conj(qy2)

            self._propagate_trace(ltree, symmetric)

        if rtree is not None:
            qx2 = transform_q(tree.right_abcd_x, qx1, tree.nr, rtree.nr)
            qy2 = transform_q(tree.right_abcd_y, qy1, tree.nr, rtree.nr)

            self.trace[rtree.node_id].qx.q = qx2
            self.trace[rtree.node_id].qy.q = qy2
            if symmetric:
                self.trace[rtree.opp_node_id].qx.q = -conj(qx2)
                self.trace[rtree.opp_node_id].qy.q = -conj(qy2)

            self._propagate_trace(rtree, symmetric)

    cpdef trace_beam(self) :
        """Traces the beam through the paths which are dependent upon changing
        geometric parameter(s).

        This method will modify those entries in the ``self.trace`` C array
        which were previously determined to have changing beam parameter values.

        Returns
        -------
        validity : bool
            True if the tracing was successful, or False if an unstable
            cavity combination prevented a beam trace from being performed.

        Raises
        ------
        ex : :class:`.BeamTraceException`
            If the ``"unstable_handling"`` entry of the associated
            :attr:`.Model.sim_trace_config` dict is ``"abort"`` and
            any unstable cavities were encountered.
        """
        cdef:
            TraceTree tree
            Py_ssize_t tree_idx

            CavityWorkspace cav_ws
            bint source_is_cav

            complex_t qx_src, qy_src

            # The actual trace forest which gets traced. In most circumstances
            # this will be self.trace_forest but if changing cavities enter an
            # unstable regime then this will be temporarily swapped out for the
            # contingent forest for this data point (see below).
            TraceForest trace_forest

            # Objects necessary for dealing with newly unstable cavities
            tuple ch_unstable_cavities
            TraceForest contingent_forest

        # No changing beam parameters, do nothing
        if self.trace_forest.empty():
            return True

        # First we loop over the source trees and find any changing
        # cavities which have become unstable
        ch_unstable_cavities = self._find_new_unstable_cavities()

        # If we did find any newly unstable cavities then the current trace_forest
        # is invalidated at the current data point so we must build a new forest with
        # the unstable cavities disabled
        # NOTE (sjr) Don't worry about increased Python interaction in
        #            this block as this will rarely be executed anyway
        if ch_unstable_cavities:
            unstable_handling = self.model.sim_trace_config["unstable_handling"]

            # Abort simulation if tracing config set-up to do so when
            # encountering any unstable cavities
            if unstable_handling == "abort":
                raise BeamTraceException(
                    "Aborting simulation due to presence of unstable cavities: "
                    f"{','.join([cav.name for cav in ch_unstable_cavities])}"
                )
            # Or if tracing config is set-up to abort only the retrace when
            # any unstable cavities encountered, flag this to notify that
            # appropriate detector outputs should be masked
            if unstable_handling == "mask":
                LOGGER.info(
                    "Aborting retrace as simulation tracing configuration is set-up "
                    "to mask at any data point(s) where unstable cavities occur."
                )
                return False

            LOGGER.info(
                "Attempting to use a contingent trace forest due "
                "to the presence of unstable cavities"
            )
            # Look-up the combination of unstable cavities to see if a
            # contingent forest was already built from this
            contingent_forest = self.contingent_trace_forests.get(ch_unstable_cavities)

            # No previous forest built from the given combination of disabled
            # unstable cavities so need to build one here
            if contingent_forest is None:
                LOGGER.debug(
                    "For unstable cavity combination %s no cached contingent "
                    "trace forest found, now attempting to build a new one...",
                    [uc.name for uc in ch_unstable_cavities],
                )
                contingent_forest = self._initialise_contingent_forest(ch_unstable_cavities)
                # If there are no dependencies left after disabling the
                # unstable cavities then a beam trace cannot be performed
                # at this data point so inform of this on return
                if contingent_forest is None:
                    return False

                # Cache the contingent forest for this combination of unstable
                # cavities as these typically occur in blocks (or across strides)
                # of data points so we don't want to keep rebuilding the same
                # contingency forests for identical unstable cavity combos
                self.contingent_trace_forests[ch_unstable_cavities] = contingent_forest
            else:
                LOGGER.debug(
                    "For unstable cavity combination %s found and using "
                    "cached contingent trace forest:%s",
                    [uc.name for uc in ch_unstable_cavities],
                    contingent_forest
                )

            # Make sure only the correctly changing beam parameters, according
            # to self.trace_forest, get reflagged when exiting from the unstable
            # region again
            self.needs_reflag_changing_q = True

            # Use the contingent forest for this data point
            trace_forest = contingent_forest

        # Otherwise we just use the standard changing trace forest of the simulation
        else:
            trace_forest = self.trace_forest

            # If we've just exited an unstable cavity region where a contingent trace
            # forest was being used, then we need to reflag the beam parameters which
            # are changing
            if self.needs_reflag_changing_q:
                if self._determine_changing_beam_params(forest=None, set_tree_node_ids=False):
                    return False
                self.needs_reflag_changing_q = False

        # Now do the actual beam tracing by simply traversing the forest
        # and propagating the beam through each tree
        for tree_idx in range(trace_forest.size()):
            tree = trace_forest.forest[tree_idx]

            if tree.is_source:
                cav_ws = self.cavity_workspaces.get(tree.dependency)
                source_is_cav = cav_ws is not None

                if not source_is_cav: # Source tree is from a Gauss
                    # TODO (sjr) Should probably make some workspace for Gauss objects
                    #            which then uses cy_expr's for evaluating these things
                    #            if they're symbolic. But for now this will do.
                    qx_src = complex(tree.dependency.qx.q)
                    qy_src = complex(tree.dependency.qy.q)
                else: # Source tree is from a Cavity
                    qx_src = cav_ws.qx
                    qy_src = cav_ws.qy

                self.trace[tree.node_id].qx.q = qx_src
                self.trace[tree.node_id].qy.q = qy_src
                if trace_forest.symmetric:
                    self.trace[tree.opp_node_id].qx.q = -conj(qx_src)
                    self.trace[tree.opp_node_id].qy.q = -conj(qy_src)

            self._propagate_trace(tree, trace_forest.symmetric)

        return True

    cpdef run_carrier(self) :
        """Runs the carrier matrix solver for the current state of the model.
        This will update all the C based structs with the current model state so
        that filling and calculations can be performed.

        Returns
        -------
        validity : bool
            True if this was a valid run, or False if a recoverable error occurred
            which results in the output being invalid for this call.
        """
        # NOTE (sjr) Just updating all parameter values on each call to run for
        #            now. This may not be the most optimal thing to do, but it
        #            avoids duplicating these parameter update calls in different
        #            places (e.g. refill, compute_knm_matrices, set_gouy_phases) and
        #            should be safe in that no parameters get accidentally missed at
        #            any data point.
        # ddb - this just updates everything, even things that are not changing as
        # it acts on all the workspaces, probably not the best idea
        self.update_all_parameter_values()

        # Update HOM stuff
        if self.is_modal:
            # Immediately return if invalid beam trace region encountered
            # no need to go ahead and fill or solve as they won't be used
            if not self.modal_update():
                return False

        self.carrier.run()

        return True

    cpdef run_signal(self, solve_noises=True) :
        """Runs the signal matrix solver for the current state. This function should assume that
        a call to the `run_carrier` method has preceeded it. Many modal and parameter updates
        should happen in there already, so do not need to be repeated here.
        """
        self.model_settings.fsig = float(self.model.fsig.f.value)
        # Probably some other preparatory stuff needs to go here in the future
        self.signal.run()

        # Then ask components for their noise contributions
        if solve_noises and self.signal.noise_sources:
            self.signal.fill_noise_inputs()
            self.signal.solve_noises()

    def setup_output_workspaces(self):
        from finesse.detectors.general import NoiseDetector
        from finesse.components.readout import _Readout
        from finesse.detectors.workspace import DetectorWorkspace

        # Once the simulations are started we can tell all the detectors to
        # prepare themselves
        self.detector_workspaces = []
        self.readout_workspaces = []

        for rd in self.model.get_elements_of_type(_Readout):
            # Readouts can emulate multiple detectors, so here we
            # get a collection of them depending on what the readout
            # is doing and add them to the list
            for output, ws in rd._get_output_workspaces(self).items():
                if not isinstance(ws, DetectorWorkspace):
                    raise TypeError(f"Readout detector ({rd}) workspace ({output.ws}) not a DetectorWorkspace type")
                self.readout_workspaces.append(ws)
                self.workspace_name_map[output.name] = ws
                if rd.output_detectors:
                    self.detector_workspaces.append(ws)

        for det in self.model.detectors:
            ws = det._get_workspace(self)
            self.workspace_name_map[det.name] = ws

            if ws is not None:
                if not isinstance(ws, DetectorWorkspace):
                    raise TypeError(f"Detector ({det}) workspace ({ws}) not a DetectorWorkspace type")

                self.detector_workspaces.append(ws)
                if self.signal and isinstance(ws.owner, NoiseDetector):
                    self.signal.workspaces.noise_detectors.append(ws)

        for _ in self.detector_workspaces:
            _.compile_cy_exprs()

        if self.signal:
            self.signal.workspaces.detector_list_to_C()

    def __enter__(self):
        self.pre_build()
        self.build()
        self.post_build()

    def __exit__(self, type_, value, traceback):
        self.unbuild()

    cpdef update_all_parameter_values(self) :
        """Loops through all workspaces to update the C structs so they
        represent the current model element parameter values.
        """
        cdef:
            ElementWorkspace ws

            Py_ssize_t i
            # TODO (sjr) Should probably cache these or move away from
            #            lists for best performance
            Py_ssize_t Ncws = len(self.workspaces)

        for i in range(Ncws):
            ws = self.workspaces[i]
            ws.update_parameter_values()

    def get_q(self, node):
        """Returns a tuple of (qx, qy) for a given node. The returned
        value is only valid until this simulations trace forest has
        been updated.

        Parameters
        ----------
        node : :class:`finesse.components.OpticalNode`
            Node to get beam parameters at

        Returns
        -------
        (qx, qy)
            Tuple of x and y beam parameters
        """
        cdef NodeBeamParam *nodebp

        idx = self.trace_node_index[node]
        if idx >= 0 and idx < len(self.model.optical_nodes):
            nodebp = &self.trace[idx]
            return (
                BeamParam(q=nodebp.qx.q, nr=nodebp.qx.nr, wavelength=nodebp.qx.wavelength),
                BeamParam(q=nodebp.qy.q, nr=nodebp.qy.nr, wavelength=nodebp.qy.wavelength),
            )
        else:
            raise IndexError("Node index is not in simulation")

    cdef initialise_trace_forest(self, optical_nodes) :
        cdef TraceForest model_trace_forest
        cdef double nr

        self.trace_node_index = {n: i for i, n in enumerate(optical_nodes)}

        # Before we setup the workspaces some initial beam trace must be done
        # so that workspaces can initialise themselves
        if self.is_modal:
            # Make sure the model trace forest gets re-planted
            # when building a new simulation
            self.model._rebuild_trace_forest = True
            LOGGER.info(
                "Performing initial beam trace with configuration options:\n    %s",
                self.model.sim_trace_config,
            )
            # Plant the model trace_forest and execute initial beam trace
            self.initial_trace_sol = self.model.beam_trace(**self.model.sim_initial_trace_args)
            model_trace_forest = self.model.trace_forest
            self.nodes_with_changing_q = model_trace_forest.get_nodes_with_changing_q()
            self.changing_mismatch_edges = OrderedSet()

            LOGGER.info(
                "Nodes with changing q during simulation:\n    %s",
                self.nodes_with_changing_q,
            )
            self.retrace = self.model.sim_trace_config["retrace"]
            self.trace = <NodeBeamParam*> calloc(len(optical_nodes), sizeof(NodeBeamParam))
            if not self.trace:
                raise MemoryError()

            for i, n in enumerate(optical_nodes):
                qx, qy = self.initial_trace_sol[n]
                nr = qx.nr
                self.trace[i] = NodeBeamParam(
                    beam_param(qx.q, nr, self.model_settings.lambda0),
                    beam_param(qy.q, nr, self.model_settings.lambda0),
                    n in self.nodes_with_changing_q
                )

            if self.retrace:
                # Construct the forest of changing trace trees - it's important
                # that this is done before initialising connector workspaces as
                # they need the changing forest to be present for refill flag
                self.trace_forest = model_trace_forest.make_changing_forest()
                self.retrace &= not self.trace_forest.empty()

                if self.retrace:
                    LOGGER.info(
                        "Determined changing trace trees:%s", self.trace_forest
                    )
                    # Get the nodes at which trees of the changing forest intersect
                    # with trees of the full forest which have different trace
                    # dependencies. These couplings will have potentially changing
                    # mode mismatches during the simulation.
                    self.changing_mismatch_couplings = self.trace_forest.find_potential_mismatch_couplings(
                        model_trace_forest
                    )
                    # The above returns node objects. It is more useful to also store
                    # the equivalent simulation specific "node IDs" which is just an
                    # integer and used more in the cythonised code as some nodes get
                    # dropped when not used in a simulation.
                    # Optical nodes for signal and carrier all have the same IDs
                    for i, (ni, no) in enumerate(self.changing_mismatch_couplings):
                        self.changing_mismatch_edges.add(
                            tuple((self.trace_node_index[ni], self.trace_node_index[no]))
                        )

                    if self.changing_mismatch_couplings:
                        LOGGER.info(
                            "Found changing mismatched node couplings: %s",
                            [f"{n1.full_name} -> {n2.full_name}"
                            for n1, n2 in self.changing_mismatch_couplings]
                        )
            else:
                self.trace_forest = TraceForest(self.model, self.model.sim_trace_config["symmetric"])
        else:
            # just make an empty TraceForest
            self.trace_forest = TraceForest(self.model, self.model.sim_trace_config["symmetric"])

    cdef initialise_model_settings(self) :
        self.model_settings = self.model._settings

        if self.model.fsig.f.value is None:
            self.model_settings.fsig = 0
        else:
            self.model_settings.fsig = float(self.model.fsig.f.value)

    cdef initialise_sim_config_data(self) :
        # Nominal number of threads will be Nhoms / 10
        self.config_data.nthreads_homs = determine_nthreads_even(self.model_settings.num_HOMs, 10)

        LOGGER.info("Using %d threads for HOM parallel loops.", self.config_data.nthreads_homs)

    def generate_carrier_frequencies(self):
        """Returns a list of Frequency objects that the model has requested"""
        from finesse.frequency import Frequency, generate_frequency_list
        if len(self.model._frequency_generators) == 0:
            # Nothing in the model is generating a carrier frequency. Typical
            # situation is when no laser is included for signal modelling.
            # Simple solution, just use a default 0Hz
            frequencies_to_use = [Constant(0.0)]
        else:
            frequencies_to_use = generate_frequency_list(self.model)

        carrier_frequencies = list()

        LOGGER.info("Generating simulation with user carrier frequencies %s", self.model.frequencies)

        for i, f in enumerate(self.model.frequencies):
            try:
                f_name = str(f.eval(keep_changing_symbols=True))
            except AttributeError:
                f = Constant(f)
                f_name = str(f)

            carrier_frequencies.append(Frequency(f_name, f, index=i))

        N = len(self.model.frequencies)
        LOGGER.info("Generating simulation with carrier frequencies %s", frequencies_to_use)
        for i, f in enumerate(frequencies_to_use):
            carrier_frequencies.append(
                Frequency(
                    str(f.eval(keep_changing_symbols=True)),
                    f,
                    index=N+i
                )
            )

        fcnt = FrequencyContainer(carrier_frequencies)
        return fcnt

    def generate_signal_frequencies(self, nodes, FrequencyContainer carrier_optical_frequencies):
        """Generates the optical, mechanical, and electrical frequencies that should be
        modelled by the signal simulation.
        """
        from finesse.components.node import NodeType

        optical_frequencies = [] # All optical frequencies are present at all nodes
        # elec and mech can have different frequencies on a per node basis
        signal_frequencies = {}

        for i, f in enumerate(carrier_optical_frequencies.frequencies):
            fp = f.f + self.model.fsig.f.ref
            fm = f.f - self.model.fsig.f.ref

            optical_frequencies.append(
                Frequency(str(fp.eval(keep_changing_symbols=True)),
                            fp, index=2*i, audio_order=1,
                            audio=True, audio_carrier_index=i,
                            audio_carrier_object=f)
            )
            optical_frequencies.append(
                Frequency(str(fm.eval(keep_changing_symbols=True)),
                            fm, index=2*i+1, audio_order=-1,
                            audio=True, audio_carrier_index=i,
                            audio_carrier_object=f)
            )

        fcnt = FrequencyContainer(optical_frequencies, carrier_cnt=carrier_optical_frequencies)

        # Audio matrix frequencies are more complicated as they can have multiple frequencies
        # in mechanical and electrical, on a per-node basis...
        fsig = FrequencyContainer(
            (Frequency("fsig", self.model.fsig.f.ref, index=0), )
        )

        for node in nodes:
            if node.type == NodeType.OPTICAL:
                continue

            #-----------------------------------------------------------------------------------
            # Mechanical frequencies
            #-----------------------------------------------------------------------------------
            # By default mechanical frequencies just have a single frequency at the Model.fsig.f
            # However for more complicated systems we can have multiple frequencies.
            elif node.type == NodeType.MECHANICAL:
                fs = []
                freqs = node.frequencies
                if len(freqs) == 1 and freqs[0] == self.model.fsig.f.ref:
                    # Most components will just use a single fsig so reuse same object
                    # for efficient filling later
                    signal_frequencies[node] = fsig
                else:
                    for i, sym in enumerate(node.frequencies):
                        fs.append(
                            Frequency(
                                str(fm.eval(keep_changing_symbols=True)),
                                sym,
                                index=i,
                            )
                        )
                    signal_frequencies[node] = FrequencyContainer(tuple(fs))

            #-----------------------------------------------------------------------------------
            # Electrical frequencies
            #-----------------------------------------------------------------------------------
            elif node.type == NodeType.ELECTRICAL:
                signal_frequencies[node] = fsig
            else:
                raise ValueError("Unexpected")

        return fcnt, signal_frequencies
