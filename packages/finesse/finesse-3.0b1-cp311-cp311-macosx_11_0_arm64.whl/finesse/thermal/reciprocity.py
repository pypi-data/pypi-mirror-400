"""Compute thermo-elastic deformations in optical substrates using reciprocity theorem
:cite:`PhysRevD.92.022005`. This provides a more accurate method to model thermo-elastic
deformation of surfaces when the temperature distribution is known throughout a
substrate. Reciprocity used here requires finite-element model results for volumetric
strain due to a Zernike based force applied to the surface of the substrate. Substrate
temperature distributions can then be converted into displacements and overlaps with the
volumetric strain calculated. The coefficients of these overlaps then describes the
zernike surface decomposition.

Equations all based on :cite:`PhysRevD.92.022005`:

    Modeling thermoelastic distortion of optics using elastodynamic reciprocity
    Eleanor King, Yuri Levin, David Ottaway, and Peter Veitch
    Phys. Rev. D 92, 022005 - Published 20 July 2015
    https://doi.org/10.1103/PhysRevD.92.022005

The methods here have been adapted from code and work done by Huy Tuong Cao
<huy-tuong.cao@LIGO.org>.
"""

import numpy as np
from finesse.cymath import zernike


class AxisymmetricFEAData:
    """An object that contains the finite element analysis data required to perform
    Axisymmetric thermal reciprocity calculations. This data can either be loaded from a
    numpy npz file that contains the r, z, V, and material data or can be provided
    directly to the the constructor.

    Attributes
    ----------
    a : float
        Radius of optic in meter
    h : float
        Thickness of optic in meter
    r : array_like
        1D radial point vector ranging from [0, a] with Nr elements
    z : array_like
        1D thickness point vector ranging from [0, h] with Nz elements
    R, Z : array_like
        2D meshgrid arrays of self.r, self.z
    V : array_like
        An (NV, Nz, Nr) shaped array representing the 2D basis functions for
        this reciprocity.
    material : :class:`finesse.materials.Material`
        An object containing various thermal and mechanical properties for the
        optic being modelled. Must match the values being used in the finite
        element model generating `self.V`.
    """

    def __init__(self, r=None, z=None, V=None, material=None, filepath=None):
        if filepath:
            load = np.load(filepath, allow_pickle=True)
            self.r = load["r"]
            self.z = load["z"]
            self.V = load["V"]
            self.material = load["material"][()]
        elif r is not None and z is not None and V is not None and material is not None:
            self.r = r
            self.z = z
            self.V = V
            self.material = material
        else:
            raise RuntimeError(
                "Please specify r, z, V, and material or provide a .npz filename that does contain them."
            )

        if self.V.shape[1:] != (self.z.size, self.r.size):
            raise RuntimeError(
                f"Shape of {self.V.shape} is not correct for the r and z vector"
            )

        self.a = self.r.max()
        self.h = self.z.max()
        self.R, self.Z = np.meshgrid(self.r, self.z)

    @property
    def NV(self):
        return self.V.shape[0]

    @property
    def Nr(self):
        """Number of points in the radial vector."""
        return self.r.size

    @property
    def Nz(self):
        return self.z.size

    @property
    def dr(self):
        return self.r[1] - self.r[0]

    @property
    def dz(self):
        return self.z[1] - self.z[0]


def zernike_coefficients_axisymmetric(data: AxisymmetricFEAData, T):
    """Compute the Zernike coefficient from temperature substrate profile and volumetric
    strain. This is for axially symmetric heating profiles and distortions.

    Parameters
    ----------
    data : :class:`AxisymmetricFEAData`
        Finite element model data
    T : array_like
        Array of shape (data.Nz, data.Nr) of temperature over the finite
        element model domain.

    Returns
    -------
    Z_coeffs : array_like
        Array of shape data.NV of Zernike coefficients of the surface
    """
    Z_coeffs = np.zeros(data.NV)
    dr = data.a * (1 / (data.Nr))
    dz = data.h * (1 / (data.Nz))
    CZern = (
        (1 / data.a**2)
        * data.material.E
        * data.material.alpha
        / (1 - 2 * data.material.poisson)
    )
    dA = dr * dz
    # TODO - This could be sped up a bit with numpy broadcasting
    for i in range(data.NV):
        Z_coeffs[i] = 2 * np.pi * CZern * np.sum(data.V[i] * T * data.R * dA)

    return Z_coeffs


def zernike_surface_axisymmetric(data: AxisymmetricFEAData, Z_coeffs):
    """Reconstruct the surface deformation from Zernike coefficients.

    Parameters
    ----------
    data : :class:`AxisymmetricFEAData`
        Finite element model data
    Z_coeffs : array_like
        Zernike coefficients in an array of shape `data.NV`

    Returns
    -------
    W : array_like
        Surface displacement in metres
    """
    n0_2D = np.arange(2, 2 * data.NV + 2, 2)  # Even Zernike n-coeffs
    m0_2D = np.zeros(len(n0_2D))
    W = np.zeros(data.r.shape)  # Variable to store deformation
    # TODO - This could be sped up a bit with numpy broadcasting
    for iN, iM, cZ in zip(n0_2D, m0_2D, Z_coeffs):
        W -= cZ * zernike.Znm_eval(data.r, np.array([0]), iN, iM, data.a)
    W -= W[0]  # zero center of displacement
    return W
