import pytest
from finesse.script.spec import KATSPEC, KatSpec, make_element
from finesse.components import Mirror


@pytest.mark.parametrize("directive", KATSPEC.directives.keys())
def test_directives_in_reference(directive, DIRECTIVES_REFERENCE):
    assert directive in DIRECTIVES_REFERENCE


def test_reference_directives_present(DIRECTIVES_REFERENCE):
    assert DIRECTIVES_REFERENCE == set(KATSPEC.directives.keys())


def test_python_class_name_present_in_spec():
    class Spec(KatSpec):
        def _register_constructs(self):
            self.register_element(make_element(int, "integer"))

    spec = Spec()
    assert "int" in spec.directives
    assert "integer" in spec.directives


def test_get_element_class():
    assert KATSPEC.get_element_class("Mirror") is Mirror


def test_get_element_class_missing():
    with pytest.raises(ValueError):
        KATSPEC.get_element_class("FooMirror")
