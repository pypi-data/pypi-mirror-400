import pytest

from finesse.components import Mirror
from finesse import Model
from finesse.exceptions import FinesseException


@pytest.fixture
def mirror_1():
    return Mirror("m1")


@pytest.fixture
def mirror_2():
    return Mirror("m2")


def test_add(model, mirror_1):
    mirror_1 = model.add(mirror_1)
    assert hasattr(model, "m1")
    assert "m1" in model.elements
    assert mirror_1 == model.m1


def test_add_multiple_models(mirror_1):
    model_1 = Model()
    model_2 = Model()
    mirror_1 = model_1.add(mirror_1)
    with pytest.raises(FinesseException):
        model_2.add(mirror_1)


def test_add_duplicate(model, mirror_1):
    model.add(mirror_1)
    with pytest.raises(FinesseException):
        model.add(mirror_1)


def test_add_unremovable(model, mirror_1):
    model.add(mirror_1, unremovable=True)
    with pytest.raises(FinesseException):
        model.remove(mirror_1)


def test_add_iterable(model, mirror_1, mirror_2):
    m1, m2 = model.add([mirror_1, mirror_2])
    assert m1 == mirror_1
    assert m2 == mirror_2
    assert mirror_1.name in model.elements
    assert mirror_2.name in model.elements
