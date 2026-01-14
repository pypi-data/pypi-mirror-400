import pytest
from finesse.script.exceptions import KatScriptError


def test_lambda_default(model):
    assert model.lambda0 == 1064e-9


@pytest.mark.parametrize("lambda0", (1, 3.141, 10))
def test_lambda(model, lambda0):
    model.parse(f"lambda({lambda0})")
    assert float(model.lambda0) == lambda0


_LAMBDA0_FAIL = pytest.mark.xfail(
    reason="lambda0 validation not implemented for this value yet"
)


@pytest.mark.parametrize(
    "lambda0",
    (
        0,
        0.0,
        pytest.param(-1, marks=_LAMBDA0_FAIL),
        pytest.param(-3.141, marks=_LAMBDA0_FAIL),
        pytest.param(-10, marks=_LAMBDA0_FAIL),
        "'hi'",
        1 + 2j,
    ),
)
def test_invalid_lambda(model, lambda0):
    with pytest.raises(KatScriptError):
        model.parse(f"lambda({lambda0})")
