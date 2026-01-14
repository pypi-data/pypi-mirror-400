cimport numpy as np
from finesse.cymath.complex cimport complex_t, DenseZMatrix


cdef class KnmMatrix:
    cdef readonly:
        np.ndarray data
        np.ndarray modes
        np.ndarray homs
        str name

    cdef:
        complex_t[:, ::1] data_view
        DenseZMatrix mtx
        const int[:, ::1] modes_view

    cdef (Py_ssize_t, Py_ssize_t) field_indices_from(self, key)
    cdef complex_t coupling(self, int n1, int m1, int n2, int m2) noexcept nogil


cpdef make_unscaled_X_scatter_knm_matrix(int[:,::1] modes)
cpdef make_unscaled_Y_scatter_knm_matrix(int[:,::1] modes)


# Compute loss from scattering for each coupling,
# required for  quantum noise calculations
cdef void knm_loss(const complex_t* knm_mat, double* out, Py_ssize_t N) noexcept nogil

cdef void c_zero_tem00_phase(
    const complex_t[:, ::1] knm_mat,
    complex_t[:, ::1] out
) noexcept nogil

cdef void c_flip_odd_horizontal(
    DenseZMatrix *knm_mat,
    const int[:, ::1] homs
) noexcept nogil

cdef void c_reverse_gouy_phases(
    double x_gouy1, double y_gouy1,
    double x_gouy2, double y_gouy2,
    const complex_t[:, ::1] knm_mat,
    const int[:, ::1] homs,
    complex_t[:, ::1] out
) noexcept nogil

cdef complex_t rev_gouy(
    double x_gouy1,
    double y_gouy1,
    double x_gouy2,
    double y_gouy2,
    complex_t k,
    int n1, int m1, int n2, int m2,
) noexcept nogil
