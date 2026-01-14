import pytest

from finesse.components import Mirror, Laser


def test_link_between(model):
    model.add(Laser("l1"))
    model.add(Mirror("m1", R=0.9, T=0.1))
    model.link("l1", 10.0, "m1")
    assert model.spaces.l1_p1__m1_p1.L == 10.0


def test_link_between_wrong_order(model):
    model.add(Laser("l1"))
    model.add(Mirror("m1", R=0.9, T=0.1))
    with pytest.raises(ValueError):
        model.link("l1", "m1", 10.0)
