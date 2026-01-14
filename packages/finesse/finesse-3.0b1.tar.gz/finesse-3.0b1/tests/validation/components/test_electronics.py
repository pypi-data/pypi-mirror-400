import numpy as np
import scipy.signal as sig

import finesse
from finesse.utilities import zpk_fresp
import pytest


def test_zpk_filter():
    model = finesse.Model()
    model.parse(
        """
    # Finesse always expects some optics to be present
    # so we make a laser incident on some photodiode
    l l1 P=1
    readout_dc PD l1.p1.o
    # Amplitude modulate a laser
    sgen sig l1.pwr

    variable R 1
    variable C 1
    zpk ZPK_RC [] [-1/(R*C)]
    link(PD.DC, ZPK_RC)
    ad lpf ZPK_RC.p2.o f=fsig

    fsig(1/(2*pi*R*C))
    """
    )

    sol = model.run()
    # Should always get the 1/sqrt(2) drop at the pole frequency
    # for a single pole filter.
    assert np.allclose(abs(sol["lpf"]), 1 / np.sqrt(2))
    model.ZPK_RC.gain *= 0
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 0)
    model.ZPK_RC.gain = 1
    model.ZPK_RC.p = []
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 1)
    # Try resetting as symbols
    model.ZPK_RC.p = [-1 / (model.R.ref * model.C.ref)]
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 1 / np.sqrt(2))
    # cancel out poles with zeros
    model.ZPK_RC.z = [-1 / (model.R.ref * model.C.ref)]
    model.ZPK_RC.p = [-1 / (model.R.ref * model.C.ref)]
    sol = model.run()
    np.testing.assert_allclose(abs(sol["lpf"]), 1)


@pytest.mark.parametrize(
    "zeros, poles, gain",
    [
        ([0], [-1], 1),  # Simple case
        ([0, -2], [-1, -3], 2),  # Multiple zeros and poles
        ([], [-1, -2], 1),  # Edge case with no zeros
        ([1, -1], [0.5, -0.5], 0.5),  # Mixed zeros and poles
        ([0, 1j, -1j], [-0.5, -1j, 1j], 1),  # Complex zeros and poles
        ([0.5, -0.5], [0.1, -0.1], 2),  # Small magnitude zeros and poles
        ([1, -1, 2], [-0.5, -1.5, 0.5], 0.1),  # Mixed with different magnitudes
        ([0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], 1),  # Small positive zeros and poles
        ([0, 0, 0], [-1, -1, -1], 1),  # Repeated zeros and poles
        (
            [1j, -1j, 2j, -2j],
            [0.5j, -0.5j, 1.5j, -1.5j],
            1,
        ),  # Purely imaginary zeros and poles
        ([0, 1 + 1j, 1 - 1j], [5 + 1j, 5 - 1j, 30, 15 + 2j, 15 - 2j], 8),
        (
            [0, 0.5, 1, 1.5, 2],
            [-0.5, -1, -1.5, -2, -2.5],
            1,
        ),  # Increasing sequence of zeros and poles
        (
            [0, 1, 2, 3, 4],
            [-1, -2, -3, -4, -5],
            0.5,
        ),  # Larger sequence of zeros and poles
        (
            [0, 1j, -1j, 2j, -2j, 3j, -3j],
            [0.5j, -0.5j, 1.5j, -1.5j, 2.5j, -2.5j],
            1,
        ),  # More complex imaginary zeros and poles
        (
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [-0.1, -0.2, -0.3, -0.4, -0.5],
            2,
        ),  # Small positive zeros and poles with higher gain
        (
            [0, 1, -1, 2, -2, 3, -3],
            [0.5, -0.5, 1.5, -1.5, 2.5, -2.5, 3.5, -3.5],
            0.1,
        ),  # Mixed sequence with different magnitudes
        (
            [0, 1 + 1j, 1 - 1j, 2 + 2j, 2 - 2j],
            [5 + 1j, 5 - 1j, 10 + 2j, 10 - 2j, 15 + 3j, 15 - 3j],
            5,
        ),  # Complex zeros and poles with higher gain
        # New cases with more poles than zeros
        ([0], [-1, -2, -3], 1),  # More poles than zeros
        ([0, 1], [-1, -2, -3, -4], 2),  # More poles than zeros with multiple zeros
        ([0, 1j], [-1, -2, -3, -4, -5], 1),  # Complex zeros with more poles
        (
            [0.5, -0.5],
            [-0.1, -0.2, -0.3, -0.4],
            2,
        ),  # Small magnitude zeros with more poles
        ([1, -1, 2], [-0.5, -1.5, -2.5, -3.5], 0.1),  # Mixed magnitudes with more poles
        (
            [0.1, 0.2],
            [-0.1, -0.2, -0.3, -0.4, -0.5],
            1,
        ),  # Small positive zeros with more poles
        ([0, 0], [-1, -1, -2, -2], 1),  # Repeated zeros with more poles
        (
            [1j, -1j],
            [0.5j, -0.5j, 1.5j, -1.5j],
            1,
        ),  # Purely imaginary zeros with more poles
        (
            [0, 1 + 1j],
            [5 + 1j, 5 - 1j, 30, 15 + 2j, 15 - 2j, 20],
            8,
        ),  # Complex zeros with more poles
    ],
)
def test_zpk_fresp_vs_scipy(zeros, poles, gain):
    """Tests the finesse zpk frequency response function evaluated on a simple zpk
    filter multiplied by a large number of zeros and divided by the same number of
    identical poles.

    This is tested against the scipy evaluation of the simple filter which cannot handle
    the large number of roots.
    """
    npts = 1000
    z0 = -np.array(zeros)
    p0 = -np.array(poles)
    zs = np.concatenate((z0, np.ones(npts) * 5))
    ps = np.concatenate((p0, np.ones(npts) * 5))
    w = 2 * np.pi * np.geomspace(0.1, 100, 100)
    tf1 = zpk_fresp(zs, ps, gain, w)
    tf2 = sig.freqs_zpk(z0, p0, gain, w)[1]
    np.testing.assert_allclose(tf1, tf2)
