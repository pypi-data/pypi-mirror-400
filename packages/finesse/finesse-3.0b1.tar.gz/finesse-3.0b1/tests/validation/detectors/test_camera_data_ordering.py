import pytest
import numpy as np

import finesse


TILT = 2.5e-5


@pytest.fixture(
    params=[
        {"ybeta": +TILT, "xbeta": +TILT, "idx": (+0, +0)},  # bottom-left
        {"ybeta": -TILT, "xbeta": +TILT, "idx": (-1, +0)},  # top-left
        {"ybeta": -TILT, "xbeta": -TILT, "idx": (-1, -1)},  # top-right
        {"ybeta": +TILT, "xbeta": -TILT, "idx": (+0, -1)},  # bottom-right
    ]
)
def solution(request):
    xbeta = request.param["xbeta"]
    ybeta = request.param["ybeta"]

    maxtem = 20
    xmax = 0.15 / 2
    w0 = 8e-3
    L = 100
    ccd_points = 10
    ccdxmax = xmax / 15
    ccdymax = xmax / 10

    code = f"""
    l l1 P=1
    gauss g1 m1.p1.i w0={w0} z=0
    m m1 R=1 T=0 phi=0
    s s1 l1.p1 m1.p1 L={L}

    # CCD like detectors
    ccd ccd1 l1.p1.i {ccdxmax} {ccdymax} {ccd_points} w0_scaled=false

    # field camera detectors
    fcam fcam1 l1.p1.i {ccdxmax} {ccdymax} {ccd_points} f=0 w0_scaled=false
    """
    model = finesse.Model()
    model.modes(maxtem=maxtem)
    model.parse(code)
    model.m1.xbeta = xbeta
    model.m1.ybeta = ybeta
    sol = model.run()

    return sol, request.param


def test_data_ordering_ccd(solution):
    """In the solution the beam is reflected by a tilted mirror in the direction of
    one of the corner of the camera. Consequently, the data of the corresponding corner
    should be higher in magnitude then the other corners. This allows us to test the
    ordering of the data comparing the data at those corners."""
    sol, param = solution
    idx_max = param["idx"]

    smaller_idx = [p for p in [(0, 0), (0, -1), (-1, 0), (-1, -1)] if p != idx_max]
    ccd_data = sol["ccd1"]
    fcam_data = np.abs(sol["fcam1"])

    for idx in smaller_idx:
        # Checking if it at least 2x bigger to remove close values
        assert ccd_data[idx] < 0.5 * ccd_data[idx_max]
        assert fcam_data[idx] < 0.5 * fcam_data[idx_max]
