"""Expression unparsing tests."""

from finesse.script import KATSPEC, unparse
from finesse.symbols import simplification


def test_expression_references__unsimplified(model):
    """Test expressions containing references, without simplification.

    Without simplification (the default), Finesse will leave the expression for variable
    'c' in its original form, so the unparser will generate equivalent KatScript.
    """
    model.add_parameter("a", 1.0)
    model.add_parameter("b", 2.0)
    model.add_parameter(
        "c",
        (model.a.ref / model.b.ref + model.a.ref * model.b.ref + 2 - model.b.ref),
    )

    adapter = KATSPEC.elements["variable"]
    # Get the dump for the last variable.
    dump = list(adapter.getter(adapter, model))[2]
    script = unparse(dump)
    assert script == "variable c ((((a/b)+(a*b))+2)-b)"


def test_expression_references__simplified(model):
    """Test expressions containing references, with simplification.

    With simplification, Finesse will convert the expression for variable 'c' to a
    simplified form, and the unparser will generate a nested binary/unary expression
    from it.
    """
    model.add_parameter("a", 1.0)
    model.add_parameter("b", 2.0)

    with simplification():
        model.add_parameter(
            "c",
            (model.a.ref / model.b.ref + model.a.ref * model.b.ref + 2 - model.b.ref),
        )

    adapter = KATSPEC.elements["variable"]
    # Get the dump for the last variable.
    dump = list(adapter.getter(adapter, model))[2]
    script = unparse(dump)
    assert script == "variable c ((((-1*b)+2)+(a*(b**-1)))+(a*b))"
