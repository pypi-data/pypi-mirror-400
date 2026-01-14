"""Higher order functions."""

from functools import update_wrapper
from enum import Enum


class valuedispatchmethod:
    """Method decorator that performs single-dispatch based on value.

    Transforms a method into a generic method, which can have different behaviours
    depending upon the value of its first argument (after `self`). The decorated
    method acts as the default implementation, and additional implementations can be
    registered using the register() attribute of the generic method.

    The default implementation must accept at least one argument, the value. Specialised
    implementations are not passed the value. Both implementations are passed any
    additional positional and keyword arguments specified in the call to `get`.

    Values registered via register() must be hashable.

    Based on :class:`functools.singledispatchmethod`.

    Examples
    --------
    Define a class with a value dispatch method, register a method to handle particular
    values, and call it:

    >>> from finesse.utilities.functools import valuedispatchmethod
    >>> class Example:
    ...     @valuedispatchmethod
    ...     def get(self, value):
    ...          return f"got {value} (default)"
    ...     @get.register(1)
    ...     def _(self):
    ...         return "got 1"
    ...
    >>> myobj = Example()
    >>> myobj.get(1)
    got 1
    >>> myobj.get(2)
    got 2 (default)
    """

    def __init__(self, func):
        if not callable(func) and not hasattr(func, "__get__"):
            raise TypeError(f"{func!r} is not callable or a descriptor")

        self.func = func
        self.registry = {}

    def dispatch(self, value):
        return self.registry.get(value)

    def _validate_key(self, key):
        pass

    def register(self, value):
        """Register a new implementation of the generic method for the given value."""
        self._validate_key(value)

        def wrap(method):
            self.registry[value] = method
            return method

        return wrap

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            args = list(args)
            value = args.pop(0)

            if (method := self.dispatch(value)) is not None:
                return method.__get__(obj, cls)(*args, **kwargs)
            else:
                # Call the default with the value.
                return self.func(cls, value, *args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        return _method

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, "__isabstractmethod__", False)


class flagdispatchmethod(valuedispatchmethod):
    """Method decorator that performs single-dispatch based on a flag enumeration.

    Transforms a method into a generic method, which can have different behaviours
    depending upon the value of its first argument (after `self`). The decorated
    method acts as the default implementation, and additional implementations can be
    registered using the register() attribute of the generic method.

    The default implementation must accept at least one argument, the flags. Specialised
    implementations are not passed the flags. Both implementations are passed any
    additional positional and keyword arguments specified in the call to `get`.

    As long as the given flag is contained within a registered flag enumeration, it
    triggers that corresponding method. The method corresponding to the first registered
    flag that matches is returned.

    Based on :class:`functools.singledispatchmethod`.

    Examples
    --------
    Define a class with a flag dispatch method, register a method to handle particular
    flags, and call it:

    >>> from enum import auto, Flag
    >>> from finesse.utilities.functools import flagdispatchmethod
    >>> class Flags(Flag):
    ...     A = auto()
    ...     B = auto()
    ...     C = auto()
    ...     D = auto()
    ...
    >>> class Example:
    ...     @flagdispatchmethod
    ...     def get(self, flag):
    ...          return f"got {flag} (default)"
    ...     @get.register(Flags.A)
    ...     def _(self):
    ...         return f"got {Flags.A}"
    ...     @get.register(Flags.B)
    ...     @get.register(Flags.C)
    ...     def _(self):
    ...         return f"got {Flags.B}"
    ...
    >>> myobj = Example()
    >>> myobj.get(Flags.A)
    got Flags.A
    >>> myobj.get(Flags.A | Flags.B)
    got Flags.B|A (default)
    >>> myobj.get(Flags.C)
    got Flags.B
    >>> myobj.get(Flags.D)
    got Flags.D (default)
    """

    def _validate_key(self, key):
        if not isinstance(key, Enum):
            raise ValueError(f"{self.__class__.__name__} requires Enum values")

    def dispatch(self, enumeration):
        for key, method in self.registry.items():
            if enumeration in key:
                return method
