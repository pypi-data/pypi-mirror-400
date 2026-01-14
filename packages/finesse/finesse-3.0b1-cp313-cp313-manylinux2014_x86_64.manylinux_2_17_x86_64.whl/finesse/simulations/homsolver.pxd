from finesse.cymath cimport complex_t
from finesse.simulations.base cimport ModelSettings, NodeBeamParam, SimConfigData
from finesse.frequency cimport frequency_info_t, FrequencyContainer, Frequency
from .simulation cimport CNodeInfo
from .basesolver cimport BaseSolver
import cython


node_id_str_object = cython.fused_type(cython.integral, cython.object, cython.str)


cdef class HOMSolver(BaseSolver):
    cdef:
        public complex_t[::1] out_view
        public Py_ssize_t out_view_size

        readonly int nhoms
        readonly dict _noise_matrices
        readonly dict _submatrices
        readonly dict _diagonals
        readonly dict _noise_submatrices
        CNodeInfo* _c_node_info

    cdef get_node_matrix_params(self, node, Py_ssize_t *Ns, Py_ssize_t *Nf, frequency_info_t** fptr)
    cpdef add_noise_matrix(self, object key)

    cpdef Py_ssize_t field(self, object node, Py_ssize_t freq=?, Py_ssize_t hom=?)
    cdef Py_ssize_t field_fast(self, Py_ssize_t node_id, Py_ssize_t freq=?, Py_ssize_t hom=?) noexcept nogil
    cdef inline Py_ssize_t field_fast_2(
        self,
        Py_ssize_t node_rhs_idx,
        Py_ssize_t num_hom,
        Py_ssize_t freq,
        Py_ssize_t hom
    ) noexcept nogil

    cdef Py_ssize_t findex_fast(self, Py_ssize_t node_id, Py_ssize_t freq) nogil

    cpdef complex_t get_out(self, object node, Py_ssize_t freq=?, Py_ssize_t hom=?)
    cdef complex_t get_out_fast(self, Py_ssize_t node_id, Py_ssize_t freq, Py_ssize_t hom) noexcept nogil

    cpdef set_source(self, object node, int freq_idx, int hom_idx, complex value)
    cdef int set_source_fast(self, Py_ssize_t node_id, Py_ssize_t freq_idx, Py_ssize_t hom_idx, complex_t value, Py_ssize_t rhs_index) except -1
    cdef int set_source_fast_2(self, Py_ssize_t rhs_idx, complex_t value) except -1
    cdef int set_source_fast_3(self, Py_ssize_t rhs_idx, complex_t value, Py_ssize_t rhs_index) except -1

    cpdef complex_t[::1] node_field_vector(self, node_id_str_object node, Py_ssize_t freq_idx)
    cdef complex_t* node_field_vector_fast(self, Py_ssize_t node_idx, Py_ssize_t freq_idx, Py_ssize_t *size) noexcept nogil
