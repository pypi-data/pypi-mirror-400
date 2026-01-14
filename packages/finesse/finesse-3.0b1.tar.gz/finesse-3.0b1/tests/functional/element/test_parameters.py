"""Parameter unit tests."""

from finesse.symbols import Constant
from finesse.parameter import int_parameter, bool_parameter
from finesse.element import ModelElement


def test_parameter_equality_checks(model):
    """Test that parameters can be directly compared to numbers and other symbols."""
    model.parse("laser l1 P=3.14")
    assert model.l1.P == 3.14
    assert model.l1.P == Constant(3.14)
    assert model.l1.P == (Constant(3.14) + Constant(3.14)) / 2
    assert model.l1.P.ref == model.l1.P


def test_parameter_ref_substitution(model):
    """Test that parameter refs can be subsituted for in expressions."""
    model.parse("laser l1 P=3.14")
    assert model.l1.P.eval() == 3.14
    assert (model.l1.P.ref + 1).eval(subs={model.l1.P: 4}) == 5


def test_bool_parameter_checks(model):
    """Test bool parameters get boolean checked properly."""

    @bool_parameter("bool", "")
    class TEST(ModelElement):
        pass

    model.add(TEST("test"))
    model.test.bool = True
    assert model.test.bool
    assert model.test.bool.ref
    model.test.bool = False
    assert not model.test.bool
    assert not model.test.bool.ref


def test_parameter_table(model):
    @int_parameter("test_param", "number", "Hz")
    class TEST(ModelElement):
        pass

    model.add(TEST("test1"))
    model.add(TEST("test2"))
    model.test1.test_param = 10
    model.test2.test_param = model.test1.test_param.ref
    assert model.test1.info() == (
        "TEST test1\n\n"
        "Parameters:\n"
        "┌─────────────┬───────┐\n"
        "│ Description │ Value │\n"
        "╞═════════════╪═══════╡\n"
        "│ number      │ 10 Hz │\n"
        "└─────────────┴───────┘\n"
    )
    assert model.test2.info() == (
        "TEST test2\n\n"
        "Parameters:\n"
        "┌─────────────┬─────────────────────┐\n"
        "│ Description │ Value               │\n"
        "╞═════════════╪═════════════════════╡\n"
        "│ number      │ test1.test_param Hz │\n"
        "└─────────────┴─────────────────────┘\n"
    )
    assert model.test2.info(eval_refs=True) == (
        "TEST test2\n\n"
        "Parameters:\n"
        "┌─────────────┬───────┐\n"
        "│ Description │ Value │\n"
        "╞═════════════╪═══════╡\n"
        "│ number      │ 10 Hz │\n"
        "└─────────────┴───────┘\n"
    )


def test_parameter_ref_string_repr(model):
    "Test functionality for resolving refs when printing parameter values"
    model.parse("laser l1 P=3.14")
    model.parse("laser l2 l1.P")
    assert str(model.l1.P) == "3.14 W"
    assert str(model.l2.P) == "l1.P W"
    model.l2.P.eval_string = True
    assert str(model.l2.P) == "3.14 W"
