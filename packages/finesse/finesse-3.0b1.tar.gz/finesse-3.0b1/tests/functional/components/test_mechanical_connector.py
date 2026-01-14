import pytest

import finesse
from finesse.exceptions import DoubleConnectionError
from finesse.components import Mirror, Pendulum, FreeMass, SuspensionZPK


@pytest.mark.parametrize("mech_kls", (Pendulum, FreeMass, SuspensionZPK))
def test_double_pendulum(mech_kls):
    model = finesse.Model()
    m1 = model.add(Mirror("m1"))
    extra_kwargs = {}
    if mech_kls is SuspensionZPK:
        extra_kwargs["zpk_plant"] = {}
    model.add(mech_kls("mech1", m1.mech, **extra_kwargs))
    with pytest.raises(DoubleConnectionError):
        model.add(mech_kls("mech2", m1.mech, **extra_kwargs))
