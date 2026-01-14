import logging
import numpy as np
cimport numpy as np

from libc.stdlib cimport free, calloc

from finesse.components.node import NodeType
from finesse.frequency cimport FrequencyContainer

LOGGER = logging.getLogger(__name__)


cdef class MatrixSystemWorkspaces:
    def __cinit__(self):
        self.ptr_to_refill = NULL
        self.ptr_to_rhs_refill = NULL
        self.ptr_to_noise_refill = NULL
        self.ptr_to_noise_input_refill = NULL
        self.ptr_noise_detectors = NULL

    def __init__(self):
        self.to_initial_fill = []
        self.to_refill = []
        self.to_rhs_refill = []
        self.to_noise_refill = []
        self.to_noise_input_refill = []
        self.noise_detectors = []

    def list_to_C(self):
        """Converts the python lists of workspaces into C Pyobject arrays for
        fast loop access.
        """
        if (
            self.ptr_to_refill != NULL
            or self.ptr_to_rhs_refill != NULL
            or self.ptr_to_noise_refill != NULL
            or self.ptr_to_noise_input_refill != NULL
        ):
            raise MemoryError()

        self.num_to_refill = len(self.to_refill)
        self.ptr_to_refill = <PyObject**> calloc(self.num_to_refill, sizeof(PyObject*))
        if not self.ptr_to_refill:
            raise MemoryError()
        cdef int i
        for i in range(self.num_to_refill):
            self.ptr_to_refill[i] = <PyObject*>self.to_refill[i]

        self.num_to_rhs_refill = len(self.to_rhs_refill)
        self.ptr_to_rhs_refill = <PyObject**> calloc(self.num_to_rhs_refill, sizeof(PyObject*))
        if not self.ptr_to_rhs_refill:
            raise MemoryError()
        for i in range(self.num_to_rhs_refill):
            self.ptr_to_rhs_refill[i] = <PyObject*>self.to_rhs_refill[i]

        self.num_to_noise_refill = len(self.to_noise_refill)
        self.ptr_to_noise_refill = <PyObject**> calloc(self.num_to_noise_refill, sizeof(PyObject*))
        if not self.ptr_to_noise_refill:
            raise MemoryError()
        for i in range(self.num_to_noise_refill):
            self.ptr_to_noise_refill[i] = <PyObject*>self.to_noise_refill[i]

        self.num_to_noise_input_refill = len(self.to_noise_input_refill)
        self.ptr_to_noise_input_refill = <PyObject**> calloc(self.num_to_noise_input_refill, sizeof(PyObject*))
        if not self.ptr_to_noise_input_refill:
            raise MemoryError()
        for i in range(self.num_to_noise_input_refill):
            self.ptr_to_noise_input_refill[i] = <PyObject*>self.to_noise_input_refill[i]

    def clear_workspaces(self):
        self.to_initial_fill.clear()
        self.to_refill.clear()
        self.to_rhs_refill.clear()
        self.to_noise_refill.clear()
        self.to_noise_input_refill.clear()
        self.noise_detectors.clear()

    def detector_list_to_C(self):
        self.num_noise_detectors = len(self.noise_detectors)
        if self.ptr_noise_detectors != NULL:
            raise MemoryError()
        self.ptr_noise_detectors = <PyObject**> calloc(self.num_noise_detectors, sizeof(PyObject*))
        if not self.ptr_noise_detectors:
            raise MemoryError()
        for i in range(self.num_noise_detectors):
            self.ptr_noise_detectors[i] = <PyObject*>self.noise_detectors[i]

    def __dealloc__(self):
        if self.ptr_to_refill:
            free(self.ptr_to_refill)

        if self.ptr_to_rhs_refill:
            free(self.ptr_to_rhs_refill)

        if self.ptr_to_noise_refill:
            free(self.ptr_to_noise_refill)

        if self.ptr_to_noise_input_refill:
            free(self.ptr_to_noise_input_refill)

        if self.ptr_noise_detectors:
            free(self.ptr_noise_detectors)


cdef class BaseSolver:
    """A linear set of systems can be represented as a matrix, each equation
    in this system is a particular state which we want to compute. The system
    is solved by applying some inputs into various states, or the right hand
    side (RHS) vector, and solving the system.

    The underlying matrix can be either a sparse or dense matrix. This class
    should not assume either, but merely call upon a standard matrix interface.
    Therefore the algorithm used for solving can vary significantly.
    The overall matrix is sectioned into submatricies which connect various
    states together.

    Nodes represent a physical location in the model in which some state of
    the system must be computed. Some nodes can have multiple states, such
    as multiple optical modes.
    """

    def __init__(
        self,
        str name,
        list nodes,
        FrequencyContainer optical_frequencies,
        dict signal_frequencies,
        bint is_signal_matrix,
        bint forced_refill,
        dict node_aliases,
        bint debug_mode = False,
    ):
        if is_signal_matrix:
            if signal_frequencies is None:
                raise Exception("Signal frequency containers not provided")
        else:
            if signal_frequencies is not None:
                raise Exception("Signal frequency container incorrectly provided for carrier simulation")

        self.is_signal_matrix = is_signal_matrix
        self.manual_rhs = False
        self.workspaces = MatrixSystemWorkspaces()
        self.forced_refill = forced_refill
        self.optical_frequencies = optical_frequencies
        self.signal_frequencies = signal_frequencies
        self.debug_mode = debug_mode

        if is_signal_matrix:
            # Get the unique FrequencyContainer objects for filling the info of.
            # This could be more optimal and dive into the references and check if
            # frequency containers are actually unique, but this mostly just stops
            # there being 100s of fsig containers from each node
            # TODO - optimise this away from a tuple
            self.unique_elec_mech_fcnts = tuple(set(signal_frequencies.values()))
            self.noise_sources = dict()

        self.any_frequencies_changing = False
        # Global flag for if any frequency is changing
        for _f in self.optical_frequencies.frequencies:
            if _f.symbol.is_changing:
                self.any_frequencies_changing = True
                break

        self.setup_nodes(nodes, node_aliases)

    def input_components(self):
        """Components that are injecting something into the simulation"""
        components = set()
        for ws in self.workspaces.to_rhs_refill:
            components.add(ws.owner)
        return components

    cpdef tuple get_node_frequencies(self, node):
        if node.type == NodeType.OPTICAL:
            return self.optical_frequencies.frequencies
        elif node.type == NodeType.MECHANICAL:
            return self.signal_frequencies[node].frequencies
        elif node.type == NodeType.ELECTRICAL:
            return self.signal_frequencies[node].frequencies
        else:
            raise ValueError()

    cpdef setup_nodes(self, list all_nodes, dict node_aliases):
        self.nodes = {n.full_name : n for n in all_nodes}
        self.num_nodes = len(self.nodes)
        self.node_aliases = {a.full_name: b.full_name for a, b, in node_aliases.items()}

        self.node_2_index = {}
        self.index_2_node = {}
        i = 0

        for n in self.nodes.values():
            if n in node_aliases:
                continue

            self.node_2_index[n.full_name] = i
            self.index_2_node[i] = n.full_name
            i += 1

        for n, a in node_aliases.items():
            # Map node n to node a details, essentially just an alias
            self.node_2_index[n.full_name] = self.node_2_index[a.full_name]

    cpdef assign_operators(self, connector_workspaces):
        """An important function. This takes all the connector workspaces - i.e. model elements
        that have requested some type of connection in the model - and ensures they have the
        correct submatrix allocated to them in for this solver.
        """
        raise NotImplementedError()

    cpdef assign_noise_operators(self, connector_workspaces):
        raise NotImplementedError()

    cpdef add_rhs(self, unicode key):
        raise NotImplementedError

    cpdef factor(self):
        raise NotImplementedError()

    cpdef refactor(self):
        raise NotImplementedError()

    cpdef solve(self):
        raise NotImplementedError()

    cpdef solve_noises(self):
        raise NotImplementedError()

    def initialise(self, sim):
        pass

    cpdef initial_fill(self):
        raise NotImplementedError()

    cpdef refill(self):
        raise NotImplementedError()

    cpdef refill_rhs(self):
        raise NotImplementedError()

    cpdef fill_rhs(self):
        raise NotImplementedError()

    cpdef fill_noise_inputs(self):
        raise NotImplementedError()

    cpdef construct(self):
        """This is called when workspaces and submatrices have been setup. Calling
        construct should now go and allocate the memory for the matrix and RHS.

        This method should be overwritten by an inheriting solver class with
        specfics of the solving technique.
        """
        raise NotImplementedError()

    cpdef destruct(self):
        """This is called when finishing and unbuilding the simulation.

        Classes that override this call should mindful of what this method is doing
        to and call it.
        """
        self.workspaces.clear_workspaces()

    cpdef initial_run(self):
        """Once a solver has been constructed it will most likely need to be initially
        filled and ran. Some sparse solvers for example must do a full factor first, then
        can perform faster refactors.

        This method should be overwritten by an inheriting solver class with
        specfics of the solving technique.
        """
        raise NotImplementedError()

    cpdef run(self):
        """Executes the simulation for model in its current state.

        Takes the following steps to compute an output:
         * If self.manual_rhs:
            * Clears the RHS vector
            * Fills the RHS vector
         * Fills the matrix
         * Solves
        """
        if not self.manual_rhs:
            self.clear_rhs()
            self.refill_rhs()
        self.refill()
        self.solve()
        if self.debug_mode:
            self.print_matrix()
            print("\nMatrix in dense format:\n")
            print(self._M.to_scipy_csr().todense())
            print("\nRight hand side vector:")
            self._M.print_rhs()

    def print_matrix(self):
        raise NotImplementedError()

    cpdef clear_rhs(self):
        raise NotImplementedError()

    cpdef Py_ssize_t findex(self, object node, Py_ssize_t freq):
        """
        Returns simulation unique index for a given frequency at this node.
        Used to refer to submatrices of HOMs in the interferometer matrix.

        Parameters
        ----------
        node : :class:`.Node`
            Node object to get the index of.
        freq : int
            Frequency index.

        Returns
        -------
        index : int
            Index of the `node` for a given frequency.
        """
        raise NotImplementedError()

    cpdef Py_ssize_t node_id(self, object node):
        if type(node) is str:
            return self.node_2_index[node]
        else:
            return self.node_2_index[node.full_name]

    cpdef get_node_info(self, node):
        """For a given node (object or name) the key parameters for where this node is
        represented in the matrix of linear equations.

        Parameters
        ----------
        node : [str | Node]
            The name or the Node object of the node.

        Returns
        -------
        dict: A dictionary containing the following information about the node:
            - index: The index of the node.
            - rhs_index: The index of the right-hand side vector associated with the node.
            - freq_index: The index of the frequency vector associated with the node.
            - nfreqs: The number of frequencies.
            - nhoms: The number of higher order modes. [TODO generalise to pixels/HOMs/whatever]
        """
        raise NotImplementedError()

    def get_frequency_object(self, frequency, node):
        """Get a :class:`.Frequency` object corresponding to a numerical or symbolic value.
        Returns none if nothing has been found.

        Parameters
        ----------
        f : number or :class:`.Symbol`
            Frequency to search for in this simulation.

        Returns
        -------
        :class:`.Frequency`
            The frequency object.
        """
        from finesse.symbols import Symbol

        if node.type == NodeType.OPTICAL:
            frequencies = self.optical_frequencies.frequencies
        elif node.type == NodeType.MECHANICAL:
            if not self.is_signal_matrix:
                return None
            frequencies = self.signal_frequencies[node].frequencies
        elif node.type == NodeType.ELECTRICAL:
            if not self.is_signal_matrix:
                return None
            frequencies = self.signal_frequencies[node].frequencies

        if isinstance(frequency, Symbol):
            if frequency.is_changing:
                # if it's tunable we want to look for the symbol that is just this
                # lasers frequency, as it will be changing
                for f in frequencies:
                    if f.symbol == frequency:
                        return f

        f_value = float(frequency)
        # otherwise do some value comparisons
        for f in frequencies:
            if np.isclose(float(f.f), f_value, atol=1e-15, rtol=1e-15):
                return f

        return None

    cpdef update_frequency_info(self):
        self.optical_frequencies.update_frequency_info()
        if self.is_signal_matrix:
            for i in range(len(self.unique_elec_mech_fcnts)):
                (<FrequencyContainer>self.unique_elec_mech_fcnts[i]).update_frequency_info()
