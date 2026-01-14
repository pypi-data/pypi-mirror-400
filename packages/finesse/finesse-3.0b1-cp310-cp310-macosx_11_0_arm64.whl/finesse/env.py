"""Finesse environment information."""

import sys
import warnings
import shutil
import traceback
import abc

from packaging.version import Version

try:
    import IPython
    from IPython.core.ultratb import AutoFormattedTB
except ImportError:
    IPython = None

from . import datastore

# Platform detection.
IS_WINDOWS = sys.platform.startswith("win")

# Sizing for wrapping and indenting console output.
# Terminal width code copied from :class:`click.formatting.HelpFormatter`.
TERMINAL_WIDTH = max(min(shutil.get_terminal_size().columns, 80) - 2, 50)
INDENT = " " * 4


def traceback_handler_instance():
    if IPython is None:
        return datastore.init_singleton(_TracebackHandler)
    else:
        return datastore.init_singleton(_TracebackHandlerInteractive)


def session_instance():
    return datastore.init_singleton(_FinesseSession)


def is_interactive():
    """Check if Finesse is being run from an interactive environment.

    Returns
    -------
    bool
        `True` if a Jupyter notebook, Qt console or IPython shell is in use, `False`
        otherwise.
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return True  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def show_tracebacks(show_tb=None):
    """Get or set whether to show tracebacks in Jupyter/IPython in full form or just as
    a single error message.

    Parameters
    ----------
    show_tb : bool, optional
        Set whether to show tracebacks; defaults to None, which doesn't change the
        current setting.

    Returns
    -------
    bool
        The current setting value (if `show_tb` was not set) or the previous setting
        value (if `show_tb` was set).
    """
    tb = traceback_handler_instance()
    previous = tb.show_tb
    if show_tb is not None:
        tb.show_tb = show_tb
    return previous


# see https://gitlab.com/ifosim/finesse/finesse3/-/issues/597 for colors argument
def tb(colors=True):
    """Show the last traceback in full.

    Parameters
    ----------
    colors : bool, optional
        Use colored output (using ANSI escape sequences), by default True
        Can set to false if output is saved to a medium that doesn't support it
        (for example, html and pdf docs)
    """
    tb = traceback_handler_instance()
    tb.show_last(colors=colors)


def has_pygraphviz():
    """Determine if pygraphviz and graphviz are available on the current path.

    Returns
    -------
    bool
        `True` if pygraphviz and graphviz are available, `False` otherwise.

    Notes
    -----

    This returns `False` if either pygraphviz or graphviz is not installed or correctly
    configured. If pygraphviz is installed but graphviz is not installed or could not be
    found, an import error complaining about something like "libagraph.so.1" is emitted
    (see the `pygraphviz FAQ
    <https://pygraphviz.github.io/documentation/stable/reference/faq.html>`_).
    """
    try:
        import pygraphviz  # noqa: F401
    except ImportError:
        return False
    return True


def info(*args, **kwargs):
    session_instance().info(*args, **kwargs)


def warn(*args, stacklevel=1, **kwargs):
    session_instance().warn(*args, stacklevel=stacklevel + 1, **kwargs)


class _TracebackHandlerBase(abc.ABC):
    """Handler for user errors during parse and build.

    This detects the environment within which the user is running Finesse - either a
    normal Python terminal or script or within IPython or JupyterLab. Depending on the
    environment, either complete tracebacks are shown or else only the error message.

    The behaviour of this handler can be configured globally using
    :func:`.show_tracebacks`.

    Do not instantiate this class directly; use :func:`traceback_handler_instance`.
    """

    def __init__(self):
        self.show_tb = True
        self.etype = None
        self.evalue = None
        self.tb = None
        self.stb = None
        self.text = None

    def store_tb(self):
        self.etype, self.evalue, self.tb = sys.exc_info()

    @abc.abstractmethod
    def _format_tb(self):
        pass

    @abc.abstractmethod
    def get_stb(self):
        pass

    def show_last(self):
        self._format_tb()
        print(self.text)


class _TracebackHandlerInteractive(_TracebackHandlerBase):
    def __init__(self):
        super().__init__()
        assert IPython

        # color_theme has become theme_name in IPython 9
        # https://ipython.readthedocs.io/en/9.0.0/config/details.html#terminal-colors
        if Version(IPython.__version__) < Version("9.0.0"):
            kwargs = {"color_scheme": "Neutral"}
        else:
            kwargs = {"theme_name": "neutral"}
        self.formatter = AutoFormattedTB(mode="Context", tb_offset=1, **kwargs)

    def store_tb(self):
        super().store_tb()
        self._format_tb()

    def _format_tb(self):
        # make sure an exception has been stored
        assert self.etype is not None
        self.stb = self.formatter.structured_traceback(
            self.etype, self.evalue, self.tb, tb_offset=1
        )
        self.text = self.formatter.stb2text(self.stb)

    def get_stb(self):
        if self.show_tb:
            return self.stb
        else:
            return self.stb[-1:]

    def show_last(self, colors=True):
        """Print the latest traceback.

        Parameters
        ----------
        colors : bool, optional
            Use coloured output (using ANSI escape sequences), by default True
            Can set to false if output is saved to a medium that doesn't support it
            (for example, html and pdf docs)
        """
        if (colors and not self.formatter.has_colors) or (
            not colors and self.formatter.has_colors
        ):
            self.formatter.color_toggle()
        return super().show_last()


class _TracebackHandler(_TracebackHandlerBase):
    def _format_tb(self):
        self.text = traceback.format_exc()

    def get_stb(self):
        raise NotImplementedError(
            "Structured traceback not available for non-interactive environment"
        )


class _FinesseSession:
    """Environment-aware session handler.

    This is a wrapper around Python print and warning functions that obeys the user's
    verbosity preference. It may be expanded in the future to encompass other features.

    This class should not be used directly.
    """

    _verbosity_levels = {
        # Must remain sorted!
        "info": 20,  # Prints and warnings.
        "warn": 10,  # Just warnings.
        "quiet": 0,  # Nothing (except exceptions).
    }

    _default_verbosity_level = "info"

    def __init__(self):
        self._verbosity = None
        self.verbosity = self._verbosity_levels[self._default_verbosity_level]

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        from .utilities import option_list

        try:
            verbosity = self._verbosity_levels[verbosity.casefold()]
        except KeyError:
            raise ValueError(
                f"Verbosity level {repr(verbosity)} doesn't exist. Did you mean "
                f"{option_list(self._verbosity_levels)}?"
            )
        except AttributeError:
            verbosity = int(verbosity)

        self._verbosity = verbosity

    @property
    def level(self):
        """The current verbosity level.

        The level is the first named level at or below the current verbosity setting.
        """
        levelitems = reversed(self._verbosity_levels.items())
        current_level, _ = next(levelitems)
        for level, value in levelitems:
            if value > self.verbosity:
                break
            current_level = level
        return current_level

    def louder(self):
        """Increase verbosity by one level."""
        levels = list(self._verbosity_levels)
        # Go to the verbosity corresponding to the previous index or the start of the
        # levels list.
        previndex = max(levels.index(self.level) - 1, 0)
        _, self.verbosity = list(self._verbosity_levels.items())[previndex]

    def quieter(self):
        """Decrease verbosity by one level."""
        levels = list(self._verbosity_levels)
        # Go to the verbosity corresponding to the next index or the end of the levels
        # list.
        nextindex = min(levels.index(self.level) + 1, len(levels) - 1)
        _, self.verbosity = list(self._verbosity_levels.items())[nextindex]

    def verbose_for(self, level):
        return self.verbosity >= self._verbosity_levels[level.casefold()]

    def info(self, *args, **kwargs):
        if not self.verbose_for("info"):
            return

        print(*args, **kwargs)

    def warn(self, *args, stacklevel=1, **kwargs):
        if not self.verbose_for("warn"):
            return

        # Add 1 to stacklevel since we're wrapping `warnings.warn`, so that the original
        # line that emitted the warning is shown instead.
        stacklevel += 1

        warnings.warn(*args, stacklevel=stacklevel, **kwargs)
