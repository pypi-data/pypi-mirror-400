cdef extern from "math.h" nogil:
    double atan2(double y, double x)
    double cos(double arg)
    double exp(double arg)
    double fabs(double arg)
    double fmax(double x, double y)
    double log(double x)
    double sin(double arg)
    double sqrt(double arg)
    double asin(double arg)
    double acos(double arg)
    double cosh(double arg)
    double sinh(double arg)
    double ceil(double arg)
    double floor(double arg)
    int isfinite(float arg)
    float NAN
    float INF

cdef extern from "constants.h":
    long double PI
    double DEG2RAD
    double RAD2DEG
    double ROOT2

## TODO (sjr) Used the fused type below on some functions
##            in this file for template-like behaviour

#ctypedef fused real_numeric_t: # non-complex numeric type
#    short
#    int
#    long
#    float
#    double

cpdef inline double degrees(double x) noexcept nogil:
    return x * RAD2DEG


cpdef inline double radians(double x) noexcept nogil:
    return x * DEG2RAD

cpdef inline int sgn(double x) noexcept nogil:
    return (0.0 < x) - (x < 0.0)

cpdef inline double msign(int n) noexcept nogil:
    return -1.0 if n % 2 else 1.0


cpdef inline int nmin(int n, int m) noexcept nogil:
    return n if n < m else m


cpdef inline int nmax(int n, int m) noexcept nogil:
    return n if n > m else m


cpdef inline bint float_eq(double x, double y) noexcept nogil:
    if x == 0.0 and y == 0.0:
        return 1
    else:
        return fabs(x - y) / fmax(fabs(x), fabs(y)) < 1e-13


cpdef double factorial(int n) noexcept nogil
cpdef double sqrt_factorial(int n) noexcept nogil

cpdef double hermite(int n, double x) noexcept nogil
