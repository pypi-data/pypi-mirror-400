# cython: profile=False
import logging

from finesse.detectors.general import NoiseDetector
from finesse.components.general import NoiseType
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.sparse.solver cimport SparseSolver
from finesse.components.modal.workspace cimport KnmConnectorWorkspace
from finesse.components.workspace cimport ConnectorCallbacks
from finesse.components.workspace cimport ConnectorWorkspace, ConnectorMatrixSimulationInfo
from finesse.cymath.cmatrix cimport KLUMatrix

LOGGER = logging.getLogger(__name__)


cdef class SparseMatrixSimulation(BaseSimulation):
    """
    A simulation type which solves the carrier and signal simulations using large
    sparse matrices, solving systems such as Ma=b.
    """

    def __init__(self, model, unicode name, dict simulation_options, bint needs_matrix=True):
        super().__init__(model, name, simulation_options)

    def build_carrier_solver(self, nodes, optical_frequencies):
        if not issubclass(self.simulation_options["carrier_solver"], SparseSolver):
            raise Exception("Solver should inherit from SparseSolver")
        return self.simulation_options["carrier_solver"](
            "carrier",
            nodes,
            optical_frequencies,
            None,
            False,
            self.model.force_refill,
            {},
            self.model_settings.num_HOMs,
            debug_mode=self.simulation_options["debug_mode"],
            matrix_kwargs=self.simulation_options.get("carrier_solver_kwargs", {})
        )

    def build_signal_solver(self, nodes, optical_frequencies, signal_frequencies):
        if not issubclass(self.simulation_options["signal_solver"], SparseSolver):
            raise Exception("Solver should inherit from SparseSolver")

        return self.simulation_options["signal_solver"](
            "signal",
            nodes,
            optical_frequencies,
            signal_frequencies,
            True,
            self.model.force_refill,
            {},
            self.model_settings.num_HOMs,
            matrix_kwargs=self.simulation_options.get("signal_solver_kwargs", {})
        )

    def setup_build(self):
        if self.compute_signals:
            self.initialise_noise_matrices()

        self.initialise_workspaces()
        self.update_all_parameter_values()

        if self.compute_signals:
            self.initialise_noise_sources()
            self.initialise_noise_selection_vectors()

        if self.is_modal:
            # compute all the initial:
            #     - scattering matrices
            #     - space Gouy phases
            #     - laser tem Gouy phases
            for ws in self.workspaces:
                # if the connector scatters modes then initialise the
                # knm workspaces here and store the connector workspace
                # in to_scatter_matrix_compute for future use
                if isinstance(ws, (KnmConnectorWorkspace)):
                    (<KnmConnectorWorkspace> ws).initialise_knm_workspaces()
                    self.to_scatter_matrix_compute.append(ws)
            self.compute_knm_matrices()
            self.set_gouy_phases()
            # ... then determine which beam parameters will be changing
            # so that only the items from above which change get
            # re-computed on subsequent calls to their respective functions
            self._determine_changing_beam_params()

        self.carrier.initialise(self)
        self.carrier.assign_operators(self.workspaces)
        self.carrier.construct()
        self.carrier.initial_run()

        if self.signal:
            self.signal.initialise(self)
            self.signal.assign_operators(self.workspaces)
            self.signal.assign_noise_operators(self.workspaces)
            self.signal.construct()
            self.signal.initial_run()

    cpdef modal_update(self):
        if not BaseSimulation.modal_update(self):
            return False
        # Compute the changing scattering matrices
        self.compute_knm_matrices()
        return True

    cpdef compute_knm_matrices(self):
        cdef KnmConnectorWorkspace ws
        for ws in self.to_scatter_matrix_compute:
            ws.update_changing_knm_workspaces()
            ws.compute_scattering_matrices()
            # TODO (sjr) Probably want a flag to check if quantum noise calcs
            #            being performed and to only do this call if so
            ws.compute_knm_losses()

    cpdef initialise_workspaces(self) :
        cdef ConnectorMatrixSimulationInfo info
        from finesse.components import Connector, Cavity
        # TODO ddb - probably need to move away from lists as they aren't that fast to iterate
        # over. Maybe once we have all the lists filled we can covert them into some PyObject
        # memoryview
        self.workspace_name_map = {}
        self.workspaces = []
        self.cavity_workspaces = {}
        self.to_scatter_matrix_compute = []
        self.gouy_phase_workspaces = []

        if self.is_modal and self.trace == NULL:
            raise Exception("Beam trace has not been set before workspaces are initialised")

        # Get any callbacks for the elements in the model
        # tell the element that we have now built the model and it
        # should do some initialisations for running simulations
        for el in self.model.elements.values():
            el._setup_changing_params()

            if isinstance(el, Connector):
                ws = el._get_workspace(self)
                if ws is None:
                    continue

                self.workspaces.append(ws) # store all workspaces here
                self.workspace_name_map[el.name] = ws

                if isinstance(ws, ConnectorWorkspace):
                    # Determine if we should be adding this workspace to any
                    # todo list for looping over later

                    # Here we grab the information objects from each workspace
                    # which describes the connections and filling to be done
                    # for each element for each simulation type
                    if self.signal:
                        x = (
                            (ws.carrier, self.carrier),
                            (ws.signal, self.signal)
                        )
                    else:
                        x = ((ws.carrier, self.carrier),)

                    for info, mtx in x:
                        ws_store = mtx.workspaces
                        if info.callback_flag & ConnectorCallbacks.FILL_MATRIX:
                            ws_store.to_initial_fill.append(ws) # Initial fill all
                            if info.matrix_fills.num_refills > 0 or mtx.forced_refill:
                                ws_store.to_refill.append(ws)

                        if info.callback_flag & ConnectorCallbacks.FILL_RHS:
                            ws_store.to_rhs_refill.append(ws)

                        if info.callback_flag & ConnectorCallbacks.FILL_NOISE:
                            try:
                                if any([x in self.signal.noise_sources for x in ws.owner.noises]):
                                    ws_store.to_noise_refill.append(ws)
                            except AttributeError:
                                # Component isn't a NoiseGenerator, but can still generate quantum
                                # noise
                                if NoiseType.QUANTUM in self.signal.noise_sources:
                                    ws_store.to_noise_refill.append(ws)

                        # Quantum noise is special, as all connectors can be a source if they have
                        # open inputs
                        if info.callback_flag & ConnectorCallbacks.FILL_INPUT_NOISE:
                            if NoiseType.QUANTUM in self.signal.noise_sources:
                                ws_store.to_noise_input_refill.append(ws)

                    if ws.fn_gouy_c is not None or ws.fn_gouy_py is not None:
                        self.gouy_phase_workspaces.append(ws)

                elif ws is not None:
                    # None means the component doesn't want anything
                    # to do with this simulation
                    raise Exception("Unexpected workspace type")
            elif isinstance(el, Cavity):
                self.cavity_workspaces[el] = el._get_workspace(self)
                self.workspace_name_map[el.name] = self.cavity_workspaces[el]

        # Compile cy_exprs for changing symbolics, these are stored
        # in ElementWorkspace.chprm_expr which is used for fast evaluating
        # of the changing symbolic expressions
        for ws in self.workspaces:
            ws.compile_cy_exprs()
            # Also compile the changing ABCD matrix elements, these are
            # stored in the relevant cy_expr** field of the associated
            # workspace -> note that the cy_expr* element is NULL for non
            # changing elements
            if self.is_modal:
                ws.compile_abcd_cy_exprs()

        LOGGER.info("Refilling carrier elements:\n%s", self.carrier.workspaces.to_refill)

        self.carrier.workspaces.list_to_C()
        if self.signal:
            LOGGER.info("Refilling signal elements:\n%s", self.signal.workspaces.to_refill)
            self.signal.workspaces.list_to_C()
        #print(self.name)
        #print("MATRIX")
        #print("carrier to_refill", len(self.carrier.workspaces.to_refill))
        #print("signal to_refill", len(self.signal.workspaces.to_refill))
        #print("to_rhs_refill", self.to_rhs_refill)


    cpdef initialise_noise_matrices(self) :
        from finesse.detectors.general import NoiseDetector

        # Which noise types are we measuring?
        for el in self.model.detectors:
            if isinstance(el, NoiseDetector):
                if el.noise_type not in self.signal.noise_sources:
                    self.signal.noise_sources[el.noise_type] = []
                    self.signal.add_noise_matrix(el.noise_type)

    cpdef initialise_noise_sources(self) :
        from finesse.components.general import NoiseGenerator

        for el in self.model.elements.values():
            if isinstance(el, NoiseGenerator):
                for _type, nodes in el.noises.items():
                    # Only consider noise sources for the types of noise we'll be measuring
                    if _type in self.signal.noise_sources:
                        self.signal.noise_sources[_type].append((el, nodes))

    cpdef initialise_noise_selection_vectors(self) :
        cdef KLUMatrix mtx = self.signal._M
        for el in self.model.elements.values():
            if hasattr(el, "_requested_selection_vectors"):
                for name in el._requested_selection_vectors:
                    el._requested_selection_vectors[name] = mtx.request_rhs_view()
