from contextlib import nullcontext

import numpy as np
import pytest

import finesse
from finesse.components import Laser, Modulator, SignalGenerator
from finesse.analysis.actions import DCFields
from finesse.enums import ModulatorType


@pytest.mark.parametrize(
    "mod_type, signal_node, raises",
    (
        (ModulatorType.am, "eom.amp.i", pytest.raises(NotImplementedError)),
        (ModulatorType.am, "eom.phs.i", pytest.raises(NotImplementedError)),
        (ModulatorType.pm, "eom.amp.i", nullcontext()),
        (ModulatorType.pm, "eom.phs.i", pytest.raises(NotImplementedError)),
    ),
)
def test_not_implemented_signal(mod_type, signal_node, raises):
    model = finesse.Model()
    model.add(Laser("l1"))
    model.add(Modulator("eom", f=100, midx=1, order=1, mod_type=mod_type))
    model.add(SignalGenerator("sgen", node=model.get(signal_node)))
    model.fsig.f = 1

    with raises:
        model.run()


def test_modulator_positive_only(model):
    """Test that the positive only option generates only the positive sidebands"""
    model.add(Laser("Laser", P=1))
    model.add(Modulator("Mod", 9e6, 0.2, order=2))
    model.connect(model.Laser.p1, model.Mod.p1)
    sol1 = model.run(DCFields())
    model.Mod.positive_only = True
    sol2 = model.run(DCFields())
    node = model.Mod.p2.o
    pos = sol1[node].squeeze()
    pos[sol1.frequencies < 0] = 0
    pos[0] = 1 - 0.5 * (1 - pos[0])
    np.testing.assert_allclose(pos, sol2[node].squeeze())
