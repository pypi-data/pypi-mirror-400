import pytest
from finesse.utilities.collections import OrderedSet


def test_init():
    oset = OrderedSet([1, 2, 3])
    assert list(oset) == [1, 2, 3]


def test_add():
    oset = OrderedSet()
    oset.add(1)
    assert list(oset) == [1]
    oset.add(2)
    assert list(oset) == [1, 2]
    oset.add(1)  # Adding duplicate
    assert list(oset) == [1, 2]  # Should remain unchanged


def test_remove():
    oset = OrderedSet([1, 2, 3])
    oset.remove(2)
    assert list(oset) == [1, 3]
    with pytest.raises(KeyError):
        oset.remove(4)  # Trying to remove an element not in the set


def test_difference_update():
    oset = OrderedSet([1, 2, 3, 4])
    oset.difference_update([2, 4, 5])
    assert list(oset) == [1, 3]


def test_update():
    oset = OrderedSet([1, 2, 3])
    oset.update([3, 4, 5])
    assert list(oset) == [1, 2, 3, 4, 5]


def test_clear():
    oset = OrderedSet([1, 2, 3])
    oset.clear()
    assert list(oset) == []


def test_contains():
    oset = OrderedSet([1, 2, 3])
    assert 1 in oset
    assert 4 not in oset


def test_len():
    oset = OrderedSet([1, 2, 3])
    assert len(oset) == 3
    oset.add(4)
    assert len(oset) == 4
    oset.remove(2)
    assert len(oset) == 3


def test_iter():
    oset = OrderedSet([1, 2, 3])
    assert list(iter(oset)) == [1, 2, 3]


def test_repr():
    oset = OrderedSet([1, 2, 3])
    assert repr(oset) == "OrderedSet(1, 2, 3)"


def test_ordering():
    # Test ordering on initialization
    oset = OrderedSet([3, 1, 2])
    assert list(oset) == [3, 1, 2], "Initial ordering failed"

    # Test ordering with add
    oset.add(4)
    assert list(oset) == [3, 1, 2, 4], "Ordering failed after adding new element"

    # Adding an existing element should not change order
    oset.add(2)
    assert list(oset) == [
        3,
        1,
        2,
        4,
    ], "Ordering changed after adding an existing element"

    # Test ordering with update
    oset.update([5, 0, 2])
    assert list(oset) == [3, 1, 2, 4, 5, 0], "Ordering failed after update"

    # Test ordering with difference_update
    oset.difference_update([1, 0])
    assert list(oset) == [3, 2, 4, 5], "Ordering failed after difference_update"


def test_sub():
    oset1 = OrderedSet([1, 2, 3, 4])
    oset2 = OrderedSet([3, 4, 5])
    oset3 = oset1 - oset2
    assert list(oset3) == [1, 2], "Subtraction did not return the expected result"

    oset4 = OrderedSet([1, 2])
    oset5 = oset1 - oset4
    assert list(oset5) == [
        3,
        4,
    ], "Subtraction did not return the expected result when subtracting another subset"


def test_union():
    # Test union of two OrderedSets with some common elements
    oset1 = OrderedSet([1, 2, 3])
    oset2 = OrderedSet([3, 4, 5])
    oset3 = oset1 | oset2
    assert list(oset3) == [1, 2, 3, 4, 5], "Union failed with common elements"

    # Test union with an empty OrderedSet
    oset4 = OrderedSet()
    oset5 = oset1 | oset4
    assert list(oset5) == [
        1,
        2,
        3,
    ], "Union with an empty set should return the original set"

    # Test union where one set is a subset of the other
    oset6 = OrderedSet([1, 2])
    oset7 = oset1 | oset6
    assert list(oset7) == [
        1,
        2,
        3,
    ], "Union failed when one set was a subset of the other"

    # Test union where both sets are identical
    oset8 = oset1 | oset1
    assert list(oset8) == [
        1,
        2,
        3,
    ], "Union of identical sets should return the same set"

    # Test union with no common elements
    oset9 = OrderedSet([6, 7])
    oset10 = oset1 | oset9
    assert list(oset10) == [
        1,
        2,
        3,
        6,
        7,
    ], "Union with no common elements should return all elements from both sets"


def test_intersection():
    # Test intersection of two OrderedSets with some common elements
    oset1 = OrderedSet([1, 2, 3])
    oset2 = OrderedSet([2, 3, 4])
    oset3 = oset1 & oset2
    assert list(oset3) == [2, 3], "Intersection failed with common elements"

    # Test intersection with an empty OrderedSet
    oset4 = OrderedSet()
    oset5 = oset1 & oset4
    assert (
        list(oset5) == []
    ), "Intersection with an empty set should return an empty set"

    # Test intersection where one set is a subset of the other
    oset6 = OrderedSet([1, 2])
    oset7 = oset1 & oset6
    assert list(oset7) == [
        1,
        2,
    ], "Intersection failed when one set was a subset of the other"

    # Test intersection where both sets are identical
    oset8 = oset1 & oset1
    assert list(oset8) == [
        1,
        2,
        3,
    ], "Intersection of identical sets should return the same set"

    # Test intersection with no common elements
    oset9 = OrderedSet([4, 5])
    oset10 = oset1 & oset9
    assert (
        list(oset10) == []
    ), "Intersection with no common elements should return an empty set"


def test_issubset():
    oset1 = OrderedSet([1, 2, 3])
    oset2 = OrderedSet([1, 2, 3, 4, 5])
    oset3 = OrderedSet([2, 3])
    oset4 = OrderedSet([1, 4])

    assert oset1.issubset(oset2) is True, "Set should be a subset of the other"
    assert oset1.issubset(oset3) is False, "Set should not be a subset of the other"
    assert oset3.issubset(oset1) is True, "Set should be a subset of the other"
    assert oset4.issubset(oset1) is False, "Set should not be a subset of the other"


def test_equality():
    oset1 = OrderedSet([1, 2, 3])
    oset2 = OrderedSet([1, 2, 3])
    oset3 = OrderedSet([3, 2, 1])
    oset4 = OrderedSet([1, 2, 4])
    oset5 = OrderedSet()
    native_set = {1, 2, 3}
    native_set_different = {2, 3, 4}

    # Test equality with another OrderedSet
    assert (
        oset1 == oset2
    ), "Sets with the same elements in the same order should be equal"
    assert (
        oset1 != oset3
    ), "Sets with the same elements but different order should not be equal"
    assert oset1 != oset4, "Sets with different elements should not be equal"
    assert oset1 != oset5, "Sets with different elements should not be equal"
    assert oset5 == OrderedSet(), "Empty sets should be equal"

    # Test equality with other collection types
    assert (
        oset1 == native_set
    ), "OrderedSet should be equal to a set with the same elements"
    assert (
        oset1 != native_set_different
    ), "OrderedSet should not be equal to a set with different elements"
    assert oset1 != [1, 2, 3], "OrderedSet should not be equal to a list"
    assert oset1 != (1, 2, 3), "OrderedSet should not be equal to a tuple"
    assert oset1 != "123", "OrderedSet should not be equal to a string"
    assert oset1 != 123, "OrderedSet should not be equal to an integer"
