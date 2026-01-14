import finesse
import numpy as np


def test_model_parameter_extract_noxaxis():
    model = finesse.script.parse(
        """
    l l1 P=2.3
    mathd P l1.P
    mathd P_10 10*l1.P
    """
    )
    out = model.run()

    assert out["P"] == model.l1.P.value
    assert out["P_10"] == model.l1.P.value * 10


def test_model_parameter_extract_xaxis():
    model = finesse.script.parse(
        """
    l l1 P=2.3
    mathd P l1.P
    mathd P_10 10*l1.P
    xaxis(l1.P, lin, 0, 1, 3)
    """
    )
    out = model.run()

    assert np.allclose(out["P"].astype(float), out.x1)
    assert np.allclose(out["P_10"].astype(float), out.x1 * 10)


def test_power_detector():
    model = finesse.script.parse(
        """
    l l1
    pd Y l1.p1.o
    mathd Z1 Y
    mathd Z2 Y*10
    xaxis(l1.P, lin, 0, 1, 3)
    """
    )
    out = model.run()

    assert np.allclose(out["Z1"].astype(float), out.x1)
    assert np.allclose(out["Z2"].astype(float), out.x1 * 10)


def test_power_detector_1_fsig():
    model = finesse.script.parse(
        """
    l l1
    pd1 Y l1.p1.o f=fsig
    sgen sg l1.pwr.i phase=90
    mathd Z1 Y
    mathd Z2 Y*10
    xaxis(fsig, log, 1, 10, 3)
    fsig(1)
    """
    )
    out = model.run()
    assert np.allclose(out["Z1"].astype(complex), 1j * np.ones_like(out.x1))
    assert np.allclose(out["Z2"].astype(complex), 1j * np.ones_like(out.x1) * 10)


def test_noise_detector():
    model = finesse.script.parse(
        """
    l l1
    qnoised Y l1.p1.o
    mathd Z1 Y
    mathd Z2 Y*10
    xaxis(fsig, log, 1, 10, 3)
    fsig(1)
    """
    )
    out = model.run()
    hf = model.f0 * finesse.constants.H_PLANCK

    assert np.allclose(out["Z1"].astype(float) ** 2 / hf, 2 * np.ones_like(out.x1))
    assert np.allclose(
        out["Z2"].astype(float) ** 2 / hf, 2 * np.ones_like(out.x1) * 100
    )
