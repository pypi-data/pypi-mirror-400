from finesse.cymath cimport complex_t
from finesse.tracing.tree cimport TraceTree
from finesse.tracing.forest cimport TraceForest
from finesse.simulations.base cimport ModelSettings, NodeBeamParam, SimConfigData
from finesse.frequency cimport frequency_info_t, FrequencyContainer, Frequency
from cpython.ref cimport PyObject
from .simulation cimport CNodeInfo


cdef class MatrixSystemWorkspaces:
    cdef readonly:
        list to_initial_fill
        list to_refill
        list to_rhs_refill
        list to_noise_refill
        list to_noise_input_refill
        list noise_detectors
        int num_to_refill
        int num_to_rhs_refill
        int num_to_noise_refill
        int num_to_noise_input_refill
        int num_noise_detectors
    cdef:
        PyObject** ptr_to_refill
        PyObject** ptr_to_rhs_refill
        PyObject** ptr_to_noise_refill
        PyObject** ptr_to_noise_input_refill
        PyObject** ptr_noise_detectors


cdef class BaseSolver:
    cdef:
        readonly MatrixSystemWorkspaces workspaces
        readonly dict connections
        readonly dict nodes
        readonly dict node_aliases
        readonly dict node_2_index
        readonly dict index_2_node

        Py_ssize_t num_nodes

        readonly FrequencyContainer optical_frequencies
        readonly dict signal_frequencies
        readonly tuple unique_elec_mech_fcnts # Unique frequency containers for mech/elec

        readonly dict noise_sources
        readonly bint any_frequencies_changing
        bint is_signal_matrix # TODO refactor to something not matrix named
        readonly bint forced_refill
        public bint manual_rhs # When true the RHS/input vector is
        readonly unsigned int num_solves # number of times solve has been called

        # Edges that have a changing mode mismatch, Node ID pair (in, out)
        readonly int[:, ::1] changing_mismatch_node_ids
        bint debug_mode

    cpdef setup_nodes(self, list nodes, dict node_aliases)
    cpdef clear_rhs(self)
    cpdef initial_fill(self)
    cpdef refill(self)
    cpdef refill_rhs(self)
    cpdef fill_rhs(self)
    cpdef fill_noise_inputs(self)
    cpdef refactor(self)
    cpdef factor(self)
    cpdef solve(self)
    cpdef solve_noises(self)
    cpdef construct(self)
    cpdef destruct(self)
    cpdef initial_run(self)
    cpdef run(self)

    cpdef tuple get_node_frequencies(self, node)

    cpdef update_frequency_info(self)
    cpdef assign_operators(self, workspaces)
    cpdef assign_noise_operators(self, workspaces)

    cpdef add_rhs(self, unicode key)

    cpdef Py_ssize_t findex(self, object node, Py_ssize_t freq)

    cpdef Py_ssize_t node_id(self, object node)
    cpdef get_node_info(self, name)
