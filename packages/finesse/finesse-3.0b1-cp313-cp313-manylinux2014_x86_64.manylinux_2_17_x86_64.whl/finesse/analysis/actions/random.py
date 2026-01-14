"""Random collection of Actions that do no warrant a separate module."""

from ...parameter import Parameter
from .base import Action, convert_str_to_parameter
from finesse.solutions import BaseSolution

import logging

LOGGER = logging.getLogger(__name__)


class SaveModelAttrSolution(BaseSolution):
    """
    Attributes
    ----------
    values : dict
        Dictionary of model attribute values
    """


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Plot(Action):
    def __init__(self, name="abcd"):
        super().__init__(name)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        raise NotImplementedError()


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Printer(Action):
    def __init__(self, *args, name="printer", eval=True):
        super().__init__(name)
        self.args = args
        self._eval = eval

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        if self._eval:
            out = []
            for _ in self.args:
                if hasattr(_, "eval"):
                    out.append(_.eval())
                else:
                    out.append(_)
            print(*out)
        else:
            print(*(_ for _ in self.args))


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class PrintModel(Action):
    """An action that prints the model object being currently used to run actions."""

    def __init__(self, name="print_model"):
        super().__init__(name)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        print(state.model)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class StoreModelAttr(Action):
    def __init__(self, *args):
        super().__init__(self.__class__.__name__)
        self.args = tuple(a if isinstance(a, str) else a.full_name for a in args)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        sol = SaveModelAttrSolution(self.name)
        sol.values = {}
        for _ in self.args:
            p = state.model.get(_)
            if hasattr(p, "eval"):
                sol.values[_] = p.eval()
            else:
                sol.values[_] = p
        return sol


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class PrintModelAttr(Action):
    """Prints an attribute of the model being currently used.

    Parameters
    ----------
    *args : (str,)
        Strings input for the attribute to print

    eval : bool, optional
        When `True` symbolic expressions will be evaluated before printing.
        Defaults to `True`.

    prefix : str, optional
        Optional string to print before the attributes

    Examples
    --------
    You can print the current value of parameters and such using:

    >>> PrintModelAttr("m1.R", "bs.phi")
    """

    def __init__(self, *args, eval=True, prefix=""):
        super().__init__(self.__class__.__name__)
        self.args = tuple(a if isinstance(a, str) else a.full_name for a in args)
        self.prefix = prefix
        self._eval = eval

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        out = [self.prefix]
        for _ in self.args:
            obj = state.model.get(_)
            if hasattr(obj, "eval") and self._eval:
                out.append(f"{_}={obj.eval()}")
            else:
                out.append(f"{_}={obj}")
        print(*out)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Change(Action):
    """Changes a model Parameter to some value during an analysis.

    Parameters
    ----------
    change_dict : dict, optional
        Dictionary of parameter:value pairs to change.
    relative : bool, optional
        Whether to increment from the parameters current value or not
    name : str, optional
        Name of action
    **kwargs
        Alternative method to specify parameter:value pairs to change

    Examples
    --------
    A simple change of a parameter between running two `noxaxis` analyses:

    >>> model = finesse.script.parse("l L1 P=1")
    >>> model.run('series(noxaxis(), change(L1.P=2), noxaxis())')

    Or increment from the current value:
    >>> model.run('series(noxaxis(), change(L1.P=1, relative=True), noxaxis())')
    """

    def __init__(self, change_dict=None, *, relative=False, name="change", **kwargs):
        super().__init__(name)
        self.change_dict = change_dict
        self.kwargs = kwargs
        self.relative = relative

    @property
    def change_kwargs(self):
        kwargs = self.kwargs or {}
        if self.change_dict:
            kwargs.update(self.change_dict)
        return kwargs

    def _requests(self, model, memo, first=True):
        for el in self.change_kwargs.keys():
            p = convert_str_to_parameter(model, el)
            if isinstance(p, Parameter):
                memo["changing_parameters"].append(el)
            else:
                raise TypeError(
                    f"{el} is not a name of a Parameter or Component in the model"
                )

    def _do(self, state):
        for el, val in self.change_kwargs.items():
            p = convert_str_to_parameter(state.model, el)
            if self.relative:
                p.value += val
            else:
                p.value = val


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Execute(Action):
    """An action that will execute the function passed to it when it is run.

    Parameters
    ----------
    do_fn : function
        A function that takes an AnalysisState, and the name of the Exec action as its
        only arguments. If this function returns a
        :class:`finesse.solutions.base.BaseSolution` object then it will be added to the
        simulations solution to return to the user.
    parameters : list, optional
        A list of parameters that will be changed by do_fn, if any.
    name : str
        The name to give this action.

    Examples
    --------
    A simple function to execute might use a pattern such as this, which generates
    a Solution that is returned back to the user.

    >>> from finesse.solutions import SimpleSolution
    >>> def my_action(state, name):
    ...     sol = SimpleSolution(name)
    ...     return sol

    The :class:`finesse.solutions.simple.SimpleSolution` object is just an object you
    can store anything you want in. You can extract any state information about the
    simulation or model and store it here. This allows you to probe and store details
    that might not be available as a detector, for example.
    """

    def __init__(self, do_fn, parameters=None, name="execute"):
        super().__init__(name)
        self.do_fn = do_fn
        self.parameters = parameters

    def _do(self, state):
        sol = self.do_fn(state, self.name)
        if isinstance(sol, BaseSolution):
            return sol

    def _requests(self, model, memo, first=True):
        if self.parameters is not None:
            memo["changing_parameters"].extend(self.parameters)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class UpdateMaps(Action):
    """Update any maps that might be changing in the simulation."""

    def __init__(self, name="update_maps", *args, **kwargs):
        super().__init__(name)
        self.args = args
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        return None

    def _do(self, state):
        state.sim.update_map_data()


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class LogModelAttribute(Action):
    def __init__(self, *attrs):
        super().__init__("print_parmeter")
        self.attrs = attrs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        LOGGER.info(*(f"{_}={state.model.get(str(_))}" for _ in self.attrs))


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Scale(Action):
    """Action for scaling simulation outputs by some fixed amount. Included for
    compatibility with legacy Finesse code. New users should apply any desired scalings
    manually from Python.

    Parameters
    ----------
    detectors : dict
        A dictionary of `detector name: scaling factor` mappings.
    """

    def __init__(self, scales: dict, **kwargs):
        super().__init__(None)
        self.kwargs = kwargs
        self.scales = scales

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        sol = state.previous_solution
        for det, fac in self.scales.items():
            sol._outputs[det][()] *= fac


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class MakeTransparent(Action):
    """Action to make all provided surfaces transparent. Simply sets the reflectivity to
    zero and transmitivity to one.

    Parameters
    ----------
    surfaces : list
        A list of surface component names to be made transparent.
    """

    def __init__(self, surfaces, name="make transparent"):
        super().__init__(name)
        self.surfaces = surfaces

    def _do(self, state):
        for name, el in state.sim.model.elements.items():
            if name in self.surfaces:
                el.set_RTL(R=0, T=1)

    def _requests(self, model, memo, first=True):
        for name, el in model.elements.items():
            if name in self.surfaces:
                memo["changing_parameters"].extend(
                    [el.R.full_name, el.T.full_name, el.L.full_name]
                )
