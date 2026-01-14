import pytest
import numpy as np
from testutils.data import NONE, BOOLEANS, STRINGS, INTEGERS, FLOATS, IMAGINARIES


# Override default element to take one argument.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


@pytest.mark.parametrize(
    "_,expected,arg", NONE + BOOLEANS + STRINGS + INTEGERS + FLOATS + IMAGINARIES
)
def test_terminal_value(
    unbuilder, model, element_dump, fake_element_cls, _, expected, arg
):
    """Values like ints, floats, strings; those without additional dependencies."""
    model.add(fake_element_cls("myel", a=arg))
    dump = next(iter(element_dump("fake_element", fake_element_cls, model)))
    script = unbuilder.unbuild(dump)
    assert script == f"fake_element myel a={expected}"


def test_nan(unbuilder, model, element_dump, fake_element_cls):
    """A not-a-number value that yields a __FIXME__ KatScript value."""
    model.add(fake_element_cls("myel", a=np.nan))
    dump = next(iter(element_dump("fake_element", fake_element_cls, model)))

    with pytest.warns(
        UserWarning, match="The generated script contains invalid values"
    ):
        script = unbuilder.unbuild(dump)

    assert script == "fake_element myel a=__FIXME__"
