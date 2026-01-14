from finesse.cymath.complex cimport complex_t

### Workspace for Bayer-Helms calculations ###

cdef struct knm_bh_workspace:
    bint matched
    bint aligned
    bint is_mm_changing
    bint is_alignment_changing

    # Beam parameters for coupling from basis q1 -> q2
    complex_t q1
    complex_t q2
    # Factor that applies to a tilt angle which yields
    # the actual misalignment angle gamma
    double beta_factor
    # Misalignment angle between the two systems
    double gamma
    double nr
    double lambda0

    # The Gouy phases of q1 and q2, respectively. These are
    # used in the reverse Gouy calculations.
    double gouy1
    double gouy2

    # The following are mismatch parameters and dependencies
    complex_t K_conj
    complex_t k1
    double K0
    complex_t F
    complex_t FS

    # These contain the misaligment parameters
    complex_t X
    complex_t XS
    double ex # equal to exp(-Re{0.5 * X * XS})
    # pre-calculated cos and sin phases for application
    # of imag part of E^(x) equation
    double ex_cos_phase
    double ex_sin_phase

    # Size of the below caches, equal to 1 + maxtem where
    # maxtem is highest order mode included
    int pow_cache_size
    # Integer power caches for each of {F, FS, X, XS}
    complex_t* F_pow_cache
    complex_t* FS_pow_cache
    complex_t* X_pow_cache
    complex_t* XS_pow_cache
    # And cache for (1 + K0)^{n/2 + 1/4}
    double* K0_plus1_pow_cache

cdef void knm_bh_ws_init(
    knm_bh_workspace* kws,
    complex_t q1,
    complex_t q2,
    double beta,
    double beta_factor,
    double nr,
    double lambda0,
    int maxtem,
    bint is_mismatch_changing=?,
    bint is_alignment_changing=?
) noexcept nogil
cdef void knm_bh_ws_free(knm_bh_workspace* kws) noexcept nogil

cdef bint knm_bh_ws_is_changing(const knm_bh_workspace* kws) noexcept nogil
cdef void knm_bh_ws_recompute(knm_bh_workspace* kws, complex_t q1, complex_t q2, double beta) noexcept nogil
cdef void knm_bh_ws_recompute_mismatch(knm_bh_workspace* kws, complex_t q1, complex_t q2) noexcept nogil
cdef void knm_bh_ws_recompute_misalignment(knm_bh_workspace* kws, double beta) noexcept nogil


### Below are the functions to be used in the compute_scattering_matrices ###
###  function of KnmConnectorWorkspace, each is optimised to the extreme  ###

cdef void fast_compute_knm_matrix_bh(
    const knm_bh_workspace* kws_x, const knm_bh_workspace* kws_y,
    const int* homs,
    complex_t* out,
    Py_ssize_t Nhoms,
    int nthreads,
) noexcept

### Function for computing BH matrix with no modifications. ###
### The modification functions are defined separately here. ###

cdef void compute_knm_matrix_bh(
    const knm_bh_workspace* kws_x, const knm_bh_workspace* kws_y,
    const int[:, ::1] homs,
    complex_t[:, ::1] out,
    bint parallel=?
) noexcept
