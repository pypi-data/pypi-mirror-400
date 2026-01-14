from finesse.cymath.complex cimport complex_t, cnorm, cabs, cimag, creal, conj

cdef extern from "math.h" nogil:
    double atan2(double y, double x)
    double fabs(double arg)
    double sqrt(double arg)

cdef extern from "constants.h":
    long double PI


### Low-level beam parameter struct and functions ###

cdef struct beam_param:
    complex_t q
    # TODO (sjr) Should probably change below to pointers to
    # refractive index and wavelength because these get initialised
    # in a simulation via the connector workspaces and model data
    # respectively so could just keep addresses here
    double nr
    double wavelength

cdef inline double bp_beamsize(const beam_param* bp) noexcept nogil:
    return beam_size(bp.q, bp.nr, bp.wavelength)

cdef inline double bp_waistsize(const beam_param* bp) noexcept nogil:
    return waist_size(bp.q, bp.nr, bp.wavelength)

cdef inline double bp_waistpos(const beam_param* bp) noexcept nogil:
    return creal(bp.q)

cdef inline double bp_rayleigh(const beam_param* bp) noexcept nogil:
    return cimag(bp.q)

cdef inline double bp_gouy(const beam_param* bp) noexcept nogil:
    return gouy(bp.q)

cdef inline double bp_divergence(const beam_param* bp) noexcept nogil:
    return divergence(bp.q, bp.nr, bp.wavelength)

cdef inline double bp_radius_curvature(const beam_param* bp) noexcept nogil:
    return radius_curvature(bp.q)

cdef inline double bp_defocus(const beam_param* bp) noexcept nogil:
    return defocus(bp.q)


cdef inline double bp_overlap(const beam_param* bp_x, const beam_param* bp_y) noexcept nogil:
    return overlap(bp_x.q, bp_y.q)


### Corresponding functions acting on standard complex_t data ###

cpdef inline double beam_size(complex_t q, double nr, double lambda0) noexcept nogil:
    return cabs(q) * sqrt(lambda0 / (nr * PI * cimag(q)))

cpdef inline double waist_size(complex_t q, double nr, double lambda0) noexcept nogil:
    return sqrt(lambda0 * cimag(q) / (PI * nr))

cpdef inline double gouy(complex_t q) noexcept nogil:
    return atan2(creal(q), cimag(q))

cpdef inline double divergence(complex_t q, double nr, double lambda0) noexcept nogil:
    return lambda0 / (waist_size(q, nr, lambda0) * PI)

cpdef inline double radius_curvature(complex_t q) noexcept nogil:
    cdef:
        double z = creal(q)
        double zr = cimag(q)
        double zr_on_z = zr / z

    return z * (1 + zr_on_z * zr_on_z)

cpdef inline double defocus(complex_t q) noexcept nogil:
    cdef:
        double z = creal(q)
        double zr = cimag(q)

    return z / (z * z + zr * zr)


cpdef complex_t transform_q(
    const double[:, ::1] M,
    complex_t q1,
    double nr1,
    double nr2
) noexcept nogil

cdef complex_t c_transform_q(
    const double* M,
    complex_t q1,
    double nr,
    double nr2
) noexcept nogil

cpdef complex_t inv_transform_q(
    const double[:, ::1] M,
    complex_t q2,
    double nr1,
    double nr2
) noexcept nogil


cpdef inline double overlap(complex_t qx, complex_t qy) noexcept nogil:
    return fabs(4 * cimag(qx) * cimag(qy)) / cnorm(conj(qx) - qy)


cdef void c_abcd_multiply(
    const double* m1,
    const double* m2,
    double* out,
) noexcept nogil

cdef void abcd_multiply(
    const double[:, ::1] m1,
    const double[:, ::1] m2,
    double[:, ::1] out,
) noexcept nogil

cpdef void sym_abcd_multiply(
    object[:, ::1] m1,
    object[:, ::1] m2,
    object[:, ::1] out,
) noexcept

cpdef bint is_abcd_changing(object[:, ::1] M) noexcept
