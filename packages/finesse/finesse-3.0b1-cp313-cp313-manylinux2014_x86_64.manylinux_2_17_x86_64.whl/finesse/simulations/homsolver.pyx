import cython
import contextlib
import logging
import numpy as np

from libc.stdlib cimport free, calloc

from finesse.components.node import NodeType
from finesse.frequency cimport frequency_info_t, FrequencyContainer
from finesse.cymath.complex cimport complex_t

LOGGER = logging.getLogger(__name__)


cdef class HOMSolver(BaseSolver):
    """This is class provides an interface for generic simulations that are solving
    for a vector of higher order modes at each node. This allows detectors and other
    calculation code to be able to perform the same calculations without being
    specified. This class should be inherited to provide specific implementations.
    Considerations are:

        - HOM vector at each node should be contiguous in memory
        - Not all nodes will have a HOM vector if it isn't being solved for
        - Signal nodes will have a single "HOM"


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
        int num_optical_homs,
        bint debug_mode = False,
    ):
        assert(num_optical_homs >= 1)
        self.nhoms = num_optical_homs
        super().__init__(
            name,
            nodes,
            optical_frequencies,
            signal_frequencies,
            is_signal_matrix,
            forced_refill,
            node_aliases,
            debug_mode=debug_mode
            )

        if is_signal_matrix:
            self._noise_matrices = dict()

    cpdef setup_nodes(self, list all_nodes, dict node_aliases):
        cdef:
            Py_ssize_t i, s_rhs_idx, s_f_idx, Nsm, Neq
            CNodeInfo *info
            frequency_info_t *finfo_ptr = NULL

        BaseSolver.setup_nodes(self, all_nodes, node_aliases)

        self._c_node_info = <CNodeInfo*> calloc(self.num_nodes, sizeof(CNodeInfo))
        if not self._c_node_info:
            raise MemoryError()

        s_rhs_idx = 0 # total number of states in the matrix so far
        s_f_idx = 0 # Number of frequency submatrices so far
        i = 0

        for n in self.nodes.values():
            if n in node_aliases:
                continue

            self.get_node_matrix_params(n, &Neq, &Nsm, &finfo_ptr)
            info = &self._c_node_info[i]

            info.index = self.node_2_index[n.full_name]
            info.rhs_index = s_rhs_idx
            info.freq_index = s_f_idx
            info.nfreqs = Nsm
            info.nhoms = Neq
            info.frequencies = finfo_ptr

            s_rhs_idx += Neq * Nsm  # Track how many equations we are going through
            s_f_idx   += Nsm        # keep track of how many frequencies*nodes
            i += 1

        self.out_view_size = s_rhs_idx

    cpdef construct(self):
        self.out_view = np.zeros(self.out_view_size, dtype=np.complex128)

    @contextlib.contextmanager
    def component_edge_fill(self, comp, edgestr, f1, f2, conjugate = False):
        """
        Returns a matrix for the submatrix an element has requested
        for different connections it needs. The key is::

            (element, connection_name, ifreq, ofreq)

        This is a context manager, to be used like with sim.component_edge_fill(key) as mat::

            mat[:] = computations

        Parameters
        ----------
        element : finesse.component.Connector
            The object reference that created the requests.
        connection_name : str
            String name given to the connection.
        ifreq : finesse.Frequency
            Incoming frequency.
        ofreq : finesse.Frequency
            Outgoing frequency.

        Returns
        -------
        matrix
        """
        #the two-stage nature of this will make some fill checks and hooks
        #much more safe (and powerfull)

        #this will be helpful for on-demand filling and will also help improve
        #make DC simulation of squeezers work (because post-fill transformations
        #will be needed)
        key = (comp, edgestr, f1.index, f2.index)
        mat = self._submatrices[key]
        yield mat
        #check things, or transform things here
        if conjugate:
            mat[:].imag *= -1
        return

    @contextlib.contextmanager
    def component_edge_fill3(self, owner_idx, conn_idx, f1_index, f2_index):
        if conn_idx < 0:
            raise IndexError(f"This connection was not included in the simulation. {owner_idx, conn_idx, f1_index, f2_index}")
        mat = self._submatrices[(owner_idx, conn_idx, f1_index, f2_index)]
        yield mat
        return

    cdef get_node_matrix_params(self, node, Py_ssize_t *Ns, Py_ssize_t *Nf, frequency_info_t** fptr):
        """For a given node in the simulation this should set the provided pointers
        regarding the number of states and submatricies that are required in the matrix:
            - Ns : Number of unique states at the node per frequency
            - Nf : Number of frequencies at the node
            - fptr : Pointer to frequency_info_t for details on the number of frequencies
        """
        assert(Ns)
        assert(Nf)
        assert(fptr)
        assert(self.nhoms > 0)
        assert(self.optical_frequencies.size > 0)

        cdef FrequencyContainer ficnt
        if node.type is NodeType.OPTICAL:
            Ns[0] = self.nhoms
            Nf[0] = self.optical_frequencies.size
            fptr[0] = &self.optical_frequencies.frequency_info[0]
        elif node.type is NodeType.MECHANICAL:
            # Higher order mechanical modes at a particular frequency. This should probably
            # be kept as 1 mode per frequency, additional mechanical degrees of freedom should
            # be defined as a separate node in a port.
            ficnt = <FrequencyContainer>(self.signal_frequencies[node])
            Ns[0] = 1
            Nf[0] = ficnt.size
            fptr[0] = &(ficnt.frequency_info[0])
        elif node.type is NodeType.ELECTRICAL:
            ficnt = <FrequencyContainer>(self.signal_frequencies[node])
            Ns[0] = 1 # no higher order modes of electronics as far as I'm aware...
            Nf[0] = ficnt.size
            fptr[0] = &(ficnt.frequency_info[0])
        else:
            raise Exception("Node type not handled")

    cpdef add_noise_matrix(self, object key):
        raise NotImplementedError

    cpdef set_source(self, object node, int freq_idx, int hom_idx, complex value):
        raise NotImplementedError()

    cdef int set_source_fast(self, Py_ssize_t node_id, Py_ssize_t freq_idx, Py_ssize_t hom_idx, complex_t value, Py_ssize_t rhs_index) except -1:
        return -1

    cdef int set_source_fast_2(self, Py_ssize_t rhs_idx, complex_t value) except -1:
        return -1

    cdef int set_source_fast_3(self, Py_ssize_t rhs_idx, complex_t value, Py_ssize_t rhs_index) except -1:
        return -1

    cpdef Py_ssize_t findex(self, object node, Py_ssize_t freq):
        return self.findex_fast(self.node_id(node), freq)

    cdef Py_ssize_t findex_fast(self, Py_ssize_t node_id, Py_ssize_t freq) nogil:
        assert self._c_node_info != NULL
        cdef:
            CNodeInfo ni = self._c_node_info[node_id]
            Py_ssize_t freq_idx = ni.freq_index

        return freq_idx + freq

    cpdef Py_ssize_t field(self, object node, Py_ssize_t freq=0, Py_ssize_t hom=0):

        """
        Returns simulation unique index of a field at a particular frequency
        index at this node.

        Parameters
        ----------
        node : :class:`.Node`
            Node object to get the index of.
        freq : int
            Frequency index.
        hom : int, optional
            Higher Order Mode index, defaults to zero.
        """
        return self.field_fast(self.node_id(node), freq, hom)

    cdef Py_ssize_t field_fast(self, Py_ssize_t node_id, Py_ssize_t freq=0, Py_ssize_t hom=0) noexcept nogil:
        if self._c_node_info == NULL:
            return -1
        cdef:
            CNodeInfo ni = self._c_node_info[node_id]
            Py_ssize_t Nh = ni.nhoms
            Py_ssize_t rhs_idx = ni.rhs_index
        return rhs_idx + freq * Nh + hom

    cdef inline Py_ssize_t field_fast_2(
        self,
        Py_ssize_t node_rhs_idx,
        Py_ssize_t num_hom,
        Py_ssize_t freq,
        Py_ssize_t hom) noexcept nogil:
        """Inlined function to return field index fast."""
        return node_rhs_idx + freq * num_hom + hom

    cpdef complex_t get_out(self, object node, Py_ssize_t freq=0, Py_ssize_t hom=0):
        return self.get_out_fast(self.node_id(node), freq, hom)

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

        assert self._c_node_info != NULL
        cdef int i
        if type(node) is str:
            i = self.node_2_index[node]
        else:
            i = self.node_2_index[node.full_name]

        cdef CNodeInfo ni = self._c_node_info[i]
        return {
            "index": ni.index,
            "rhs_index": ni.rhs_index,
            "freq_index": ni.freq_index,
            "nfreqs": ni.nfreqs,
            "nhoms": ni.nhoms,
        }

    cpdef complex_t[::1] node_field_vector(self, node_id_str_object node, Py_ssize_t freq_idx):
        """
        Returns the higher order mode field vector of a given node at a specific
        frequency index.

        Parameters
        ----------
        node : [int|object|str]
            The node for which to retrieve the field vector. This can be a string full-name
            of a node, 'm1.p1.i', or a node object. It can also be an integer index of the
            node for this simulation.
        freq_idx : unsigned long
            The index of the frequency at which to retrieve the field vector.

        Returns
        -------
        np.ndarray:
            A copy of the field vector of the node at the specified frequency index.
        """
        cdef:
            Py_ssize_t N = 0
            Py_ssize_t i = 0
            complex_t *ptr = NULL

        if cython.int is node_id_str_object or cython.long is node_id_str_object:
            ptr = self.node_field_vector_fast(node, freq_idx, &N)
        else:
            i = self.node_id(node)
            ptr = self.node_field_vector_fast(i, freq_idx, &N)

        # TODO this is marked as slow in cython annotation, should check if we
        # can speed that up, maybe many cases do not need a copy but a view
        return (<complex_t[:N]>ptr)[:]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef complex_t* node_field_vector_fast(self, Py_ssize_t node_idx, Py_ssize_t freq_idx, Py_ssize_t *size) noexcept nogil:
        """
        Returns a pointer to the higher order mode field vector for a given node
        and frequency index.

        Parameters
        ----------
        node_idx : Py_ssize_t
            The index of the node.
        freq_idx : Py_ssize_t
            The index of the frequency.
        size : Py_ssize_t*
            A pointer to store the size of the field vector.

        Returns
        -------
        complex_t*
            A pointer to the field vector if the node index is valid and the frequency
            index is within range, otherwise returns NULL.
        """
        cdef Py_ssize_t idx

        if size != NULL:
            size[0] = self.nhoms

        if node_idx >= 0 and node_idx < self.num_nodes:
            idx = self._c_node_info[node_idx].rhs_index + freq_idx * self.nhoms
            if idx < self.out_view_size:
                return &self.out_view[idx]
            else:
                return NULL
        else:
            return NULL

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef complex_t get_out_fast(self, Py_ssize_t node_id, Py_ssize_t freq, Py_ssize_t hom) noexcept nogil:
        """
        Get the output value at a specific node, frequency, and higher order mode index.

        Parameters
        ----------
        node_id : Py_ssize_t
            The ID of the node.
        freq : Py_ssize_t, optional
            The frequency index.
        hom : Py_ssize_t, optional
            The higher order mode index.

        Returns
        -------
        complex_t
            The output value at the specified node, frequency, and homodyne index.
        """
        cdef Py_ssize_t field_idx = self.field_fast(node_id, freq, hom)
        return self.out_view[field_idx]

    def __dealloc__(self):
        if self._c_node_info != NULL:
            free(self._c_node_info)
