"""Functions for computing outputs for higher order aberrations of spherical optical
components."""

import numpy as np


def spherical_surface(X, Y, R, degrees=0):
    """Computes the spherical height (sagitta) for a spherical mirror normal incidence.
    Will return NaNs for regions in X**2+Y**2 > R**2.

    Parameters
    ----------
    X, Y : [array_like| float]
        Coordinates to compute surface at
    R : float
        Radius of curvature
    degrees : float
        Angle of incidence in degrees

    Returns
    -------
    Z : [array_like|float]
        Height of the spherical surface

    Notes
    -----
    Coorindate system used is left-handed with positive R being in the +z direction.
    Formula is from equation 29 in :cite:`Hello_1996`.
    """
    sign = np.sign(R)
    R = abs(R)
    X_sq = X ** 2
    Y_sq = Y ** 2

    if degrees != 0:
        radians = np.radians(degrees)
        cos = np.cos(radians)
        sin = np.sin(radians)
        cos2 = np.cos(2 * radians)
        sin2 = np.sin(2 * radians)
        f_xy = R * cos - np.sqrt(R ** 2 * cos ** 2 - 2 * R * X * sin - X_sq - Y_sq)
        g_xy = np.sqrt(cos ** 2 - 2 * X * sin / R - (X_sq + Y_sq) / R ** 2)
        numer = X * sin2 - f_xy * cos2
        denom = 2 * sin2 * g_xy * (sin + X / R) - cos2 * (1 - 2 * g_xy ** 2)
        s_xy = sign * (f_xy - numer / denom)
    else:
        # simplify angle = 0
        f_xy = R - np.sqrt(R ** 2 - X_sq - Y_sq)
        g_xy = np.sqrt(1 - (X_sq + Y_sq) / R ** 2)
        s_xy = sign * f_xy * (1 - 1 / (1 - 2 * g_xy ** 2))
    return s_xy / 2  # includes factor of 2 on reflection
