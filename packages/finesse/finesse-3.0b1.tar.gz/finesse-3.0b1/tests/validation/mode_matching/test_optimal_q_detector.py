import finesse
import numpy as np
from finesse.gaussian import optimise_HG00_q_scipy
import pytest
from scipy.optimize import OptimizeResult
from finesse.analysis.actions import DCFields
from finesse.components import Mirror, Laser
from finesse.knm.tools import make_bayerhelms_matrix


@pytest.mark.parametrize("z", [0, -1, 2])
@pytest.mark.parametrize("w0", [0.011, 0.006, 0.003])
def test_optimise_HG00_q_scipy(z, w0, model):
    qi = finesse.BeamParam(w0=6e-3, z=0)
    qo = finesse.BeamParam(w0=w0, z=z)
    model.add(Laser("l1"))
    model.add(Mirror("mirror", T=1, R=0))
    model.connect(model.l1.p1, model.mirror.p1)
    model.mirror.p1.i.q = qi
    model.mirror.p2.o.q = qo
    model.modes("even", maxtem=20)

    sol = model.run(DCFields())
    Eo = sol["mirror.p2.o"].squeeze()
    result = optimise_HG00_q_scipy(
        Eo,
        qo,
        model.homs,
        accuracy=1e-9,
        method="nelder-mead",
    )
    result2 = optimise_HG00_q_scipy(
        Eo,
        qo,
        model.homs,
        accuracy=1e-9,
        full_output=True,
        method="nelder-mead",
    )

    kmat = make_bayerhelms_matrix(
        qo,
        result2[0].q,
        qo,
        result2[1].q,
        0,
        0,
        select=model.homs,
        reverse_gouy=False,
    )
    field = kmat.data @ Eo

    assert np.allclose(model.mirror.p1.i.qx.q, result[0].q, rtol=1e-3)
    assert np.allclose(model.mirror.p1.i.qy.q, result[1].q, rtol=1e-3)
    assert np.allclose(result2[-1]["field"], field)
    assert isinstance(result2[-1]["res"], OptimizeResult)


@pytest.mark.parametrize("z", [0, -1, 2])
@pytest.mark.parametrize("w0", [0.011, 0.006, 0.003])
def test_optimal_q_detector(z, w0):
    model = finesse.script.parse(
        f"""
    l l1
    mirror n1 T=1 R=0
    link(l1, n1)
    gauss g1 n1.p1.i w0=6m z=0
    gauss g2 n1.p2.o w0={w0} z={z}
    fd Ei n1.p1.i f=0
    fd Eo n1.p2.o f=0
    modes(even, maxtem=20)
    optimal_q_detector Q n1.p2.o 0
    """
    )
    sol = model.run()

    assert np.allclose(model.n1.p1.i.qx.q, sol["Q"][0].q, rtol=1e-3)
    assert np.allclose(model.n1.p1.i.qy.q, sol["Q"][1].q, rtol=1e-3)
