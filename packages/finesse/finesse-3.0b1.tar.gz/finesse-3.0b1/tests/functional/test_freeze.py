import pytest
from finesse.freeze import Freezable, canFreeze


@canFreeze
class FreezeTest:
    test_attr = 5


class WithName(FreezeTest):
    name = "test_name"


class UnderscoreName(FreezeTest):
    __name = "underscore_name"


def test_setattr_unfrozen():
    f = FreezeTest()
    assert f.test_attr == 5
    f.test_attr = 4
    assert f.test_attr == 4


@pytest.mark.parametrize(
    "cls, name",
    (
        (FreezeTest, FreezeTest.__name__),
        (WithName, WithName.name),
        (UnderscoreName, UnderscoreName._UnderscoreName__name),
    ),
)
def test_setattr_frozen(cls, name):
    f = cls()
    f._freeze()

    # we can still modify existing attributes
    assert f.test_attr == 5
    f.test_attr = 4
    assert f.test_attr == 4

    # we can not add new attributes
    msg = f"'{name}' does not have attribute called 'new_attr'"
    with pytest.raises(TypeError, match=msg):
        f.new_attr = 10


class FreezableTest(Freezable):
    def __init__(self):
        self.a = 1
        self.b = 2
        super().__init__()


def test_freezable_frozen():
    f = FreezableTest()
    with pytest.raises(TypeError):
        f.new_attribute = 10
    f._unfreeze()
    f.new_attribute = 10


def test_freezable_iter():
    f = FreezableTest()
    assert list(f) == [1, 2]


def test_freezable_items():
    f = FreezableTest()
    assert tuple(f.items()) == (("a", 1), ("b", 2))
