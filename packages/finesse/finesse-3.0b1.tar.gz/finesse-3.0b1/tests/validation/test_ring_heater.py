from os import path

import numpy as np

from finesse.materials import FusedSilica
from finesse.thermal.ring_heater import (
    substrate_temperature,
    thermal_lens,
    substrate_deformation_depth,
    surface_deformation,
)


def test_fea(request):
    FEA = np.load(path.join(path.dirname(request.fspath), "test_ring_heater_fea.npz"))
    r = FEA["r"]
    a = 0.17
    b = 50e-3
    c = 70e-3
    h = 0.2
    z = np.linspace(-h / 2, h / 2, 1000)
    dz = z[1] - z[0]
    material = FusedSilica

    W = thermal_lens(r, a, b, c, h, material)
    W -= W.min()
    assert abs(W - FEA["substrate"]).max() < 1e-8

    # rough approximation for surface deformation
    Z = W / FusedSilica.dndT * FusedSilica.alpha
    assert abs(Z - FEA["surface"]).max() < 1e-9

    # integrate sub temp for total thermal lens
    T_rh_per_W = substrate_temperature(r, z, a, b, c, h, material)
    W = T_rh_per_W.sum(0) * dz * material.dndT
    W -= W.min()
    assert abs(W - FEA["substrate"]).max() < 1e-8


def test_substrate_deformation_vs_surface(request):
    def subtract_max(arr):
        return arr - arr.max()

    a = 0.17
    b = 50e-3
    c = 70e-3
    h = 0.2
    z = np.linspace(-h / 2, h / 2, 1000)
    material = FusedSilica
    a = 170e-3  # radius of optic
    h = 0.2  # thickness of itm

    r = np.linspace(-a, a, 100)  # radial points along optic
    z = np.linspace(-h / 2, +h / 2, 1000)  # depth points along optic
    # @@@ using the full 2d substrate_thermal_expansion_depth_HG00 function @@@
    # 2d array of displacements of the optic due to CP AR1 coating heating
    Uz_method2 = -surface_deformation(r, a, b, c, h, material) * (FusedSilica.nr - 1)
    Uz_2d_method1 = substrate_deformation_depth(r, z, a, b, c, h, material) * (
        FusedSilica.nr - 1
    )

    assert np.allclose(subtract_max(Uz_method2), subtract_max(Uz_2d_method1[0, :]))
