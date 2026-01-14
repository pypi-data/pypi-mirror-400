"""Tests for making sure that order in KatScript doesn't matter."""

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import permutations
from finesse.script import parse
from testutils.diff import assert_models_equivalent
from testutils.fuzzing import DEADLINE


# A script with a `cav` command which normally has to be built last.
CAV_SCRIPT = """
l L0 P=1
s s0 L0.p1 EOM1.p1
mod EOM1 f=100M midx=0.1 order=1 mod_type=pm
s s1 EOM1.p2 ITM.p1 L=1
m ITM R=0.99 T=0.01 Rc=-0.9
s sCAV ITM.p2 ETM.p1 L=1
m ETM R=0.99 T=0.01 phi=123 Rc=0.9
pd1 REFL_I ITM.p1.o 100M 0
cav FP ITM.p2.o
"""


def test_space_instruction_order_doesnt_matter():
    """Test that the order in which a space is defined in kat script does not matter."""
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1
        s CAV ITM.p2 ETM.p1 L=1  # Defined before the ITM and ETM components.
        m ITM R=0.99 T=0.01 Rc=-10
        m ETM R=0.99 T=0.01 Rc=10
        modes(even, 4)
        """
    )


def test_cavity_property_detector():
    """Cavity property detector should parse after cavity.

    The cavity property detector takes a cavity as a parameter, but cavities are
    `build_last` components so get built after everything that isn't. Cavity property
    detectors therefore have to be built after cavities.
    """
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1
        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2
        cav FP ITM.p2
        cp gx FP g x
        modes(maxtem=2)
        xaxis(ITM.phi, lin, 0, 180, 100)
        """
    )


def test_gouy_detector():
    """Gouy detector should parse in the second build step.

    The gouy detector has implicit dependencies like `cavity`, in that it requires for
    there to exist a path between its start and end nodes by the time it itself gets
    built. It therefore is set to `build_last` in the :class:`.KatSpec`. This test
    checks that the gouy detector still parses correctly.
    """
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1
        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2
        cav FP ITM.p2
        gouy gFP from_node=ITM.p2 to_node=ETM.p1
        modes(maxtem=2)
        xaxis(ITM.phi, lin, 0, 180, 100)
        """
    )


@pytest.fixture(scope="package")
def reference_model():
    """The parsed model without any re-ordering."""
    return parse(CAV_SCRIPT)


@given(scriptlines=permutations(CAV_SCRIPT.splitlines()))
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_script_order_doesnt_matter(scriptlines, reference_model):
    """Test that script order does not matter.

    This test works by randomly reordering the lines of the reference script, then
    parsing and comparing the model to the reference model.
    """
    model = parse("\n".join(scriptlines))
    assert_models_equivalent(reference_model, model)
