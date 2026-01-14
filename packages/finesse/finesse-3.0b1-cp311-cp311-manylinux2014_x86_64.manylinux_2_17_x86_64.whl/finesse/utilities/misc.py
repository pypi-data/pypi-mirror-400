"""Miscellaneous utility functions for any part of Finesse."""

from os import fspath, PathLike
import functools
import re
from itertools import tee
from contextlib import contextmanager, closing, nullcontext
from functools import partial, reduce

import numpy as np


def reduce_getattr(obj, key: str, delimiter: str = "."):
    """Applies a nested getattr with reduce to select an attribute of a nested object
    within `obj`.

    Parameters
    ----------
    obj : object
        Object to search

    key : str
        Delimited string of attributes

    delimiter : str, optional
        Delimiter character of key

    Returns
    -------
    Attribute of object
    """
    attrs = key.strip().split(delimiter)
    return reduce(getattr, attrs, obj)


def calltracker(func):
    """Decorator used for keeping track of whether the current state is inside the
    decorated function or not.

    Sets an attribute `has_been_called` on the function which gets switched on when the
    function is being executed and switched off after the function has returned. This
    allows you to query ``func.has_been_called`` for determining whether the code being
    executed has been called from within `func`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        out = func(*args, **kwargs)
        wrapper.has_been_called = False

        return out

    wrapper.has_been_called = False
    return wrapper


def valid_name(name):
    """Validate the specified name."""
    return re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$").match(name)


def check_name(name):
    """Checks the validity of a component or node name.

    A name is valid if it contains only alphanumeric characters and underscores, and is
    not empty.

    Parameters
    ----------
    name : str
        The name to check.

    Returns
    -------
    name : str
        The name passed to this function if valid.

    Raises
    ------
    ValueError
        If `name` contains non-alphanumeric / underscore characters.
    """
    if not valid_name(name):
        raise ValueError(
            f"'{name}' can only contain alphanumeric and underscore characters"
        )
    return name


def pairwise(iterable):
    """Iterates through each pair in a iterable.

    Parameters
    ----------
    iterable : :py:class:`collections.abc.Iterable`
        An iterable object.

    Returns
    -------
    zip
        A zip object whose `.next()` method returns a tuple where the i-th
        element comes from the i-th iterable argument.
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def find(x, value):
    """Finds `value` in the list `x` and returns its index, returning `None` if `value`
    is not in the list."""
    try:
        return x.index(value)
    except ValueError:
        return None


def find_nearest(x, value, index=False):
    idx = np.argmin(np.abs(x - value))
    if index:
        return idx
    return x[idx]


def is_iterable(obj):
    """Reliable check for whether an object is iterable.

    Note that strings are treated as non-iterable objects
    when performing this check. This will only return true
    for iterable non-str objects.

    Returns
    -------
    flag : bool
        True if `obj` is iterable, False otherwise.
    """
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return not isinstance(obj, str)


@contextmanager
def opened_file(filename, mode):
    """Get an open file regardless of whether a string or an already open file is
    passed.

    Adapted from :func:`numpy.loadtxt`.

    Parameters
    ----------
    filename : str, :class:`pathlib.Path`, or file-like
        The path or file object to ensure is open. If `filename` is an already open file
        object, it is yielded as-is, and is *not* closed after the wrapped context
        exits. If `filename` is a string, it is opened with the specified `mode` and
        yielded, then closed once the wrapped context exits.

    mode : str
        The mode to open `filename` with, if it is not already open.

    Yields
    ------
    :class:`io.FileIO`
        The open file with the specified `mode`.

    Notes
    -----
    If `filename` is an open file, `mode` is ignored; it is the responsibility of the
    calling code to check that it is opened with the correct mode.
    """
    if isinstance(filename, PathLike):
        filename = fspath(filename)

    if isinstance(filename, str):
        fid = open(filename, mode)
        fid_context = closing(fid)
    else:
        fid = filename
        fid_context = nullcontext(fid)

    with fid_context:
        yield fid


def graph_layouts():
    """Available NetworkX and graphviz (if installed) graph plotting layouts."""
    return {**networkx_layouts(), **graphviz_layouts()}


def networkx_layouts():
    """Available NetworkX graph plotting layouts."""
    import inspect
    import networkx

    # Excluded layouts.
    excluded = (
        "rescale",
        # These layouts need the network to first be grouped into sets.
        "bipartite",
        "multipartite_layout",
    )

    layouts = {}
    suffix = "_layout"

    def find_layouts(members):
        for name, func in members:
            if name.startswith("_") or not name.endswith(suffix):
                # Not a public layout.
                continue

            # Strip the "_layout" part.
            name = name[: -len(suffix)]

            if name in excluded:
                continue

            layouts[name] = func

    find_layouts(inspect.getmembers(networkx.drawing.layout, inspect.isfunction))

    return layouts


def graphviz_layouts():
    """Available graphviz graph plotting layouts."""
    import networkx
    from ..env import has_pygraphviz

    layouts = {}

    if has_pygraphviz():
        for layout in ["neato", "dot", "fdp", "sfdp", "circo"]:
            # Returns callable that can be called like `networkx.drawing.layout` members.
            layouts[layout] = partial(
                networkx.drawing.nx_agraph.pygraphviz_layout, prog=layout
            )

    return layouts


def doc_element_parameter_table(cls):
    """Prints table for a particular element class."""
    import finesse
    from finesse.utilities.tables import Table
    from IPython.core.display import HTML

    def process_changeable(pinfo):
        if pinfo.changeable_during_simulation:
            return "✓"
        else:
            return "✗"

    headers = (
        "Name",
        "Description",
        "Units",
        "Data type",
        "Can change during simualation",
    )

    tbl = [headers] + [
        (p.name, p.description, p.units, p.dtype.__name__, process_changeable(p))
        for p in finesse.element.ModelElement._param_dict[cls][::-1]
    ]
    if len(tbl) == 0:
        raise RuntimeError(f"{cls} has no model parameters to display.")

    a = Table(
        tbl,
        headerrow=True,
        headercolumn=False,
        alignment=(("left", "left", "center", "center", "center"),),
    )
    for index, p in enumerate(finesse.element.ModelElement._param_dict[cls][::-1]):
        if p.changeable_during_simulation:
            a.color[index + 1, 4] = (0, 255, 0)
        else:
            a.color[index + 1, 4] = (255, 0, 0)
    return HTML(a.generate_html_table())


class DeprecationHelper:
    """Used for deprecating classes."""

    def __init__(self, old_name, new_name, new_target, until_version):
        self.new_target = new_target
        self.old_name = old_name
        self.new_name = new_name
        self.until_version = until_version

        self.msg = (
            f"{self.old_name} is deprecated as of version {self.until_version}: use "
            f"instead {self.new_name}"
        )

    def _warn(self):
        deprecation_warning(self.msg, self.until_version)

    def __call__(self, *args, **kwargs):
        self._warn()
        return self.new_target(*args, **kwargs)


def deprecation_warning(msg, until_version):
    """Function that warns a user about a deprecation. If the current version is past
    when this feature is deprecated it will raise `DeprecationWarning` instead.

    Parameters
    ----------
    msg : str
        Message to warn user with.
    until_version : str
        PEP 440 version string. After this version an exception is thrown.

    Raises
    ------
    DeprecationWarning
        When current version is >= `until_version`
    """
    from warnings import warn
    from packaging import version
    from finesse import __version__ as finesse_version

    if version.parse(finesse_version) >= version.parse(until_version):
        raise DeprecationWarning(msg)
    else:
        warn(msg, DeprecationWarning, stacklevel=4)


def inheritors(klass: type) -> set[type]:
    """Returns all classes that inherit from ``klass``

    Parameters
    ----------
    klass : type
        Class to get inheritors from

    Returns
    -------
    set[type]
        set of classes that are a subclass of ``klass``
    """
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses
