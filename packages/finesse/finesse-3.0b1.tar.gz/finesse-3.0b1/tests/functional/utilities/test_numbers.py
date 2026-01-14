import numpy as np
import pytest

from finesse.utilities import clip_with_tolerance


@pytest.mark.parametrize(
    "number, min, max, tol, expected",
    (
        (0.5, 0.1, 1.0, 1e-12, 0.5),
        (-0.3, 0.3, 3.0, 1e-6, -0.3),
        (0.41, 0.5, 0.9, 0.1, 0.5),
        (0.4, 0.5, 0.9, 0.1, 0.4),
        (-3, -10, -4, 2, -4),
    ),
)
def test_clip_with_tolerance(number, min, max, tol, expected):
    res = clip_with_tolerance(number, min, max, tol)
    np.testing.assert_allclose(res, expected)
