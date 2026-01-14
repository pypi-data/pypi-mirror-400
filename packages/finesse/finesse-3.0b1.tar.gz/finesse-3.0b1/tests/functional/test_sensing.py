# %%
import finesse
from finesse.analysis.actions import OptimiseRFReadoutPhaseDC
import numpy as np
import pytest


def test_auto_OptimiseRFReadoutPhaseDC_PDH_I():
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)

    lock cav_lock PD_I m2.phi 0.01 1e-3
    """
    )
    action = OptimiseRFReadoutPhaseDC()
    sol = model.run(action)
    out = model.run("xaxis(m2.phi, lin, -0.1, 0.1, 3, relative=True)")
    # optimal here should be 0 demod phase
    assert sol.previous_phases["PD"] == 33
    assert np.allclose(model.l1.phase.value, 0)
    assert np.all(sol.phases["PD"] != 33)
    # 2e-7 picked from scaning and seeing how small value should be
    assert np.allclose(out["PD_Q"], 0, atol=2e-7)
    assert sol.phases["PD"] == model.PD.phase.value


def test_auto_OptimiseRFReadoutPhaseDC_PDH_Q():
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)

    lock cav_lock PD_Q m2.phi 0.01 1e-3
    """
    )
    action = OptimiseRFReadoutPhaseDC()
    sol = model.run(action)
    out = model.run("xaxis(m2.phi, lin, -0.1, 0.1, 3, relative=True)")
    # optimal here should be 0 demod phase
    assert sol.previous_phases["PD"] == 33
    assert np.allclose(model.l1.phase.value, 0)
    assert np.all(sol.phases["PD"] != 33)
    # 2e-7 picked from scaning and seeing how small value should be
    assert np.allclose(out["PD_I"], 0, atol=2e-7)
    assert sol.phases["PD"] == model.PD.phase.value


def test_auto_OptimiseRFReadoutPhaseDC_non_RF_lock():
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_dc PD optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)

    lock cav_lock PD_DC m2.phi 0.01 1e-3
    """
    )
    action = OptimiseRFReadoutPhaseDC()
    sol = model.run(action)
    assert len(sol.phases) == 0  # should not do anything


@pytest.mark.parametrize("drive", ["m1.phi", "m2.phi", "l1.f"])
@pytest.mark.parametrize(
    "quadrature,other_quadrature",
    (
        ("I", "Q"),
        ("Q", "I"),
    ),
)
def test_user_OptimiseRFReadoutPhaseDC(drive, quadrature, other_quadrature):
    model = finesse.Model()
    readout = "PD"
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)
    """
    )
    action = OptimiseRFReadoutPhaseDC(drive, readout + "_" + quadrature)
    sol = model.run(action)
    out = model.run(f"xaxis({drive}, lin, -0.1, 0.1, 3, relative=True)")
    # optimal here should be 0 demod phase
    assert sol.previous_phases[readout] == 33
    assert np.allclose(model.l1.phase.value, 0)
    assert np.all(sol.phases[readout] != 33)
    # 2e-7 picked from scaning and seeing how small value should be
    assert np.allclose(out[f"{readout}_{other_quadrature}"], 0, atol=2e-7)
    assert sol.phases[readout] == model.PD.phase.value


def test_manual_OptimiseRFReadoutPhaseDC_readout():
    # This should run until the deprecition kicks in and becomes an exception
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)

    lock cav_lock PD_I m2.phi 0.01 1e-3
    """
    )
    action = OptimiseRFReadoutPhaseDC("m2.phi", "PD_I")
    sol = model.run(action)
    out = model.run("xaxis(m2.phi, lin, -0.1, 0.1, 3, relative=True)")
    # optimal here should be 0 demod phase
    assert sol.previous_phases["PD"] == 33
    assert np.allclose(model.l1.phase.value, 0)
    assert np.all(sol.phases["PD"] != 33)
    # 2e-7 picked from scaning and seeing how small value should be
    assert np.allclose(out["PD_Q"], 0, atol=2e-7)
    assert sol.phases["PD"] == model.PD.phase.value


def test_auto_OptimiseRFReadoutPhaseDC_PDH_I_DOF():
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=33 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.99 T=0.01
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)
    dof CAV m2.phi +1
    lock cav_lock PD_I CAV.DC 0.01 1e-3
    """
    )
    action = OptimiseRFReadoutPhaseDC()
    sol = model.run(action)
    out = model.run("xaxis(CAV.DC, lin, -0.1, 0.1, 3, relative=True)")
    # optimal here should be 0 demod phase
    assert sol.previous_phases["PD"] == 33
    assert np.allclose(model.l1.phase.value, 0)
    assert np.all(sol.phases["PD"] != 33)
    # 2e-7 picked from scaning and seeing how small value should be
    assert np.allclose(out["PD_Q"], 0, atol=2e-7)
    assert sol.phases["PD"] == model.PD.phase.value
