"""Tools for making an arbitrary Finesse object freezable."""


def canFreeze(cls):
    """A function to be used as a decorator for classes which should have the ability to
    be frozen and unfrozen.

    Parameters
    ----------
    cls : object
        Class to make freezable, should never be called directly as
        this function is to be used as a decorator.

    Returns
    -------
    cls : object
        The class with frozen attributes set.

    Examples
    --------
    To make a custom object in Finesse frozen simply use this
    function as a decorator to the class definition::

        from finesse.freeze import canFreeze

        @canFreeze
        class FinesseObject:
            ...
    """

    def _freeze(self):
        self.__dict__["____FROZEN____"] = True

    def _unfreeze(self):
        self.__dict__["____FROZEN____"] = False

    def frozensetattr(self, name, value):
        if (
            "____FROZEN____" in self.__dict__
            and self.__dict__["____FROZEN____"]
            and not hasattr(self, name)
        ):
            # due to python name mangling
            private_name = f"_{self.__class__.__name__}__name"
            if hasattr(self, "name"):
                n = self.name
            elif hasattr(self, private_name):
                n = getattr(self, private_name)
            else:
                n = self.__class__.__name__

            raise TypeError("'%s' does not have attribute called '%s'" % (n, name))

        super(cls, self).__setattr__(name, value)

    cls.__setattr__ = frozensetattr
    cls._freeze = _freeze
    cls._unfreeze = _unfreeze
    return cls


@canFreeze
class Freezable:
    """An object which can be frozen and unfrozen, it is frozen upon construction."""

    def __init__(self):
        """Constructs a new instance of `Freezable` and freezes it."""
        self._freeze()

    def __iter__(self):
        return (val for _, val in self.items())

    def items(self):
        return ((key, val) for key, val in self.__dict__.items() if key[0] != "_")
