# %%
import finesse
from finesse.analysis.actions import (
    DragLocks,
    OptimiseRFReadoutPhaseDC,
    SetLockGains,
    RunLocks,
    Series,
    Maximize,
    Change,
    Noxaxis,
)
import pytest

finesse.configure(plotting=True)


@pytest.fixture
def locks_model():
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s l_mod1 L0.p1 eo1.p1
        mod eo1 10M 0.1

        s s0 eo1.p2 BS.p1
        bs BS R=0.5 T=0.5

        s s1 BS.p2 NI.p1
        m NI R=0.99 T=0.01 Rc=1429 phi=90
        s CAV NI.p2 NE.p1 L=10
        m NE R=0.991 T=0.009 Rc=1430 phi=90

        s s2 BS.p3 EI.p1
        m EI R=0.99 T=0.01 Rc=1429 phi=0
        s CAV2 EI.p2 EE.p1 L=10
        m EE R=0.991 T=0.009 Rc=1430 phi=0

        dof NEz NE.dofs.z +1
        dof EEz EE.dofs.z +1
        dof NIz NI.dofs.z +1

        readout_rf rd_pdh1 NI.p1.o f=10M
        readout_rf rd_pdh2 EI.p1.o f=10M
        readout_rf rd_DF BS.p4.o f=10M

        lock cav1_lock rd_pdh1.outputs.I NEz.DC 1 1e-9
        lock cav2_lock rd_pdh2.outputs.I EEz.DC 1 1e-9
        lock DF_lock rd_DF.outputs.I NIz.DC 1 1e-9

        cav cav1 NI.p2.o
        cav cav2 EI.p2.o
        """
    )
    return kat


def test_run_locks_newton_method(locks_model):
    sol = locks_model.run(RunLocks(method="newton", display_progress=False))
    assert sol.iters < 10


def test_drag_locks_newton_method(locks_model):
    sol = locks_model.run(
        DragLocks(
            method="newton",
            parameters=["BS.xbeta"],
            stop_points=[2e-6],
            display_progress=False,
            relative=True,
        )
    )
    assert sol.iters < 10


def test_pdh_lock_optimisation_action():
    model = finesse.Model()
    model.parse(
        """
    l l1
    mod mod1 10M 0.1 mod_type=pm
    readout_rf PD f=mod1.f phase=37.3 output_detectors=True optical_node=m1.p1.o
    m m1 R=0.9999 T=0.0001
    m m2 R=1 T=0
    link(l1, mod1, m1, 1, m2)
    dof CAV m2.phi +1
    lock cav_lock PD_I CAV.DC 0.01 1e-3

    pd Pcirc m2.p1.o
    ad Ecirc m2.p1.o f=0
    ad Ein m1.p1.i f=0
    """
    )

    test_lock = Series(
        Maximize(model.Pcirc, model.CAV.DC),
        OptimiseRFReadoutPhaseDC(),
        SetLockGains(),
        Change({model.CAV.DC: 0.1}, relative=True),
        RunLocks(),
        Noxaxis(),
    )
    sol = model.run(test_lock)
    g = 4 / model.m1.T  # approximate cavity gain for high finesse
    # model.CAV.DC, model.PD.phase, model.cav_lock.gain, abs(sol['noxaxis']['Ein'])**2 * g, sol['noxaxis']['Pcirc']
    assert abs(abs(sol["noxaxis"]["Ein"]) ** 2 * g - sol["noxaxis"]["Pcirc"]) < 3
