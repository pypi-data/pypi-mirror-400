#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Standard mathematical functions for non-complex calculations.

Most of the standard functions of the C ``"math.h"`` header are exposed
at a C level via this module. Refer to the `Common Mathematical Functions C reference
<https://en.cppreference.com/w/c/numeric/math>`_ for the names, arguments
and further details on these functions. One can ``cimport`` such functions
in the same way as cimporting any other C exposed Cython function. For example::

    from finesse.cymath.math cimport sin

will ``cimport`` the `sin <https://en.cppreference.com/w/c/numeric/math/sin>`_ function
for use on ``double`` data types in another Cython extension.
"""


cdef double NATLOGS_N[101]
cdef int NATLOG_MAX = 0

# TODO can probably just store many more than [0-20]!
# pre-computed factorials up to (and including) 20!
# -> stored as double to avoid integer overflow, factorials
#    required for just floating point calcs (so far) anyway
cdef double* FACTORIALS = [
    1.0,
    1.0,
    2.0,
    6.0,
    24.0,
    120.0,
    720.0,
    5040.0,
    40320.0,
    362880.0,
    3628800.0,
    39916800.0,
    479001600.0,
    6227020800.0,
    87178291200.0,
    1307674368000.0,
    20922789888000.0,
    355687428096000.0,
    6402373705728000.0,
    121645100408832000.0,
    2432902008176640000.0
]

cdef double* SQRT_FACTORIALS = [
    1.0,
    1.0,
    1.4142135623730951,
    2.4494897427831779,
    4.8989794855663558,
    10.9544511501033224,
    26.8328157299974777,
    70.9929573971953971,
    200.7984063681781208,
    602.3952191045343625,
    1904.9409439665053014,
    6317.9743589223280651,
    21886.1051811417564750,
    78911.4744508046860574,
    295259.7012800764641725,
    1143535.9058639130089432,
    4574143.6234556520357728,
    18859677.3062531463801861,
    80014834.2854498475790024,
    348776576.6344293951988220,
    1559776268.6284978389739990,
]


cpdef double factorial(int n) noexcept nogil:
    global FACTORIALS

    if n < 21:
        return FACTORIALS[n]

    cdef int i

    global NATLOGS_N
    global NATLOG_MAX

    if n <= NATLOG_MAX:
        return exp(NATLOGS_N[n])

    for i in range(NATLOG_MAX + 1, n + 1):
        NATLOGS_N[i] = NATLOGS_N[i - 1] + log(i)

    NATLOG_MAX = n

    return exp(NATLOGS_N[n])


cpdef double sqrt_factorial(int n) noexcept nogil:
    global SQRT_FACTORIALS

    if n < 21:
        return SQRT_FACTORIALS[n]

    return sqrt(factorial(n))

cpdef double hermite(int n, double x) noexcept nogil:
    cdef int k
    cdef double y1, y2=1.0, y3 = 0.0
    cdef double scale = 2**(n/2.0)
    x *= ROOT2
    # Uses probability hermite polynomials but
    # the scaling ox x and scale factor transform
    # it back into physicist
    if n == 0:
        return scale
    # Hard code the first few as there's some overhead with the loop
    elif n == 1:
        return x * scale
    elif n == 2:
        return (x*x - 1) * scale
    elif n == 3:
        return (x*x - 3) * x * scale
    elif n == 4:
        return (x*x*x*x - 6*x*x + 3) * scale
    elif n == 5:
        return (x*x*x*x*x - 10*x*x*x + 15*x) * scale
    elif n == 6:
        return (x*x*x*x*x*x - 15*x*x*x*x + 45*x*x - 15) * scale
    elif n == 7:
        return (x*x*x*x*x*x*x - 21*x*x*x*x*x + 105*x*x*x - 105*x) * scale
    elif n == 8:
        return (x*x*x*x*x*x*x*x - 28*x*x*x*x*x*x + 210*x*x*x*x - 420*x*x + 105) * scale
    elif n == 9:
        return (x*x*x*x*x*x*x*x*x - 36*x*x*x*x*x*x*x + 378*x*x*x*x*x - 1260*x*x*x + 945*x) * scale
    elif n == 10:
        return (x*x*x*x*x*x*x*x*x*x - 45*x*x*x*x*x*x*x*x + 630*x*x*x*x*x*x -3150*x*x*x*x + 4725*x*x - 945) * scale
    else:
        # looping rather than recursive call is significantly faster
        for k in range(n, 1, -1):
            y1 = x*y2 - k*y3
            y3 = y2
            y2 = y1
        return (x*y2 - y3) * scale
