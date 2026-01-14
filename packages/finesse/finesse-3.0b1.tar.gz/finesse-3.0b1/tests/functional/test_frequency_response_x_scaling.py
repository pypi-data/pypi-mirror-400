"""This test ensures the output of `run_fsig_sweep` performed by the `FrequencyResponse`
action is independent of `x_scale`."""
from finesse import Model
from finesse.analysis.actions import FrequencyResponse

import numpy as np

import pytest


# prepare some models
@pytest.fixture()
def swinging_mirror_no_filter():
    model = Model()
    model.parse(
        """
        m m1 R=1 T=0

        pendulum m1_sus m1.mech mass=1

        fsig(1)
        """
    )
    return model


@pytest.fixture()
def swinging_mirror_with_e_filter():
    model = Model()
    model.parse(
        """
        fsig(1)

        m m1 R=1 T=0
        zpk ctrl [] [] 1 gain=1
        pendulum m1_sus m1.mech mass=1

        link(ctrl, m1.mech.F_z)
        """
    )
    return model


@pytest.fixture()
def swinging_mirror_with_m_filter():
    model = Model()
    model.parse(
        """
        fsig(1)

        m m1 R=1 T=0
        pendulum m1_sus m1.mech mass=1
        zpk filter [] [] 1 gain=1

        link(m1.mech.z, filter)
        """
    )
    return model


@pytest.fixture()
def swinging_mirror_with_both_filters():
    model = Model()
    model.parse(
        """
        m m1 R=1 T=0

        zpk ctrl [] [] 1 gain=1
        pendulum m1_sus m1.mech mass=1
        link(ctrl, m1.mech.F_z)

        zpk filter [] [] 1 gain=1
        link(m1.mech.z, filter)

        fsig(1)
        """
    )
    return model


# prepare comparisons
def get_outs(model, inject_into, read_out_of, open_loop=False):
    """Runs and returns two FRs with different x_scale values."""

    f = np.logspace(-1, 6, 11)

    model1 = model.deepcopy()
    model1._settings.x_scale = 1e-9
    out1 = model1.run(
        FrequencyResponse(f, inject_into, read_out_of, open_loop=open_loop)
    )

    model2 = model.deepcopy()
    model2._settings.x_scale = 1
    out2 = model2.run(
        FrequencyResponse(f, inject_into, read_out_of, open_loop=open_loop)
    )

    return out1.out, out2.out


# run some tests
#
# These tests run through every possible input/output signal type combination
#   for both closed loop and open loop to ensure scaling is working.
#
# 1) m to m
# 2) m to m (with a zpk present)
# 3) e to m
# 4) e to e
# 5) m to e


# m to m
def test_cl_frequency_response_x_scale_m_to_m(swinging_mirror_no_filter):
    """Test effect of changing x_scale on mech to mech frequency response in closed
    loop."""

    # closed loop
    out1, out2 = get_outs(swinging_mirror_no_filter, "m1.mech.F_z", "m1.mech.z")
    assert abs(out1 - out2).all() <= 1e-15


def test_ol_frequency_response_x_scale_m_to_m(swinging_mirror_no_filter):
    """Test effect of changing x_scale on mech to mech frequency response in open
    loop."""

    # open loop
    out1, out2 = get_outs(
        swinging_mirror_no_filter, "m1.mech.F_z", "m1.mech.z", open_loop=True
    )
    assert abs(out1 - out2).all() <= 1e-15


# m to m w/ e filter
def test_cl_frequency_response_x_scale_m_to_m_w_e_filter(swinging_mirror_with_e_filter):
    """Test effect of changing x_scale on mech to mech frequency response in closed
    loop."""

    # closed loop
    out1, out2 = get_outs(swinging_mirror_with_e_filter, "m1.mech.F_z", "m1.mech.z")
    assert abs(out1 - out2).all() <= 1e-15


def test_ol_frequency_response_x_scale_m_to_m_w_e_filter(swinging_mirror_with_e_filter):
    """Test effect of changing x_scale on mech to mech frequency response in open
    loop."""

    # open loop
    out1, out2 = get_outs(
        swinging_mirror_with_e_filter, "m1.mech.F_z", "m1.mech.z", open_loop=True
    )
    assert abs(out1 - out2).all() <= 1e-15


# e to m
def test_cl_frequency_response_x_scale_e_to_m(swinging_mirror_with_e_filter):
    """Test effect of changing x_scale on elec to mech frequency response in closed
    loop."""

    # closed loop
    out1, out2 = get_outs(swinging_mirror_with_e_filter, "ctrl.p1", "m1.mech.z")
    assert abs(out1 - out2).all() <= 1e-15


def test_ol_frequency_response_x_scale_e_to_m(swinging_mirror_with_e_filter):
    """Test effect of changing x_scale on elec to mech frequency response in open
    loop."""

    # open loop
    out1, out2 = get_outs(
        swinging_mirror_with_e_filter, "ctrl.p1", "m1.mech.z", open_loop=True
    )
    assert abs(out1 - out2).all() <= 1e-15


# e to e
def test_cl_frequency_response_x_scale_e_to_e(swinging_mirror_with_both_filters):
    """Test effect of changing x_scale on elec to mech frequency response in closed
    loop."""

    # closed loop
    out1, out2 = get_outs(swinging_mirror_with_both_filters, "ctrl.p1", "filter.p2")
    assert abs(out1 - out2).all() <= 1e-15


def test_ol_frequency_response_x_scale_e_to_e(swinging_mirror_with_both_filters):
    """Test effect of changing x_scale on elec to mech frequency response in open
    loop."""

    # open loop
    out1, out2 = get_outs(
        swinging_mirror_with_both_filters, "ctrl.p1", "filter.p2", open_loop=True
    )
    assert abs(out1 - out2).all() <= 1e-15


# m to e
def test_cl_frequency_response_x_scale_m_to_e(swinging_mirror_with_m_filter):
    """Test effect of changing x_scale on mech to mech frequency response in closed
    loop."""

    # closed loop
    out1, out2 = get_outs(swinging_mirror_with_m_filter, "m1.mech.F_z", "filter.p2")
    assert abs(out1 - out2).all() <= 1e-15


def test_ol_frequency_response_x_scale_m_to_e(swinging_mirror_with_m_filter):
    """Test effect of changing x_scale on mech to mech frequency response in open
    loop."""

    # open loop
    out1, out2 = get_outs(
        swinging_mirror_with_m_filter, "m1.mech.F_z", "filter.p2", open_loop=True
    )
    assert abs(out1 - out2).all() <= 1e-15
