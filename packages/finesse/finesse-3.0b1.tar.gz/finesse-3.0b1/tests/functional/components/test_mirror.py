"""Mirror tests.

Tests for the code shared with :class:`.Surface` are in test_surface.py.
"""

import pytest
from hypothesis import given, settings, HealthCheck
import numpy as np
from finesse import Model
from finesse.components import Mirror, Laser, Space
from finesse.detectors import PowerDetector
from testutils.data import RADII_OF_CURVATURE_PAIRS
from testutils.fuzzing import DEADLINE, laser_powers, rtl_sets


@pytest.mark.parametrize("Rcx,Rcy", RADII_OF_CURVATURE_PAIRS)
def test_abcd(Rcx, Rcy):
    """Test that the ABCD matrix of particular combinations of ports shows symmetry with
    other ports.

    The sign of Rc matters when we test against port pairs on the opposite surface. See
    https://finesse.readthedocs.io/en/latest/api/components/mirror/generated/finesse.components.mirror.Mirror.ABCD.html#finesse.components.mirror.Mirror.ABCD.

    For REFLECTION:

        Mirror( Rcx,  Rcy).p1.i -> Mirror( Rcx,  Rcy).p1.o

                            is equal to:

        Mirror(-Rcx, -Rcy).p2.i -> Mirror(-Rcx, -Rcy).p2.o

    For TRANSMISSION:

        Mirror( Rcx,  Rcy).p1.i -> Mirror( Rcx,  Rcy).p2.o

                            is equal to:

        Mirror(-Rcx, -Rcy).p2.i -> Mirror(-Rcx, -Rcy).p1.o
    """

    m_ref = Mirror("m", Rc=(Rcx, Rcy))
    m_cmp = Mirror("m", Rc=(-Rcx, -Rcy))

    ## Each test below checks x- then y-directions.

    # Reflection
    r_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="x")
    r_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="y")

    assert np.all(r_lhs_x == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p2.o, direction="x"))
    assert np.all(r_lhs_y == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p2.o, direction="y"))

    # Transmission
    t_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="x")
    t_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="y")

    # (1)
    assert np.all(t_lhs_x == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p1.o, direction="x"))
    assert np.all(t_lhs_y == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p1.o, direction="y"))


@given(RTL=rtl_sets(), P=laser_powers)
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
@pytest.mark.parametrize(
    "inport,reflnode,trnsnode",
    (
        ("p1", "p1.o", "p2.o"),
        ("p2", "p2.o", "p1.o"),
    ),
)
def test_round_trip_power_fuzzing(P, RTL, inport, reflnode, trnsnode):
    """Test reflection and transmission of beamsplitter."""
    R, T, L = RTL
    model = Model()
    model.add(Laser("L0", P=P))
    model.add(Mirror("mirror"))
    model.add(Space("s0", model.L0.p1, model.get(f"mirror.{inport}")))
    model.add(PowerDetector("refl", model.get(f"mirror.{reflnode}")))
    model.add(PowerDetector("trns", model.get(f"mirror.{trnsnode}")))
    model.mirror.set_RTL(R=R, T=T, L=L)

    out = model.run()
    assert out["refl"] == pytest.approx(P * R)
    assert out["trns"] == pytest.approx(P * T)
