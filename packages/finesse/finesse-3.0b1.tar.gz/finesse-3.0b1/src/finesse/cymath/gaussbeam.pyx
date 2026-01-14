#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Low-level calculations for Gaussian beam properties.

This module provides functions for computing properties of Gaussian beams
and transforming Gaussian beam parameters via the ABCD ray-matrix framework.

.. note::
    These are low-level functions intended for use in Cython extensions. Users
    should use the functions and classes given in :mod:`finesse.gaussian` instead
    of those defined here.
"""

cpdef complex_t transform_q(
    const double[:, ::1] M,
    complex_t q1,
    double nr1,
    double nr2
) noexcept nogil:
    cdef:
        complex_t q1_factor = q1 / nr1

    return nr2 * (M[0][0] * q1_factor + M[0][1]) / (M[1][0] * q1_factor + M[1][1])

cdef complex_t c_transform_q(
    const double* M,
    complex_t q1,
    double nr1,
    double nr2
) noexcept nogil:
    """Assumes M is a C-contiguous array of size 2x2"""
    cdef:
        complex_t q1_factor = q1 / nr1

    return nr2 * (M[0] * q1_factor + M[1]) / (M[2] * q1_factor + M[3])

cpdef complex_t inv_transform_q(
    const double[:, ::1] M,
    complex_t q2,
    double nr1,
    double nr2
) noexcept nogil:
    cdef:
        complex_t q2_factor = q2 / nr2

    return nr1 * (M[0][1] - M[1][1] * q2_factor) / (M[1][0] * q2_factor - M[0][0])


cdef void c_abcd_multiply(
    const double* m1,
    const double* m2,
    double* out
) noexcept nogil:
    assert m1 != NULL
    assert m2 != NULL
    assert out != NULL
    cdef:
        double A1 = m1[0]
        double B1 = m1[1]
        double C1 = m1[2]
        double D1 = m1[3]

        double A2 = m2[0]
        double B2 = m2[1]
        double C2 = m2[2]
        double D2 = m2[3]

    out[0] = A1 * A2 + B1 * C2
    out[1] = A1 * B2 + B1 * D2
    out[2] = C1 * A2 + D1 * C2
    out[3] = C1 * B2 + D1 * D2

cdef void abcd_multiply(
    const double[:, ::1] m1,
    const double[:, ::1] m2,
    double[:, ::1] out,
) noexcept nogil:
    cdef:
        double A1 = m1[0][0]
        double B1 = m1[0][1]
        double C1 = m1[1][0]
        double D1 = m1[1][1]

        double A2 = m2[0][0]
        double B2 = m2[0][1]
        double C2 = m2[1][0]
        double D2 = m2[1][1]

    out[0][0] = A1 * A2 + B1 * C2
    out[0][1] = A1 * B2 + B1 * D2
    out[1][0] = C1 * A2 + D1 * C2
    out[1][1] = C1 * B2 + D1 * D2

cpdef void sym_abcd_multiply(
    object[:, ::1] m1,
    object[:, ::1] m2,
    object[:, ::1] out,
) noexcept:
    cdef:
        object A1 = m1[0][0]
        object B1 = m1[0][1]
        object C1 = m1[1][0]
        object D1 = m1[1][1]

        object A2 = m2[0][0]
        object B2 = m2[0][1]
        object C2 = m2[1][0]
        object D2 = m2[1][1]

    out[0][0] = A1 * A2 + B1 * C2
    out[0][1] = A1 * B2 + B1 * D2
    out[1][0] = C1 * A2 + D1 * C2
    out[1][1] = C1 * B2 + D1 * D2


cpdef bint is_abcd_changing(object[:, ::1] M) noexcept:
    cdef:
        Py_ssize_t i, j
        bint is_changing

    for i in range(2):
        for j in range(2):
            is_changing = getattr(M[i][j], "is_changing", False)
            if is_changing:
                return True

    return False
