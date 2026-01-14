#cython: unraisable_tracebacks=True
"""Base solution interface.

Solution classes contain the output from a Finesse simulation, and convenience methods
for accessing, plotting and serialising that output.

Solutions intentionally do not contain references to the model that produced its
results. This is so that the solution can be serialised without requiring the model that
produced it itself be serialisable.
"""
import logging
from collections.abc import Set, Iterable
from itertools import zip_longest
from functools import reduce
import numpy as np
from finesse.tree cimport TreeNode
from finesse.solutions.array import ArraySolutionSet
from finesse.solutions.array import ArraySolution
from finesse.exceptions import FinesseException

LOGGER = logging.getLogger(__name__)


cdef class ParameterChangingTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.parameters_changing = ()

    def get_all_parameters_changing(self):
        return reduce(
            lambda a, b: (*a, *b.parameters_changing),
            self.get_all_children(),
            (*self.parameters_changing,),
        )


class SolutionSet(Set):
    """
    A SolutionSet is a collection of solution objects that have been generated
    from running a model. When nested analyses have been used then you must then
    extract each of the nested solutions. The SolutionSet object makes this easier
    by collecting a variety of Solutions together so you can select common nested
    solutions within them, or extract some common attribute.

    Take some overly simplistic example here where we have swept some variable
    and performed some other analysis at each step.

    >>> import finesse
    >>> model = finesse.Model()
    >>> model.parse('''
    ... l l1 P=1
    ... pd P l1.p1.o
    ... xaxis(l1.P, lin, 0, 1, 2,
    ...     pre_step=series(
    ...         minimize(P, l1.P)
    ...     )
    ... )
    ... ''')
    >>>
    >>> sol = model.run()
    >>> print(sol)
    - Solution Tree
    ● xaxis - ArraySolution
    ╰──○ pre_step
       ├──○ series
       │  ╰──○ minimize - OptimizeSolution
       ├──○ series
       │  ╰──○ minimize - OptimizeSolution
       ╰──○ series
           ╰──○ minimize - OptimizeSolution

    Here we have an optimisation solution buried in the ``pre_step`` events of the
    axis. We can get them all by simply calling:

    >>> sol['pre_step', 'series', 'minimize']
    <finesse.solutions.base.SolutionSet object at ...>

    You can see which solutions you have selected using:

    >>> sol['pre_step', 'series', 'minimize'].solutions
    [<OptimizeSolution of series/xaxis/pre_step/series/minimize @ ... children=0>,
     <OptimizeSolution of series/xaxis/pre_step/series/minimize @ ... children=0>,
     <OptimizeSolution of series/xaxis/pre_step/series/minimize @ ... children=0>]

    We can select a common attribute from these similar solutions by just acting
    on the SolutionSet, the attribute request is evaluated on each Solution present in
    the set and returned. For example, we can get the `result` attribute from each
    `OptimisationSolution` using:

    >>> print(sol['pre_step', 'series', 'minimize'].result)
    [ final_simplex: (array([[0.00e+00],
            [6.25e-05]]), array([0.00e+00, 6.25e-05]))
                fun: 0.0
            message: 'Optimization terminated successfully.'
               nfev: 6
                nit: 3
             status: 0
            success: True
                  x: array([0.])
      ...
    ]

    The returned attribute request will be a numpy array of objects or numerical
    values. This means it is possible to easily extract an array of values from
    a set of nested solutions.

    Which returns a tuple of the requested attributes from each of the nested solutions.
    You can also slice the solution object, which will again returns a reduced
    SolutionSet:

    >>> sol['pre_step', 'series', 'minimize'][::2]
    <finesse.solutions.base.SolutionSet object at ...>

    Each individual solution can be extracted using the `SolutionSet.solutions`
    attribute which returns a list of solution you can iterate over.
    """

    def __init__(self, solutions):
        if not isinstance(solutions, Iterable):
            raise Exception(f"{solutions} is not iterable")

        self.solutions = lst = []
        for value in solutions:
            if value not in lst:
                lst.append(value)

    def __iter__(self):
        return iter(self.solutions)

    def __contains__(self, value):
        return value in self.solutions

    def __len__(self):
        return len(self.solutions)

    def __getattr__(self, key):
        return np.asarray(tuple(getattr(_, key) for _ in self.solutions))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return SolutionSet(self.solutions[key])
        else:
            return SolutionSet(_[key] for _ in self.solutions)


cdef class BaseSolution(ParameterChangingTreeNode):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.time = 0

    def __str__(self):
        def fn_name(child):
            if type(child) is not BaseSolution:
                r = f" - {child.__class__.__name__}"
            else:
                r = ""
            return child.name + r

        return self.draw_tree(fn_name, title="Solution Tree")

    def __getitem__(self, key):
        try:
            if isinstance(key, (slice, int)):
                return self.children[key]
            elif isinstance(key, str) or not isinstance(key, Iterable):
                rtn = tuple(child for child in self.children if child.name == str(key))
                if len(rtn) == 1:
                    return rtn[0]
                else:
                    # return specific set for certain solutions
                    if isinstance(rtn[0], ArraySolution):
                        return ArraySolutionSet(rtn)
                    else:
                        return SolutionSet(rtn)
            else:  # We're an iterable that isn't a string
                if len(key) == 1:
                    return self[key[0]]
                elif isinstance(key[0], slice):
                    raise NotImplementedError(
                        "Solution indexing only supports slices at the end of a key"
                    )
                else:
                    return self[key[0]][key[1:]]
        except IndexError as ex:
            # One last try if its us
            if isinstance(key, str) and self.name == key:
                return self
            raise FinesseException(f"Could not find an output `{key}` in the solution object {repr(self)}")

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self.get_path()} @ {hex(id(self))} children={len(self.children)}>"

    # NOTE [ssl]: this exists to allow the CLI to plot any solution (so it doesn't need
    # to know ahead of time if a given action is plottable). In general plotting across
    # the solution classes should be made more consistent (see #191).
    def plot(self, *args, show=True, **kwargs):
        """Plot solution(s).

        If the solution contains child solutions, they are plotted in order. Solutions
        without plot arguments are skipped. Positional arguments passed to this method
        are assumed to be :class:`dict` and are unpacked into calls to each child's plot
        method. Global arguments to be passed to all plot methods can be specified
        directly as keyword arguments. Duplicate arguments specified in a positional
        argument :class:`dictionaries <dict>` take precendence over global arguments.

        Parameters
        ----------
        show : :class:`bool`, optional
            Show the figures.

        Other Parameters
        ----------------
        *args
            Sequence of :class:`dict` to use as parameters for the call to each child
            solution's `plot` method.

        **kwargs
            Keyword arguments supported by the child solution(s).

        Notes
        -----
        If the Nth solution contains no plot method, it still consumes the Nth
        positional argument passed to this method.
        """
        import matplotlib.pyplot as plt

        for child, child_kwargs in zip_longest(self.children, args, fillvalue={}):
            if not hasattr(child, "plot"):
                LOGGER.info(f"Skipping {child} as it is not plottable")
                continue

            # Merge child kwargs with global kwargs, overwriting duplicates in favour
            # of the former.
            child_kwargs = {**kwargs, **child_kwargs}

            if "show" not in child_kwargs:
                # Avoid blocking execution, only showing at the end, unless explicitly
                # set in the child kwargs.
                child_kwargs["show"] = False

            child.plot(**child_kwargs)

        if show:
            plt.show()
