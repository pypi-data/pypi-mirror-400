"""Wigner moment operators and functions written to work on an optical fields described
in a HG mode basis, rather than a cartesian grid, which makes many calculations faster
and more pratical when working in FINESSE.

Code is predominantly written by Alexei Ciobanu, some code tidying and documentation by
Daniel Brown.
"""

import numpy as np
import scipy.special
from dataclasses import dataclass


def q2w(q, lam=1064e-9):
    """Get beam size from q parameter.

    Parameters
    ----------
    q : complex
        Gaussian beam parameter
    lam : float
        Wavelength
    """
    w0 = q2w0(q, lam=lam)
    zr = np.imag(q)
    return w0 * np.abs(q) / zr


def q2w0(q, lam=1064e-9):
    """Get waist size from q parameter.

    Parameters
    ----------
    q : complex
        Gaussian beam parameter
    lam : float
        Wavelength
    """
    zr = np.imag(q)
    return np.sqrt(zr * lam / np.pi)


def herm(n, x):
    c = np.zeros(n + 1)
    c[-1] = 1
    return np.polynomial.hermite.hermval(x, c)


def gauss_norm(n, q, lam=1064e-9, include_gouy=True):
    """The normalization factor for a 1D HG electric field distribution to ensure that
    the overlap integral equates to 1.

    Traditionally the normalization includes a Gouy phase factor for free space
    propagation but that can be turned off by setting include_gouy=False

    Parameters
    ----------
    n : int
        1D Hermite-gaussian mode order
    q : complex
        Gaussian beam parameter
    lam : float
        Wavelength
    """
    zr = np.imag(q)
    w0 = q2w0(q, lam=lam)
    w = q2w(q, lam=lam)

    t1 = np.sqrt(np.sqrt(2 / np.pi))
    t2 = np.sqrt(1.0 / (2.0**n * scipy.special.factorial(n) * w0))
    if include_gouy:
        t3 = np.sqrt(1j * zr / q)
        t4 = (-np.conj(q) / q) ** (n / 2)
    else:
        t3 = np.sqrt(w0 / w)
        t4 = 1

    return t1 * t2 * t3 * t4


def X_hg(n, q, lam=1064e-9, include_gouy=False):
    w = q2w(q)
    hn = gauss_norm(n, q, lam=lam, include_gouy=include_gouy)
    # h0 = gauss_norm(0, q, lam=lam, include_gouy=include_gouy)
    hnp = gauss_norm(n + 1, q, lam=lam, include_gouy=include_gouy)
    if n > 0:
        hnm = gauss_norm(n - 1, q, lam=lam, include_gouy=include_gouy)
        anm = n / hnm
    else:
        anm = 0
    out = w / np.sqrt(2) * hn * np.array([anm, 1 / (2 * hnp)])
    return out


def X_hg_full(N, q, lam=1064e-9, include_gouy=False):
    X = np.zeros([N + 1, N], dtype=complex)

    for n in range(N):
        anm, anp = X_hg(n, q, lam=lam, include_gouy=include_gouy)
        if n > 0:
            X[n - 1, n] = anm
            X[n + 1, n] = anp
        else:
            X[n + 1, n] = anp
    return X


def D_hg(n, q, lam=1064e-9, include_gouy=False):
    k = 2 * np.pi / lam
    w = q2w(q, lam=lam)
    hn = gauss_norm(n, q, lam=lam, include_gouy=include_gouy)
    if n > 0:
        hnm = gauss_norm(n - 1, q, lam=lam, include_gouy=include_gouy)
        anm = np.sqrt(2) / w * 2 * n * hn / hnm
    else:
        anm = 0

    an_x = -1j * k / q * X_hg(n, q, lam=1064e-9, include_gouy=include_gouy)
    an_d = np.array([anm, 0])
    out = lam / (1j * 2 * np.pi) * (an_d + an_x)
    return out


def D_hg_full(N, q, lam=1064e-9, include_gouy=False):
    D = np.zeros([N + 1, N], dtype=complex)

    for n in range(N):
        anm, anp = D_hg(n, q, lam=lam, include_gouy=include_gouy)
        if n > 0:
            D[n - 1, n] = anm
            D[n + 1, n] = anp
        else:
            D[n + 1, n] = anp
    return D


@dataclass
class WignerMomentsHG:
    """Wigner moment outputs from the Hermite-Gaussian wigner function
    :func:`wigner_moments_2D_hg`.

    Attributes
    ----------
    xu, xy, xv, xx, ux, uy, uv, uu, yx, yu, yv, yy, vx, vu, vy, vv: float
        elements of the wigner matrix for easier access
    wig_matrix : array_like
        4x4 Wigner moment matrix
    m2, m2x, m2y : float
        Total M2 (M-squared) value, and the M2 values in the x and y directions
    wig_qx, wig_qy : complex
        x and y complex gaussian beam parameter for this Wigner basis
    wig_zx, wig_zr, wig_wx, wig_zx, wig_zr, wig_wy
        Waist position, Rayleigh range, and spot size of the Wigner bases in the
        x and y directions
    wig_x, wig_y : float
        Displacement of beam in units of meters
    wig_u, wig_v : float
        Angle of beam in units of radians
    """

    xu: float
    xy: float
    xv: float
    xx: float
    ux: float
    uy: float
    uv: float
    uu: float
    yx: float
    yu: float
    yv: float
    yy: float
    vx: float
    vu: float
    vy: float
    vv: float

    wig_matrix: np.ndarray

    m2: float
    m2x: float
    m2y: float
    wig_zx: float
    wig_zrx: float
    wig_qx: complex
    wig_wx: float
    wig_zx: float
    wig_zrx: float
    wig_qy: complex
    wig_wy: float

    wig_x: float
    wig_y: float
    wig_u: float
    wig_v: float


def E_1D_to_2D(E_1D, homs):
    pass


def wigner_moments_2D_hg(
    E, qx, qy, lam=1064e-9, assume_wigner_matrix_symmetry=True, include_gouy=False
):
    """Function for computing the Wigner moments of a set of HG mode amplitudes in a
    given basis (qx,qy). This function also computes other useful metrics from the
    Wigner moments such as the M2 (M-squared) and the Wigner basis of a beam.

    Parameters
    ----------
    E : array_like
        HG mode coefficient matrix. If you have a 1D array of HG mode amplitudes
        use the `E_1D_to_2D` method to convert it first.
    qx, qy : complex | :class:`finesse.gaussian.BeamParam`
        x and y direction complex guassian beam paramters
    lam : float
        wavelength of light used
    include_gouy : bool
        Include Gouy phase in HG normalisation [experimental]
    assume_wigner_matrix_symmetry : bool
        When True only lower half of the Wigner matrix is calculated

    Returns
    -------
    result : :class:`WignerMomentsHG`
        Collection of calculations outputs from Wigner moment calculations

    Notes
    -----
    It should be noted that the Wigner basis calculation and the M2 values along each axis (m2x, m2y) are only
    valid in the case where the general astigmatic wigner moments of the beam are close to zero.
    The general astigmatic components of a wigner distribution are xv, vx, yu, uy and potentially xy, yx, uv, vu (not sure about those).
    """
    assert np.ndim(E) == 2
    assert np.ndim(qx) == 0
    assert np.ndim(qy) == 0
    assert np.ndim(lam) == 0

    M, N = E.shape
    Econj = np.conj(E.ravel())

    Ix = np.eye(N)
    Iy = np.eye(M)

    Xxb = X_hg_full(N + 1, qx, lam=lam, include_gouy=include_gouy)
    Dxb = D_hg_full(N + 1, qx, lam=lam, include_gouy=include_gouy)
    Xyb = X_hg_full(M + 1, qy, lam=lam, include_gouy=include_gouy)
    Dyb = D_hg_full(M + 1, qy, lam=lam, include_gouy=include_gouy)
    Xxa = Xxb[:-1, :-1]
    Dxa = Dxb[:-1, :-1]
    Xya = Xyb[:-1, :-1]
    Dya = Dyb[:-1, :-1]
    Xx = Xxa[:-1, :]
    Dx = Dxa[:-1, :]
    Xy = Xya[:-1, :]
    Dy = Dya[:-1, :]

    # first wigner moments
    Ex = E @ Xx.T
    Eu = E @ Dx.T
    Ey = Xy @ E
    Ev = Dy @ E

    wig_x = Econj @ Ex.ravel()  # displacement
    wig_u = Econj @ Eu.ravel()  # displacement
    wig_y = Econj @ Ey.ravel()  # tilt
    wig_v = Econj @ Ev.ravel()  # tilt

    # second wigner moments
    XxXx = Xxb @ Xxa
    XxXx = XxXx[:-2, :]
    Wxx = XxXx - 2 * wig_x * Xx + Ix * wig_x**2
    Exx = E @ Wxx.T

    XyXy = Xyb @ Xya
    XyXy = XyXy[:-2, :]
    Wyy = XyXy - 2 * wig_y * Xy + Iy * wig_y**2
    Eyy = Wyy @ E

    DxDx = Dxb @ Dxa
    DxDx = DxDx[:-2, :]
    Wuu = DxDx - 2 * wig_u * Dx + Ix * wig_u**2
    Euu = E @ Wuu.T

    DyDy = Dyb @ Dya
    DyDy = DyDy[:-2, :]
    Wvv = DyDy - 2 * wig_v * Dy + Iy * wig_v**2
    Evv = Wvv @ E

    XxDx = Xxb @ Dxa
    XxDx = XxDx[:-2, :]
    Wux = XxDx - wig_u * Xx - wig_x * Dx + Ix * wig_x * wig_u
    Eux = E @ Wux.T

    XyDy = Xyb @ Dya
    XyDy = XyDy[:-2, :]
    Wvy = XyDy - wig_v * Xy - wig_y * Dx + Iy * wig_y * wig_v
    Evy = Wvy @ E

    Wx = Xx - wig_x * Ix
    Wy = Xy - wig_y * Iy
    Wu = Dx - wig_u * Ix
    Wv = Dy - wig_v * Iy

    Exy = Wy @ E @ Wx.T
    Euy = Wy @ E @ Wu.T
    Evx = Wv @ E @ Wx.T
    Euv = Wv @ E @ Wu.T

    wig_xx = Econj @ Exx.ravel()
    wig_yy = Econj @ Eyy.ravel()
    wig_uu = Econj @ Euu.ravel()
    wig_vv = Econj @ Evv.ravel()
    wig_ux = Econj @ Eux.ravel()
    wig_vy = Econj @ Evy.ravel()
    wig_xy = Econj @ Exy.ravel()
    wig_uv = Econj @ Euv.ravel()
    wig_vx = Econj @ Evx.ravel()
    wig_uy = Econj @ Euy.ravel()

    if assume_wigner_matrix_symmetry:
        wig_xu = wig_ux
        wig_yv = wig_vy
        wig_yx = wig_xy
        wig_vu = wig_uv
        wig_xv = wig_vx
        wig_yu = wig_uy
    else:
        raise NotImplementedError()

    # rescale wigner matrix elements and force them to be real
    s = np.pi * 4 / lam
    # Unclear why real part has to be taken here?
    xu = s * np.real(wig_xu)
    xy = s * np.real(wig_xy)
    xv = s * np.real(wig_xv)
    xx = s * np.real(wig_xx)
    ux = s * np.real(wig_ux)
    uy = s * np.real(wig_uy)
    uv = s * np.real(wig_uv)
    uu = s * np.real(wig_uu)
    yx = s * np.real(wig_yx)
    yu = s * np.real(wig_yu)
    yv = s * np.real(wig_yv)
    yy = s * np.real(wig_yy)
    vx = s * np.real(wig_vx)
    vu = s * np.real(wig_vu)
    vy = s * np.real(wig_vy)
    vv = s * np.real(wig_vv)

    wig_matrix = np.array(
        [[xx, xy, xu, xv], [yx, yy, yu, yv], [ux, uy, uu, uv], [vx, vy, vu, vv]]
    )

    m2 = np.linalg.det(wig_matrix) ** 0.5
    m2x = (xx * uu - ux * xu) ** 0.5
    m2y = (yy * vv - yv * vy) ** 0.5

    wig_zrx = m2x / uu
    wig_zx = -ux / uu

    wig_zry = m2y / vv
    wig_zy = -vy / vv

    wig_qx = wig_zx + 1j * wig_zrx
    wig_qy = wig_zy + 1j * wig_zry

    wig_wy = np.sqrt((yy / m2y) * (lam / np.pi))
    wig_wx = np.sqrt((xx / m2x) * (lam / np.pi))

    result = WignerMomentsHG()
    result.xu = xu
    result.xy = xy
    result.xv = xv
    result.xx = xx
    result.ux = ux
    result.uy = uy
    result.uv = uv
    result.uu = uu
    result.yx = yx
    result.yu = yu
    result.yv = yv
    result.yy = yy
    result.vx = vx
    result.vu = vu
    result.vy = vy
    result.vv = vv

    result.wig_matrix = wig_matrix
    result.m2 = m2
    result.m2x = m2x
    result.m2y = m2y
    result.wig_zx = wig_zx
    result.wig_zrx = wig_zrx
    result.wig_qx = wig_qx
    result.wig_wx = wig_wx
    result.wig_zx = wig_zx
    result.wig_zrx = wig_zrx
    result.wig_qy = wig_qy
    result.wig_wy = wig_wy

    return result
