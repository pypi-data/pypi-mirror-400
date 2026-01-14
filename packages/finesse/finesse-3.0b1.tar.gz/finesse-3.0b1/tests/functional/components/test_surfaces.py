"""Surface tests.

This tests the common parts shared by beamsplitter and mirrors in :class:`.Surface`.
"""

import numpy as np
import pytest
from hypothesis import given, settings, HealthCheck

from finesse.analysis.actions import Xaxis
from finesse.components import Beamsplitter, Mirror
from finesse.symbols import Symbol
from finesse import Model
from finesse.script.compiler import KatParameterBuildError
from finesse.exceptions import InvalidRTLError


from testutils.data import RADII_OF_CURVATURES, RADII_OF_CURVATURE_PAIRS, RTL_SETS
from testutils.fuzzing import DEADLINE, rtl_sets, rtl_sets_two_vals

surfaces = pytest.mark.parametrize("surface", (Beamsplitter, Mirror))


@pytest.mark.parametrize("R,T,L", RTL_SETS)
@surfaces
def test_rtl(surface, R, T, L):
    """Test that a surface's R, T and L are correctly set by the constructor."""
    obj = surface("cmp1", R=R, T=T, L=L)
    assert float(obj.R) == R
    assert float(obj.T) == T
    assert float(obj.L) == L


@given(RTL=rtl_sets())
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
@surfaces
def test_rtl_fuzzing(surface, RTL):
    """Test that a surface's R, T and L are correctly set by the constructor."""
    R, T, L = RTL
    obj = surface("cmp1", R=R, T=T, L=L)
    assert float(obj.R) == R
    assert float(obj.T) == T
    assert float(obj.L) == L


@pytest.mark.parametrize("R,T,L", RTL_SETS)
@surfaces
def test_rtl__two_from_three(surface, R, T, L):
    """Test that a surface's constructor correctly forces R+T+L = 1 from provided
    pairs."""

    def _do_two_from_three_test(specified_params, other_param_name):
        obj = surface("cmp1", **specified_params)
        value = float(getattr(obj, other_param_name))
        assert value == pytest.approx(rtl_data[other_param_name])

    rtl_data = dict(R=R, T=T, L=L)
    keys = list(rtl_data)

    data1 = dict(rtl_data)
    del data1[keys[0]]
    _do_two_from_three_test(data1, keys[0])

    data1 = dict(rtl_data)
    del data1[keys[1]]
    _do_two_from_three_test(data1, keys[1])

    data1 = dict(rtl_data)
    del data1[keys[2]]
    _do_two_from_three_test(data1, keys[2])


@pytest.mark.parametrize(
    "R,T,L", ((-1, 0.5, 0.5), (0.5, -0.5, 1), (0.5, 0.7, -0.2), (-1, -1, -1))
)
@surfaces
def test_rtl__negative_invalid(surface, R, T, L):
    """Test that a surface's R, T and L cannot be negative."""
    with pytest.raises(InvalidRTLError):
        surface("cmp1", R=R, T=T, L=L)


@given(ab=rtl_sets_two_vals())
@surfaces
@pytest.mark.parametrize("symbolic_par", ("R", "T", "L"))
def test_rtl_third_parameter_symbolic(surface, ab, symbolic_par):
    a, b = ab
    float_pars = ["R", "T", "L"]
    float_pars.remove(symbolic_par)
    kwargs = {float_pars[0]: a, float_pars[1]: b}
    surf = surface("cmp1", **kwargs)
    par = getattr(surf, symbolic_par).value
    assert isinstance(par, Symbol)
    np.testing.assert_allclose(par.eval(), 1.0 - a - b, atol=1e-3, rtol=1e-3)


@surfaces
def test_rtl_exceeds_RTL_sum(surface):
    model = Model()
    n = surface.__name__
    with pytest.raises(KatParameterBuildError):
        model.parse(f"{n} cmp1 R=(1-cmp1.T) T=0.1 L=0.5")


@surfaces
def test_rtl_update_symbolic_outside01range(surface):
    model = Model()
    n = surface.__name__
    model.parse(f"{n} cmp1 R=0.3 L=0.5")
    with pytest.raises(InvalidRTLError):
        model.cmp1.R = 0.8


@surfaces
def test_rtl_self_reference(surface):
    model = Model()
    n = surface.__name__
    model.parse(f"{n} cmp1 R=1-cmp1.L L=0.5")
    np.testing.assert_allclose(model.cmp1.R.eval(), 0.5)
    np.testing.assert_allclose(model.cmp1.T.eval(), 0.0)
    np.testing.assert_allclose(model.cmp1.L.eval(), 0.5)


@surfaces
def test_rtl_self_reference_exceeds_01(surface):
    model = Model()
    n = surface.__name__
    with pytest.raises(KatParameterBuildError):
        model.parse(f"{n} cmp1 R=2-cmp1.L L=0.5")


@surfaces
def test_rtl_sum_check_during_sweep(surface):
    model = Model()
    n = surface.__name__
    model.parse(f"{n} cmp1 R=0.5 T=0.5 L=0")
    with pytest.raises(InvalidRTLError):
        model.run(Xaxis(model.cmp1.T, "lin", 0, 1, 2))


@surfaces
def test_rtl_check_during_sweep(surface):
    model = Model()
    n = surface.__name__
    model.parse(f"{n} cmp1 R=0.5 T=0.5 L=0")
    with pytest.raises(InvalidRTLError):
        model.run(Xaxis(model.cmp1.T, "lin", -1, -2, 2))


@surfaces
def test_rtl_self_reference_exceeds_rtlsum(surface):
    model = Model()
    n = surface.__name__
    with pytest.raises(KatParameterBuildError):
        model.parse(f"{n} cmp1 R=0.3+cmp1.L L=0.8")


@pytest.mark.parametrize("Rc", (0, 0.0))
@surfaces
def test_rc__invalid(surface, Rc):
    """Test that a surface's radius of curvature cannot be 0."""
    with pytest.raises(InvalidRTLError):
        surface(name="cmp1", Rc=Rc)


@pytest.mark.parametrize("Rc", RADII_OF_CURVATURES)
@surfaces
def test_rc_sets_rcx_and_rcy__single(surface, Rc):
    """Test that setting a surface's Rc sets Rcx and Rcy to the same value."""
    obj = surface(name="cmp1")
    obj.Rc = Rc
    Rcx, Rcy = obj.Rc
    assert float(Rcx) == float(Rcy) == pytest.approx(Rc)


@pytest.mark.parametrize("Rc", RADII_OF_CURVATURE_PAIRS)
@surfaces
def test_rc_sets_rcx_and_rcy__separate(surface, Rc):
    """Test that setting a surface's Rc to a two-valued sequence sets Rcx and Rcy to
    those respective values."""
    obj = surface(name="cmp1")
    obj.Rc = Rc
    assert float(obj.Rc[0]) == pytest.approx(Rc[0])
    assert float(obj.Rc[1]) == pytest.approx(Rc[1])
