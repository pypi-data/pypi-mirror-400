import numpy as np
from finesse.utilities.polyfit import (
    polyfit2d,
    polyfit2d_eval,
    polyfit2d_indices,
    polyfit2d_index,
)


def test_fit_unity_coefficients():
    x = np.linspace(-1, 1, num=201)
    y = np.linspace(-1, 1, num=201)
    kx = ky = 5
    X, Y = np.meshgrid(x, y)
    true_coeffs = np.ones((kx + 1, ky + 1))
    Z = polyfit2d_eval(x, y, true_coeffs, kx, ky)
    fit_coeffs, _, _, _ = polyfit2d(x, y, Z, kx, ky)
    assert np.all(abs(fit_coeffs - true_coeffs.ravel()) < 1e-12)


def test_indices():
    kx = ky = 2
    indices = polyfit2d_indices(kx, ky)
    assert np.all(
        indices
        == np.array(
            [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
        )
    )


def test_index():
    kx = 2
    ky = 2
    indices = polyfit2d_indices(kx, ky)
    for index, (a, b) in enumerate(indices):
        assert polyfit2d_index(kx, a, b) == index
