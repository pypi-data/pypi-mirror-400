from finesse.cymath cimport complex_t
from finesse.tracing.tree cimport TraceTree
from finesse.tracing.forest cimport TraceForest
from finesse.simulations.base cimport ModelSettings, NodeBeamParam, SimConfigData
from finesse.frequency cimport frequency_info_t, FrequencyContainer, Frequency
from cpython.ref cimport PyObject
from finesse.utilities.collections cimport OrderedSet

from .basesolver cimport BaseSolver


cdef extern from "constants.h":
    long double PI
    double C_LIGHT


# Structure to store the various information about each individual node
# such as where the node sits in the RHS vector, what the unique index is
# in a given simulation.
cdef struct CNodeInfo:
    Py_ssize_t index # unique index
    Py_ssize_t rhs_index # index node starts in RHS vector
    Py_ssize_t freq_index
    Py_ssize_t nfreqs # number of frequencies at this node
    Py_ssize_t nhoms # number of HOMs at this node
    frequency_info_t *frequencies # Frequencies array present at this node, size nfreqs


cdef class BaseSimulation:
    cdef:
        object __weakref__
        readonly ModelSettings model_settings
        SimConfigData config_data

        readonly dict simulation_options
        readonly BaseSolver carrier
        readonly BaseSolver signal
        readonly bint compute_signals
        readonly list optical_nodes_to_use
        readonly list signal_nodes_to_use

        readonly FrequencyContainer signal_optical_frequencies_to_use
        readonly dict signal_frequencies_to_use
        readonly FrequencyContainer carrier_frequencies_to_use

        readonly unicode name
        readonly OrderedSet changing_parameters
        readonly OrderedSet tunable_parameters
        readonly object model
        readonly bint is_modal

        readonly list detector_workspaces
        readonly list readout_workspaces

        public dict workspace_name_map
        public list workspaces
        public list variable_workspaces
        readonly list gouy_phase_workspaces

        ### Tracing stuff ###
        public dict cavity_workspaces
        readonly dict trace_node_index # map of node objects to integer indicies used for tracing
        NodeBeamParam* trace
        # Beam parameters in initial state as a BeamTraceSolution object
        readonly object initial_trace_sol
        # The TraceForest of geometrically changing branches. This is an
        # empty forest for any simulation in which geometric parameters
        # are not changing.
        readonly TraceForest trace_forest
        # Node couplings which will have changing mode mismatches,
        # determined from trace_forest via tree intersection searching
        readonly tuple changing_mismatch_couplings
        # Optical node id pairs (in, out) where mismatch is happening
        readonly OrderedSet changing_mismatch_edges
        readonly OrderedSet nodes_with_changing_q # Nodes that will potentially have a changing q
        # A dict of {<tuple of newly unstable cavities> : <contingent TraceForest>}
        # required for when a scan results in a geometrically changing cavity becoming
        # unstable -> invalidating self.trace_forest temporarily for that data point
        dict contingent_trace_forests
        bint needs_reflag_changing_q # Used when exiting from unstable cavity regions
        bint retrace

        # List of workspaces for components which scatter modes
        list to_scatter_matrix_compute


    cdef initialise_model_settings(self)
    cdef initialise_sim_config_data(self)

    cpdef update_all_parameter_values(self)
    cpdef update_map_data(self)
    cpdef update_cavities(self)

    cdef int set_gouy_phases(self) except -1
    cpdef modal_update(self)

    cpdef run_carrier(self)
    cpdef run_signal(self, solve_noises=?)

    cdef initialise_trace_forest(self, optical_nodes)
    # Methods to construct the changing TraceForest for the simulation
    cdef int _determine_changing_beam_params(self, TraceForest forest=?, bint set_tree_node_ids=?)
    cdef _setup_trace_forest(self, TraceForest forest=?, bint set_tree_node_ids=?)
    cdef _setup_single_trace_tree(self, TraceTree tree, bint set_tree_node_ids=?)

    # Find the newly unstable cavity instances from the changing forest
    cdef tuple _find_new_unstable_cavities(self)
    cdef TraceForest _initialise_contingent_forest(self, tuple unstable_cavities)

    # Perform the beam trace on the changing TraceForest
    cdef void _propagate_trace(self, TraceTree tree, bint symmetric) noexcept
    cpdef trace_beam(self)
