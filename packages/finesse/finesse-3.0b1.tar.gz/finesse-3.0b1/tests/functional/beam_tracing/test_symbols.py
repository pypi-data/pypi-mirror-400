import finesse
import pytest
from finesse.detectors import KnmDetector
import finesse.warnings


@pytest.fixture()
def model_cavity():
    IFO = finesse.Model()
    IFO.parse(
        """
        l L0 P=3
        s s0 L0.p1 ITM.p1
        m ITM T=7m L=37.5u Rc=-5580
        s LY ITM.p2 ETM.p1 L=10k
        m ETM T=6u L=37.5u Rc=5580
        var dummy 6000
        cav ARM ITM.p2
        """
    )
    return IFO.deepcopy()


@pytest.mark.parametrize("mirror", ("ETM", "ITM"))
@pytest.mark.parametrize("direction", ("x", "y"))
@pytest.mark.parametrize("node1", (1, 2))
@pytest.mark.parametrize("node2", (1, 2))
@pytest.mark.parametrize("dummy", (True, False))
def test_ABCDs_xaxis_reset(model_cavity, mirror, direction, node1, node2, dummy):
    if dummy:
        # use dummy variable to scan RoCs instead
        model_cavity.ETM.Rcx = model_cavity.dummy.ref
        model_cavity.parse("xaxis(dummy, lin, 6000, 9000, 1)")
    else:
        model_cavity.parse("xaxis(ETM.Rcx, lin, 6000, 9000, 1)")

    model_cavity.ETM.Rcy = model_cavity.ETM.Rcx.ref
    model_cavity.ITM.Rcx = -1 * model_cavity.ETM.Rcx.ref
    model_cavity.ITM.Rcy = -1 * model_cavity.ETM.Rcx.ref

    m1 = model_cavity.elements[mirror].ABCD(node1, node2, direction=direction).copy()
    model_cavity.run()
    m2 = model_cavity.elements[mirror].ABCD(node1, node2, direction=direction).copy()
    assert (m1 == m2).all()


def test_cvalues_update_abcd(model_cavity):
    IFO = model_cavity
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref
    IFO.ITM.Rcx = -1 * IFO.ETM.Rcx.ref
    IFO.ITM.Rcy = -1 * IFO.ETM.Rcx.ref
    IFO.parse("xaxis(ETM.Rcx, lin, 5580, 9000, 1)")
    IFO.add_matched_gauss(IFO.L0.p1.o, "gL0")
    IFO.add(KnmDetector("k00", IFO.ITM, "11", 0, 0, 0, 0))

    out1 = IFO.run()
    out2 = IFO.run()
    assert (out1["k00"] == out2["k00"]).all()


def test_cvalues_update_abcd_dummy_var(model_cavity):
    IFO = model_cavity
    IFO.ETM.Rcx = IFO.dummy.ref
    IFO.ETM.Rcy = IFO.dummy.ref
    IFO.ITM.Rcx = -1 * IFO.dummy.ref
    IFO.ITM.Rcy = -1 * IFO.dummy.ref
    IFO.parse("xaxis(dummy, lin, 5580, 9000, 1)")
    IFO.add_matched_gauss(IFO.L0.p1.o, "gL0")
    IFO.add(KnmDetector("k00", IFO.ITM, "11", 0, 0, 0, 0))

    out1 = IFO.run()
    out2 = IFO.run()
    assert (out1["k00"] == out2["k00"]).all()


def test_symbolic_cavity_geometry():
    # https://gitlab.com/ifosim/finesse/finesse3/-/issues/573
    import finesse
    import finesse.components as fc
    import finesse.element
    import numpy as np
    from finesse.exceptions import BeamTraceException
    import pytest
    import warnings

    model = finesse.Model()
    # Doesn't like inf values
    model.add_parameter("R", np.inf)
    model.modes("even", maxtem=0)
    LASER = model.add(fc.Laser("LASER", P=125 * 50))
    ITM = model.add(fc.Mirror("ITM", T=0.015, L=0, Rc=2 / (2 / 1935 + 2 / model.R.ref)))
    ETM = model.add(fc.Mirror("ETM", T=0, L=100e-6, Rc=2245))
    model.link(LASER.p1, ITM.p2, ITM.p1, 4000, ETM.p1)
    model.add(fc.Cavity("ARM", ITM.p1.o))
    with warnings.catch_warnings():
        # Cause all warnings to always be triggered.
        warnings.simplefilter("error", finesse.warnings.CavityUnstableWarning)
        # This should run and not raise an error
        try:
            model.run()
        except BeamTraceException:
            pytest.fail("Raises BeamTraceException, but should not.")
        except Exception as e:
            raise e

        try:
            model.run("xaxis(R, lin, 1e6, 2e6, 1)")
        except BeamTraceException:
            pytest.fail("Raises BeamTraceException, but should not.")
        except Exception as e:
            raise e


def test_symbolic_cavity_geometry_lens():
    # https://gitlab.com/ifosim/finesse/finesse3/-/issues/573

    import finesse.element
    import warnings

    with warnings.catch_warnings():
        # Cause all warnings to always be triggered.
        warnings.simplefilter("error", finesse.warnings.CavityUnstableWarning)
        model = finesse.script.parse(
            """
        var A 1e-15
        l L
        m m1 Rc=1000
        lens l1 f=1/A
        m m2 Rc=1000
        link(L, m1.p2, m1.p1, 300, l1, 300, m2.p1)
        cav CAV m2.p1.o
        """
        )

        model.A.is_tunable = True
        model.run()
