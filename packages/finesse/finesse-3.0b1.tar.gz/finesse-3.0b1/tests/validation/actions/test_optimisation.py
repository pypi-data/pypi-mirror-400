import numpy as np
import pytest

import finesse
from finesse.analysis.actions import Maximize
from finesse.analysis.actions.optimisation import OptimizationWarning


def test_minimize_basic():
    # Test basic minimisation that uses nelder-mead arguments
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    pd P l1.p1.o
    minimize(P, l1.P)
    """
    )
    sol = model.run()
    assert sol.x < 1e-2


def test_minimize_basic_nelder_mead():
    # Test basic minimisation that uses nelder-mead arguments
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    pd P l1.p1.o
    minimize(P, l1.P, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    assert sol.x < 1e-6


@pytest.fixture
def converge_first_value():
    model = finesse.Model()
    model.parse(
        """
        laser l1 P=1
        link(l1, ITM)
        m ITM
        link(ITM, ETM)
        m ETM
        pd circ ITM.p2.o
    """
    )
    action = Maximize(model.circ, model.ETM.phi, verbose=True)
    return model, action


# https://gitlab.com/ifosim/finesse/finesse3/-/issues/635
def test_maximize_converge_first_value(converge_first_value):
    model, action = converge_first_value
    assert model.ETM.phi.value == 0
    sol = model.run(action)
    assert sol.x[0] == 0
    assert model.ETM.phi.value == 0


def test_single_iteration_warning(converge_first_value):
    model, action = converge_first_value
    model.ETM.phi.value = 1e-3
    with pytest.warns(OptimizationWarning):
        model.run(action)


def test_minimize_RF_readout_phase():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    mod mod1 f=10M midx=0.1 mod_type=am
    link(l1, mod1)
    pd1 RF mod1.p2.o 10M 0
    minimize(RF, RF.phase, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    # Max solution should be at 90 phase
    assert np.allclose(sol.x, 90, atol=1e-6)


def test_maximize_RF_readout_phase():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    mod mod1 f=10M midx=0.1 mod_type=am
    link(l1, mod1)
    pd1 RF mod1.p2.o 10M 0
    maximize(RF, RF.phase, xatol=1e-6, adaptive=True)
    """
    )
    sol = model.run()
    # Max solution should be at 0 phase
    assert np.allclose(sol.x, 0, atol=1e-6)


def test_maximize_multiple_targets():
    """Coupled cavity optimize."""
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 R=0.98 T=0.02 phi=10
    m m2 R=0.99 T=0.01
    m m3 R=1 T=0 phi=-20
    link(l1, m1, m2, m3)
    pd P m3.p1.i

    maximize(P, [m1.phi, m3.phi], xatol=1e-7, adaptive=True)
    """
    )
    sol = model.run()
    assert np.allclose(sol.x, [90, 0], atol=1e-6)


def test_bounds():
    model = finesse.Model()
    model.parse(
        """
    l l1
    l l2
    bs BS R=0.5 T=0.5
    link(l1, BS.p1)
    link(l2, BS.p4)
    pd P BS.p2.o
    """
    )

    sol = model.run(
        """
    series(
        maximize(P, [l1.P, l2.P, l1.phase], bounds=[[0,4], [0, 4], [-180, 180]]),
        noxaxis()
    )
    """
    )

    assert abs(sol["noxaxis"]["P"] - 8) < 1e-6


def test_optimise_squeezing_modematch():
    kat = finesse.script.parse(
        """
        l l1 P=1e14
        s s1 l1.p1 bs1.p4

        #squeezed source
        sq sq1 db=20
        s s2 sq1.p1 dbs1.p1

        #first filter cavity
        dbs dbs1
        s s21 dbs1.p3 ITM.p1
        m ITM R=0.99 T=0.01 Rc=-2.5
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0.0 Rc=2.5

        #----------------------------------------
        # Mode matching telescope
        #----------------------------------------
        s st1 dbs1.p4 lens1.p1 L=1
        lens lens1 f=1
        s st2 lens1.p2 lens2.p1 L=1
        lens lens2 f=1
        s st3 lens2.p2 dbsf.p1 L=1
        #----------------------------------------

        #second filter cavity
        dbs dbsf
        s s21f dbsf.p3 ITMf.p1
        m ITMf R=0.99 L=0 Rc=-2.5
        s sCAVf ITMf.p2 ETMf.p1 L=1
        m ETMf R=1 T=0.0 Rc=2.5
        s s4f dbsf.p4 bs1.p1

        #homodyne
        bs bs1 T=1e-14 L=0 alpha=45 phi=-4.5

        #cavities
        cav FP ITM.p2.o priority=0
        cav FP2 ITMf.p2.o priority=1

        fsig(1)

        qnoised sqzd_noise bs1.p2.o

        modes(maxtem=4)
        """
    )
    sol0 = kat.run()
    opt = kat.run("minimize(sqzd_noise, [lens1.f, lens2.f])")
    kat.run("minimize(sqzd_noise, l1.phase)")
    sol1 = kat.run()
    assert opt.x[0] != 1
    assert opt.x[1] != 1
    assert sol1["sqzd_noise"] < sol0["sqzd_noise"]
    assert kat.cavity_mismatch("FP", "FP2")[0] < 1e-5
    assert kat.cavity_mismatch("FP", "FP2")[1] < 1e-5
