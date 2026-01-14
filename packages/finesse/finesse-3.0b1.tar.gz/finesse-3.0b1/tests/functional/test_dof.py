# %%
import finesse
from finesse.analysis.actions import FrequencyResponse, For
from finesse.components import LocalDegreeOfFreedom, DegreeOfFreedom
import numpy as np
import pytest


def test_symbolic_dof_power():
    model = finesse.script.parse(
        """
    var Y 1
    l l1
    readout_dc PD
    link(l1, PD)
    dof INT l1.dofs.pwr Y
    fsig(1)
    """
    )

    values = [1, 2, 3, 4, 5]
    out = model.run(
        For(
            model.Y,
            values,
            FrequencyResponse([1], [model.INT.AC.i], [model.PD.DC.o]),
        )
    )

    result = [complex(sol.out.squeeze()) for sol in out.children]
    assert np.allclose(values, result)


def test_ldof_network_edges():
    model = finesse.script.parse(
        """
    var Y 1
    l l1
    readout_dc PD
    link(l1, PD)
    dof INT l1.dofs.amp Y
    fsig(1)
    """
    )
    DOF = model.INT
    AC_IN = model.l1.dofs.amp.AC_IN.full_name
    AC_OUT = model.l1.dofs.amp.AC_OUT.full_name

    assert (AC_OUT, DOF.AC.o.full_name) in model.network.out_edges(AC_OUT)
    assert (DOF.AC.i.full_name, AC_IN) in model.network.in_edges(AC_IN)


@pytest.mark.parametrize("IN", [None, "l1.amp.i"])
@pytest.mark.parametrize("OUT", ["l1.amp.i", None])
def test_custom_local_dof(IN, OUT):
    model = finesse.script.parse(
        """
    l l1
    readout_dc PD
    link(l1, PD)
    fsig(1)
    """
    )
    l1 = model.l1
    ldof = LocalDegreeOfFreedom(
        "ldof",
        l1.P,
        None if IN is None else model.get(IN),
        None,
        None if OUT is None else model.get(OUT),
    )

    DOF = model.add(DegreeOfFreedom("DOF", ldof, 1))

    if IN is not None:
        AC_IN = ldof.AC_IN.full_name
        assert (DOF.AC.i.full_name, AC_IN) in model.network.in_edges(AC_IN)
        sol = model.run(
            FrequencyResponse([1], IN, [DOF.AC.i]),
        )
        assert np.all(sol.out == 0)

    if OUT is not None:
        AC_OUT = ldof.AC_OUT.full_name
        assert (AC_OUT, DOF.AC.o.full_name) in model.network.out_edges(AC_OUT)
        sol = model.run(
            FrequencyResponse([1], OUT, [OUT, DOF.AC.o]),
        )
        assert np.all(sol.out == 1)


def test_external_set():
    model = finesse.script.parse(
        """
        var Y 1
        l l1
        readout_dc PD
        link(l1, PD)
        dof INT l1.dofs.amp Y
        fsig(1)
        """
    )

    assert model.l1.P == 1 + model.Y.ref * model.INT.DC.ref


def test_external_set_error():
    from finesse.exceptions import ExternallyControlledException

    model = finesse.script.parse(
        """
        var Y 1
        l l1
        readout_dc PD
        link(l1, PD)
        dof INT l1.dofs.pwr Y
        fsig(1)
        """
    )
    with pytest.raises(ExternallyControlledException):
        model.run("xaxis(l1.P, lin, 0, 1, 1)")


@pytest.mark.parametrize("enabled", (True, False))
def test_dc_enabled(enabled):
    model = finesse.Model()

    model.parse(
        """
    m m1
    dof dof_m m1.xbeta +1
    """
    )
    if enabled:
        assert model.dof_m.dc_enabled
    else:
        model.dof_m.drives[0].DC = None
        assert model.dof_m.dc_enabled is False


# https://gitlab.com/ifosim/finesse/finesse3/-/issues/691
def test_angular_dofs():
    model = finesse.Model()
    model.parse(
        """
    l l1
    m m1 Rc=-0.55
    s scav m1.p2 m2.p1 L=1
    m m2 Rc=0.55
    link(l1, m1.p1)

    cav cav1 m1.p2

    ad ad_00 m2.p1.o f=0 n=0 m=0
    ad ad_10 m2.p1.o f=0 n=1 m=0

    modes(maxtem=1)
    """
    )

    model2 = model.deepcopy()
    model2.m2.xbeta = 1e-9
    out2 = model2.run()

    model3 = model.deepcopy()
    model3.parse("dof dof_yaw m2.dofs.yaw +1")
    model3.dof_yaw.DC = 1e-9
    out3 = model3.run()

    np.testing.assert_allclose(out2["ad_10"], out3["ad_10"])
    assert np.abs(out2["ad_10"]) > 1e-6
