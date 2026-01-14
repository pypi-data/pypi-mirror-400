cimport numpy as np

cdef extern from "math.h" nogil:
    double cos(double arg)
    double sin(double arg)

ctypedef np.complex128_t complex_t


cdef:
    double complex COMPLEX_0 = 0.0
    double complex COMPLEX_1 = 1.0
    double complex COMPLEX_I = 1.0j


IF UNAME_SYSNAME != "Windows":
    cdef extern from "complex.h" nogil:
        double cabs(double complex z)
        double carg(double complex z)
        double complex cexp(double complex z)
        double cimag(double complex z)
        double creal(double complex z)
        double complex csqrt(double complex z)
        double complex conj(double complex z)
        double complex clog(double complex z)

    cpdef inline double cnorm(complex_t z) noexcept nogil:
        return creal(z) * creal(z) + cimag(z) * cimag(z)

    cpdef inline complex_t inverse_unsafe(complex_t z) noexcept nogil:
        cdef double inv_abs_sqd_z = 1.0 / cnorm(z)
        return creal(z) * inv_abs_sqd_z - 1.0j * cimag(z) * inv_abs_sqd_z

    cpdef inline complex_t crotate2(complex_t z, double cph, double sph) noexcept nogil:
        cdef:
            double zre = creal(z)
            double zim = cimag(z)

        return zre * cph - zim * sph + 1j * (zre * sph + zim * cph)

ELSE:
    cdef extern from "<complex.h>" nogil:
        ctypedef struct _Dcomplex:
            pass
        double _cabs "cabs"(_Dcomplex z)
        double _carg "carg"(_Dcomplex z)
        _Dcomplex _cexp "cexp"(_Dcomplex z)
        double _cimag "cimag"(_Dcomplex z)
        double _creal "creal"(_Dcomplex z)
        _Dcomplex _csqrt "csqrt"(_Dcomplex z)
        _Dcomplex _conj "conj"(_Dcomplex z)
        _Dcomplex _clog "clog"(_Dcomplex z)
        _Dcomplex _Cbuild( double real, double imaginary)

    # --------------------------------------------------------------------
    # Here we provide an interface between the python complex and windows
    # _Dcomplex type... this will be slower probably, but until MSVC
    # supports proper complex types it's a complete pain to work with
    # and would require changing the rest of the code base to go back to
    # the finesse 2 z_by_z, etc. style
    # --------------------------------------------------------------------
    cdef inline double cabs(complex_t z) noexcept nogil:
        return _cabs((<_Dcomplex*>&z)[0])

    cdef inline double carg(complex_t z) noexcept nogil:
        return _carg((<_Dcomplex*>&z)[0])

    cdef inline complex_t cexp(complex_t z) noexcept nogil:
        cdef _Dcomplex _z = _cexp((<_Dcomplex*>&z)[0])
        return (<complex_t*>&_z)[0]

    cdef inline complex_t csqrt(complex_t z) noexcept nogil:
        cdef _Dcomplex _z = _csqrt((<_Dcomplex*>&z)[0])
        return (<complex_t*>&_z)[0]

    cdef inline complex_t conj(complex_t z) noexcept nogil:
        cdef _Dcomplex _z = _conj((<_Dcomplex*>&z)[0])
        return (<complex_t*>&_z)[0]

    cdef inline complex_t clog(complex_t z) noexcept nogil:
        cdef _Dcomplex _z = _clog((<_Dcomplex*>&z)[0])
        return (<complex_t*>&_z)[0]

    cdef inline double creal(complex_t z) noexcept nogil:
        return z.real

    cdef inline double cimag(complex_t z) noexcept nogil:
        return z.imag
    # --------------------------------------------------------------------

    cpdef inline double cnorm(complex_t z) noexcept nogil:
        cdef double re = creal(z)
        cdef double im = cimag(z)
        return re*re + im*im

    cpdef inline complex_t inverse_unsafe(complex_t z) noexcept nogil:
        cdef double inv_abs_sqd_z = 1.0 / cnorm(z)
        cdef _Dcomplex _z = _Cbuild(inv_abs_sqd_z * creal(z), -inv_abs_sqd_z * cimag(z))
        return (<complex_t*>&_z)[0]

    cpdef inline complex_t crotate2(complex_t z, double cph, double sph) noexcept nogil:
        cdef:
            double zre = creal(z)
            double zim = cimag(z)

        cdef _Dcomplex _z = _Cbuild(zre * cph - zim * sph, (zre * sph + zim * cph))
        return (<complex_t*>&_z)[0]

cpdef inline complex_t crotate(complex_t z, double ph) noexcept nogil:
    cdef:
        double cph = cos(ph)
        double sph = sin(ph)

    return crotate2(z, cph, sph)

cpdef inline bint czero(complex_t z):
    return creal(z) == 0.0 and cimag(z) == 0

cpdef complex_t cpow_re(complex_t z, double n) noexcept nogil
cpdef bint ceq(complex_t z1, complex_t z2) noexcept nogil

"""Dense complex matrix, contiguous in memory"""
cdef struct DenseZMatrix:
    complex_t *ptr
    Py_ssize_t stride1 # in units of 16 bytes
    Py_ssize_t stride2 # in units of 16 bytes
    Py_ssize_t size1
    Py_ssize_t size2


"""Dense complex vector, contiguous in memory"""
cdef struct DenseZVector:
    complex_t *ptr
    Py_ssize_t stride # in units of 16 bytes
    Py_ssize_t size
