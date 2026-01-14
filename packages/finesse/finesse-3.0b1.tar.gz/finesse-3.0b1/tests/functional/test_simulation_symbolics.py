"""Tests checking that symbolic equations are set-up correctly during simulations."""

import numpy as np
from numpy.testing import assert_allclose
from finesse import Model
import finesse
import pytest
from finesse.exceptions import NotChangeableDuringSimulation


def test_mirror_refl_trns_self_ref():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    link(L0, ITM)
    m ITM R=1 T=1-ITM.R

    pd refl ITM.p1.o
    pd trns ITM.p2.o

    xaxis(ITM.R, lin, 0, 1, 2)
    """
    )

    out = IFO.run()

    assert_allclose(out["refl"], np.array([0, 0.5, 1]))
    assert_allclose(out["trns"], np.array([1, 0.5, 0]))


def test_mirror_refl_trns_via_variable():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    link(L0, ITM)
    m ITM R=v T=1-v

    pd refl ITM.p1.o
    pd trns ITM.p2.o

    var v 1
    xaxis(v, lin, 0, 1, 2)
    """
    )

    out = IFO.run()

    assert_allclose(out["refl"], np.array([0, 0.5, 1]))
    assert_allclose(out["trns"], np.array([1, 0.5, 0]))


def test_zero_expression():
    """When b is zero then c simplifies to `0` eventually when the sim is run this
    checks this is handled properly and it doesn't get cythonised."""
    model = Model()
    model.parse(
        """
    variable a 25.5
    variable b 0
    variable c b*a
    """
    )
    model.a.is_tunable = True
    try:
        model.run()
    except finesse.exceptions.NoLinearEquations:
        pass


def test_nonchangeable_symbolics():

    import numpy as np
    from finesse import Model
    import finesse.components as fc
    import finesse.analysis.actions as fa

    model = Model()
    Lcav1 = model.add_parameter("Lcav1", 16).ref
    Lcav2 = model.add_parameter("Lcav2", 0.5).ref
    alpha1_deg = np.arccos(1 - 0.5 * Lcav2**2 / Lcav1**2) * 180 / np.pi / 2
    alpha2_deg = np.arccos(Lcav2 / (2 * Lcav1)) * 180 / np.pi / 2
    MC1 = model.add(fc.Beamsplitter("MC1", T=6e-3, L=0, alpha=alpha2_deg))
    MC2 = model.add(fc.Beamsplitter("MC2", T=0, L=0, alpha=alpha1_deg))
    MC3 = model.add(fc.Beamsplitter("MC3", T=6e-3, L=0, alpha=alpha2_deg))
    model.connect(MC1.p2, MC2.p1, L=Lcav1, name="MC1_MC2")
    model.connect(MC2.p2, MC3.p1, L=Lcav1, name="MC2_MC3")
    model.connect(MC3.p2, MC1.p1, L=Lcav2, name="MC3_MC1")
    model.add(fc.Laser("Laser", P=1))
    model.connect(model.Laser.p1, MC1.p4)
    model.Lcav1 = 18

    with pytest.raises(NotChangeableDuringSimulation):
        model.run(fa.Xaxis(MC1.alpha, "lin", 15, 17, 100))

    with pytest.raises(NotChangeableDuringSimulation):
        model.run(fa.Xaxis("Lcav1", "lin", 15, 17, 100))
