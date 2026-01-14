import pytest


# Override default element to take one model parameter argument.
@pytest.fixture
def fake_element_cls(fake_element_cls, fake_float_parameter):
    @fake_float_parameter("value", "Fake Parameter", is_default=True)
    class FakeElement(fake_element_cls):
        def __init__(self, name, value):
            super().__init__(name)
            self.value = value

    return FakeElement


@pytest.fixture
def spec(
    spec,
    set_spec_constructs,
    fake_element_adapter_factory,
    fake_element_cls,
    finesse_binop_add,
    finesse_binop_sub,
    finesse_binop_mul,
    finesse_binop_div,
    finesse_binop_pow,
):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    set_spec_constructs(
        "binary_operators",
        {
            "+": finesse_binop_add,
            "-": finesse_binop_sub,
            "*": finesse_binop_mul,
            "/": finesse_binop_div,
            "**": finesse_binop_pow,
        },
    )

    return spec


def test_expression_references(unbuilder, model, element_dump, fake_element_cls):
    """Test expressions containing references."""
    model.add(fake_element_cls("a", 1.0))
    model.add(fake_element_cls("b", 2.0))
    model.add(
        fake_element_cls(
            "c",
            (
                model.a.value.ref / model.b.value.ref
                + model.a.value.ref * model.b.value.ref
                + 2
                - model.b.value.ref
            ),
        )
    )

    dumps = iter(element_dump("fake_element", fake_element_cls, model))
    assert unbuilder.unbuild(next(dumps)) == "fake_element a value=1.0"
    assert unbuilder.unbuild(next(dumps)) == "fake_element b value=2.0"
    assert unbuilder.unbuild(next(dumps)) == (
        "fake_element c value=((((a/b)+(a*b))+2)-b)"
    )
