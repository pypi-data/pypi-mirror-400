from hypothesis import given, settings, note, HealthCheck
from testutils.text import stringify_list
from testutils.fuzzing import DEADLINE, recursive_arrays


@given(expected=recursive_arrays(operations=True))
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_array_fuzzing(fuzz_argument, expected):
    array = stringify_list(expected)
    note(f"Array: {array}")
    assert fuzz_argument(array) == eval(array)
