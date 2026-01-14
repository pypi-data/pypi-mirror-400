"""Controlling an interferometer via error signals."""

import logging

from finesse.parameter import ParameterRef, bool_parameter, float_parameter
from finesse.element import ModelElement

LOGGER = logging.getLogger(__name__)


@float_parameter("gain", "Gain of the lock")
@float_parameter("accuracy", "Accuracy to reach for the lock")
@float_parameter("offset", "Offset applied to the input of the error signal")
@bool_parameter("enabled", "Whether the lock is enabled or not")
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Lock(ModelElement):
    """A simple lock which computes and applies the feedback to a given parameter using
    an error signal.

    Parameters
    ----------
    name : str
        Name of newly created lock.

    error_signal : Any
        An error signal parameter or an object capable of producing a real-type error signal. This
        is typically a demodulated :class:`.PowerDetector` instance (or the name of the instance).

    feedback : :class:`.Parameter`
        A parameter of the model to apply the locks' feedback signal to.

    gain : float
        Control loop gain.

    accuracy : float
        Threshold to decide whether the loop is locked.

    enabled : boolean
        If true this lock will run when the `RunLocks()` action is used. Explicitly specifying
        the name of the lock will override this setting, e.g. `RunLocks(name)`.

    offset : float
        An offset that is applied to the error signal before it is used.
    """

    def __init__(
        self, name, error_signal, feedback, gain, accuracy, *, enabled=True, offset=0
    ):
        super().__init__(name)

        self.enabled = enabled
        self.__errsig = error_signal
        self.__feedback = feedback
        self.gain = gain
        self.accuracy = accuracy
        self.offset = offset

    def _on_add(self, model):
        if isinstance(self.__errsig, str):
            self.__errsig = model.elements[self.__errsig]

    @property
    def disabled(self):
        return not self.enabled.value

    @property
    def error_signal(self):
        """The error signal of the lock."""
        return self.__errsig

    @error_signal.setter
    def error_signal(self, value):
        self.__errsig = self._model.get_element(value)

    @property
    def feedback(self):
        """A handle to the parameter which the feedback signal is applied to."""
        if isinstance(self.__feedback, ParameterRef):
            return self.__feedback.parameter
        else:
            return self.__feedback

    @feedback.setter
    def feedback(self, value):
        self.__feedback = value

    def __repr__(self):
        return f"<'{self.name}' @ {hex(id(self))} ({self.__class__.__name__}) enabled={self.enabled.value}>"
