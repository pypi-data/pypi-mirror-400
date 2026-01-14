"""Finesse-specific warnings."""


class FinesseWarning(Warning):
    """A generic warning thrown by Finesse."""


class ModelParameterSettingWarning(FinesseWarning):
    """An elements parameter is not using its prefer setter method."""


class CavityUnstableWarning(FinesseWarning):
    """A cavity geometry has become unstable and its eigenmode is no longer
    calculable."""


class KeywordUsedWarning(FinesseWarning):
    """A KatScript keyword was used as a name for some element in the model."""


class InvalidSweepVariableWarning(FinesseWarning):
    """An invalid variable value was used during a sweep action.

    Can occur when trying to sweep relative to an infinite value, or using a NaN.
    """


class UnreasonableComponentValueWarning(FinesseWarning):
    """A not-wrong-but-probably-unreasonable component value was set."""
