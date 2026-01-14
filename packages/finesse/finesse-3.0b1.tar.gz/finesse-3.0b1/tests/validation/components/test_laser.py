import pytest
import finesse
import numpy as np


@pytest.fixture
def solution():
    base = finesse.Model()
    base.parse(
        """
        l L0 P=1

        s s0 L0.p1 m1.p1

        m m1 R=0 T=1

        ad a00 m1.p2.o 0 n=0 m=0
        ad a10 m1.p2.o 0 n=1 m=0
        ad a01 m1.p2.o 0 n=0 m=1
        pd P m1.p2.o

        gauss g1 L0.p1.o w0=1m z=0

        modes(maxtem=1)
        """
    )

    base.L0.tem(0, 0, 1, 0)
    base.L0.tem(1, 0, 2, 0)
    base.L0.tem(0, 1, 4, 0)

    return base.run()


def test_power_conserved(solution):
    sol = solution
    assert abs(sol["P"] - 1) <= 1e-15


def test_hom_relative_power(solution):
    sol = solution
    assert abs(2 * abs(sol["a00"]) ** 2 - abs(sol["a10"]) ** 2) <= 1e-15
    assert abs(4 * abs(sol["a00"]) ** 2 - abs(sol["a01"]) ** 2) <= 1e-15


def test_laser_power():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    pd P l1.p1.o
    ad a l1.p1.o f=0
    xaxis(l1.P, lin, 0, 10, 10)
    """
    )
    sol = model.run()
    assert np.allclose(sol["P"], sol.x1, atol=1e-14)
    assert np.allclose(abs(sol["a"]), np.sqrt(sol.x1), atol=1e-14)


def test_laser_amplitude():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    ad a l1.p1.o f=0
    xaxis(l1.phase, lin, -180, 180, 10)
    """
    )
    sol = model.run()
    assert np.allclose(np.angle(sol["a"], deg=True), sol.x1, atol=1e-14)


@pytest.mark.parametrize("add_gouy_phase,z", [(True, False), (0, 10)])
def test_laser_set_output_field(add_gouy_phase, z):
    model = finesse.Model()
    model.parse(
        f"""
    l l1 P=1
    fd E l1.p1.o 0
    modes(x, maxtem=1)
    gauss g1 l1.p1.o w0=1e-3 z={z}
    """
    )
    model.l1.add_gouy_phase = add_gouy_phase
    model.l1.set_output_field([1, 2j], model.homs)
    out = model.run()
    assert np.allclose(out["E"], [1, 2j])


def test_laser_gouy_phase():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    fd E l1.p1.o 0
    modes(x, maxtem=1)
    gauss g1 l1.p1.o w0=1e-3 z=1e15
    """
    )
    model.l1.tem(0, 0, 1, 0)
    model.l1.tem(1, 0, 1, 0)
    sol = model.run()
    assert np.allclose(sol["E"][1], 1j * sol["E"][0], atol=1e-14)


def test_laser_gouy_phase_fsig():
    model = finesse.Model()
    model.parse(
        """
    fsig(1)
    sgen sig l1.amp
    l l1 P=1
    fd E l1.p1.o fsig
    modes(x, maxtem=1)
    gauss g1 l1.p1.o w0=1e-3 z=1e15
    """
    )
    model.l1.tem(0, 0, 1, 0)
    model.l1.tem(1, 0, 1, 0)
    sol = model.run()
    assert np.allclose(sol["E"][1], 1j * sol["E"][0], atol=1e-14)


def test_laser_signal_amp():
    out = finesse.script.parse(
        """
        fsig(1)
        l l1 P=1
        readout_dc PD
        link(l1, PD)
        ad up l1.p1.o +fsig
        ad lo l1.p1.o -fsig
        sgen sg l1.amp.i amplitude=1 phase=0
        """
    ).run()
    assert np.allclose(out["up"], 0.5, atol=1e-14)
    assert np.allclose(out["lo"], 0.5, atol=1e-14)


def test_laser_signal_power():
    out = finesse.script.parse(
        """
        fsig(1)
        l l1 P=1
        readout_dc PD
        link(l1, PD)
        ad up l1.p1.o +fsig
        ad lo l1.p1.o -fsig
        sgen sg l1.pwr.i amplitude=1 phase=0
        """
    ).run()
    assert np.allclose(out["up"], 0.25, atol=1e-14)
    assert np.allclose(out["lo"], 0.25, atol=1e-14)


def test_laser_signal_phase():
    out = finesse.script.parse(
        """
        fsig(1)
        l l1 P=1
        readout_dc PD
        link(l1, PD)
        ad up l1.p1.o +fsig
        ad lo l1.p1.o -fsig
        sgen sg l1.phs.i amplitude=1 phase=0
        """
    ).run()
    assert np.allclose(out["up"], 0.5j, atol=1e-14)
    assert np.allclose(out["lo"], 0.5j, atol=1e-14)


def test_laser_signal_frequency():
    model = finesse.script.parse(
        """
    fsig(10)
    l l1 P=1
    readout_dc PD
    link(l1, PD)
    ad up l1.p1.o +fsig
    ad lo l1.p1.o -fsig
    sgen sg l1.frq.i amplitude=1 phase=0
    """
    )
    out = model.run()
    assert np.allclose(out["up"], +0.5 / model.fsig.f, atol=1e-13)
    assert np.allclose(out["lo"], -0.5 / model.fsig.f, atol=1e-13)
