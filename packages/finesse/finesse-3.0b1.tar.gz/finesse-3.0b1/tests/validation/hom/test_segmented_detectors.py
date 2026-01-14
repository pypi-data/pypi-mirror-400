import pytest
import finesse
import numpy as np
from scipy.special import erf


@pytest.fixture
def dc_xysplit_model():
    model = finesse.Model()
    model.parse(
        """
    l l1
    bs bs1 R=1 T=0 ybeta=bs1.xbeta
    nothing n1
    pd X n1.p1.i pdtype=xsplit
    pd Y n1.p1.i pdtype=ysplit
    link(l1, bs1, 10, n1)
    modes(maxtem=1)
    gauss g1 bs1.p2.o w0=1m z=0
    xaxis(bs1.xbeta, lin, -10u, 10u, 10)
    """
    )
    return model


def test_dc_xysplit(dc_xysplit_model):
    model = dc_xysplit_model
    model.run()


@pytest.mark.parametrize("D", [1, 10, 100])
@pytest.mark.parametrize("a,b,sign", [("x", "y", +1), ("y", "x", -1)])
def test_pd_split(D, a, b, sign):
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    bs bs1 R=1 T=0 {b}beta=-bs1.{a}beta # Steering mirror
    nothing n1
    pd qpdx n1.p1.i pdtype=xsplit
    pd qpdy n1.p1.i pdtype=ysplit
    link(l1, bs1, {D}, n1)

    modes(maxtem=1)
    gauss g1 bs1.p2.o w0=1m z=0
    xaxis(bs1.{a}beta, lin, -1n, 1n, 1)
    """
    )

    out = model.run()
    delta = out.x1 * D
    err_x = out["qpdx"] + sign * erf(2 * np.sqrt(2) * delta / model.n1.p1.i.qx.w)
    err_y = out["qpdy"] - sign * erf(2 * np.sqrt(2) * delta / model.n1.p1.i.qx.w)

    assert abs(err_x).max() < 1e-15
    assert abs(err_y).max() < 1e-15
