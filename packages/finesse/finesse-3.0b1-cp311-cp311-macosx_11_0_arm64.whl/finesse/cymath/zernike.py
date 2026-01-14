"""Math functions for computing Zernike polynomial information.

TODO: write tests and document these functions properly
"""

import numpy as np
import scipy


def Rnm_p(n, m):
    """Generate radial polynomial for radial Zernikee."""
    pc = []
    m = abs(m)
    for ik in range(int((n - m) / 2) + 1):
        num = (-1) ** ik * scipy.special.factorial(int(n - ik))
        den = (
            scipy.special.factorial(int(ik))
            * scipy.special.factorial(int((n + m) / 2 - ik))
            * scipy.special.factorial(int((n - m) / 2 - ik))
        )
        pc.append(num / den)
    return np.array(pc)


def Rnm_eval(_r, _phi, n, m, a0):
    """Function to evaluate  radial components."""
    # Obtain the polynomial coeffs:
    pn = Rnm_p(n, m)
    Rnm = np.zeros(_r.shape)
    for idx, ip in enumerate(pn):
        Rnm += ip * (_r / a0) ** (n - 2 * idx)
    # Noll normalissation:
    Nnm = np.sqrt(2 * n + 2)
    return Nnm * Rnm


def ZPhi_eval(_phi, m):
    """Fuction to generate azimuthal component."""
    if m < 0:
        ZPhi = 1 / np.sqrt(np.pi) * np.sin(m * _phi)
    elif m > 0:
        ZPhi = 1 / np.sqrt(np.pi) * np.cos(m * _phi)
    else:
        ZPhi = 1 / np.sqrt(2 * np.pi) * np.ones(_phi.shape)
    return ZPhi


def Znm_eval(_r, _phi, n, m, a0):
    _Rnm = Rnm_eval(_r, _phi, n, m, a0)
    _Pnm = ZPhi_eval(_phi, m)
    return _Rnm * _Pnm


def Gen_nm(n):
    """Generate n and m  vectors containing n and m indices up to n, excluding zeroth
    mode."""
    vlen = np.sum(np.arange(2, n + 2))
    _n = np.zeros(vlen)
    _m = np.zeros(vlen)
    for iN in range(1, n + 1):
        iStart = np.sum(np.arange(2, iN - 1 + 2))
        iStop = np.sum(np.arange(2, iN + 2))
        _n[iStart:iStop] = iN
        for im in range(iN + 1):
            _m[iStart + im] = -iN + im * 2
    return _n, _m
