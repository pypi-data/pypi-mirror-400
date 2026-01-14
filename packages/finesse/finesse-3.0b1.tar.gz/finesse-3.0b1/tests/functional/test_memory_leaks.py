import finesse
import gc
import psutil
import pytest


@pytest.mark.xfail(
    reason=(
        "With numpy 2.4.0 MacOS and Windows fail the memleak test, "
        "marking them for now as expected to fail. See issue #776"
    )
)
@pytest.mark.parametrize(
    "element",
    [
        "l el",
        "m el",
        "bs el",
        "lens el",
        "sq el db=0",
        "readout_dc el",
        "readout_rf el",
        "dbs el",
    ],
)
# see https://gitlab.com/ifosim/finesse/finesse3/-/issues/626
def test_model_build_memory_leak(element):
    base = finesse.Model()
    base.parse(element)
    base.modes("off")
    base.run()  # initial run to get things imported
    process = psutil.Process()

    attempts = 3
    trials = 20
    fails = []

    for _ in range(attempts):
        p0 = process.memory_info().rss
        for _ in range(trials):
            base.run()
        gc.collect()
        p2 = process.memory_info().rss
        loss_per_trial = (p2 - p0) / (trials)

        fails.append(loss_per_trial >= 2**12)  # maybe too strict?

    assert not all(fails)
