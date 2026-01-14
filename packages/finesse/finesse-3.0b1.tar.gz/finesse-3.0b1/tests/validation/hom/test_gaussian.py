import finesse
import numpy as np
from finesse.gaussian import optimise_HG00_q
from finesse.knm.tools import make_scatter_matrix
import pytest


@pytest.fixture
def model():
    model = finesse.Model()
    model.modes("even", maxtem=4)
    return model


@pytest.mark.parametrize("z1x", [-10000, 10000])
@pytest.mark.parametrize("z2x", [-10000, 10000])
@pytest.mark.parametrize("z1y", [-10000, 10000])
@pytest.mark.parametrize("z2y", [-10000, 10000])
@pytest.mark.parametrize("w1x", [0.95, 1.05])
@pytest.mark.parametrize("w2x", [0.95, 1.05])
@pytest.mark.parametrize("w1y", [0.95, 1.05])
@pytest.mark.parametrize("w2y", [0.95, 1.05])
def test_optimise_HG00_q(model, z1x, w1x, z1y, w1y, z2x, w2x, z2y, w2y):
    q1x = finesse.BeamParam(w0=w1x, z=z1x)
    q1y = finesse.BeamParam(w0=w1y, z=z1y)
    q2x = finesse.BeamParam(w0=w2x, z=z2x)
    q2y = finesse.BeamParam(w0=w2y, z=z2y)
    kmat = make_scatter_matrix(
        "bayerhelms", q1x, q2x, q1y, q2y, 0, 0, select=model.homs
    )
    E = np.zeros(len(model.homs), dtype=complex)
    E[0] = 1
    E = kmat.data @ E  # new mode vector
    q3x, q3y = optimise_HG00_q(
        E, (q2x, q2y), model.homs, accuracy=1e-6, max_iterations=100
    )
    assert abs(q3x.w0 - q1x.w0) / abs(q1x.w0) < 0.001
    assert abs(q3x.z - q1x.z) / abs(q1x.z) < 0.001
    assert abs(q3y.w0 - q1y.w0) / abs(q1y.w0) < 0.001
    assert abs(q3y.z - q1y.z) / abs(q1y.z) < 0.001
