"""Hello-Vinet equations for thermal lenses in cylindrical mirrors.
Higher order mode thermal effects are not implemented here. Therefore
all the functions return some axially symmetric data.

Equations all based on :cite:`vinet_liv_rev`:

    Jean-Yves Vinet, "On Special Optical Modes and Thermal Issues in
    Advanced Gravitational Wave Interferometric Detectors"
    Living Review 2009
"""

from scipy.optimize.cython_optimize cimport brentq
from scipy.special import jv, j0, eval_laguerre
import numpy as np
cimport numpy as np
from finesse.knm.integrators import composite_newton_cotes_weights

cdef double SIGMA_F = 5.6710e-8

cdef struct f_args:
    double chi
    int n

# find solutions of f eq 3.11
cdef double f(double x, void *args) noexcept:
    cdef f_args *fargs = <f_args*>args
    return x * jv(fargs.n + 1, x) - fargs.chi * jv(fargs.n, x)


cpdef zeros_of_xjn_1_chi_jn(double chi, int n_max, int s_max, double accuracy) :
    """Compute the roots of the equation

    .. math::
        x J_{n+1}(x) - \chi J_{n}(x) = 0

    which is used throughout the Hello-Vinet thermal equations.

    Parameters
    ----------
    chi : float
        Reduced radiation constant
    n_max : int
        Max bessel order to compute up to, must be > 0
    s_max : int
        Max number of zeros to compute, must be >= 2
    accuracy : double
        absolute error on zero finding brentq algorithm

    Returns
    -------
    eta_n_s : array_like
        Array of s_max zeros for the n_max bessel functions

    Notes
    -----
    This is based on the calculations in :cite:`vinet_liv_rev`. The zeros of this function
    are used in multiple calculations throughout the text.

    This algorithm finds the first two zeros of the 0th order bessel function
    then from there assumes the next zero is approximately the difference between
    the last two further away.

    For higher order bessels, the zeros are always between the zeros of n-1 zeros
    which can be used as bounds for root finding.


    """
    cdef:
        Py_ssize_t n, s
        double dx = 0
        f_args args

    if chi == 0:
        raise RuntimeError("Chi should be > 0")
    if not (n_max >= 0):
        raise RuntimeError("n_max must >= 0")
    if not (s_max >= 2):
        raise RuntimeError("s_max must >= 2")

    args.chi = chi
    args.n = 0

    cdef double[:,::1] zeros = np.zeros((n_max+1, s_max), dtype=np.float64)
    # Depedning on the value of chi
    # first zero is always between 0 and first zero of j0 (plus a little)
    zeros[0, 0] = brentq(f, 1e-6, 2.4048+0.2, <f_args *> &args, accuracy, 0, 10000, NULL)
    # next zero will be between this and the second zero of j1
    zeros[0, 1] = brentq(f, zeros[0, 0]+1e-3, 7.0156-0.1, <f_args *> &args, accuracy, 0, 10000, NULL)

    for s in range(2, s_max):
        # after the first few zeros, the rest are relatively consistently separated
        # by just using the previous difference between the zeros, as the bessels
        # start acting sinusoidally, eventually this just tends to pi separation
        # between the zeros
        dx = zeros[0, s-1]-zeros[0, s-2]
        # factors 0.8 and 1.2 are just experimentally chosen, works for small and large chi
        # values ok
        zeros[0, s] = brentq(f, zeros[0, s-1]+0.7*dx, zeros[0, s-1]+1.3*dx, <f_args *> &args, accuracy, 0, 10000, NULL)
    # zeros of n+1 are always between the zeros of n
    for n in range(1, n_max+1):
        args.n = n
        for s in range(s_max-1):
            zeros[n, s] = brentq(f, zeros[n-1, s], zeros[n-1, s+1], <f_args *> &args, accuracy, 0, 10000, NULL)
        # Get final zero
        s += 1
        dx = zeros[n-1, s] - zeros[n-1, s-1]
        zeros[n, s] = brentq(f, zeros[n-1, s], zeros[n-1, s]+dx, <f_args *> &args, accuracy, 0, 10000, NULL)

    return np.asarray(zeros)


def get_p_n_s(a, w, n, m, chi, eta_n_s, eta_n_s_sq):
    """Returns beam intensity overlap coefficients as calculated by Eq 3.33
    in :cite:`vinet_liv_rev`.

    Parameters
    ----------
    a : float
        mirror radius
    w : float
        spot size radius
    n, m : int
        LG mode order
    chi : float
        Reduced radiation constant
    eta_n_s : array_like
        2D array with dimensions (n_max, s_max) for the n-th order Bessel
        and the first s zeros of the Bessel equation 3.11 :cite:`vinet_liv_rev`.
        See :func:`finesse.thermal.hello_vinet.zeros_of_xjn_1_chi_jn` to compute these.
    eta_n_s_sq : array_like
        Cached (eta_n_s)^2 values

    Notes
    -----
    This is currently limited to computing only the LG00 mode, higher order
    modes are still on the todo list.


    """
    y_0_s = eta_n_s_sq[0,:] * w**2/ (8*a*a) # Eq 3.37
    L_n = eval_laguerre(n, y_0_s)
    L_n_m = eval_laguerre(n+m, y_0_s)
    p_0_s = eta_n_s_sq[0,:] / (chi*chi + eta_n_s_sq[0,:]) / j0(eta_n_s[0,:])**2 * np.exp(-y_0_s) * L_n * L_n_m # Eq 3.33
    return p_0_s # only handle n=0 at the moment


def eval_p_n_s_numerical(result):
    """Evaluates a Fourier-Bessel decomposition fit performed with
    :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`.

    Returns
    -------
    I_r : ndarray
        Irradiance from fit
    """
    r, _, _, p_n_s, _, Jn_k_ns_r_a, _ = result
    return 1 / (np.pi*r.max()**2) * (p_n_s * Jn_k_ns_r_a).sum(2).T.squeeze()


def get_p_n_s_numerical(I, a, s_max, material, barrel_material = None, n_max=0, T_ext=293.15, root_accuracy=1e-6, newton_cotes_order=2):
    """Performs a Fourier-Bessel decomposition of some axisymmetric
    irradiance distribution.

    Parameters
    ----------
    I : ndarray
        Axisymmetric irradiance distribution [Wm^-2], defined from r = 0 -> a.
        Radial point array is internally inferred from the size of I.
    a : float
        mirror radius
    s_max : int
        Number of zeros in each Bessel expansion
    material : Material
        Mirror substrate material, see :py:mod:`finesse.materials`
    barrel_material : Material
        Barrel coating material, see :py:mod:`finesse.materials`
    n_max : int, optional
        Number of bessel functions to expand with, typically 0
    T_ext : float, optional
        External temperature around mirror
    root_accuracy : float, optional
        Absolute accuracy of root Bessel function root finding
    newton_cotes_weight : int, optional
        Order of newton-cotes weight for integral

    Returns
    -------
    r : ndarray
        Radial points [m]
    chi_edge : float
        Reduced thermal constant for barrel surface
    chi_face : float
        Reduced thermal constant for end faces
    p_n_s : ndarray
        Fourier-Bessel coefficients
    eta_n_s : ndarray
        Zeros of Bessel function
    Jn_k_ns_r_a : ndarray
        Fourier-Bessel expansion bases

    Examples
    --------

    import finesse.materials
    import finesse.thermal.hello_vinet as hv
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.special import eval_hermite

    finesse.init_plotting()
    # aLIGO like test mass substrate
    material = finesse.materials.FusedSilica
    a = 0.17
    h = 0.2
    w = 53e-3
    r = np.linspace(0, a, 101)
    # 5th order hermite radial distribution
    E = eval_hermite(5, np.sqrt(2)*r/w) * np.exp(-(r/w)**2)
    I = E*E
    plt.plot(r, I)
    # perform Fourier-Bessel decomposition
    fit = hv.get_p_n_s_numerical(I, a, 10, material)
    plt.plot(r, hv.eval_p_n_s_numerical(fit), ls='--', lw=2, label='s_max=10')
    # perform Fourier-Bessel decomposition
    fit = hv.get_p_n_s_numerical(I, a, 20, material)
    plt.plot(r, hv.eval_p_n_s_numerical(fit), ls='--', lw=2, label='s_max=20')
    plt.legend()
    plt.xlabel("r [m]")
    plt.ylabel("I(r) [Wm^-2]")
    plt.title("Fourier-Bessel decomposition of irradiance")

    Notes
    -----
    This returns beam intensity overlap coefficients as calculated by Eq 3.15
    in :cite:`vinet_liv_rev` for an arbitrary radial intensity distribution.
    Typically n_max=0 and s_max is chosen for the required fit.
    The integral is performed using composite Newton-Cotes rule, which by
    default is set to a Simpsons Rule (order 2) which provides better accuracy
    when fewer sample points in the intensity are present. Higher orders
    are not necessarily more accurate as over-fitting from using too high
    a polynomial order can introduce artifacts.

    The resulting fit can be compared using the returned values by passing the tuple of
    results to :func:`finesse.thermal.hello_vinet.eval_p_n_s_numerical`.
    Comparing the above to the original intensity will show how accurate the fit is and
    will determine what s_max and weight ordering you should use. Sharp features in the
    intensity will not fit well.
    """
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge = material.emiss

    N = I.size
    r = np.linspace(0, a, N)
    ns = np.arange(n_max+1)
    chi_edge = 4 * emiss_edge * 5.6710e-8 * T_ext**3 * a / material.kappa
    chi_face = 4 * emiss_face * 5.6710e-8 * T_ext**3 * a / material.kappa
    dr = r[1]-r[0]
    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    W = composite_newton_cotes_weights(len(r), newton_cotes_order)

    Jn_k_ns_r_a = jv(ns[:,None,None], eta_n_s[:, :, None] * r[None, None, :] / a)

    scaling = 2 * np.pi * eta_n_s**2 / ((chi_edge**2 + eta_n_s**2 - ns[:,None])*jv(ns[:,None], eta_n_s)**2)
    integrals = scaling * ((I * r * W)[None,None,:] * Jn_k_ns_r_a).sum(2) * dr
    # final transpose to put basis functions in shape [n, r, s]
    Jn_k_ns_r_a = Jn_k_ns_r_a.transpose((0, 2, 1))

    return (
        r,
        chi_edge,
        chi_face,
        integrals,
        eta_n_s,
        Jn_k_ns_r_a,
        material
    )


def substrate_temperatures_HG00(r, z, a, h, w, material, barrel_material=None, T_ext=293.15, n_max=0, s_max=10, root_accuracy=1e-6):
    """Computes the 2D substrate temperature distribution per
    Watt of absorbed power in each of the coating and substrate
    from a HG00 beam.

    Parameters
    ----------
    r : ndarray
        Radial points
    z : ndarray
        Longitudinal points, should sample points between -h/2 and h/2.
        Sampling outside this region will yield incorrect results.
    a : float
        mirror radius
    h : float
        mirror thickness
    w : float
        spot size radius
    material : Material
        Mirror substrate material, see :py:mod:`finesse.materials`
    barrel_material : Material
        Barrel coating material, see :py:mod:`finesse.materials`
    T_ext : float, optional
        External temperature surrounding mirror
    n_max : int, optional
        Maximum Bessel order for expansion
    s_max : int, optional
        Maximum number of zeros to compute
    root_accuracy : float, optional
        Accuracy of root finding

    Returns
    -------
    T_coat : ndarray(shape=(z.size, r.size))
        2D array of temperature in substrate from
        coating absorption per watt of power absorbed in coating
    T_bulk : ndarray(shape=(z.size, r.size))
        2D array of temperature throughout substrate from
        bulk absorption per watt of power absorber through
        the entire substrate.

    Notes
    -----
    This is using equation 3.20 and 3.25 in :cite:`vinet_liv_rev` for :math:`\phi=0`.

    Currently only works for n_max == 0.


    """
    assert(n_max == 0)
    # Compute data for HG00 heating
    ns = np.arange(n_max+1)
    K = material.kappa
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge = material.emiss
    material.dndT
    chi_edge = 4 * emiss_edge * SIGMA_F * T_ext**3 * a / K
    chi_face = 4 * emiss_face * SIGMA_F * T_ext**3 * a / K
    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    Jn_k_ns_r_a = jv(ns, (eta_n_s[ np.newaxis,:, :] * r[:, np.newaxis])/ a)
    eta_n_s_sq = eta_n_s**2
    z[:, np.newaxis, np.newaxis] * eta_n_s[np.newaxis,:,:] / a # Eq 3.18 shape = (z, n_max, s_max)
    p_n_s = get_p_n_s(a, w, 0, 0, chi_edge, eta_n_s, eta_n_s_sq)
    data = r, chi_edge, chi_face, p_n_s, eta_n_s, Jn_k_ns_r_a, material
    return substrate_temperatures(data, z, h)


def substrate_temperatures(data, z, h):
    """Computes the 2D substrate temperature distribution per
    Watt of absorbed power in each of the coating and substrate
    for an arbitrary axisymmetric heating irradiance computed
    with :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`.

    Parameters
    ----------
    data : tuple
        Irradiance fit data from :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`
    z : ndarray
        Longitudinal points, should sample points between -h/2 and h/2.
        Sampling outside this region will yield incorrect results.
    h : float
        Longitudinal points

    Returns
    -------
    T_coat : ndarray(shape=(z.size, r.size))
        2D array of temperature in substrate from
        coating absorption per watt of power absorbed in coating
    T_bulk : ndarray(shape=(z.size, r.size))
        2D array of temperature throughout substrate from
        bulk absorption per watt of power absorber through
        the entire substrate.

    Notes
    -----
    This is using equation 3.20 and 3.25 in :cite:`vinet_liv_rev` for :math:`\phi=0`.

    Currently only works for n_max == 0.
    """
    # custom irradiance used
    r, _, chi_face, p_n_s, eta_n_s, Jn_k_ns_r_a, material = data
    n_max = eta_n_s.shape[0] - 1
    K = material.kappa
    a = r.max()
    assert(n_max == 0)

    eta_n_s_z_a = z[:, np.newaxis, np.newaxis] * eta_n_s[np.newaxis,:,:] / a # Eq 3.18 shape = (z, n_max, s_max)

    gamma_n_s = eta_n_s * h / (2*a)
    sinh_gamma = np.sinh(gamma_n_s)
    cosh_gamma = np.cosh(gamma_n_s)
    d1_n_s = eta_n_s * sinh_gamma + chi_face * cosh_gamma # Eq 3.19
    d2_n_s = eta_n_s * cosh_gamma + chi_face * sinh_gamma # Eq 3.19

    cosh_d1 = np.cosh(eta_n_s_z_a)/d1_n_s
    sinh_d2 = np.sinh(eta_n_s_z_a)/d2_n_s

    # Assumes that 1W is absorbed so needs to be scaled by user
    T_coat_n_s_z = 1 / (2*np.pi*K*a) * p_n_s * (cosh_d1 - sinh_d2) # Eq 3.20
    #                                                   ^ ± sets which face heating is on
    T_bulk_n_s_z = p_n_s / (np.pi * K * eta_n_s**2) * (1 - chi_face * cosh_d1) # Eq 3.25

    return ( # Eq 3.12
        (T_coat_n_s_z * Jn_k_ns_r_a).sum(2),
        (T_bulk_n_s_z * Jn_k_ns_r_a).sum(2)/h
    )


def thermal_lenses_HG00(r, a, h, w, material, barrel_material = None, T_ext=293.15, n_max=0, s_max=20, root_accuracy=1e-6):
    """Computes the substrate thermal lens per Watt of absorbed
    power in each of the coating and substrate from a HG00 beam.

    Parameters
    ----------
    r : ndarray
        Radial points
    a : float
        mirror radius
    h : float
        mirror thickness
    w : float
        spot size radius
    material : Material
        Mirror substrate material, see :py:mod:`finesse.materials`
    barrel_material : Material
        Barrel cotaing material, see :py:mod:`finesse.materials`
    T_ext : float, optional
        External temperature surrounding mirror
    n_max : int, optional
        Maximum Bessel order for expansion
    s_max : int, optional
        Maximum number of zeros to compute
    root_accuracy : float, optional
        Accuracy of root finding

    Returns
    -------
    Z_coat : ndarray(shape=(r.size,))
        Array of optical path difference in bulk from
        coating absorption per watt of power absorbed
        in coating

    Z_bulk : ndarray(shape=(r.size,))
        Array of optical path difference in bulk from
        bulk absorption per watt absorbed through
        entire substrate [1W/h]

    Notes
    -----
    This is using equation 3.20 and 3.25 in :cite:`vinet_liv_rev` for :math:`\phi=0`.

    Currently only works for n_max == 0.
    """
    assert(n_max == 0)
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge = material.emiss
    K = material.kappa
    chi_edge = 4 * emiss_edge * SIGMA_F * T_ext**3 * a / K
    chi_face = 4 * emiss_face * SIGMA_F * T_ext**3 * a / K

    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    eta_n_s_sq = eta_n_s**2
    p_n_s = get_p_n_s(a, w, 0, 0, chi_edge, eta_n_s, eta_n_s_sq)
    data = r, chi_edge, chi_face, p_n_s, eta_n_s, None, material
    return thermal_lenses(data, h)

def thermal_lenses(data, h):
    """Computes the substrate thermal lens per Watt of absorbed
    power in each of the coating and substrate for an arbitrary
    axisymmetric heating irradiance computed with
    :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`.

    Parameters
    ----------
    data : tuple
        Irradiance fit data from :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`
    h : float
        mirror thickness

    Returns
    -------
    Z_coat : ndarray(shape=(r.size,))
        Array of optical path difference in bulk from
        coating absorption per watt of power absorbed
        in coating

    Z_bulk : ndarray(shape=(r.size,))
        Array of optical path difference in bulk from
        bulk absorption per watt absorbed through
        entire substrate [1W/h]

    Notes
    -----
    This is using equation 3.20 and 3.25 in :cite:`vinet_liv_rev` for :math:`\phi=0`.

    Currently only works for n_max == 0.
    """
    r, _, chi_face, p_n_s, eta_n_s, Jn_k_ns_r_a, material = data
    a = r.max()
    n_max = eta_n_s.shape[0] - 1
    dndT = material.dndT
    ns = np.arange(n_max+1)
    K = material.kappa
    assert(n_max == 0) # i.e. n_max == 0

    gamma_n_s = eta_n_s * h / (2*a)
    sinh_gamma = np.sinh(gamma_n_s)
    cosh_gamma = np.cosh(gamma_n_s)
    d1_n_s = eta_n_s * sinh_gamma + chi_face * cosh_gamma # Eq 3.19

    sinh_gamma_d1 = sinh_gamma/d1_n_s
    # no idea why k_n_s is used in the eqution in manuscript
    Jn_k_ns_r_a = jv(ns, (eta_n_s[ np.newaxis,:, :] * r[:, np.newaxis])/ a)

    # Assumes that 1W is absorbed so needs to be scaled by user
    Z_coat = dndT / (np.pi * K) * (p_n_s / eta_n_s * sinh_gamma_d1 * Jn_k_ns_r_a).sum((0,2)) # Eq 3.41
    # Typo in 3.42 p_s should be p_n_s I assume
    # No h in here as we do 1W absorbed per substrate length
    Z_bulk = dndT / (np.pi*K) * ((p_n_s / eta_n_s**2) * (1 - 2 * chi_face * a / (eta_n_s*h) * sinh_gamma_d1) * Jn_k_ns_r_a).sum((0,2)) # Eq 3.42

    return Z_coat, Z_bulk


def substrate_thermal_expansion_depth_HG00(r, z, a, h, w, material, barrel_material=None, T_ext=293.15, n_max=0, s_max=20, root_accuracy=1e-6):
    """Computes the depth displacements throughout the bulk
    of an optic due to coating absorption. Displacement is
    in units of m per absorbed Watts for a HG00 heating
    beam.

    Parameters
    ----------
    r : ndarray
        Radial points
    z : ndarray
        Longitudinal points, should sample points between -h/2 and h/2.
        Sampling outside this region will yield incorrect results.
    a : float
        mirror radius
    h : float
        mirror thickness
    w : float
        spot size radius
    material : Material
        Mirror substrate material, see :py:mod:`finesse.materials`
    barrel_material : Material
        Barrel cotaing material, see :py:mod:`finesse.materials`
    T_ext : float, optional
        External temperature surrounding mirror
    n_max : int, optional
        Maximum Bessel order for expansion
    s_max : int, optional
        Maximum number of zeros to compute
    root_accuracy : float, optional
        Accuracy of root finding

    Returns
    -------
    U_z_coat_per_W : ndarray(shape=(z.size, r.size))
        D Array of z displacements throughout the substrate
        per absorbed Watts of HG00 beam in coating

    Notes
    -----
    Solving equation 3.117 and 3.118 in :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    assert(n_max == 0)
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge = material.emiss
    K = material.kappa
    chi_edge = 4 * emiss_edge * SIGMA_F * T_ext**3 * a / K
    chi_face = 4 * emiss_face * SIGMA_F * T_ext**3 * a / K
    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    eta_n_s_sq = eta_n_s**2
    p_n_s = get_p_n_s(a, w, 0, 0, chi_edge, eta_n_s, eta_n_s_sq)
    data = r, chi_edge, chi_face, p_n_s, eta_n_s, None, material
    return substrate_thermal_expansion_depth(data, z, h)


def substrate_thermal_expansion_depth(data, z, h):
    """Computes the depth displacements throughout the bulk
    of an optic due to coating absorption. Displacement is
    in units of m per absorbed Watts for a custom axisymmetric
    heating beam, see :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`.

    Parameters
    ----------
    data : tuple
        Irradiance fit data from :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`
    z : ndarray
        Longitudinal points, should sample points between -h/2 and h/2.
        Sampling outside this region will yield incorrect results.
    h : float
        mirror thickness

    Returns
    -------
    U_z_coat_per_W : ndarray(shape=(z.size, r.size))
        D Array of z displacements throughout the substrate
        per absorbed Watts of HG00 beam in coating

    Notes
    -----
    Solving equation 3.117 and 3.118 in :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    r, chi_edge, chi_face, p_n_s, eta_n_s, _, material = data
    a = r.max()
    n_max = eta_n_s.shape[0]-1
    assert(n_max == 0)

    # setup up broadcasting with numpy arrays
    z = z[:,np.newaxis, np.newaxis]
    r = r[:,np.newaxis]
    eta_n_s_z_a = z * eta_n_s / a # Eq 3.18 shape = (z, n_max, s_max)

    gamma_n_s = eta_n_s * h / (2*a)
    sinh_gamma = np.sinh(gamma_n_s)
    cosh_gamma = np.cosh(gamma_n_s)
    d1_n_s = eta_n_s * sinh_gamma + chi_face * cosh_gamma # Eq 3.19
    d2_n_s = eta_n_s * cosh_gamma + chi_face * sinh_gamma # Eq 3.19

    sinh_gamma_d1 = sinh_gamma/d1_n_s

    cosh_d2 = np.cosh(eta_n_s_z_a)/d2_n_s
    sinh_d1 = np.sinh(eta_n_s_z_a)/d1_n_s
    eta_n_s_r_a = r * eta_n_s / a # Eq 3.18 shape = (z, n_max, s_max)

    omega_0 = material.alpha * material.E * chi_edge /(np.pi*material.kappa*h)
    omega_0 *= (p_n_s * jv(0, eta_n_s)/(eta_n_s**3) * sinh_gamma_d1).sum(1) # Eq 3.113

    omega_1 = -12*material.alpha * material.E * chi_edge *a/(np.pi*material.kappa*h**3)
    omega_1 *= (p_n_s * jv(0, eta_n_s)/(eta_n_s**4) * (gamma_n_s * cosh_gamma - sinh_gamma)/d2_n_s).sum(1) # Eq 3.113
    # Eq 3.117
    u_z = material.alpha * (1+material.poisson) /(2 * np.pi * material.kappa)
    u_z *= (p_n_s/eta_n_s * (1/d2_n_s + (sinh_d1 - cosh_d2) * jv(0, eta_n_s_r_a))).sum(2)
    # Eq 3.118
    du_z = (-2*material.poisson/material.E *(omega_0 + 0.5*omega_1 * z) * z \
            - (1-material.poisson)/(2*material.E) * omega_1 * (r**2)).sum(2)
    return u_z + du_z


def surface_deformation_coating_heating_HG00(r, a, h, w, material, barrel_material = None, T_ext=293.15, n_max=0, s_max=20, root_accuracy=1e-6):
    """Computes the depth displacement change of the surface
    of an optic due to coating absorption. Displacement is
    in units of m per absorbed Watts for a HG00 heating
    beam.

    Parameters
    ----------
    r : ndarray
        Radial points
    a : float
        mirror radius
    h : float
        mirror thickness
    w : float
        spot size radius
    material : Material
        Mirror substrate material, see :mod:`finesse.materials`
    barrel_material : Material
        Barrel cotaing material, see :mod:`finesse.materials`
    T_ext : float, optional
        External temperature surrounding mirror
    n_max : int, optional
        Maximum Bessel order for expansion
    s_max : int, optional
        Maximum number of zeros to compute
    root_accuracy : float, optional
        Accuracy of root finding per Watt of power
        absorbed in coating

    Returns
    -------
    U_z_coat_per_W : ndarray(shape=(r.size.))
        Array of z displacements

    Notes
    -----
    Solving equation 3.121 and 3.122 in :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    assert(n_max == 0)
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge =  material.emiss
    chi_edge = 4 * emiss_edge * SIGMA_F * T_ext**3 * a / material.kappa
    chi_face= 4 * emiss_face * SIGMA_F * T_ext**3 * a / material.kappa
    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    p_n_s = get_p_n_s(a, w, 0, 0, chi_edge, eta_n_s, eta_n_s**2)
    data = r, chi_edge, chi_face, p_n_s, eta_n_s, None, material
    return surface_deformation_coating_heating(data, h)


def surface_deformation_coating_heating(data, h):
    """Computes the depth displacement change of the surface
    of an optic due to coating absorption. Displacement is
    in units of m per absorbed Watts for a custom axisymmetric
    heating profile, see :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical` on how
    to generate the data for this.

    Parameters
    ----------
    data : tuple
        Irradiance fit data from :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`
    z : ndarray
        Longitudinal points, should sample points between -h/2 and h/2.
        Sampling outside this region will yield incorrect results.
    h : float
        mirror thickness

    Returns
    -------
    U_z_coat_per_W : ndarray(shape=(r.size.))
        Array of z displacements

    Notes
    -----
    Solving equation 3.121 and 3.122 in :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    r, chi_edge, chi_face, p_n_s, eta_n_s, _, material = data
    a = r.max()
    n_max = eta_n_s.shape[0]-1
    assert(n_max == 0)

    gamma_n_s = eta_n_s * h / (2*a)
    sinh_gamma = np.sinh(gamma_n_s)
    cosh_gamma = np.cosh(gamma_n_s)
    d1_n_s = eta_n_s * sinh_gamma + chi_face * cosh_gamma # Eq 3.19
    d2_n_s = eta_n_s * cosh_gamma + chi_face * sinh_gamma # Eq 3.19

    sinh_gamma_d1 = sinh_gamma/d1_n_s
    cosh_gamma_d2 = cosh_gamma/d2_n_s

    eta_n_s_r_a = r[:, None] * eta_n_s / a # Eq 3.18

    omega_1 = -12*material.alpha * material.E * chi_edge *a/(np.pi*material.kappa*h**3)
    omega_1 *= (p_n_s * jv(0, eta_n_s)/(eta_n_s**4) * (gamma_n_s * cosh_gamma - sinh_gamma)/d2_n_s).sum(1) # Eq 3.113
    # Eq 3.121
    u_s = material.alpha * (1+material.poisson) /(2 * np.pi * material.kappa)
    u_s *= p_n_s/eta_n_s * (sinh_gamma_d1 + cosh_gamma_d2)
    # Eq 3.120
    u_z = (u_s*(1-jv(0, eta_n_s_r_a))).sum(1)
    # Eq 3.121
    du_z = - (1-material.poisson)/(2*material.E) * (omega_1 * r**2)
    return u_z + du_z


def surface_deformation_substrate_heating_HG00(r, a, h, w, material, barrel_material = None, T_ext=293.15, n_max=0, s_max=20, root_accuracy=1e-6):
    """Computes the depth displacement change of the surface
    of an optic due to bulk absorption from a HG00 beam.
    Displacement returned is in units of m per absorbed Watts
    through entire substrate.

    The accuracy of this computation decreases as h/a > 1.
    The substrate modelled must be disk like. The error is
    more pronounced towards the edge of the substrate.

    Parameters
    ----------
    r : ndarray
        Radial points
    a : float
        mirror radius
    h : float
        mirror thickness
    w : float
        spot size radius
    material : Material
        Mirror substrate material, see :py:mod:`finesse.materials`
    barrel_material : Material
        Barrel cotaing material, see :py:mod:`finesse.materials`
    T_ext : float, optional
        External temperature surrounding mirror
    n_max : int, optional
        Maximum Bessel order for expansion
    s_max : int, optional
        Maximum number of zeros to compute
    root_accuracy : float, optional
        Accuracy of root finding

    Returns
    -------
    U_z_bulk_per_W : ndarray(shape=(r.size.))
        Array of z displacements per watt of
        absorbed power through entire substrate [1W/h]

    Notes
    -----
    Solving equation 3.165 :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    assert(n_max == 0)
    # setup up broadcasting with numpy arrays
    if barrel_material:
        emiss_face = material.emiss
        emiss_edge = barrel_material.emiss
    else:
        emiss_face = emiss_edge =  material.emiss
    chi_edge = 4 * emiss_edge * SIGMA_F * T_ext**3 * a / material.kappa
    chi_face = 4 * emiss_face * SIGMA_F * T_ext**3 * a / material.kappa
    eta_n_s = zeros_of_xjn_1_chi_jn(chi_edge, n_max, s_max, root_accuracy)
    eta_n_s_sq = eta_n_s * eta_n_s
    p_n_s = get_p_n_s(a, w, 0, 0, chi_edge, eta_n_s, eta_n_s_sq)
    data = r, chi_edge, chi_face, p_n_s, eta_n_s, None, material
    return surface_deformation_substrate_heating(data, h)


def surface_deformation_substrate_heating(data, h):
    """Computes the depth displacement change of the surface
    of an optic due to bulk absorption from a generic
    axisymmetric heating profile. Displacement returned is
    in units of m per absorbed Watts through entire substrate.

    The accuracy of this computation decreases as h/a > 1.
    The substrate modelled must be disk like. The error is
    more pronounced towards the edge of the substrate.

    Parameters
    ----------
    data : tuple
        Irradiance fit data from :func:`finesse.thermal.hello_vinet.get_p_n_s_numerical`
    h : float
        mirror thickness

    Returns
    -------
    U_z_bulk_per_W : ndarray(shape=(r.size.))
        Array of z displacements per watt of
        absorbed power through entire substrate [1W/h]

    Notes
    -----
    Solving equation 3.165 :cite:`vinet_liv_rev`

    Currently only works for n_max == 0.
    """
    r, _, chi_face, p_n_s, eta_n_s, _, material = data
    r = r[:, np.newaxis]
    a = r.max()
    n_max = eta_n_s.shape[0]-1
    assert(n_max == 0)

    eta_n_s_sq = eta_n_s * eta_n_s
    eta_n_s_cubed = eta_n_s_sq * eta_n_s
    eta_n_s_r_a = r * eta_n_s / a # Eq 3.18

    gamma_n_s = eta_n_s * h / (2*a)

    sinh_gamma = np.sinh(gamma_n_s)
    cosh_gamma = np.cosh(gamma_n_s)
    Gamma_s = sinh_gamma * cosh_gamma + gamma_n_s # Eq. 3.146

    d1_n_s = eta_n_s * sinh_gamma + chi_face * cosh_gamma # Eq 3.19
    # Theta and du_z is just a simple scalar factor which adds piston. As we remove
    # piston we might as well not calculate it in the first place...
    # Eq. 3.160
    # theta = material.alpha * a * material.E * chi / ((1 - material.poisson) * np.pi * material.kappa)
    # theta *= (jv(0, eta_n_s) * p_n_s / eta_n_s_quart * (1 - sinh_gamma/gamma_n_s * ((1 - material.poisson) * chi / d1_n_s + 2 * material.poisson * sinh_gamma / Gamma_s)))
    # Eq. 3.162 - typo in equation, still has z in it??
    # z = -h/2 # reflecting surface
    # du_z = 2*material.poisson / material.E * theta * z
    # First part of Eq. 3.165
    u_z = material.alpha * (1 + material.poisson) * a / (np.pi * material.kappa)
    u_z *= (p_n_s/eta_n_s_cubed * sinh_gamma * (2*sinh_gamma/Gamma_s - chi_face/d1_n_s) * jv(0, eta_n_s_r_a)).sum(1)
    u_z /= h # divide by mirror thickness to get 1W absorbed through entire substrate
    return u_z - u_z.max() # + du_z


def ring_radiator_intensity(r, a, b_c, D_c, P_c):
    """Calculates the intesity of incident on a mirror
    surface from an ideally thin ring radiator.

    Parameters
    ----------
    r : ndarray
        Radial points [m]
    a : float
        Mirror radius
    b_c : float
        Radius of ring radiator (b_c > D_c) [m]
    D_c : float
        Distance from ring radiator to mirror surface [m]
    P_c : float
        Power emitted by ring [W]

    Returns
    -------
    I_r : ndarray(shape=(r.size,))
        Radial variation in intensity on mirror from ring.

    Notes
    -----
    Solving equation 4.11 :cite:`vinet_liv_rev`
    """
    if (b_c > D_c):
        raise RuntimeError("b_c <= D_c")

    fac = (a**2+D_c**2-b_c**2)/(2*b_c*D_c)
    # Eq 4.12
    inv_I_0 = np.pi * np.log( b_c/D_c * (np.sqrt(fac+1) + fac))
    I_0 = 1 / inv_I_0

    return P_c * I_0 / np.sqrt((b_c**2 + D_c**2)**2 - 2*(b_c**2 - D_c**2)*r**2 + r**4)
