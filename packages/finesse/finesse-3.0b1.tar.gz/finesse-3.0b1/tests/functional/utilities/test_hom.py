import numpy as np
import finesse
import scipy.special
import pytest


def test_make_modes_LG():
    assert np.all(
        finesse.utilities.homs.make_modes_LG(2)
        == np.array([[0, 0], [0, -1], [0, 1], [0, -2], [0, 2], [1, 0]])
    )


def test_HG_to_LG_matrix():
    maxtem = 2
    hg_modes = finesse.utilities.homs.make_modes(maxtem=maxtem)
    lg_modes = finesse.utilities.homs.make_modes_LG(maxtem)
    K = finesse.utilities.homs.HG_to_LG_matrix(hg_modes, lg_modes)
    assert np.allclose(
        K,
        np.array(
            [
                [
                    1.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                ],
                [
                    0.0 + 0.0j,
                    0.70710678 + 0.0j,
                    0.0 + 0.70710678j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                ],
                [
                    0.0 + 0.0j,
                    0.70710678 + 0.0j,
                    0.0 - 0.70710678j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                ],
                [
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.5 + 0.0j,
                    0.0 + 0.70710678j,
                    -0.5 + 0.0j,
                ],
                [
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.5 + 0.0j,
                    0.0 - 0.70710678j,
                    -0.5 + 0.0j,
                ],
                [
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    0.0 + 0.0j,
                    -0.70710678 + 0.0j,
                    0.0 + 0.0j,
                    -0.70710678 + 0.0j,
                ],
            ]
        ),
    )


@pytest.mark.parametrize("n", [0, 1, 2])
@pytest.mark.parametrize("a", [0, 1, 2])
@pytest.mark.parametrize("b", [0, 1, 2])
def test_jacobi_real_x(n, a, b):
    x = np.linspace(-2, 2)
    assert np.allclose(
        finesse.utilities.homs.jacobi_real_x(n, a, b, x),
        scipy.special.jacobi(n, a, b)(x),
    )
