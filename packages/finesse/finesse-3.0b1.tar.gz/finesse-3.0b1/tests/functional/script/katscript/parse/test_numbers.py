from hypothesis import given, assume, settings, HealthCheck
from hypothesis.strategies import floats, complex_numbers
from testutils.fuzzing import DEADLINE, c_integer


@given(value=c_integer)
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_integer_fuzzing(fuzz_argument, value):
    assert fuzz_argument(value) == value


@given(value=floats(allow_nan=False, allow_infinity=True))
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_float_fuzzing(fuzz_argument, value):
    assume(not str(value).endswith("e"))
    assert fuzz_argument(value) == value


@given(value=complex_numbers(allow_nan=False, allow_infinity=False))
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_complex_fuzzing(fuzz_argument, value):
    assert fuzz_argument(value) == value
