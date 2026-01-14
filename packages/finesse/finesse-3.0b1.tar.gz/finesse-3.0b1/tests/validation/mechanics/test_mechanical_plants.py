import numpy as np
import scipy.signal as sig

import finesse.components as fc
import finesse.analysis.actions as fa


def test_changing_parameters(model):
    """Tests that masses and moments of inertia can change during a simulation and give
    the correct plants."""
    model.add(fc.Mirror("ETM", T=0, L=0))
    model.add(fc.Mirror("ITM", T=0.014, L=0))
    model.add(fc.FreeMass("ETM_sus", model.ETM.mech))
    model.add(fc.Pendulum("ITM_sus", model.ITM.mech))
    model.fsig.f = F0_Hz = 2

    inertia = 10
    Q = 80
    F_Hz = 5
    dofs = ["z", "pitch", "yaw"]
    props = ["mass", "I_pitch", "I_yaw"]
    for dof in dofs:
        model.set(f"ITM_sus.f{dof}", F0_Hz)
        model.set(f"ITM_sus.Q{dof}", Q)

    to = [f"{tm}_sus.mech.{dof}" for tm in ["ETM", "ITM"] for dof in dofs]
    fr = [f"{tm}_sus.mech.F_{dof}" for tm in ["ETM", "ITM"] for dof in dofs]
    change = {f"{tm}_sus.{p}": inertia for tm in ["ETM", "ITM"] for p in props}

    sol = model.run(
        fa.Series(
            fa.FrequencyResponse([F_Hz], fr, to, name="fresp1"),
            fa.Change(change),
            fa.FrequencyResponse([F_Hz], fr, to, name="fresp2"),
        )
    )

    assert np.all(sol["fresp1"].out == 0)
    free_mass_sus = -1 / (inertia * (2 * np.pi * F_Hz) ** 2)
    pendulum_sus = (
        1 / (inertia * (2 * np.pi) ** 2) / (F0_Hz**2 - F_Hz**2 + 1j * F_Hz * F0_Hz / Q)
    )
    np.testing.assert_allclose(np.diag(sol["fresp2"].out[0, :3, :3]), free_mass_sus)
    np.testing.assert_allclose(np.diag(sol["fresp2"].out[0, 3:, 3:]), pendulum_sus)


def test_SuspensionZPK(model):
    """Tests that SuspensionZPK can correctly model cross-couplings."""
    QQ = 0.01 + 1j
    ps = -np.array([1, 10]) * QQ * 2 * np.pi
    ps = np.concatenate((ps, ps.conjugate()))
    zs = -np.array([5 * QQ, 5 * QQ.conjugate()]) * 2 * np.pi
    zpk_plant = {}
    zpk_plant["z", "F_z"] = (zs, ps, 1)
    zpk_plant["pitch", "F_z"] = ([0], ps, 8)
    model.fsig.f = 1
    model.add(fc.Mirror("ETM", T=0, L=0))
    model.add(fc.SuspensionZPK("ETM_sus", model.ETM.mech, zpk_plant))
    sus = "ETM_sus"
    fr = [f"{sus}.mech.F_z"]
    to = [f"{sus}.mech.{dof}" for dof in ["z", "pitch"]]
    F_Hz = np.geomspace(0.1, 100, 100)
    sol = model.run(fa.FrequencyResponse(F_Hz, fr, to))
    np.testing.assert_allclose(
        sol.out[..., 0, 0],
        sig.freqs_zpk(*zpk_plant["z", "F_z"], 2 * np.pi * F_Hz)[1],
    )
    np.testing.assert_allclose(
        sol.out[..., 1, 0],
        sig.freqs_zpk(*zpk_plant["pitch", "F_z"], 2 * np.pi * F_Hz)[1],
    )
