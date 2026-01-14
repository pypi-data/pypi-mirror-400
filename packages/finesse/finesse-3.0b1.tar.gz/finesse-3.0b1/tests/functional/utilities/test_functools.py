"""Higher order function tests."""

from enum import auto, unique, Enum, Flag, IntFlag
import pytest
from finesse.utilities.functools import valuedispatchmethod, flagdispatchmethod


@unique
class ValueField(Enum):
    A = 1
    B = 2
    C = "foo"
    C2 = "bar"


class ValueDispatchNoArgs:
    @valuedispatchmethod
    def get(self, value):
        return value

    @get.register(1)
    def _(self):
        return 1

    @get.register(2)
    def _(self):
        return 2

    @get.register(ValueField.A)
    def _(self):
        return ValueField.A

    @get.register(ValueField.B)
    def _(self):
        return ValueField.B

    @get.register(ValueField.C)
    @get.register(ValueField.C2)
    def _(self):
        return ValueField.C


class ValueDispatchArgs:
    @valuedispatchmethod
    def get(self, value, a, b):
        return value, a, b

    @get.register(1)
    def _(self, a, b):
        return 1, a, b

    @get.register(2)
    def _(self, a, b):
        return 2, a, b

    @get.register(ValueField.A)
    def _(self, a, b):
        return ValueField.A, a, b

    @get.register(ValueField.B)
    def _(self, a, b):
        return ValueField.B, a, b

    @get.register(ValueField.C)
    @get.register(ValueField.C2)
    def _(self, a, b):
        return ValueField.C, a, b


values = pytest.mark.parametrize(
    "value,expected",
    (
        (-1, -1),
        (1, 1),
        (2, 2),
        (ValueField.A, ValueField.A),
        (ValueField.B, ValueField.B),
        (ValueField.C, ValueField.C),
        (ValueField.C2, ValueField.C),
    ),
)


class Flags(Flag):
    A = auto()
    B = auto()
    C = auto()
    C2 = auto()
    D = auto()
    E = auto()
    F = auto()
    UNDEFINED = auto()


class FlagDispatch:
    @flagdispatchmethod
    def get(self, flags):
        return

    @get.register(Flags.A)
    def _(self):
        return Flags.A

    @get.register(Flags.B)
    def _(self):
        return Flags.B

    @get.register(Flags.C)
    @get.register(Flags.C2)
    def _(self):
        return Flags.C

    @get.register(Flags.D | Flags.E)
    @get.register(Flags.F)
    def _(self):
        return Flags.D


flags = pytest.mark.parametrize(
    "flag,expected",
    (
        (Flags.A, Flags.A),
        (Flags.B, Flags.B),
        (Flags.C, Flags.C),
        (Flags.C2, Flags.C),
        (Flags.D, Flags.D),
        (Flags.E, Flags.D),
        (Flags.D | Flags.E, Flags.D),
        (Flags.F, Flags.D),
        (Flags.UNDEFINED, None),
    ),
)


class IntFlags(IntFlag):
    A = auto()
    B = auto()
    C = auto()
    C2 = auto()
    D = auto()
    E = auto()
    F = auto()
    UNDEFINED = auto()


class IntFlagDispatch:
    @flagdispatchmethod
    def get(self, flags):
        return

    @get.register(IntFlags.A)
    def _(self):
        return IntFlags.A

    @get.register(IntFlags.B)
    def _(self):
        return IntFlags.B

    @get.register(IntFlags.C)
    @get.register(IntFlags.C2)
    def _(self):
        return IntFlags.C

    @get.register(IntFlags.D | IntFlags.E)
    @get.register(IntFlags.F)
    def _(self):
        return IntFlags.D

    @get.register(IntFlags.D | IntFlags.F)
    def _(self):
        raise RuntimeError("shouldn't be reached")


intflags = pytest.mark.parametrize(
    "flag,expected",
    (
        (IntFlags.A, IntFlags.A),
        (IntFlags.B, IntFlags.B),
        (IntFlags.C, IntFlags.C),
        (IntFlags.C2, IntFlags.C),
        (IntFlags.D, IntFlags.D),
        (IntFlags.E, IntFlags.D),
        (IntFlags.D | IntFlags.E, IntFlags.D),
        (IntFlags.F, IntFlags.D),
        (IntFlags.UNDEFINED, None),
    ),
)


@values
def test_value_dispatch_noargs(value, expected):
    dispatcher = ValueDispatchNoArgs()
    assert dispatcher.get(value) == expected


@values
def test_value_dispatch_args(value, expected):
    dispatcher = ValueDispatchArgs()
    assert dispatcher.get(value, 1, 2) == (expected, 1, 2)


@flags
def test_flag_dispatch(flag, expected):
    dispatcher = FlagDispatch()
    assert dispatcher.get(flag) == expected


@intflags
def test_int_flag_dispatch(flag, expected):
    dispatcher = IntFlagDispatch()
    assert dispatcher.get(flag) == expected
