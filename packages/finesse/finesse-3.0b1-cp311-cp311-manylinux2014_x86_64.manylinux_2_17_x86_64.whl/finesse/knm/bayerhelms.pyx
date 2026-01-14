#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Computation of modal coupling coefficients via the Bayer-Helms
analytic formalism."""

from libc.stdlib cimport calloc, free
from libc.string cimport memset

from cython.parallel import prange

cimport numpy as np
import numpy as np

from finesse.cymath.complex cimport conj, creal, cimag, csqrt, COMPLEX_0 # Standard complex.h functions
from finesse.cymath.complex cimport ceq, inverse_unsafe, crotate2, cpow_re
from finesse.cymath.math cimport exp, sqrt, cos, sin # Standard math.h functions
from finesse.cymath.math cimport factorial, sqrt_factorial, msign, nmin, nmax
from finesse.cymath.gaussbeam cimport gouy, waist_size

from finesse.utilities.cyomp cimport determine_nthreads_even

from finesse.knm.matrix cimport KnmMatrix, rev_gouy, c_reverse_gouy_phases


### Python functions for computing Bayer-Helms coefficients and matrices ###
###            not associated with any component or workspace            ###

def compute_bayerhelms_coeff(
    qx1, qx2, qy1, qy2,
    double xgamma, double ygamma,
    int n1, int m1, int n2, int m2,
    double nr=1.0, double wavelength=1064e-9,
    bint reverse_gouy=False,
):
    """Computes the coupling coefficient, via Bayer-Helms :cite:`BayerHelms`,
    from mode (n1, m1) -> mode (n2, m2).

    .. note::

        Use :func:`.make_bayerhelms_matrix` to compute a scattering matrix of these
        coefficients rather than calling this function in a loop.

    Parameters
    ----------
    qx1 : :class:`.BeamParam` or complex
        Input beam parameter in the tangential plane.

    qx2 : :class:`.BeamParam` or complex
        Output beam parameter in the tangential plane.

    qy1 : :class:`.BeamParam` or complex
        Input beam parameter in the sagittal plane.

    qy2 : :class:`.BeamParam` or complex
        Output beam parameter in the sagittal plane.

    xgamma : float
        Misalignment angle in the tangential plane (in radians).

    ygamma : float
        Misalignment angle in the sagittal plane (in radians).

    n1 : int
        Input tangential mode index.

    m1 : int
        Input sagittal mode index.

    n2 : int
        Output tangential mode index.

    m2 : int
        Output sagittal mode index.

    nr : float, optional; default: 1.0
        Refractive index of the associated medium.

    wavelength : float, optional; default: 1064 nm
        Wavelength of the beam (in metres).

    Returns
    -------
    coeff : complex
        The complex coupling coefficient for the specified mode coupling.
    """
    cdef:
        knm_bh_workspace kws_x
        knm_bh_workspace kws_y
        int maxtem = nmax(n1 + m1, n2 + m2)

    knm_bh_ws_init(&kws_x, qx1, qx2, xgamma, 1.0, nr, wavelength, maxtem)
    knm_bh_ws_init(&kws_y, qy1, qy2, ygamma, 1.0, nr, wavelength, maxtem)

    cdef complex_t coeff = k_nmnm(&kws_x, &kws_y, n1, m1, n2, m2)
    if reverse_gouy:
        coeff = rev_gouy(
            kws_x.gouy1, kws_y.gouy1,
            kws_x.gouy2, kws_y.gouy2,
            coeff, n1, m1, n2, m2
        )

    knm_bh_ws_free(&kws_x)
    knm_bh_ws_free(&kws_y)

    return coeff


def make_bayerhelms_matrix(
    qx1, qx2, qy1, qy2,
    double xgamma, double ygamma,
    double nr=1.0, double wavelength=1064e-9,
    bint reverse_gouy=False,
    bint parallel=True,
    **mode_selection_kwargs,
):
    """Constructs and computes a coupling coefficient scattering
    matrix using the Bayer-Helms :cite:`BayerHelms` analytic
    formalism.

    See the function :func:`.make_modes` for the arguments which
    should be passed via `mode_selection_kwargs`.

    Parameters
    ----------
    qx1 : :class:`.BeamParam` or complex
        Input beam parameter in the tangential plane.

    qx2 : :class:`.BeamParam` or complex
        Output beam parameter in the tangential plane.

    qy1 : :class:`.BeamParam` or complex
        Input beam parameter in the sagittal plane.

    qy2 : :class:`.BeamParam` or complex
        Output beam parameter in the sagittal plane.

    xgamma : float
        Misalignment angle in the tangential plane (in radians).

    ygamma : float
        Misalignment angle in the sagittal plane (in radians).

    nr : float, optional; default: 1.0
        Refractive index of the associated medium.

    wavelength : float, optional; default: 1064 nm
        Wavelength of the beam (in metres).

    reverse_gouy : bool, optional
        Removing Gouy phase terms from calculated matrix

    parallel : bool, optional; default: True
        Whether to enable multi-threaded execution via OpenMP. The
        number of threads used scales with the number of modes;
        bounded by the maximum thread count as given by
        ``omp_get_max_threads``.

    mode_selection_kwargs : keyword arguments
        See :func:`.make_modes`.

    Returns
    -------
    kmat : :class:`.KnmMatrix`
        The resulting scattering matrix as a :class:`.KnmMatrix` object.

    Examples
    --------
    See :ref:`arbitrary_scatter_matrices`.
    """
    from finesse.utilities.homs import make_modes

    cdef:
        knm_bh_workspace kws_x
        knm_bh_workspace kws_y

    modes = make_modes(**mode_selection_kwargs)
    cdef int[:, ::1] modes_view = modes
    cdef int maxtem = np.max(modes[:, 0] + modes[:, 1])

    cdef KnmMatrix kmat = KnmMatrix(modes_view)

    knm_bh_ws_init(&kws_x, qx1, qx2, xgamma, 1.0, nr, wavelength, maxtem)
    knm_bh_ws_init(&kws_y, qy1, qy2, ygamma, 1.0, nr, wavelength, maxtem)

    compute_knm_matrix_bh(&kws_x, &kws_y, modes_view, kmat.data_view, parallel)
    if reverse_gouy:
        c_reverse_gouy_phases(
            kws_x.gouy1, kws_y.gouy1,
            kws_x.gouy2, kws_y.gouy2,
            kmat.data_view, modes_view,
            kmat.data_view
        )

    knm_bh_ws_free(&kws_x)
    knm_bh_ws_free(&kws_y)

    return kmat


### Workspace for Bayer-Helms calculations ###

cdef void knm_bh_ws_init(
    knm_bh_workspace* kws,
    complex_t q1,
    complex_t q2,
    double beta,
    double beta_factor,
    double nr,
    double lambda0,
    int maxtem,
    bint is_mismatch_changing=True,
    bint is_alignment_changing=False
) noexcept nogil:
    kws.nr = nr
    kws.lambda0 = lambda0
    kws.beta_factor = beta_factor
    kws.is_mm_changing = is_mismatch_changing
    kws.is_alignment_changing = is_alignment_changing

    kws.pow_cache_size = maxtem + 1
    kws.F_pow_cache = <complex_t*> calloc(kws.pow_cache_size, sizeof(complex_t))
    if not kws.F_pow_cache:
        raise MemoryError()
    kws.FS_pow_cache = <complex_t*> calloc(kws.pow_cache_size, sizeof(complex_t))
    if not kws.FS_pow_cache:
        raise MemoryError()
    kws.X_pow_cache = <complex_t*> calloc(kws.pow_cache_size, sizeof(complex_t))
    if not kws.X_pow_cache:
        raise MemoryError()
    kws.XS_pow_cache = <complex_t*> calloc(kws.pow_cache_size, sizeof(complex_t))
    if not kws.XS_pow_cache:
        raise MemoryError()
    kws.K0_plus1_pow_cache = <double*> calloc(kws.pow_cache_size, sizeof(double))
    if not kws.K0_plus1_pow_cache:
        raise MemoryError()

    # Compute all of the workspace parameters - i.e. both mismatch
    # and misalignment terms, as well as other quantities like the
    # Gouy phases of q1, q2 required for reverse Gouy operations
    knm_bh_ws_recompute(kws, q1, q2, beta)

cdef void knm_bh_ws_free(knm_bh_workspace* kws) noexcept nogil:
    if kws.F_pow_cache != NULL: free(kws.F_pow_cache)
    if kws.FS_pow_cache != NULL: free(kws.FS_pow_cache)
    if kws.X_pow_cache != NULL: free(kws.X_pow_cache)
    if kws.XS_pow_cache != NULL: free(kws.XS_pow_cache)
    if kws.K0_plus1_pow_cache != NULL: free(kws.K0_plus1_pow_cache)

cdef void knm_bh_ws_reset_mm_cpow_caches(knm_bh_workspace* kws) noexcept nogil:
    cdef Py_ssize_t i

    memset(kws.F_pow_cache, 0, kws.pow_cache_size * sizeof(complex_t))
    memset(kws.FS_pow_cache, 0, kws.pow_cache_size * sizeof(complex_t))
    memset(kws.K0_plus1_pow_cache, 0, kws.pow_cache_size * sizeof(double))
    kws.F_pow_cache[0] = 1.0 + 0.0j
    kws.FS_pow_cache[0] = 1.0 + 0.0j

    cdef double root_K0_plus1 = sqrt(1.0 + kws.K0)
    kws.K0_plus1_pow_cache[0] = sqrt(root_K0_plus1)

    if not kws.matched:
        for i in range(1, kws.pow_cache_size):
            kws.F_pow_cache[i] = kws.F * kws.F_pow_cache[i - 1]
            kws.FS_pow_cache[i] = kws.FS * kws.FS_pow_cache[i - 1]
            kws.K0_plus1_pow_cache[i] = root_K0_plus1 * kws.K0_plus1_pow_cache[i - 1]

cdef void knm_bh_ws_reset_alignment_cpow_caches(knm_bh_workspace* kws) noexcept nogil:
    cdef Py_ssize_t i

    memset(kws.X_pow_cache, 0, kws.pow_cache_size * sizeof(complex_t))
    memset(kws.XS_pow_cache, 0, kws.pow_cache_size * sizeof(complex_t))
    kws.X_pow_cache[0] = 1.0 + 0.0j
    kws.XS_pow_cache[0] = 1.0 + 0.0j

    if not kws.aligned:
        for i in range(1, kws.pow_cache_size):
            kws.X_pow_cache[i] = kws.X * kws.X_pow_cache[i - 1]
            kws.XS_pow_cache[i] = kws.XS * kws.XS_pow_cache[i - 1]

cdef inline bint knm_bh_ws_is_changing(const knm_bh_workspace* kws) noexcept nogil:
    return kws.is_mm_changing or kws.is_alignment_changing

cdef void knm_bh_ws_recompute(knm_bh_workspace* kws, complex_t q1, complex_t q2, double beta) noexcept nogil:
    knm_bh_ws_recompute_mismatch(kws, q1, q2)
    knm_bh_ws_recompute_misalignment(kws, beta)

cdef void knm_bh_ws_recompute_mismatch(knm_bh_workspace* kws, complex_t q1, complex_t q2) noexcept nogil:
    cdef:
        double zr
        complex_t K

    kws.q1 = q1
    kws.q2 = q2

    kws.gouy1 = gouy(q1)
    kws.gouy2 = gouy(q2)

    kws.matched = ceq(q1, q2)
    if kws.matched:
        kws.K_conj = COMPLEX_0
        kws.k1 = 1.0 + 0.0j
        kws.K0 = 0.0
        kws.FS = COMPLEX_0
        kws.F = COMPLEX_0
    else:
        zr = 1.0 / cimag(q2)

        # K is the mismatch parameter
        K = 0.5 * zr * ((cimag(q1) - cimag(q2)) + (creal(q1) - creal(q2)) * 1.0j)
        kws.K_conj = conj(K)
        # The X, XS variables contain a 1/sqrt(1+K*) factor, this
        # is computed here then applied to kws.X, kws.XS later
        kws.k1 = inverse_unsafe(csqrt(1.0 + kws.K_conj))
        kws.K0 = 2.0 * creal(K)

        kws.F = 0.5 * kws.K_conj
        kws.FS = 0.5 * K / (1.0 + kws.K0)

    knm_bh_ws_reset_mm_cpow_caches(kws)

cdef void knm_bh_ws_recompute_misalignment(knm_bh_workspace* kws, double beta) noexcept nogil:
    cdef:
        double Theta, gg0, z2z0
        complex_t x1, x2, exponent

    kws.gamma = kws.beta_factor * beta
    kws.aligned = kws.gamma == 0.0
    if kws.aligned:
        kws.X = COMPLEX_0
        kws.XS = COMPLEX_0

        # These won't be used when system is aligned but here they
        # will be initialised to correct corresponding values in
        # case they get accessed accidentally at some point
        kws.ex = 1.0
        kws.ex_cos_phase = 1.0
        kws.ex_sin_phase = 0.0
    else:
        # TODO (sjr) The following should also include lateral displacement
        #            terms from Bayer-Helms (in X, XS, ex variables), see
        #            Issue #238 which tracks this

        # The divergence angle of the second mode
        Theta = waist_size(kws.q2, kws.nr, kws.lambda0) / cimag(kws.q2)
        # this gives the factor (gamma / w0) * zr
        gg0 = kws.gamma / Theta
        z2z0 = creal(kws.q2) / cimag(kws.q2)

        x1 = z2z0 - 1.0j
        x2 = z2z0 + (1.0 + 2.0 * kws.K_conj) * 1.0j

        # Here we have X  = (gamma / w0) * zr * (z2 / zr +i*(1 + 2K*)) * 1/sqrt(1 + K*)
        #                 = (gamma / w0) * (z2 + i*zr*(1 + 2K*)) / sqrt(1 + K*)
        kws.X = gg0 * x2 * kws.k1
        # And Xbar = (gamma / w0) * zr * (z2 / zr - i) * 1/sqrt(1 + K*)
        #          = (z2 - i*zr) * (gamma / w0) / sqrt(1 + K*)
        kws.XS = gg0 * x1 * kws.k1
        # This is the exponent of the E^(x) equation seen in Bayer-Helms...
        exponent = 0.5 * kws.XS * kws.X

        # ... and these correspond to the terms of E^(x)
        # i.e. exp(-ex) = exp(-Re(ex)) * exp(-i*Im(ex))
        #               = exp(-Re(ex)) * (cos(Im(ex)) - i*sin(Im(ex)))
        # we pre-calculate these for efficiency so that crotate2 can be used in k_mm
        kws.ex = exp(-creal(exponent))
        kws.ex_cos_phase = cos(cimag(exponent))
        kws.ex_sin_phase = -sin(cimag(exponent))

    knm_bh_ws_reset_alignment_cpow_caches(kws)


### Below are the functions to be used in the compute_scattering_matrices ###
###  function of KnmConnectorWorkspace, each is optimised to the extreme  ###


cdef void fast_compute_knm_matrix_bh(
    const knm_bh_workspace* kws_x, const knm_bh_workspace* kws_y,
    const int* homs,
    complex_t* out,
    Py_ssize_t Nhoms,
    int nthreads,
) noexcept:
    """Compute a reflection Bayer-Helms scattering matrix in a very highly
    optimised way. Does a single pass over the matrix: computing
    the coupling coefficients, reverse Gouy phases in-place and flips sign
    of all odd couplings in tangential plane.

    Uses a flat pointer to output matrix rather than memory-view such
    that KnmConnectorWorkspace.compute_scattering_matrices doesn't need
    to do any slow converting to memory-views from matrix pointers.
    """
    cdef:
        Py_ssize_t i, j

        int n1, m1, n2, m2
        complex_t coeff, coeff_rg

    for i in prange(Nhoms, nogil=True, num_threads=nthreads, schedule="static"):
        n1 = homs[2 * i]
        m1 = homs[2 * i + 1]
        for j in range(Nhoms):
            n2 = homs[2 * j]
            m2 = homs[2 * j + 1]

            # Compute the coefficent per BH
            coeff = k_nmnm(kws_x, kws_y, n1, m1, n2, m2)
            # Reverse the Gouy phase in-place
            coeff_rg = rev_gouy(
                kws_x.gouy1, kws_y.gouy1,
                kws_x.gouy2, kws_y.gouy2,
                coeff, n1, m1, n2, m2
            )
            out[j*Nhoms + i] = coeff_rg


### Function for computing BH matrix with no modifications. ###
### The modification functions are defined separately here. ###


cdef void compute_knm_matrix_bh(
    const knm_bh_workspace* kws_x, const knm_bh_workspace* kws_y,
    const int[:, ::1] homs,
    complex_t[:, ::1] out,
    bint parallel=True,
) noexcept:
    """Compute a Bayer-Helms scattering matrix.

    This is used only for the Python utility function `make_bayerhelms_matrix`. The
    heavily optimised versions, which get used by KnmConnectorWorkspaces during
    simulations, are above.
    """
    cdef:
        Py_ssize_t N = homs.shape[0]
        Py_ssize_t i, j

        int n1, m1, n2, m2

        int nthreads = 0

    if parallel:
        # See SparseMatrixSimulation.initialise_sim_config_data
        # for details on the thread count setting logic used here
        nthreads = determine_nthreads_even(N, 10)

    if not nthreads:
        nthreads = 1

    for i in prange(N, nogil=True, num_threads=nthreads, schedule="static"):
        n1 = homs[i][0]
        m1 = homs[i][1]
        for j in range(N):
            n2 = homs[j][0]
            m2 = homs[j][1]
            out[j][i] = k_nmnm(kws_x, kws_y, n1, m1, n2, m2)


### The functions for computing the coefficients themselves ###

cdef complex_t k_nmnm(
    const knm_bh_workspace* kws_x, const knm_bh_workspace* kws_y,
    int n1, int m1,
    int n2, int m2,
) noexcept nogil:
    cdef:
        complex_t z1, z2

    if kws_x.aligned and kws_y.aligned:
        if kws_x.matched and kws_y.matched:
            if n1 == n2 and m1 == m2:
                return 1.0 + 0.0j
            else:
                return 0.0 + 0.0j

    z1 = k_mm(kws_x, n1, n2)
    z2 = k_mm(kws_y, m1, m2)

    return z1 * z2

cdef complex_t k_mm(
    const knm_bh_workspace* kws,
    int m1, int m2,
) noexcept nogil:
    cdef:
        double out1
        complex_t out2
        complex_t sg, su

        double root_m1f_m2f = sqrt_factorial(m1) * sqrt_factorial(m2)

    # (-1)^{n'}
    out1 = msign(m2)
    # sqrt{n! n'!}
    out2 = root_m1f_m2f
    if not kws.matched:
        out2 *= (
            # (1 + K*)^{-(n + n' + 1) / 2}
            cpow_re(1.0 + kws.K_conj, -0.5 * (m1 + m2 + 1)) *
            # (1 + K0)^{n/2 + 1/4}
            kws.K0_plus1_pow_cache[m1]
        )

    sg = S_g(kws, m1, m2)
    su = S_u(kws, m1, m2)

    if kws.aligned:
        return out1 * out2 * (sg - su)

    # See comments at end of knm_bh_ws_recompute_misalignment for description
    return out1 * kws.ex * crotate2(
        out2 * (sg - su), kws.ex_cos_phase, kws.ex_sin_phase
    )

cdef complex_t S_g(const knm_bh_workspace* kws, int m1, int m2) noexcept nogil:
    cdef:
        int s1, s2
        complex_t z, z1, z2
        complex_t nom1, nom2
        double denom1, denom2
        int i, j, k # loop indices

    if m1 == 0 or m1 == 1:
        s1 = 0
    else:
        if m1 % 2: # m1 odd
            s1 = int((m1 - 1) / 2)
        else: # m1 even
            s1 = int(m1 / 2)

    if m2 == 0 or m2 == 1:
        s2 = 0
    else:
        if m2 % 2: # m2 odd
            s2 = int((m2 - 1) / 2)
        else: # m2 even
            s2 = int(m2 / 2)

    z = COMPLEX_0
    for i in range(1 + s1):
        for j in range(1 + s2):
            nom1 = kws.XS_pow_cache[m1 - 2 * i] * kws.X_pow_cache[m2 - 2 * j]
            if nom1 == COMPLEX_0:
                continue

            denom1 = (
                factorial(m1 - 2 * i) *
                factorial(m2 - 2 * j)
            )
            z1 = nom1 * msign(i) / denom1
            z2 = COMPLEX_0
            for k in range(1 + nmin(i , j)):
                nom2 = kws.FS_pow_cache[i - k] * kws.F_pow_cache[j - k]
                if nom2 == COMPLEX_0:
                    continue

                denom2 = (
                    factorial(2 * k) *
                    factorial(i - k) *
                    factorial(j - k)
                )
                z2 += nom2 * msign(k) / denom2

            z += z1 * z2

    return z

cdef complex_t S_u(const knm_bh_workspace* kws, int m1, int m2) noexcept nogil:
    cdef:
        int s3, s4
        complex_t z, z1, z2
        complex_t nom1, nom2
        double denom1, denom2
        int i, j, k # loop indices

    if m1 == 0 or m2 == 0:
        return COMPLEX_0

    if m1 == 1 or m1 == 2:
        s3 = 0
    else:
        if m1 % 2: # m1 odd -> (m1 - 1) even
            s3 = int((m1 - 1) / 2)
        else: # m1 even -> (m1 - 1) odd
            s3 = int((m1 - 2) / 2)

    if m2 == 1 or m2 == 2:
        s4 = 0
    else:
        if m2 % 2: # m2 odd -> (m2 -1) even
            s4 = int((m2 - 1) / 2)
        else:
            s4 = int((m2 - 2) / 2)

    z = COMPLEX_0
    for i in range(1 + s3):
        for j in range(1 + s4):
            nom1 = kws.XS_pow_cache[m1 - 2 * i - 1] * kws.X_pow_cache[m2 - 2 * j - 1]
            if nom1 == COMPLEX_0:
                continue

            denom1 = factorial(m1 - 2 * i - 1) * factorial(m2 - 2 * j - 1)
            z1 = nom1 * msign(i) / denom1
            z2 = COMPLEX_0
            for k in range(1 + nmin(i, j)):
                nom2 = kws.FS_pow_cache[i - k] * kws.F_pow_cache[j - k]
                if nom2 == COMPLEX_0:
                    continue

                denom2 = (
                    factorial(2 * k + 1) *
                    factorial(i - k) *
                    factorial(j - k)
                )
                z2 += nom2 * msign(k) / denom2

            z += z1 * z2

    return z
