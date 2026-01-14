import inspect

from difflib import unified_diff

import pytest

import testutils.example_benchmarks
from testutils.example_benchmarks import (
    ex_01_simple_cav,
    ex_02_pdh_lock,
    ex_03_near_unstable,
    ex_04_geometrical_params,
    ex_05_modulation,
    ex_06_radiation_pressure,
    ex_07_homodyne,
    ex_08_optical_spring,
    ex_09_aligo_sensitivity,
    ex_10_shifted_beam,
    ex_angular_radiation_pressure,
    ex_cavity_eigenmodes,
    ex_coupled_cavity_commands,
    ex_frequency_dependant_squeezing,
    ex_lock_actions,
)

from scripts import examples_to_script


@pytest.mark.linux
def test_benchmark_creation(tmp_path):
    path = tmp_path / "destination.py"
    # set hide_output to False for debugging
    examples_to_script.main(path, hide_output=True)
    with open(path, "r") as f:
        current_version = f.read()
    import testutils.example_benchmarks

    with open(testutils.example_benchmarks.__file__, "r") as f:
        committed_version = f.read()

    if current_version != committed_version:
        diff = unified_diff(
            committed_version.splitlines(),
            current_version.splitlines(),
            fromfile=testutils.example_benchmarks.__file__,
            tofile=str(path),
        )
        msg = (
            "Benchmark code does not match code in Examples section of documentation! "
            f"Run 'python {examples_to_script.__file__}' ?\n"
        )
        msg += "\n".join(diff)
        raise Exception(msg)


def test_all_benchmarks_imported():
    benchmarks_functions = set(
        v
        for k, v in inspect.getmembers(
            testutils.example_benchmarks, predicate=lambda f: inspect.isfunction(f)
        )
    )
    imported_functions = set(f for f in globals().values() if inspect.isfunction(f))

    assert benchmarks_functions.issubset(imported_functions)


def test_01_simple_cav(benchmark):
    benchmark(ex_01_simple_cav)


def test_02_pdh_lock(benchmark):
    benchmark(ex_02_pdh_lock)


# Note that example 03 currently does not have any code in the rst file
# but we keep it here so it will be automatically benchmarked when code
# is added to the example
def test_03_near_unstable(benchmark):
    benchmark(ex_03_near_unstable)


def test_04_geometrical_params(benchmark):
    benchmark(ex_04_geometrical_params)


def test_05_modulation(benchmark):
    benchmark(ex_05_modulation)


def test_06_radiation_pressure(benchmark):
    benchmark(ex_06_radiation_pressure)


def test_07_homodyne(benchmark):
    benchmark(ex_07_homodyne)


def test_08_optical_spring(benchmark):
    benchmark(ex_08_optical_spring)


def test_09_aligo_sensitivity(benchmark):
    benchmark(ex_09_aligo_sensitivity)


def test_10_shifted_beam(benchmark):
    benchmark(ex_10_shifted_beam)


def test_angular_radiation_pressure(benchmark):
    benchmark(ex_angular_radiation_pressure)


def test_cavity_eigenmodes(benchmark):
    benchmark(ex_cavity_eigenmodes)


def test_coupled_cavity_commands(benchmark):
    benchmark(ex_coupled_cavity_commands)


def test_frequency_dependant_squeezing(benchmark):
    benchmark(ex_frequency_dependant_squeezing)


def test_lock_actions(benchmark):
    benchmark(ex_lock_actions)
