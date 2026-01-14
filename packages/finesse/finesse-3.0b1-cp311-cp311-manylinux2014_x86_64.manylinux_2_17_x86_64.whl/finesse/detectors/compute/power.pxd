from finesse.cymath cimport complex_t
from finesse.cymath.sparsemath cimport CSRMatrix
from finesse.detectors.workspace cimport (
        DetectorWorkspace,
        MaskedDetectorWorkspace,
)
from finesse.element_workspace cimport BaseCValues

cdef class PD0Workspace(MaskedDetectorWorkspace):
    cdef readonly:
        int dc_node_id
        Py_ssize_t rhs_index
        CSRMatrix K

cdef class PD1Workspace(MaskedDetectorWorkspace):
    cdef readonly:
        bint output_real
        int dc_node_id
        int ac_node_id
        int[:,::1] homs
        bint is_f_changing
        bint is_phase_changing
        bint is_audio_mixing
        complex_t Aij
        PD1Values cvalues
        bint is_segmented
        CSRMatrix K # segmentation scatter matrix
    cdef:
        double phase_offset
        Py_ssize_t num_pre_set_beats
        complex** pre_set_beats[2] # 2 x num_pre_set_beats

    cpdef update_beats(self)

cdef class PD1Values(BaseCValues):
    cdef public:
        double f
        double phase

cdef object c_pd1_AC_output(DetectorWorkspace dws)

cdef class PD2Workspace(MaskedDetectorWorkspace):
    cdef readonly:
        bint output_real
        int dc_node_id
        int ac_node_id
        int[:,::1] homs
        bint is_f1_changing
        bint is_f2_changing
        bint is_phase1_changing
        bint is_phase2_changing
        bint is_audio_mixing
        complex_t z1
        complex_t z2
        PD2Values cvalues
        bint is_segmented
        CSRMatrix K # segmentation scatter matrix

cdef class PD2Values(BaseCValues):
    cdef public:
        double f1
        double phase1
        double f2
        double phase2

cdef object c_pd2_AC_output(DetectorWorkspace dws)
