"""Beamsplitter tests.

Tests for the code shared with :class:`.Surface` are in test_surface.py.
"""

import pytest
import numpy as np
import finesse
from finesse.components import Beamsplitter, Laser, Space, Nothing, Mirror
from finesse.detectors import PowerDetector
from finesse.tracing import abcd
from testutils.data import RADII_OF_CURVATURE_PAIRS, LASER_POWERS, RTL_SETS
from finesse.exceptions import NoCouplingError
from finesse.analysis.actions import DCFields


@pytest.mark.parametrize("Rcx,Rcy", RADII_OF_CURVATURE_PAIRS)
def test_abcd(Rcx, Rcy):
    """Test that the ABCD matrix of particular combinations of ports shows symmetry with
    other ports.

    The sign of Rc matters when we test against port pairs on the opposite surface. See
    https://finesse.readthedocs.io/en/latest/api/components/mirror/generated/finesse.components.mirror.Mirror.ABCD.html#finesse.components.mirror.Mirror.ABCD.

    For REFLECTION:

            Beamsplitter( Rcx,  Rcy).p1.i -> Beamsplitter( Rcx,  Rcy).p2.o

                                     is equal to:

        1.  Beamsplitter( Rcx,  Rcy).p2.i -> Beamsplitter( Rcx,  Rcy).p1.o
        2.  Beamsplitter(-Rcx, -Rcy).p3.i -> Beamsplitter(-Rcx, -Rcy).p4.o
        3.  Beamsplitter(-Rcx, -Rcy).p4.i -> Beamsplitter(-Rcx, -Rcy).p3.o

    For TRANSMISSION:

            Beamsplitter( Rcx,  Rcy).p1.i -> Beamsplitter( Rcx,  Rcy).p3.o

                                     is equal to:

        1.  Beamsplitter(-Rcx, -Rcy).p3.i -> Beamsplitter(-Rcx, -Rcy).p1.o
        2.  Beamsplitter( Rcx,  Rcy).p2.i -> Beamsplitter( Rcx,  Rcy).p4.o
        3.  Beamsplitter(-Rcx, -Rcy).p4.i -> Beamsplitter(-Rcx, -Rcy).p2.o
    """

    bs_ref = Beamsplitter("bs", Rc=(Rcx, Rcy))
    bs_cmp_p = Beamsplitter("bs", Rc=(Rcx, Rcy))
    bs_cmp_n = Beamsplitter("bs", Rc=(-Rcx, -Rcy))

    ## Each test below checks x- then y-directions.

    # Reflection
    r_lhs_x = bs_ref.ABCD(bs_ref.p1.i, bs_ref.p2.o, direction="x")
    r_lhs_y = bs_ref.ABCD(bs_ref.p1.i, bs_ref.p2.o, direction="y")

    # (1)
    assert np.all(r_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p1.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p1.o, direction="y"))

    # (2)
    assert np.all(r_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p4.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p4.o, direction="y"))

    # (3)
    assert np.all(r_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p3.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p3.o, direction="y"))

    # Transmission
    t_lhs_x = bs_ref.ABCD(bs_ref.p1.i, bs_ref.p3.o, direction="x")
    t_lhs_y = bs_ref.ABCD(bs_ref.p1.i, bs_ref.p3.o, direction="y")

    # (1)
    assert np.all(t_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p1.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p1.o, direction="y"))

    # (2)
    assert np.all(t_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p4.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p4.o, direction="y"))

    # (3)
    assert np.all(t_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p2.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p2.o, direction="y"))


@pytest.mark.parametrize("P", LASER_POWERS)
@pytest.mark.parametrize("R,T,L", RTL_SETS)
@pytest.mark.parametrize(
    "inport,reflnode,trnsnode",
    (
        ("p1", "p2.o", "p3.o"),
        ("p2", "p1.o", "p4.o"),
        ("p3", "p4.o", "p1.o"),
        ("p4", "p3.o", "p2.o"),
    ),
)
def test_round_trip_power(model, P, R, T, L, inport, reflnode, trnsnode):
    """Test reflection and transmission of beamsplitter."""
    model.add(Laser("L0", P=P))
    model.add(Beamsplitter("bs"))
    model.add(Space("s0", model.L0.p1, model.get(f"bs.{inport}")))
    model.add(PowerDetector("refl", model.get(f"bs.{reflnode}")))
    model.add(PowerDetector("trns", model.get(f"bs.{trnsnode}")))
    model.bs.set_RTL(R=R, T=T, L=L)

    out = model.run()
    assert out["refl"] == pytest.approx(P * R)
    assert out["trns"] == pytest.approx(P * T)


def test_alpha2():
    model = finesse.script.parse(
        """
    bs BS R=0.5 L=0 alpha=45
    s BSsub1 BS.p3 BSAR1.p1 L=0.0687 nr=1.45
    s BSsub2 BS.p4 BSAR2.p2 L=0.0687 nr=1.45
    bs BSAR1 L=50u R=0 alpha=-29.186885954108114
    bs BSAR2 L=50u R=0 alpha=29.186885954108114
    """
    )

    assert np.allclose(float(model.BS.alpha2), 29.186885954108114)
    assert np.allclose(float(model.BSAR1.alpha2), -45)
    assert np.allclose(float(model.BSAR2.alpha2), +45)


def test_plane_of_incidence(model):
    """Tests that the ABCD matrices are correctly swapped when the beamsplitter plane of
    incidence is swapped."""
    aoi = 20
    Rcx = 2000
    Rcy = 3000
    nr = 1.45

    def add_bs(name, plane, Rc):
        bs = model.add(
            Beamsplitter(
                name,
                T=0.5,
                L=0,
                alpha=aoi,
                Rc=Rc,
                plane=plane,
            )
        )
        tp = model.add(Nothing(f"{name}_tp"))
        model.connect(bs.p3, tp.p1, L=1, nr=nr)
        return bs

    bs_xz = add_bs("xz", "xz", (Rcx, Rcx))
    bs_yz = add_bs("yz", "yz", (Rcx, Rcx))
    bs_xz2 = add_bs("xz2", "xz", (Rcx, Rcy))
    bs_yz2 = add_bs("yz2", "yz", (Rcx, Rcy))

    # check that all of the couplings are swapped when the RoCs are equal
    for p_fr in range(1, 5):
        for p_to in range(1, 5):
            try:
                assert np.allclose(
                    bs_xz.ABCD(p_fr, p_to, "x"),
                    bs_yz.ABCD(p_fr, p_to, "y"),
                )
            except NoCouplingError:
                pass

    # check that the transmissions correctly swap the planes with unequal RoCs
    assert np.allclose(
        bs_xz2.ABCD(1, 3, "x"),
        abcd.beamsplitter_trans_t(Rcx, aoi, 1, nr),
    )
    assert np.allclose(
        bs_xz2.ABCD(1, 3, "y"),
        abcd.beamsplitter_trans_s(Rcy, aoi, 1, nr),
    )
    assert np.allclose(
        bs_yz2.ABCD(1, 3, "x"),
        abcd.beamsplitter_trans_s(Rcx, aoi, 1, nr),
    )
    assert np.allclose(
        bs_yz2.ABCD(1, 3, "y"),
        abcd.beamsplitter_trans_t(Rcy, aoi, 1, nr),
    )


@pytest.mark.parametrize("modes_kw", [{"modes": "off"}, {"maxtem": 2}])
def test_misaligned(model, modes_kw):
    """Tests that misaligning Mirrors and Beamsplitters sets the reflections to zero but
    keeps the transmissions unchanged."""
    model.add(Mirror("M1", T=0.25, L=0.01, misaligned=True))
    model.add(Mirror("M2", T=0.25, L=0.01, misaligned=True))
    model.add(Beamsplitter("BS1", T=0.25, L=0.01, misaligned=True))
    model.add(Beamsplitter("BS2", T=0.25, L=0.01, misaligned=True))
    L1 = model.add(Laser("L1"))
    L2 = model.add(Laser("L2"))
    L3 = model.add(Laser("L3"))
    L4 = model.add(Laser("L4"))
    model.connect(model.L1.p1, model.M1.p1)
    model.connect(model.L2.p1, model.M2.p2)
    model.connect(model.L3.p1, model.BS1.p1)
    model.connect(model.L4.p1, model.BS2.p4)
    q = finesse.BeamParam(w0=1, z=0)
    for comp in [L1, L2, L3, L4]:
        comp.p1.o.q = q
    model.modes(**modes_kw)
    sol = model.run(DCFields())
    refls = sol[("M1.p1.o"), ("M2.p2.o"), ("BS1.p2.o"), ("BS2.p3.o")]
    trans = sol[("M1.p2.o"), ("M2.p1.o"), ("BS1.p3.o"), ("BS2.p2.o")]
    # when the components are misaligned all reflections should be zero
    # but only the DC field of HG00 will be non-zero on transmission
    assert np.all(refls == 0)
    assert np.all(trans[..., 0] == 0.5j)
