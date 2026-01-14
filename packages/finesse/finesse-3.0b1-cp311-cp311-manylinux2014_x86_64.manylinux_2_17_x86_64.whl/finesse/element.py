from __future__ import annotations

import weakref
from copy import deepcopy
import logging
import warnings
from typing import TYPE_CHECKING

from .exceptions import ModelParameterDefaultValueError, ContextualValueError
from .utilities.tables import Table
from .freeze import canFreeze

from collections import defaultdict, ChainMap
from finesse.utilities.collections import OrderedSet

if TYPE_CHECKING:
    from finesse import Model

LOGGER = logging.getLogger(__name__)


@canFreeze
class ModelElement:
    """Base for any object which can be an element of a :class:`.Model`.

    When added to a model it will attempt to call the method `_on_add` so that the element can do
    some initialisation if required.

    Parameters
    ----------
    name : str
        Name of newly created model element.
    """

    # A global dictionary to keep a record of all the declared
    # model parameters, validators, etc.
    _param_dict = defaultdict(list)
    _validators = defaultdict(dict)
    _post_validators = defaultdict(dict)
    _default_parameter_name = dict()
    _unique_element = False
    # Info parameters.
    _info_param_dict = defaultdict(dict)

    def __new__(cls, *args, **kwargs):
        instance = super(ModelElement, cls).__new__(cls)
        instance._unfreeze()
        instance._params = []
        instance._info_params = instance._info_param_dict[cls]
        instance._unique_element = bool(cls._unique_element)
        instance._ModelElement__model = None

        return instance

    def __init__(self, name):
        from finesse.utilities import check_name

        self._params_changing = None
        self._params_evald = None
        self._legacy_script_line_number = 0

        try:
            self.__name = check_name(name)
        except ValueError:
            raise ContextualValueError(
                {"name": name},
                "can only contain alphanumeric and underscore characters",
            )

        self._add_to_model_namespace = True
        self._namespace = (".",)

        # Loop through each of the parameters that have been defined
        # in the class and instantiate an object to represent them
        # for this instance of the object
        from finesse.parameter import (
            Parameter,
            GeometricParameter,
        )

        for pinfo in self._param_dict[type(self)]:
            if pinfo.is_geometric:
                p = GeometricParameter(pinfo, self)
            else:
                p = Parameter(pinfo, self)
            setattr(self, f"__param_{pinfo.name}", p)
            self._params.append(p)

    def __str__(self):
        params = {param.name: str(param.value) for param in self.parameters}
        info_params = {param: str(getattr(self, param)) for param in self._info_params}
        values = [repr(self.name)] + [
            f"{k}={v}" for k, v in ChainMap(info_params, params).items()
        ]
        return f"{self.__class__.__name__}({', '.join(values)})"

    def __repr__(self):
        return "<'{}' @ {} ({})>".format(
            self.name, hex(id(self)), self.__class__.__name__
        )

    def __deepcopy__(self, memo):
        new = object.__new__(type(self))
        memo[id(self)] = new

        # For debugging what causes deepcopy errors
        # try:
        #     for key in self.__dict__:
        #         new.__dict__[key] = deepcopy(self.__dict__[key], memo)
        # except Exception:
        #     print("ERROR on deepcopy", key)
        #     raise

        new.__dict__.update(deepcopy(self.__dict__, memo))

        # Manually update the weakrefs to be correct
        new.__model = weakref.ref(memo[id(self.__model())])
        return new

    def info(self, eval_refs=False):
        """Element information.

        Parameters
        ----------
        eval_refs : bool
            Whether to evaluate symbolic references to their numerical values.
            Defaults to False.

        Returns
        -------
        str
            The formatted info.
        """
        params = self.parameter_table(eval_refs=eval_refs, return_str=True)
        info_params = self.info_parameter_table()

        msg = f"{self.__class__.__name__} {self.name}\n"
        msg += "\nParameters:\n"
        if params is not None:
            msg += params
        else:
            msg += "n/a\n"

        if info_params is not None:
            msg += "\nInformation:\n"
            msg += str(self.info_parameter_table())

        return msg

    def parameter_table(self, eval_refs=False, return_str=False):
        """Model parameter table.

        Parameters
        ----------
        eval_refs : bool
            Whether to evaluate symbolic references to their numerical values. Does not
            have effect when `return_str` is False. Defaults to False.
        return_str : bool
            Return str representation instead of :class:`finesse.utilities.tables.Table`
            Necessary when setting `eval_refs` to True. Defaults to False.

        Returns
        -------
        :class:`finesse.utilities.tables.Table`
            The formatted parameter info table.
        str
            String representation of the table, if 'return_str' is True
        None
            If there are no parameters.
        """

        if not self.parameters:
            return

        if eval_refs and not return_str:
            warnings.warn(
                "'eval_refs' will not have any effect when 'return_str' False",
                stacklevel=1,
            )

        table = [["Description", "Value"]]

        try:
            field_rows = []
            old_eval_strings = []
            # Loop in reverse so we can keep the natural order of each element's
            # parameters in its corresponding model parameter class decorators.
            for field in reversed(self.parameters):
                old_eval_strings.append(field.eval_string)
                field.eval_string = eval_refs
                field_rows.append([field.description, field])
            tab = Table(table + field_rows, headerrow=True, headercolumn=False)
            # If we want `eval_refs` to have any effect, we need to convert the table
            # before returning, since we are resetting the `eval_string` attribute in
            # this function
            if return_str:
                return str(tab)
            else:
                return tab
        # we don't want to permanently change the Parameter string representation
        finally:
            for eval_string, field in zip(old_eval_strings, reversed(self.parameters)):
                field.eval_string = eval_string

    def info_parameter_table(self):
        """Info parameter table.

        This provides a table with useful fields in addition to those contained in
        :meth:`.parameter_table`.

        Returns
        -------
        str
            The formatted extra info table.
        None
            If there are no info parameters.
        """

        if not self._info_params:
            return

        table = [["Description", "Value"]]

        # Loop in reverse so we can keep the natural order of each element's parameters in its
        # corresponding info parameter class decorators.
        table += [
            [description, getattr(self, name)]
            for name, (description, _) in reversed(self._info_params.items())
        ]

        return Table(table, headerrow=True, headercolumn=False)

    @property
    def parameters(self):
        """Returns a list of the parameters available for this element."""
        return self._params.copy()

    @property
    def default_parameter_name(self):
        """The default parameter to assume when the component is directly referenced.

        This is used for example in kat script when the component is directly referenced in an
        expression, instead of the model parameter, e.g. &l1 instead of &l1.P.

        Returns
        -------
        str
            The name of the default model parameter.

        None
            If there is no default.
        """
        return self._default_parameter_name.get(self.__class__)

    @property
    def name(self):
        """Name of the element.

        Returns
        -------
        str
            The name of the element.
        """
        return self.__name

    @property
    def ref(self):
        """Reference to the default model parameter, if set.

        Returns
        -------
        :class:`.ParameterRef`
            Reference to the default model parameter, if set.

        Raises
        ------
        ValueError
            If there is no default model parameter set for this element.
        """
        if self.default_parameter_name is None:
            raise ModelParameterDefaultValueError(self)

        return getattr(self, self.default_parameter_name).ref

    @property
    def _model(self):
        """Internal reference to the model this element has been added to.

        Raises
        ------
        ComponentNotConnected when not connected
        """
        from finesse.exceptions import ComponentNotConnected

        if self.__model is None:
            raise ComponentNotConnected(f"{self.name} is not connected to a model")
        else:
            return self.__model()

    @property
    def has_model(self):
        """Returns true if this element has been associated with a Model."""
        return self.__model is not None

    def _set_model(self, model):
        """A :class:`.Model` instance calls this to associate itself with the element.

        .. note::
            This method should never be called by the user, it should
            only be called internally by the :class:`.Model` class.

        Parameters
        ----------
        model : :class:`.Model`
            The model to associate with this element.

        Raises
        ------
        Exception
            If the model is already set for this element.
        """
        if model is not None and self.__model is not None:
            raise Exception("Model is already set for this element")
        if model is None:
            # The element has been removed from a model
            self.__model = None
        else:
            self.__model = weakref.ref(model)

    def _reset_model(self, new_model):
        """Resets the model that this element is associated with.

        Note, this should not be used in normal coding situations. It should only be
        used when writing new elements that override the `__deepcopy__` method.
        """
        self.__model = weakref.ref(new_model)

    def _setup_changing_params(self):
        """For any parameter that has been set to be changing during a simulation this
        method will store them and their evaluated values in the set
        `self._params_changing` and the dict `self._params_evald`."""
        # N.B. Decorators are evaluated from inside - out, so to make the order returned here match
        # the order defined, we must reverse self.parameters
        self._params_changing = OrderedSet(
            p for p in reversed(self.parameters) if p.is_changing
        )
        try:
            self._params_evald = {}
            for p in reversed(self.parameters):
                self._params_evald[p.name] = (
                    p.value.eval() if hasattr(p.value, "eval") else p.value
                )
        except ArithmeticError as ex:
            ex.args = (f"Error evaluating {p}: {str(ex)}",)
            raise ex

    def _clear_changing_params(self):
        """Sets the set `self._params_changing` and the dict `self._params_evald` to
        None after a simulation has completed."""
        self._params_changing = None
        self._params_evald = None

    def _eval_parameters(self):
        """Only call this methods when the model is built. It is optimised for returned
        changed parameter values in this state.

        To get a dictionary of parameter values in other cases use:

        >>>> values = {p.name:p.eval() for p in element.parameters}

        Returns
        -------
        params : dict(str:float)
            Dictionary of parameter values
        params_changing : OrderedSet(str)
            A set of parameter names which are changing.
        """
        # Now we know which are evaluable so no need for repeated checks
        # Also reduce memory bashing creating a ton of dictionaries and
        # reuse just one.
        for p in self._params_changing:
            self._params_evald[p.name] = p.eval()

        return self._params_evald, self._params_changing

    def _on_add(self, model: Model) -> None:
        pass
