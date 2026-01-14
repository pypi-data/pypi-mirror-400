import cmath
import numpy as np
import finesse
import finesse.components as fc
import finesse.detectors as det
from finesse.analysis.actions import FrequencyResponse


def test_sidles_sigg():
    L = 3994.5
    I = 0.757
    c = 299792458
    f_sus = 1.5

    model = finesse.Model()
    model.fsig.f = 1  # set some initial signal frequency
    model.modes(maxtem=1)  # first order modes for modelling alignment signals

    LASER = model.add(fc.Laser("LASER", P=1000))
    # Add two mirrors for the cavity and attach a pendulum mechanics
    M1 = model.add(fc.Mirror("M1", R=0.986, T=0.014, Rc=1934))
    model.add(
        fc.mechanical.Pendulum(
            "M1_sus", model.M1.mech, mass=np.inf, I_yaw=np.inf, I_pitch=I, fpitch=f_sus
        )
    )
    M2 = model.add(fc.Mirror("M2", R=1, T=0, Rc=2245))
    model.add(
        fc.mechanical.Pendulum(
            "M2_sus", model.M2.mech, mass=np.inf, I_yaw=np.inf, I_pitch=I, fpitch=f_sus
        )
    )
    model.connect(M1.p1, M2.p1, L=L)
    model.connect(LASER.p1, M1.p2)
    model.add(fc.Cavity("cavARM", M2.p1.o))
    model.add(det.PowerDetector("P", M1.p1.o))  # cavity power

    # Now we compute the decomposition of HARD and SOFT modes into motions of M1 and M2
    g_itmx = 1 - float(L / np.abs(M1.Rcx.value))
    g_etmx = 1 - float(L / np.abs(M2.Rcx.value))
    rx = 2 / ((g_itmx - g_etmx) + np.sqrt((g_etmx - g_itmx) ** 2 + 4))
    # Define what the HARD and SOFT alignment modes are for the cavity based
    # on its geometry
    model.add(fc.DegreeOfFreedom("HARD", M1.dofs.F_pitch, -1, M2.dofs.F_pitch, rx))
    model.add(fc.DegreeOfFreedom("SOFT", M1.dofs.F_pitch, rx, M2.dofs.F_pitch, +1))

    LASER.P = 1410 * 3 / 2 * 430 / 600
    sol = model.run(
        FrequencyResponse(
            np.geomspace(1, 10, 2000),
            [model.HARD.AC.i, model.SOFT.AC.i],
            [model.HARD.AC.o, model.SOFT.AC.o],
        )
    )
    out = model.run()

    omega_0 = 2 * np.pi * f_sus
    P = out["P"]
    # Eq 2 from https://opg.optica.org/ao/fulltext.cfm?uri=ao-49-18-3474
    omega_plus = np.sqrt(
        omega_0**2
        + P
        * L
        / (I * c)
        * (-(g_itmx + g_etmx) + cmath.sqrt(4 + (g_itmx - g_etmx) ** 2))
        / (1 - g_itmx * g_etmx)
    )
    omega_minus = np.sqrt(
        omega_0**2
        + P
        * L
        / (I * c)
        * (-(g_itmx + g_etmx) - cmath.sqrt(4 + (g_itmx - g_etmx) ** 2))
        / (1 - g_itmx * g_etmx)
    )

    # Make sure resonance peak is near to analytic
    assert np.allclose(
        sol.f[np.argmax(abs(sol["HARD.AC.o", "HARD.AC.i"]))],
        omega_plus / 2 / np.pi,
        atol=0.01,
    )
    assert np.allclose(
        sol.f[np.argmax(abs(sol["SOFT.AC.o", "SOFT.AC.i"]))],
        omega_minus / 2 / np.pi,
        atol=0.01,
    )
    # Make sure SOFT and HARD tend to same high frequency response
    assert np.allclose(
        sol["SOFT.AC.o", "SOFT.AC.i"][-1],
        sol["HARD.AC.o", "HARD.AC.i"][-1],
        atol=0.0001,
    )
