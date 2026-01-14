from finesse.cymath.complex cimport complex_t
from finesse.cymath.gaussbeam cimport beam_param


cdef struct unm_workspace:
    double k
    double root_w0x # sqrt(w0x)
    double root_w0y # sqrt(w0y)
    double gouyx
    double gouyy
    double root2_on_wx # sqrt(2) / wx
    double root2_on_wy # sqrt(2) / wy
    complex_t inv_qx
    complex_t inv_qy
    complex_t xgauss_exponent # - ik / (2 qx)
    complex_t ygauss_exponent # - ik / (2 qy)
    complex_t z1x # sqrt(i Im{qx} / qx)
    complex_t z1y # sqrt(i Im{qy} / qy)
    complex_t z2x # sqrt(i Im(qx) qx* / (-i Im(qx) qx))
    complex_t z2y # sqrt(i Im(qy) qy* / (-i Im(qy) qy))
    # Used when n, m specified in unm_ws_recache so that more
    # optimised fixed mode index calculations can be performed
    int n, m
    complex_t xpre_factor
    complex_t ypre_factor

cdef void unm_ws_recache_from_bp(
    unm_workspace* uws,
    const beam_param* qx,
    const beam_param* qy,
    int* n=?,
    int* m=?,
) noexcept nogil

cdef void unm_ws_recache(
    unm_workspace* uws,
    complex_t qx,
    complex_t qy,
    double nr,
    double lambda0,
    int* n=?,
    int* m=?
) noexcept nogil

cdef struct unm_factor_store:
    # (2 / pi)^{1/4} * 1 / sqrt(2**n * n! * w0x) * z1x * z2x**m
    # for each mode index n
    complex_t* xpre_factor_cache
    # same as above but for y and each mode index m
    complex_t* ypre_factor_cache
    int nsize
    int msize

cdef void unm_factor_store_init(
    unm_factor_store* ufs,
    const unm_workspace* uws,
    int max_n,
    int max_m,
    bint remove_gouy,
    bint flip_odd_x_modes
) noexcept nogil

cdef void unm_factor_store_recache(
    unm_factor_store* ufs,
    const unm_workspace* uws,
    bint remove_gouy,
    bint flip_odd_x_modes
) noexcept nogil

cdef void unm_factor_store_free(unm_factor_store* ufs) noexcept nogil

cdef complex_t u_nm(const unm_workspace* uws, int n, int m, double x, double y) noexcept nogil
cdef complex_t u_nm__fast(
    const unm_workspace* uws,
    const unm_factor_store* ufs,
    int n, int m,
    double x, double y
) noexcept nogil
cdef complex_t u_nmconst(const unm_workspace* uws, double x, double y) noexcept nogil

cdef complex_t u_n(const unm_workspace* uws, int n, double x) noexcept nogil
cdef complex_t u_n__fast(
    const unm_workspace* uws,
    const unm_factor_store* ufs,
    int n,
    double x,
) noexcept nogil
cdef complex_t u_nconst(const unm_workspace* uws, double x) noexcept nogil

cdef complex_t u_m(const unm_workspace* uws, int m, double y) noexcept nogil
cdef complex_t u_m__fast(
    const unm_workspace* uws,
    const unm_factor_store* ufs,
    int m,
    double y,
) noexcept nogil
cdef complex_t u_mconst(const unm_workspace* uws, double y) noexcept nogil


cpdef Py_ssize_t field_index(int n, int m, const int[:, ::1] homs) noexcept nogil
cpdef bint in_mask(int n, int m, const int[:, ::1] mask) noexcept nogil


cdef class HGModeWorkspace:
    cdef public int n, m

    cdef readonly:
        complex_t qx, qy
        double nr
        double lambda0

        bint is_astigmatic

    cdef unm_workspace uws

    cpdef set_values(self, qx=?, qy=?, nr=?, lambda0=?)

    cpdef u_n(self, x, complex_t[::1] out=?)
    cpdef u_m(self, y, complex_t[::1] out=?)
    cpdef u_nm(self, x, y, out=?)
