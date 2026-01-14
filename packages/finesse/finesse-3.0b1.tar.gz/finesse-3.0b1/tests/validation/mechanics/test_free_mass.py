# %%
import pytest
import finesse
from scipy.constants import c, pi
import numpy as np


# %%
@pytest.fixture
def model():
    model = finesse.script.parse(
        """
        l l1 P=3.3
        s s1 l1.p1 m1.p1
        m m1 R=1 T=0
        free_mass m1_sus m1.mech mass=1

        sgen sig l1.pwr.i 1 0

        ad adz m1.mech.z fsig.f
        ad adF_z m1.mech.F_z fsig.f

        fsig(1)
        """
    )
    return model


def mech_sus(M, w):
    return 1 / (-M * w**2)


def analytic(P, c, M, w):
    # Extra minus sign here because we push against the normal of the mirror on
    # the front (p1)
    return -2 * P / c * mech_sus(M, w)


def test_amplitude(model):
    sol = model.run()

    P = model.l1.P.value
    M = model.m1_sus.mass.value
    w = 2 * pi * model.fsig.f.value
    assert abs(sol["adz"] - analytic(P, c, M, w)) < 1e-15


def test_frequency_response1(model):
    P = model.l1.P.value
    M = model.m1_sus.mass.value
    sol = model.run("frequency_response(geomspace(1, 100, 10), [l1.pwr], [m1.mech.z])")
    w = 2 * pi * sol.f

    assert np.allclose(sol["m1.mech.z", "l1.pwr"], analytic(P, c, M, w), atol=1e-15)


def test_frequency_response4(model):
    P = model.l1.P.value
    M = model.m1_sus.mass.value
    sol4 = model.run(
        "frequency_response4([1], [l1.pwr], [[m1.p1.i, fsig], [m1.p1.i, -fsig]])"
    )
    w = 2 * pi * sol4.f
    H = sol4.out.squeeze()
    DC = model.run("dc_fields()")
    Ec = DC["m1.p1.i"].squeeze()

    # Multiply carrier with upper and lower sidebands to compute
    # P(Omega) = 2 * (conj(Ec) * Eu + Ec * conj(El))
    # 2 here because FINESSE returns P=|E|^2 scaling for fields
    P_sig = 2 * H @ np.array([Ec.conj(), Ec])
    assert np.allclose(
        -2 * P_sig / c * mech_sus(M, w), analytic(P, c, M, w), atol=1e-15
    )


@pytest.mark.skip(reason="needs factor of two from Kevin for quadratures")
def test_perfect_refl_free_mass_mirror_symbolic():
    """Physics test that came out of discussion with Kevin about factors of two not
    agreeing between quadrature and sideband picture.

    In the end the confusion seemed to be overall scaling. You need to inject 0.5W of
    upper and lower sideband in, 1W in total, then convert into the quadrature picture
    """
    import numpy as np
    import finesse
    import sympy as sy
    from finesse.analysis.actions import FrequencyResponse3, FrequencyResponse2, Series
    import scipy.constants as sc

    k, P, m, omega, lambda0, c = sy.var(
        "k P M Omega lambda0 c", real=True, positive=True
    )
    E1u, E1l, E2u, E2l, z, F = sy.var(
        "E_{1+} E^{\\dagger}_{1-} E_{2+} E^{\\dagger}_{2-} z F"
    )
    # E1u, E1l incident sidebands
    # E2u, E2l reflected sidebands
    # E2l is the conjugate of the lower sideband

    # P = 1/2 |E|^2 and E = sqrt(2*P)
    # or
    # P = |E|^2 and E = sqrt(P)
    # Either way it works but you have to include the right scaling
    # factor in the radiation pressure term too

    Ec = sy.sqrt(P)  # Carrier just sqrt power
    # Ec = sy.sqrt(2 * P)

    # Solve the output optical fields, motion, and force
    eqs = sy.FiniteSet(
        E2u - (E1u + sy.I * 2 * k * z * Ec),
        E2l - (E1l - sy.I * 2 * k * z * Ec),
        z - (F * 1 / (-m * omega**2)),
        # 2 for momentum conservation
        F - (-2 * (sy.conjugate(Ec) * E2u + Ec * E2l) / c),
        # or if you use P = 1/2 |E|^2
        # 2 for momentum conservation
        # 1/2 for the conversion from fields to power
        # F - (-2 / 2 * (sy.conjugate(Ec) * E2u + Ec * E2l) / c),
    )

    analytic = sy.solve(eqs, (E2u, E2l, z, F))

    A = 1 / sy.sqrt(2) * sy.Matrix([[1, 1], [-sy.I, sy.I]])
    Q = A @ sy.Matrix([[analytic[E2u]], [analytic[E2l]]])
    Q.simplify()

    # display("Conjugate lower", analytic[E2l].collect(4 * sy.I * P * k))
    # display("Upper", analytic[E2u].collect(4 * sy.I * P * k))

    # Convert to quadratures
    # display("Cosine quadrature:", Q[0])
    # display("Sine quadrature:", Q[1].collect(8 * P * k).collect(sy.I * m * omega**2 * c))

    # print("Injecting unit of sidebands")
    # Here we inject sqrt(1/2) for 0.5W of sidebands in each
    # upper and lower sideband
    # Q1 = Q.subs({E1l: 1 / sy.sqrt(2), E1u: 1 / sy.sqrt(2)})
    # if you don't use 0.5W in each you'll end up with an extra sqrt(2)
    # in your K term compared from the most references
    # display("Cosine quadrature:", Q1[0])
    # display("Sine quadrature:", Q1[1])

    model = finesse.script.parse(
        """
        fsig(1)
        l l1 P=1
        s s1 l1.p1 m1.p1 L=0
        m m1 R=1 T=0
        free_mass m1_sus m1.mech 1
        """
    )

    f = np.geomspace(0.01, 1, 11)
    fsig = model.fsig.f.ref
    sol = model.run(
        Series(
            FrequencyResponse3(
                f,
                [("m1.p1.i", fsig), ("m1.p1.i", -fsig)],
                [("m1.p1.o", fsig), ("m1.p1.o", -fsig)],
                name="3",
            ),
            FrequencyResponse2(
                f,
                [("m1.p1.i", fsig), ("m1.p1.i", -fsig)],
                ["m1.mech.z", "m1.mech.F_z"],
                name="2",
            ),
        )
    )

    # propagate unit amount of upper and lower sidebands
    # for the simulated results
    ROOT2 = np.sqrt(2)  # need to inject 0.5W in each sideband
    Eout = sol["3"].out.squeeze() @ [1 / ROOT2, 1 / ROOT2]
    zout = sol["2"].out.squeeze() @ [1 / ROOT2, 1 / ROOT2]

    # Substitution values for this simulation state
    values = {
        m: model.m1_sus.mass.value,
        P: model.l1.P.value,
        k: model.k0,
        E1u: 1 / ROOT2,
        E1l: 1 / ROOT2,
        c: sc.c,
    }

    analytic_upper = sy.lambdify(
        omega,
        analytic[E2u].subs(values),
    )(f * 2 * np.pi)

    analytic_z = sy.lambdify(
        omega,
        analytic[z].subs(values),
    )(f * 2 * np.pi)

    analytic_F = sy.lambdify(
        omega,
        analytic[F].subs(values),
    )(f * 2 * np.pi)

    assert np.allclose(Eout[:, 0], analytic_upper, atol=1e-14)
    assert np.allclose(zout[:, 0], analytic_z, atol=1e-14)
    assert np.allclose(zout[:, 1], analytic_F, atol=1e-14)
