"""Custom exception types raised by different Finesse functions and class methods."""

from __future__ import annotations
import abc
from typing import Any

from .env import traceback_handler_instance
from finesse.utilities.text import get_close_matches, option_list


class FinesseException(Exception):
    """The exception type which gets raised upon a Finesse failure.

    This identifies whether the current session is interactive or not, and consequently
    sets the level of verbosity. This can be overridden by calling
    :func:`~finesse.env.show_tracebacks` with ``True``.
    """

    def __init__(self, message, **kwargs):
        if not traceback_handler_instance().show_tb:
            head = "\t(use finesse.tb() to see the full traceback)\n"
        else:
            head = "\n"
        message = head + str(message)
        super().__init__(message, **kwargs)

    def _render_traceback_(self):
        """Use custom traceback in IPython/Jupyter."""
        tb = traceback_handler_instance()
        tb.store_tb()

        return tb.get_stb()


class IllegalSelfReferencing(FinesseException):
    """Raised by elements who do not allow self referencing for arg/kwarg values."""


class ExternallyControlledException(FinesseException):
    """Raised when a parameter value is changed but there are other elements that are
    controlling what the value is."""


class ComponentNotConnected(FinesseException):
    pass


class ParameterLocked(FinesseException):
    pass


class NoCouplingError(FinesseException):
    """Raised when a coupling at a component is requested but does not exist."""

    pass


class NoABCDCoupling(FinesseException):
    """Raised when an ABCD coupling at a component is requested but does not exist."""

    pass


class NodeException(FinesseException):
    """Exception associated with :class:`.Node` related run-time errors.

    Objects of type `NodeException` store the error message as well as an optional
    reference to the node(s) which caused the exception to be raised.

    Parameters
    ----------
    message : str
        The error message.

    node : :class:`.Node`, optional
        A reference to the offending node(s), defaults to `None`. This can be a single
        node or a sequence of nodes.
    """

    def __init__(self, message, node=None):
        super().__init__(message)
        self.__node = node

    @property
    def node(self):
        """The node(s) responsible for raising this exception instance.

        :`getter`: Returns the node(s) (either a single :class:`.Node` object or a
                   sequence of these objects) responsible for the exception (read-only).
        """
        return self.__node


class BeamTraceException(FinesseException):
    pass


class ConvergenceException(FinesseException):
    """Indicates an algorithm has failed to converge to some requested tolerance."""


class TotalReflectionError(FinesseException):
    """Exception indicating total reflection of a beam at a component when performing
    beam tracing.

    Parameters
    ----------
    message : str
        The error message.

    from_node, to_node : :class:`.Node`
        References to the offending source and target nodes, respectively.
    """

    def __init__(self, message, from_node=None, to_node=None):
        super().__init__(message)
        self.__from_node = from_node
        self.__to_node = to_node

    @property
    def coupling(self):
        """The tuple of (from, to) nodes responsible for the total reflection error.

        :`getter`: Returns the nodes responsible for the exception (read-only).
        """
        return (self.__from_node, self.__to_node)


class ModelAttributeError(FinesseException):
    pass

    def _add_suggestions_to_msg(
        self, target: Any, resolved_attrs: list[str], missing_name: str, msg: str
    ) -> str | None:
        # prevent circular imports
        from finesse.model import Model
        from finesse.element import ModelElement
        from finesse.components import Connector

        options = set()
        if isinstance(target, Model):
            options |= set(
                x for x in dir(target) if (not x[0] == "_" and x not in dir(Model))
            )
        else:
            if isinstance(target, ModelElement):
                options |= set(par.name for par in target.parameters)
            if isinstance(target, Connector):
                options |= set(port.name for port in target.ports)
            if not len(options):
                options |= set(dir(target))
        close_matches = get_close_matches(missing_name, options)
        if close_matches:
            prefix = ".".join(resolved_attrs) + "."
            suggestions = option_list(
                close_matches, quotechar="'", sort=True, prefix=prefix
            )
            msg += f"\n\nDid you mean: {suggestions}?"
        else:
            msg += f"\n\nNo suggestions found for '{missing_name}'"
        return msg


class ModelMissingAttributeError(ModelAttributeError):
    """Error indicating a model path was not found.

    Model paths can be e.g. `l1.P` or `s1.p1.o`.

    This exists mainly so it can be caught by the parser.
    """

    def __init__(self, target: Any, resolved_attrs: list[str], missing_name: str):
        """Generate an error for a missing model attribute, including suggestions of
        similar existing model attributes.

        Parameters
        ----------
        model : Model
            The model with the missing attribute
        pieces : list[str]
            List of strings resembling a model path
        """

        path = ".".join([*resolved_attrs, missing_name])
        if path.endswith("."):
            super().__init__(f"'{path}' should not end with a '.'")
            return
        msg = self._add_suggestions_to_msg(
            target, resolved_attrs, missing_name, msg=f"model has no attribute '{path}'"
        )
        super().__init__(msg)


class ModelClassAttributeError(ModelAttributeError):
    """Error indicating that a model path resolves to a class attribute.

    E.g. `l1.P.__dict__` or `parse` will resolve, but no usecase exists for referencing
    these class attributes in katscript.
    """

    def __init__(self, target: Any, resolved_attrs: list[str], missing_name: str):
        msg = self._add_suggestions_to_msg(
            target,
            resolved_attrs,
            missing_name,
            msg=f"Forbidden word '{missing_name}' in this context (python class attribute)",
        )
        FinesseException.__init__(self, msg)


class ModelParameterDefaultValueError(FinesseException):
    """Error indicating a model element has no default model parameter.

    Some model parameters have defaults, such that they can be referenced in kat script
    using e.g. `myvar` instead of `myvar.value`. This error indicates a model element
    without such a default was referenced directly.
    """

    def __init__(self, element):
        super().__init__(
            f"{repr(element.name)} cannot be referenced because type "
            f"{repr(element.__class__.__name__)} has no default model parameter"
        )


class ModelParameterSelfReferenceError(FinesseException):
    """Error indicating a model parameter cannot be set to refer to itself."""

    def __init__(self, value, parameter):
        super().__init__(
            f"cannot set {parameter.full_name} to self-referencing value {value}"
        )
        self.value = value
        self.parameter = parameter


class _empty:
    """Marker object for ContextualArgumentError.empty."""


class ContextualArgumentError(FinesseException, metaclass=abc.ABCMeta):
    """An argument error with additional context.

    This allows Finesse objects to provide additional information to the user when
    invalid values are passed to functions and methods.
    """

    empty = _empty


class ContextualValueError(ContextualArgumentError):
    """A value error with additional information about value(s) that caused an error."""

    def __init__(self, params, extra_info=None):
        self.params = params
        self.extra_info = extra_info

        super().__init__(self.message())

    def message(self):
        from .utilities import ngettext, option_list

        pathstrs = option_list(self.params, final_sep="and", quotechar="'")
        problem = ngettext(
            len(self.params), "invalid value", "invalid values", sub=False
        )

        # Only print the values if there aren't empty ones.
        if any([v == self.empty for v in self.params.values()]):
            valuestrs = ""
        else:
            valuestrs = option_list(
                [repr(value) for value in self.params.values()], final_sep="and"
            )
            valuestrs = f" {valuestrs}"

        extra = f" ({self.extra_info})" if self.extra_info else ""
        return f"{pathstrs}: {problem}{valuestrs}{extra}"


class ContextualTypeError(ContextualArgumentError):
    """A type error with additional information about the available types."""

    def __init__(self, param, value, allowed_types=None, name=None):
        self.param = param
        self.value = value
        self.name = name
        self.allowed_types = allowed_types

        super().__init__(self.message())

    def message(self):
        from .utilities import option_list

        if self.allowed_types:
            allowedtypes = [t.__name__ for t in self.allowed_types]
            allowedstr = option_list(allowedtypes, quotechar="'")
            gotstr = f"'{type(self.value).__name__}'"
            problem = f" (expected {allowedstr}, got {gotstr})"
        else:
            problem = ""

        if self.name:
            return f"{self.name} {self.param}: invalid type{problem}"
        else:
            return f"{self.param}: invalid type{problem}"


class NoLinearEquations(FinesseException):
    """Thrown when a simulation has no linear equations to solve."""


class LostLock(FinesseException):
    """Thrown when the lock is lost by the locking algorithm. This is typically an issue
    of:

        * the error signal has been lost (no longer linear, rotated into a different quadrature
        * The error signal slope has become too small (need more lock gain) or too large (need less lock gain)
        * multiple locks are competing and dragging the interferometer to an unstable state.

    In such cases you can run the lock action with the flag `exception_on_fail=False` to
    ensure it returns a :class:`finesse.analysis.actions.locks.RunLocksSolution`. This
    solution can then be used to diagnose the issue, `plot_error_signals` and
    `plot_control_signals` are useful for this to see which error signals are causing an
    issue.
    """


class NotChangeableDuringSimulation(FinesseException):
    """Thrown when a parameter is attempted to be changed during a simulation but is
    marked as not changeable during a simulation."""


class InvalidRTLError(FinesseException):
    """Thrown when the RTL parameters of a Surface component violate energy
    conservation."""


class EvaluateResolvingSymbolError(FinesseException):
    """Thrown when trying to evaluate a parameter that is currently resolving."""


class DoubleConnectionError(FinesseException):
    """Thrown when a connections is made to a port that is already connected"""
