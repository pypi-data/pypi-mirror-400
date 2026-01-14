"""ABCD equality tests.

Surfaces should have the same ABCD matrices for certain couplings.
"""

import pytest
import numpy as np
from finesse.components import Beamsplitter, Mirror
from testutils.data import RADII_OF_CURVATURE_PAIRS


@pytest.mark.parametrize("Rcx,Rcy", RADII_OF_CURVATURE_PAIRS)
def test_mirror_beamsplitter_abcd_matrices_match(Rcx, Rcy):
    """Test that the ABCD matrices of each surface match those of the other surfaces.

    The sign of Rc matters when we test against port pairs on the opposite surface. See
    https://finesse.readthedocs.io/en/latest/api/components/mirror/generated/finesse.components.mirror.Mirror.ABCD.html#finesse.components.mirror.Mirror.ABCD.

    For REFLECTION:

                  Mirror( Rcx,  Rcy).p1.i ->       Mirror( Rcx,  Rcy).p1.o

                                     is equal to:

        1.  Beamsplitter( Rcx,  Rcy).p1.i -> Beamsplitter( Rcx,  Rcy).p2.o
        2.  Beamsplitter( Rcx,  Rcy).p2.i -> Beamsplitter( Rcx,  Rcy).p1.o
        3.  Beamsplitter(-Rcx, -Rcy).p3.i -> Beamsplitter(-Rcx, -Rcy).p4.o
        4.  Beamsplitter(-Rcx, -Rcy).p4.i -> Beamsplitter(-Rcx, -Rcy).p3.o

    For TRANSMISSION:

                  Mirror( Rcx,  Rcy).p1.i ->       Mirror( Rcx,  Rcy).p2.o

                                     is equal to:

        1.  Beamsplitter( Rcx,  Rcy).p1.i -> Beamsplitter( Rcx,  Rcy).p3.o
        2.  Beamsplitter( Rcx,  Rcy).p2.i -> Beamsplitter( Rcx,  Rcy).p4.o
        3.  Beamsplitter(-Rcx, -Rcy).p3.i -> Beamsplitter(-Rcx, -Rcy).p1.o
        4.  Beamsplitter(-Rcx, -Rcy).p4.i -> Beamsplitter(-Rcx, -Rcy).p2.o
    """
    # Reference optics.
    m_ref = Mirror("m_ref", Rc=(Rcx, Rcy))
    bs_cmp_p = Beamsplitter("bs", Rc=(Rcx, Rcy))
    bs_cmp_n = Beamsplitter("bs", Rc=(-Rcx, -Rcy))

    ## Each test below checks x- then y-directions.

    # Reflection
    r_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="x")
    r_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="y")

    # (1)
    assert np.all(r_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p1.i, bs_cmp_p.p2.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p1.i, bs_cmp_p.p2.o, direction="y"))

    # (2)
    assert np.all(r_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p1.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p1.o, direction="y"))

    # (3)
    assert np.all(r_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p4.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p4.o, direction="y"))

    # (4)
    assert np.all(r_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p3.o, direction="x"))
    assert np.all(r_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p3.o, direction="y"))

    # Transmission
    t_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="x")
    t_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="y")

    # (1)
    assert np.all(t_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p1.i, bs_cmp_p.p3.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p1.i, bs_cmp_p.p3.o, direction="y"))

    # (2)
    assert np.all(t_lhs_x == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p4.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_p.ABCD(bs_cmp_p.p2.i, bs_cmp_p.p4.o, direction="y"))

    # (3)
    assert np.all(t_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p1.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p3.i, bs_cmp_n.p1.o, direction="y"))

    # (4)
    assert np.all(t_lhs_x == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p2.o, direction="x"))
    assert np.all(t_lhs_y == bs_cmp_n.ABCD(bs_cmp_n.p4.i, bs_cmp_n.p2.o, direction="y"))
