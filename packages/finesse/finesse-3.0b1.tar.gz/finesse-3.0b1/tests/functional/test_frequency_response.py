# %%
import pytest
import numpy as np
import finesse
from finesse import Model
from finesse.analysis.actions import (
    Xaxis,
    FrequencyResponse,
    FrequencyResponse2,
    FrequencyResponse3,
    FrequencyResponse4,
)
from finesse.components import (
    Squeezer,
    Beamsplitter,
    Laser,
    ReadoutDC,
)
import finesse.components as fc
import finesse.analysis.actions as fa


@pytest.fixture
def squeezer():
    model = finesse.Model()
    model.add(Squeezer("SQZ", 0))
    model.add(Beamsplitter("BS", T=1e-14, L=0))
    model.add(Laser("L0", P=1e14, phase=-90))
    model.add(ReadoutDC("PD", model.BS.p2.o))
    model.connect(model.SQZ.p1, model.BS.p1, 1000)
    model.connect(model.L0.p1, model.BS.p4)
    model.fsig.f = 1
    return model


def _assert_sqz_response_phase(u2u, l2l, u2l=None, l2u=None):
    # checks that the upper and conjugate lower sidebands have the same phase unity amplitude
    # and that if upper to lower and lower to upper are calculated, they are zero
    assert np.allclose(u2u, l2l)
    for tf in [u2u, l2l]:
        assert np.allclose(np.abs(tf), 1)
    for tf in [u2l, l2u]:
        if tf is not None:
            assert np.allclose(np.abs(tf), 0)


@pytest.mark.skip(reason="needs more thought on factor of two")
def test_sqz_sideband_frequency_response_phase(squeezer):
    model = squeezer

    sol = model.run(
        FrequencyResponse(
            np.geomspace(0.1, 1000, 3),
            [model.SQZ.upper, model.SQZ.lower_conj],
            model.PD.DC.o,
        )
    )
    _assert_sqz_response_phase(
        u2u=sol["PD.DC.o", "SQZ.upper"],
        l2l=sol["PD.DC.o", "SQZ.lower_conj"],
    )


@pytest.mark.skip(reason="needs more thought on factor of two")
def test_sqz_sideband_frequency_response_2_phase(squeezer):
    model = squeezer

    sol = model.run(
        FrequencyResponse2(
            np.geomspace(0.1, 1000),
            [(model.SQZ.p1.o, model.fsig.f.ref), (model.SQZ.p1.o, -model.fsig.f.ref)],
            [model.PD.DC.o],
        )
    )
    upper = sol.out[:, 0, 0, 0]
    lower_conj = sol.out[:, 0, 1, 0]
    _assert_sqz_response_phase(u2u=upper, l2l=lower_conj)


def test_sqz_sideband_frequency_response_3_phase(squeezer):
    model = squeezer
    f_u = +model.fsig.f.ref
    f_l = -model.fsig.f.ref

    sol = model.run(
        FrequencyResponse3(
            np.geomspace(0.1, 1000, 10),
            [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
            [(model.PD.p1.i, f_u), (model.PD.p1.i, f_l)],
        )
    )
    u2u = sol.out[:, 0, 0, 0, 0]
    u2l = sol.out[:, 1, 0, 0, 0]
    l2u = sol.out[:, 0, 1, 0, 0]
    l2l = sol.out[:, 1, 1, 0, 0]
    _assert_sqz_response_phase(u2u=u2u, u2l=u2l, l2u=l2u, l2l=l2l)


def test_sqz_sideband_frequency_response_4_phase(squeezer):
    model = squeezer
    fsig = model.fsig.f.ref

    sol = model.run(
        FrequencyResponse4(
            np.geomspace(0.1, 1000, 10),
            [model.SQZ.upper, model.SQZ.lower_conj],
            [
                (model.BS.p1.i, +fsig),
                (model.BS.p1.i, -fsig),
            ],
        )
    )
    u2u = sol.out[:, 0, 0, 0]
    u2l = sol.out[:, 1, 0, 0]
    l2u = sol.out[:, 0, 1, 0]
    l2l = sol.out[:, 1, 1, 0]
    _assert_sqz_response_phase(u2u=u2u, u2l=u2l, l2u=l2u, l2l=l2l)


@pytest.mark.parametrize("f", [1, "fsig.f"])
def test_frequency_response2_exception(f, squeezer):
    model = squeezer
    if isinstance(f, str):
        f_u = "+" + f
        f_l = "-" + f
    else:
        f_u = +f
        f_l = -f

    action = FrequencyResponse2(
        np.geomspace(0.1, 1000, 1),
        [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
        ["PD.DC"],
    )

    with pytest.raises(finesse.exceptions.FinesseException):
        model.run(action)


@pytest.mark.parametrize("f", [1, "fsig.f"])
def test_frequency_response3_exception(f, squeezer):
    model = squeezer
    if isinstance(f, str):
        f_u = "+" + f
        f_l = "-" + f
    else:
        f_u = +f
        f_l = -f

    action = FrequencyResponse3(
        np.geomspace(0.1, 1000, 1),
        [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
        [(model.PD.p1.i, f_u), (model.PD.p1.i, f_l)],
    )

    with pytest.raises(finesse.exceptions.FinesseException):
        model.run(action)


@pytest.mark.parametrize("f", [1, "fsig.f"])
def test_frequency_response4_exception(f, squeezer):
    model = squeezer
    if isinstance(f, str):
        f_u = "+" + f
        f_l = "-" + f
    else:
        f_u = +f
        f_l = -f

    action = FrequencyResponse4(
        np.geomspace(0.1, 1000, 1),
        [model.SQZ.upper, model.SQZ.lower_conj],
        [(model.PD.p1.i, f_u), (model.PD.p1.i, f_l)],
    )

    with pytest.raises(finesse.exceptions.FinesseException):
        model.run(action)


def test_frequency_response3_diff_inp_out():
    model = Model()
    model.add(fc.Mirror("ETM", T=0, L=0))
    model.add(fc.Mirror("ITM", T=0.014, L=0))
    model.connect(model.ITM.p1, model.ETM.p1, L=4e3)
    model.fsig.f = 1
    F_Hz = np.geomspace(1, 5e3, 10)
    fsig = model.fsig.f.ref
    model.run(
        fa.FrequencyResponse3(
            F_Hz,
            [
                (model.ITM.p2.i, +fsig),
                (model.ITM.p2.i, -fsig),
                (model.ETM.p1.o, +fsig),
                (model.ETM.p1.o, -fsig),
            ],
            [
                (model.ITM.p2.o, +fsig),
                (model.ITM.p2.o, -fsig),
            ],
        )
    )


@pytest.mark.parametrize("F_Hz", [[1], [1, 2], [1, 2, 3]])
def test_output_shape(F_Hz):
    F_Hz = np.asarray(F_Hz)
    from finesse import Model
    import finesse.analysis.actions as act
    from finesse.components import Squeezer, Mirror, Cavity, ReadoutDC

    model = Model()
    model.add(Squeezer("SQZ", db=10, angle=0))
    model.add(Mirror("ITM", T=0.014, L=0, Rc=1935))
    model.add(Mirror("ETM", T=0, L=0, Rc=2245))
    model.connect(model.ITM.p1, model.ETM.p1, 4e3)
    model.connect(model.SQZ.p1, model.ITM.p2)
    model.add(Cavity("cavARM", model.ETM.p1.o))
    model.add(ReadoutDC("REFL", model.ETM.p1.o, output_detectors=True))
    model.modes(maxtem=2)
    model.fsig.f = 1

    def run_fresp_actions(F_Hz):
        fsig = model.fsig.f.ref
        sol = model.run(
            act.Series(
                act.FrequencyResponse(
                    F_Hz,
                    ["SQZ.upper", "SQZ.lower_conj"],
                    ["REFL.DC.o"],
                    name="fresp1",
                ),
                act.FrequencyResponse2(
                    F_Hz,
                    [
                        ("SQZ.p1", +fsig),
                        ("SQZ.p1", -fsig),
                    ],
                    ["REFL.DC.o"],
                    name="fresp2",
                ),
                act.FrequencyResponse3(
                    F_Hz,
                    [
                        ("SQZ.p1.o", +fsig),
                        ("SQZ.p1.o", -fsig),
                    ],
                    [
                        ("ETM.p1.i", +fsig),
                        ("ETM.p1.i", -fsig),
                    ],
                    name="fresp3",
                ),
                act.FrequencyResponse4(
                    F_Hz,
                    ["ETM.mech.z"],
                    [
                        ("ITM.p2.o", +fsig),
                        ("ITM.p2.o", -fsig),
                    ],
                    name="fresp4",
                ),
            )
        )
        return sol

    sol = run_fresp_actions(F_Hz)
    assert sol["fresp1"].out.shape == (F_Hz.size, 1, 2)  # outputs, inputs
    assert sol["fresp2"].out.shape == (F_Hz.size, 1, 2, 6)  # outputs, inputs, homs
    assert sol["fresp3"].out.shape == (
        F_Hz.size,
        2,
        2,
        6,
        6,
    )  # outputs, inputs, homs, homs
    assert sol["fresp4"].out.shape == (F_Hz.size, 2, 1, 6)  # outputs, inputs, homs


def test_FrequencyResponseSolution_getattr_inverse():
    """Tests if [inputs, outputs] also works until it's deprecated."""
    from finesse.analysis.actions.lti import FrequencyResponseSolution

    t = FrequencyResponseSolution("name")
    t.inputs = ("A", "B", "C")
    t.outputs = ("D", "E", "F", "G")
    t.out = np.random.rand(3, len(t.outputs), len(t.inputs))

    with pytest.warns(DeprecationWarning):
        assert np.all(t[("F", "G"), ("C", "A")] == t[("C", "A"), ("F", "G")])


def test_FrequencyResponseSolution_getattr():
    from finesse.analysis.actions.lti import FrequencyResponseSolution

    t = FrequencyResponseSolution("name")
    t.inputs = ("A", "B", "C")
    t.outputs = ("D", "E", "F", "G")
    t.out = np.random.rand(3, len(t.outputs), len(t.inputs))

    assert t["name"] is t, "Didn't return the solution itself"

    with pytest.raises(KeyError):
        _ = t[1]

    with pytest.raises(KeyError):
        _ = t["1"]

    with pytest.raises(KeyError):
        _ = t[b"1"]

    with pytest.raises(KeyError):
        _ = t[1, 2, 3]

    with pytest.raises(KeyError):
        _ = t[:]

    assert np.all(t["D", "A"] == t.out[:, 0, 0])
    assert np.all(t["D", "C"] == t.out[:, 0, 2])
    assert np.all(t["F", "C"] == t.out[:, 2, 2])
    assert np.all(t["F", ("C", "A")] == t.out[:, 2, [2, 0]])
    assert np.all(t[("F", "G"), ("C", "A")] == t.out[:, [2, 3], [2, 0]])
    assert np.all(t["D", :] == t.out[:, 0, :])
    assert np.all(t["D", ::2] == t.out[:, 0, ::2])
    assert np.all(t["D", 1:] == t.out[:, 0, 1:])
    assert np.all(t[:, "B"] == t.out[:, :, 1])
    assert np.all(t[::2, "B"] == t.out[:, ::2, 1])
    assert np.all(t[1:, "B"] == t.out[:, 1:, 1])
    assert np.all(t[:, :] == t.out)

    with pytest.raises(KeyError):
        _ = t["Z", :]
    with pytest.raises(KeyError):
        _ = t[:, "Z"]
    with pytest.raises(KeyError):
        _ = t["D", "Z"]  # non existent input
    with pytest.raises(KeyError):
        _ = t["Z", "A"]  # non existent output


@pytest.fixture
def model():
    model = Model()
    model.add(fc.Laser("L", P=10))
    model.add(fc.ReadoutDC("PD"))
    model.link("L", "PD")
    model.fsig.f = 1
    return model


def test_frequency_response2_laser_pd(model):
    F_Hz = [10]
    fsig = model.fsig.f.ref
    DC = model.run("dc_fields()")
    sol2 = model.run(
        fa.FrequencyResponse2(
            F_Hz,
            [
                (model.L.p1.o, +fsig),
                (model.L.p1.o, -fsig),
            ],
            [
                model.PD.DC.o,
            ],
        )
    )

    Ec = DC["PD.p1.i"].squeeze()

    assert np.allclose(  # Half a carrier modulation in each sideband
        sol2.out.squeeze() @ (np.array([0.25, 0.25]) * Ec), 10
    )
    # Single sideband modulation
    assert np.allclose(sol2.out.squeeze() @ (np.array([0.5, 0]) * Ec), 10, atol=1e-14)
    assert np.allclose(sol2.out.squeeze() @ (np.array([0, 0.5]) * Ec), 10, atol=1e-14)


def test_frequency_response_laser_pd_product(model):
    F_Hz = [10]
    fsig = model.fsig.f.ref
    sol1 = model.run(
        fa.FrequencyResponse(
            F_Hz,
            [
                model.L.amp,
            ],
            [
                model.PD.DC.o,
            ],
        )
    )

    sol2 = model.run(
        fa.FrequencyResponse2(
            F_Hz,
            [
                (model.L.p1.o, +fsig),
                (model.L.p1.o, -fsig),
            ],
            [
                model.PD.DC.o,
            ],
        )
    )

    sol4 = model.run(
        fa.FrequencyResponse4(
            F_Hz,
            [
                model.L.amp,
            ],
            [
                (model.L.p1.o, +fsig),
                (model.L.p1.o, -fsig),
            ],
        )
    )
    # Should be the equivalent
    assert np.allclose(
        sol4.out.squeeze() @ sol2.out.squeeze(), sol1.out.squeeze(), atol=1e-14
    )


@pytest.mark.parametrize("type", ["amp", "phs", "pwr", "frq"])
def test_laser_siggen_equals_frequency_response_2(type):
    model = finesse.script.parse(
        f"""
        fsig(1)
        l l1 P=1
        readout_dc PD
        link(l1, PD)
        ad up l1.p1.o +fsig
        ad lo l1.p1.o -fsig
        sgen sg l1.{type}.i amplitude=1 phase=0
        """
    )
    out = model.run()
    sol = model.run(
        f"frequency_response4([1], [l1.{type}.i], [[l1.p1.o, +fsig], [l1.p1.o, -fsig]])"
    )
    H = sol.out.squeeze()
    assert np.allclose(H[0], out["up"], atol=1e-14)
    assert np.allclose(H[1].conj(), out["lo"], atol=1e-14)


def test_frequency_response_equals_sgen():
    f_min = 1e3
    f_max = 1e8
    steps = 100
    F = np.logspace(np.log10(f_min), np.log10(f_max), steps + 1)
    base_model = finesse.Model()
    base_model.parse(
        """
    l l1 P=1

    s sp1 l1.p1 eom.p1 L=0
    mod eom 15M 0.7 order=1
    s sp2 eom.p2 m1.p1 L=0

    m m1 R=0.9 L=0
    s cav m1.p2 m2.p1 L=1
    m m2 R=0.9 L=0
    """
    )
    readout_model = base_model.deepcopy()
    readout_model.parse(
        """
    readout_rf readout m1.p1.o f=eom.f phase=0
    fsig(1)
    """
    )
    readout_sol = readout_model.run(
        FrequencyResponse(
            F,
            inputs=[readout_model.m2.mech.z],
            outputs=[readout_model.readout.I],
        )
    )
    readout_tf = readout_sol["frequency_response"]["readout.I", "m2.mech.z"]

    pd2_model = base_model.deepcopy()
    pd2_model.parse(
        """
        fsig(1)
        sgen pzt m2.mech.z
        pd2 pd2 m1.p1.o eom.f 0 fsig.f
        """
    )
    pd2_sol = pd2_model.run(Xaxis(pd2_model.fsig.f, "log", f_min, f_max, steps))
    np.testing.assert_allclose(pd2_sol["pd2"], readout_tf)
