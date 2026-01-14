"""Collection of ABCD functions for standard optical components."""

import numpy as np
from finesse.exceptions import TotalReflectionError


def none():
    """Unit matrix for no propagation."""
    # Return object as it is used for symbolic matrix products not floating point
    return np.array([[1.0, 0.0], [0.0, 1.0]], dtype=object)


def space(L, nr=1):
    """Propagation along a physical length `L`

    Parameters
    ----------
    L : float
        Length in metres
    nr : float
        refractive index of medium

    Notes
    -----
    See :cite:`siegman`, table 15.1(a)
    """
    return np.array([[1.0, L / nr], [0.0, 1.0]])


def lens(f):
    """Propagation through a thin lens.

    Parameters
    ----------
    f : float
        Focal lenth of thin lens in metres

    Notes
    -----
    See :cite:`siegman`, table 15.1(b)
    """
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def _mirror_refl(Rc, nr=1):
    return np.array([[1.0, 0.0], [-2 * nr / Rc, 1.0]])


def mirror_refl_t(Rc, nr=1):
    """Tangential (in plane-of-incidence) reflection from a curved surface. Due to
    coordinate system change on reflection the sagittal plane is reflected (parity
    operation) and an additional minus sign is applied.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    nr : float
        refractive index of medium in which the reflection occurs

    Notes
    -----
    See :cite:`siegman`, table 15.1(c) and "Ray Inversion" section in 15.1
    """
    return -1 * _mirror_refl(Rc, nr)


def mirror_refl_s(Rc, nr=1):
    """Sagittal (perpendicular plane-of-incidence) reflection from a curved surface.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    nr : float
        refractive index of medium in which the reflection occurs

    Notes
    -----
    See :cite:`siegman`, table 15.1(c)
    """
    return +1 * _mirror_refl(Rc, nr)


def mirror_trans(Rc, nr1=1, nr2=1):
    """Transmission through a curved surface.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    nr1 : float
        refractive index of medium the beam starts in
    nr2 : float
        refractive index of medium the beam ends up in

    Notes
    -----
    See :cite:`siegman`, table 15.1(e)
    """
    return np.array([[1.0, 0.0], [(nr2 - nr1) / Rc, 1.0]])


def beamsplitter_refl_t(Rc, alpha, nr=1):
    """Tangential (in plane-of-incidence)reflection from a curved surface at a non-
    normal angle of incidence. Due to coordinate system change on reflection the
    sagittal plane is reflected (parity operation) and an additional minus sign is
    applied.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr : float
        refractive index of medium the reflection occurs in

    Notes
    -----
    See :cite:`siegman`, table 15.1(d) and "Ray Inversion" section in 15.1
    """
    alpha1 = np.radians(alpha)
    Re = Rc * np.cos(alpha1)
    C = -2 * nr / Re

    return -1 * np.array([[1.0, 0.0], [C, 1.0]])


def beamsplitter_refl_s(Rc, alpha, nr=1):
    """Sagittal (perpendicular plane-of-incidence) reflection from a curved surface at a
    non-normal angle of incidence. Due to coordinate system change on reflection the
    sagittal plane is reflected (parity operation) and an additional minus sign is
    applied.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr : float
        refractive index of medium the reflection occurs in

    Notes
    -----
    See :cite:`siegman`, table 15.1(d) and "Ray Inversion" section in 15.1
    """
    alpha1 = np.radians(alpha)
    Re = Rc / np.cos(alpha1)
    C = -2 * nr / Re

    return np.array([[1.0, 0.0], [C, 1.0]])


def beamsplitter_trans_t(Rc, alpha, nr1=1, nr2=1):
    """Tangential (in plane-of-incidence) transmission through a curved surface at an
    angle of incidence.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr1 : float
        refractive index of medium the beam starts in
    nr2 : float
        refractive index of medium the beam ends up in

    Notes
    -----
    See :cite:`siegman`, table 15.1(f)
    """
    alpha1 = np.radians(alpha)
    # we get alpha2 from Snell's law
    sin_alpha2 = (nr1 / nr2) * np.sin(alpha1)
    if abs(float(sin_alpha2)) > 1:
        raise TotalReflectionError("Total internal reflection")
    alpha2 = np.arcsin(sin_alpha2)
    cos_alpha1 = np.cos(alpha1)
    cos_alpha2 = np.cos(alpha2)

    # Tangential
    A = cos_alpha2 / cos_alpha1
    D = cos_alpha1 / cos_alpha2
    delta_n = (nr2 * cos_alpha2 - nr1 * cos_alpha1) / (cos_alpha1 * cos_alpha2)
    C = delta_n / Rc

    return np.array([[A, 0.0], [C, D]])


def beamsplitter_trans_s(Rc, alpha, nr1=1, nr2=1):
    """Sagittal (perpendicular plane-of-incidence) transmission through a curved surface
    at an angle of incidence.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr1 : float
        refractive index of medium the beam starts in
    nr2 : float
        refractive index of medium the beam ends up in

    Notes
    -----
    See :cite:`siegman`, table 15.1(g)
    """
    alpha1 = np.radians(alpha)
    # we get alpha2 from Snell's law
    sin_alpha2 = (nr1 / nr2) * np.sin(alpha1)
    if abs(float(sin_alpha2)) > 1:
        raise TotalReflectionError("Total internal reflection")
    alpha2 = np.arcsin(sin_alpha2)
    cos_alpha1 = np.cos(alpha1)
    cos_alpha2 = np.cos(alpha2)

    # sagittal
    A = 1.0
    D = 1.0
    delta_n = nr2 * cos_alpha2 - nr1 * cos_alpha1
    C = delta_n / Rc

    return np.array([[A, 0.0], [C, D]])
