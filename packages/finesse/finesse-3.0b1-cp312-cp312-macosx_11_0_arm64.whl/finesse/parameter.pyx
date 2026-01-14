cimport cython
import math
import numpy as np
cimport numpy as np
import textwrap
from enum import Enum
from copy import deepcopy
import logging
import operator
import weakref
import finesse

from collections import namedtuple
from finesse_numpydoc import ClassDoc
from .element import ModelElement
from .exceptions import (
    ComponentNotConnected, ParameterLocked, ModelParameterSelfReferenceError
)
from .env import warn
from .symbols import PYFUNCTION_MAP, Symbol, Resolving, Function
from .utilities import is_iterable
from .exceptions import FinesseException, ExternallyControlledException, NotChangeableDuringSimulation

LOGGER = logging.getLogger(__name__)


# Allowed datatypes for parameters
allowed_datatypes = (int, float, bool, Enum, np.int64, np.float64, np.bool_)


# struct for storing float_parameter information on each element
ParameterInfo = namedtuple(
    "ParameterInfo", (
        "name",
        "description",
        "dtype",
        "dtype_cast",
        "units",
        "is_geometric",
        "changeable_during_simulation"
    )
)

class ParameterRef(Symbol):
    """A symbolic instance of a parameter in the model.

    A parameter is owned by some model element, which can be used to connect its value
    to other aspects of the simulation.
    """

    def __init__(self, param):
        if param is None:
            raise ValueError("ParameterRef cannot reference None")
        self.__param = param
        self.__name = self.parameter.full_name
        self.__cyexpr_name = self.__name.replace(".", "_").lower().encode("UTF-8")
        self.__full_name = self.parameter.full_name

    @property
    def parameter(self):
        return self.__param

    @property
    def name(self):
        return self.__name

    @property
    def full_name(self):
        return self.__full_name

    @property
    def cyexpr_name(self):
        """Name of the parameter reference in ``cyexpr`` compatibility format.

        This is equivalent to :attr:`.ParameterRef.name` but with ``"."``
        replaced with ``"_"``, converted to lower case and encoded
        in UTF-8 format as a ``bytes`` object.

        The above format makes this compatible with passing to the underlying
        math evaluator engine (``tinyexpr``) used via the :mod:`.cyexpr` sub-module.

        .. note::

            This should, typically, never need to be used outside of internal usage. It
            exists primarily to act as the owner for the parameter name strings (avoiding
            dangling pointers in the expression code).

        :`getter`: Returns the ``cyexpr`` compatible name format of the pref name (read-only).
        """
        return self.__cyexpr_name

    @property
    def owner(self):
        return self.parameter.owner

    def __symeq__(self, obj):
        if isinstance(obj, Function):
            return obj == self
        elif isinstance(obj, ParameterRef):
            if obj.parameter is self.parameter:
                return True
            else:
                return False
        elif isinstance(obj, Parameter):
            if obj is self.parameter:
                return True
            else:
                return False
        else:
            # Otherwise it's not another parameter ref, I guess we could
            # also check for numeric equality?
            return False

    def __hash__(self):
        return hash(self.parameter)

    def __deepcopy__(self, memo):
        from finesse.model import Model

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.__dict__.update(deepcopy(self.__dict__, memo))
        return result

    def eval(self, keep_changing_symbols=False, subs=None, keep=None, **kwargs):
        p = self.parameter

        # variables might always need to be kept as it's value is changing
        if keep_changing_symbols and p.is_changing:
            return self

        # Always just keep if requested to
        if keep is not None:
            if self.name == keep:
                return self
            elif is_iterable(keep):
                if self.name in keep or self in keep:
                    return self

        result = None
        if subs is not None and (self.name in subs or self in subs):
            # If we are subbing the value of this symbol
            result = self.substitute(subs)
        else:
            # else lets use it's current value
            result = p.value

        if hasattr(result, "eval"):
            if subs is not None:
                result = result.substitute(subs).eval()
            else:
                result = result.eval()

        return result


cdef class Parameter:

    # __doc__ can't be changed in a cdef, but we can override the property
    # so that when the `help` is used
    @property
    def __doc__(self):
        doc = ClassDoc(type(self.__owner()))
        bkp = "\n"
        for p in doc["Parameters"]:
            if p.name == self.name:
                return textwrap.dedent(f"""{p.name} : {p.type}{bkp}{bkp.join(p.desc)}""")

    def __init__(self, parameter_info, owner):
        from finesse.element import ModelElement
        from finesse.model import Model

        self.__value = None
        self.__cvalue = 0.0
        self.__units = parameter_info.units
        self.__name = parameter_info.name
        self.__datatype = parameter_info.dtype
        self.__datatype_cast = parameter_info.dtype_cast
        self.__description = parameter_info.description
        self.__owner = weakref.ref(owner)
        self.__changeable_during_simulation = parameter_info.changeable_during_simulation
        self._locked = False
        self.__external_setters = {}
        self.__is_tunable = False
        self.__update_state()
        self.__eval_string = False
        self.is_geometric = False

        self.__resolving = False
        self.__disable_state_type_change = False

        if type(owner) != Model:
            if owner.name is None:
                raise ValueError("Owner name should not be None")
            if parameter_info.name is None:
                raise ValueError("Parameter name should not be None")

            self.__full_name = f"{owner.name}.{parameter_info.name}"
            self.__validator = ModelElement._validators[type(owner)][self.name]
            self.__post_validator = ModelElement._post_validators[type(owner)][self.name]
        else:
            # Model parameters don't have a full name as they are global
            self.__full_name = parameter_info.name

        # TODO: (jwp) temporary solution to work around deepcopy complications with Cython
        # inheritance. This would ideally be defined in GeometricParameter which inherits
        # from Parameter. We should determine if a separate class for GeometricParameter
        # is necessary.
        self.is_nr = False

    cdef __cdeepcopy__(self, Parameter new, dict memo) :
        new.__units = self.__units
        new.__name = self.__name
        new.__eval_string = self.__eval_string
        new.__datatype = self.__datatype
        new.__datatype_cast = self.__datatype_cast
        new.__full_name = self.__full_name
        new.__description = self.__description
        new._locked = self._locked
        new.__external_setters = deepcopy(self.__external_setters, memo)
        new.__is_tunable = self.__is_tunable
        new.state = self.state
        new.__value = deepcopy(self.__value, memo)
        new.__cvalue = self.__cvalue
        new.__validator = self.__validator
        new.__post_validator = self.__post_validator
        new.__changeable_during_simulation = self.__changeable_during_simulation
        new.__disable_state_type_change = self.__disable_state_type_change

        # TODO: (jwp) temporary solution, see above.
        new.is_geometric = self.is_geometric

        new.is_nr = self.is_nr

    @property
    def eval_string(self):
        "Whether to cal 'eval' on the parameter value in the string representation"
        return self.__eval_string

    @eval_string.setter
    def eval_string(self, val):
        self.__eval_string = bool(val)

    def __deepcopy__(self, memo):
        new = Parameter.__new__(Parameter)
        memo[id(self)] = new
        self.__cdeepcopy__(new, memo)

        # Manually update the weakrefs to be correct
        id_component = id(self.owner)

        if id_component not in memo:
            # We need to update this reference later on
            # This will be called when the port property
            # is accessed. When this happens we'll peak back
            # at the memo once it has been filled and get
            # the new port reference. After this the refcount
            # for this function should goto zero and be garbage
            # collected
            def update_later():
                new.__owner = weakref.ref(memo[id(self.owner)])

            new.__owner = update_later  # just in case something calls
            # this weakref in the meantime
            memo[id(self.__owner()._model)].after_deepcopy.append(update_later)
        else:
            new.__owner = weakref.ref(memo[id(self.owner)])

        return new

    cdef __update_state(self) :
        prev_state = self.state
        if issubclass(type(self.__value), allowed_datatypes):
            self.state = ParameterState.Numeric
        elif self.__value is None:
            self.state = ParameterState.NONE
        elif isinstance(self.__value, Symbol):
            self.state = ParameterState.Symbolic
        elif callable(self.__value):
            self.state = ParameterState.Unresolved
        else:
            raise Exception(f"Unexpected parameter value '{self.__value}' ({type(self.__value)})")

        if self.__disable_state_type_change and prev_state != self.state:
            raise RuntimeError(f"Trying to chanage {repr(self)} from state {prev_state} to {self.state} which should not be happening.")

    @property
    def units(self):
        if self.__units is None:
            return ""
        return self.__units

    @property
    def name(self):
        return self.__name

    @property
    def datatype(self):
        """The underlying C datatype of this parameter."""
        return self.__datatype

    def datatype_cast(self, value, ignore_failure=False):
        """Casts a value into the datatype of this parameter.

        If ignore_failure is True then if this value cannot be cast it is just returned.
        """
        try:
            return self.__datatype_cast(value)
        except (ValueError, TypeError) as ex:
            if ignore_failure:
                return value
            else:
                raise ex

    @property
    def owner(self):
        """The component/element this parameter is associated with, this could be a
        :class:`finesse.element.ModelElement` or a :class:`finesse.model.Model`."""
        return self.__owner()

    def _set_owner(self, owner):
        self.__owner = owner

    @property
    def locked(self):
        """If locked, this parameters value cannot be changed."""
        return self._locked

    @property
    def is_default_for_owner(self):
        """Whether this parameter is the default for the owning model element."""
        try:
            return self.owner.default_parameter_name == self.name
        except AttributeError:
            return False

    @property
    def changeable_during_simulation(self):
        """True if this parameter cannot be changed during a simulation."""
        return self.__changeable_during_simulation

    @property
    def _model(self):
        """Returns the model that this owner is connected to. Raises an exception if it
        is not connected to anything to stop code accidently using unconnected owner by
        accident.

        Returns
        -------
        :class:`.model.Model`

        Raises
        ------
        :class:`.exceptions.ComponentNotConnected`
        """
        if self.__owner() is None:
            raise ComponentNotConnected("Lost weak reference")
        elif isinstance(self.__owner(), finesse.model.Model):
            return self.__owner()
        else:
            return self.__owner()._model

    @property
    def full_name(self):
        return self.__full_name

    @property
    def description(self):
        return self.__description

    @property
    def ref(self):
        """Returns a reference to this parameter's value to be used in symbolic
        expressions."""
        return ParameterRef(self)

    cdef bint _is_changing(self) noexcept:
        if self.state == ParameterState.Symbolic:
            return self.value.is_changing

        return self.__is_tunable

    @property
    def is_changing(self):
        """True if this parameter will be changing during a simulation."""
        return self._is_changing()

    @property
    def is_tunable(self):
        """True if this parameter will be directly changed during a simulation."""
        return self.__is_tunable

    @property
    def is_symbolic(self):
        """True if this parameter's value is symbolic."""
        return self.state == ParameterState.Symbolic

    @is_tunable.setter
    def is_tunable(self, bint value):
        if not self.changeable_during_simulation:
            raise NotChangeableDuringSimulation(f"The parameter {self.full_name} cannot be changed during a simulation")
        if self._locked:
            raise ParameterLocked()
        if self.is_externally_controlled:
            raise ExternallyControlledException(f"{repr(self)} is being controlled by {tuple(self.__external_setters.keys())}, so it cannot be tuned directly.")
        if self.state == ParameterState.Symbolic:
            raise FinesseException(
                f"{repr(self)} depends on a symbolic value so it cannot be directly changed. Instead try changing one of its dependencies: {self.value.parameters()}"
            )

        self.__is_tunable = value

    def resolve(self):
        """When this parameters value has some dependency whose value has not yet been
        set, like during parsing, its value will be a callable object, this method will
        call this function to return the value."""
        self.__resolving = True

        if callable(self.value):
            self.value = self.value(self.owner._model)

        self.__resolving = False
        self.__update_state()

    def lambdify(self, *args):
        """Returns a lambda function that returns the value of this parameter.

        Parameters in a symbolic function can be kept as variables by passing
        the Parameter object as optional arguments. The returned lambda function
        will then have len(args) arguments - effectively subsituting values at
        call time.
        """
        if self.state == ParameterState.Symbolic:
            refs = {**self.owner._model.elements, **PYFUNCTION_MAP}
            sym_str = str(self.value)
            ARGS = []
            for i, arg in enumerate(args):
                ARGS.append(arg.full_name.replace(".", "__"))
                sym_str = sym_str.replace(arg.full_name, ARGS[-1])
            return eval(f'lambda {",".join(ARGS)}: {sym_str}', refs)
        else:
            # if len(args) > 0:
            #     raise Exception("Can't specify symbolic arguments to lambdify if this parameter isn't symbolic.")
            return lambda *x: self.value

    def eval(self, bint keep_changing_symbols=False):
        """Evaluates the value of this parameter.

        If the parameter is dependant on some symbolic statement this will evaluate
        that. If it is not the value itself is returned. This method should be used when
        filling in matrices for computing solutions of a model.
        """
        if self.state == ParameterState.Unresolved:
            self.resolve()

        if self.state == ParameterState.Symbolic:
            y = self.value.eval(keep_changing_symbols=keep_changing_symbols)
            if self.__validator is None:
                return y
            else:
                return self.__validator(self.owner, y)

        else:
            return self.value

    cdef _get_value(self) :
        return self.__value

    @property
    def value(self):
        return self._get_value()

    def set_external_setter(self, element, symbol):
        """Sets an element as an external controller of the value of this parameter. It
        is used in cases where an element is physically imposing its value onto this
        one, such as degrees of freedom.

        Parameters
        ----------
        element : ModelElement
            Element that will be controlling this parameter

        symbol : symbolic expression
            The expression that this element is imposing upon the parameter.
        """
        if element in self.__external_setters:
            raise Exception(f"{repr(element)} is already an external setter of {repr(self)}")
        self.__external_setters[element] = symbol
        self._set_value((self.value + symbol).sympy_simplify())

    def remove_external_setter(self, element):
        """Stops an element from being an external setter.

        Parameters
        ----------
        element : ModelElement
            Element that is controlling this parameter
        """
        if element not in self.__external_setters:
            raise Exception(f"{repr(element)} is not an external setter of {repr(self)}")
        # Use sympy to simplify the expression to remove the symbol
        self._set_value((self.value - self.__external_setters[element]).sympy_simplify())
        del self.__external_setters[element]

    def _get_unset_value(self):
        """Returns what the value of this parameter without any external setters."""
        if not self.is_externally_controlled:
            return self.__value
        else:
            v = self.__value
            for x in self.__external_setters.values():
                v -= x
            return v.sympy_simplify()

    @property
    def is_externally_controlled(self):
        "Whether this parameter is being externally controlled by another element."
        return len(self.__external_setters) > 0

    def _reset_cvalue(self):
        """Resets the C-level value, to be used in clean-up stage of an action."""
        self.__cvalue =  self.__datatype_cast(self.eval()) # cast to correct datatype

    cdef _set_value(self, value) :
        from finesse.element import ModelElement
        cdef bint is_symbol = isinstance(value, Symbol)
        cdef bint is_callable = (
            isinstance(value, Resolving)
            or getattr(value, "contains_unresolved_symbol", False)
        )

        if self.locked:
            if self.state == ParameterState.Symbolic:
                raise ParameterLocked(f"Parameter {repr(self)}'s value is symbolic so it cannot be directly set")
            else:
                raise ParameterLocked(f"Parameter {repr(self)} is locked")

        if is_symbol:
            for p in value.parameters():
                if p == self.ref:
                    raise ModelParameterSelfReferenceError(value, self)

        if self.__is_tunable and self.state == ParameterState.Symbolic:
            warn(
                f"{repr(self)}: setting `is_tunable` to False as new value is "
                f"symbolic; is_tunable was previously True"
            )
            self.__is_tunable = False

        if is_symbol or value is None or is_callable:
            # Don't cast here as need to keep original object
            self.__value = value
        elif self.__validator is None:
            self.__value = self.__datatype_cast(value)
        else:
            self.__value = self.__validator(self.owner, self.__datatype_cast(value))

        # post validation step so that RTL can be checked with all values updated
        if self.__post_validator is not None:
            self.__post_validator(self.owner)

        # Correspondingly set the low-level __cvalue as long as value
        # is valid and not in an unresolved state
        if value is not None and not is_callable:
            try:
                self.__cvalue =  self.__datatype_cast(self.__value)
            # Return of self.eval is allowed to be None, unfortunately, so
            # take care of that here (any other type error would invariably
            # show up earlier than this anyway)
            except TypeError:
                pass

        self.__update_state()

    @value.setter
    def value(self, value):
        #if self.is_externally_controlled:
        #    raise ExternallyControlledException(f"Model parameter {repr(self)} is being externally controlled by {tuple(self.__external_setters.keys())}")

        self._set_value(value)

    cdef int set_double_value(self, double value) except -1:
        """UNSAFE, Only use when you know the parameter should be changing!"""
        # TODO (sjr) Not sure setting of self.__value here is reqd
        #            anymore as just setting __cvalue should suffice
        #            here now (as this method should only be called
        #            during simulations anyway)
        if self.__validator is None:
            self.__value = value
        else:
            self.__value = self.__validator(self.owner, value)

        # TODO currently only surfaces call 'check_rtl' here, may be slow to run
        # a python function on every parameter update? Although it is also done above
        # in the validation call
        if self.__post_validator is not None:
            self.__post_validator(self.owner)

        self.__cvalue = value
        return 0

    def _set(self, value):
        self.value = value

    def __str__(self):
        units = self.units
        if units:
            units = " " + units
        if isinstance(self.value, (Parameter, ParameterRef)) and self.eval_string:
            value = self.value.eval()
        else:
            value = self.value
        return f"{value}{units}"

    def __repr__(self):
        if self.__owner() is None:
            return f"<LOST WEAKREF.{self.name}={str(self.value)}>"
        else:
            return f"<{self.full_name}={str(self.value)} @ {hex(id(self))}>"

    def __add__(A, B):
        return _operator(A, B, operator.add)

    def __radd__(self, other):
        return other + self.value

    def __sub__(A, B):
        return _operator(A, B, operator.sub)

    def __rsub__(self, other):
        return other - self.value

    def __mul__(A, B):
        return _operator(A, B, operator.mul)

    def __rmul__(self, other):
        return other * self.value

    def __truediv__(A, B):
        return _operator(A, B, operator.truediv)

    def __rtruediv__(self, other):
        return  other / self.value

    def __floordiv__(A, B):
        return _operator(A, B, operator.floordiv)

    def __rfloordiv__(self, other):
        return other // self.value

    def __mod__(A, B):
        return _operator(A, B, operator.mod)

    def __rmod__(self, other):
        return other % self.value

    def __divmod__(A, B):
        return _operator(A, B, operator.divmod)

    def __rdivmod__(self, other):
        return divmod(other, self.value)

    def __pow__(self, other, order):
        return pow(self.value, other, order)

    def __rpow__(self, other, order):
        return pow(other, self.value, order)

    def __neg__(self):
        return -1 * self.value

    def __pos__(self):
        return self.value

    def __abs__(self):
        return abs(self.value)

    def __complex__(self):
        return complex(self.value)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __round__(self, ndigits=None):
        return round(self.value, ndigits)

    def __trunc__(self):
        return math.trunc(self.value)

    def __floor__(self):
        return math.floor(self.value)

    def __ceil__(self):
        return math.ceil(self.value)

    def __hash__(self):
        return id(self)

    def __eq__(A, B):
        return A.value == B or (A.value == B.value if hasattr(B, "value") else False)

    def __ge__(A, B):
        return A.value >= B or (A.value >= B.value if hasattr(B, "value") else False)

    def __gt__(A, B):
        return A.value > B or (A.value > B.value if hasattr(B, "value") else False)

    def __le__(A, B):
        return A.value <= B or (A.value <= B.value if hasattr(B, "value") else False)

    def __lt__(A, B):
        return A.value < B or (A.value < B.value if hasattr(B, "value") else False)

    def __bool__(self):
        return bool(self.value)

    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        if method == "__call__":
            ARGS = (
                (_.value if isinstance(_, Parameter) else _) for _ in args
            )
            return ufunc(*ARGS, **kwargs)
        return NotImplemented



cdef class GeometricParameter(Parameter):
    """Specialised parameter class for variables which are dependencies of ABCD
    matrices. These include surface radii of curvature, lens focal lengths, beamsplitter
    angles of incidence, space lengths and space refractive indices.

    When setting the value of a GeometricParameter *outside of a simulation*, the dependent ABCD
    matrices get updated via the `update_abcd_matrices` C method. Inside a simulation,
    the ABCD matrix elements are updated in a much more efficient way via the connector
    workspaces.
    """
    def __init__(self, parameter_info, owner):
        if not isinstance(owner, finesse.element.ModelElement):
            raise ValueError(f"owner of a geometric parmameter must be a ModelElement, not `{repr(owner)}`")

        super().__init__(parameter_info, owner)
        self.is_geometric = True
        self.is_nr = self.name == "nr"

    def __deepcopy__(self, memo):
        new = GeometricParameter.__new__(GeometricParameter)
        memo[id(self)] = new
        self.__cdeepcopy__(new, memo)

        # Manually update the weakrefs to be correct
        id_component = id(self.owner)

        if id_component not in memo:
            # We need to update this reference later on
            # This will be called when the port property
            # is accessed. When this happens we'll peak back
            # at the memo once it has been filled and get
            # the new port reference. After this the refcount
            # for this function should goto zero and be garbage
            # collected
            def update_later():
                new._set_owner(weakref.ref(memo[id(self.owner)]))

            new._set_owner(update_later)  # just in case something calls
            # this weakref in the meantime
            memo[id(self.owner._model)].after_deepcopy.append(update_later)
        else:
            new._set_owner(weakref.ref(memo[id(self.owner)]))

        return new

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void update_abcd_matrices(self) noexcept:
        """Method for updating dependent ABCD matrices of the parameter *outside* of a
        simulation."""
        cdef:
            dict abcd_matrices = self.owner._abcd_matrices
            list matrix_handles = list(abcd_matrices.values())

            object full_symbolic # Full symbolic ABCD matrix
            double[:, ::1] M_num # Numeric ABCD matrix

            object[:, ::1] M_sym # Actual symbolic matrix to use

        if self.is_nr: # Parameter is a refractive index
            from finesse.components import Surface
            if self.owner.portA is not None:
                p1_comp = self.owner.portA.component
            else:
                p1_comp = None
            if self.owner.portB is not None:
                p2_comp = self.owner.portB.component
            else:
                p2_comp = None
            # and if either / both ports are associated with Surfaces
            # then append their ABCD matrices so that they get updated
            # too (as some of them depend on nr of attached space)
            if isinstance(p1_comp, Surface):
                matrix_handles.extend(list(p1_comp._abcd_matrices.values()))
            if isinstance(p2_comp, Surface):
                matrix_handles.extend(list(p2_comp._abcd_matrices.values()))

        cdef Py_ssize_t i, j, k
        cdef Py_ssize_t N = len(matrix_handles)
        for i in range(N):
            full_symbolic = matrix_handles[i][0]
            # Total reflection means no symbolic matrix is formed
            # so ignore it and move on
            if full_symbolic is None:
                continue

            M_sym = full_symbolic
            M_num = matrix_handles[i][1]

            for j in range(2):
                for k in range(2):
                    M_num[j][k] = float(M_sym[j][k])

    # NOTE (sjr) ABCD matrices are updated using cyexpr's in the relevant
    #            workspace during a simulation, so we don't override
    #            set_double_value here. The update_abcd_matrices method
    #            is only called when using the value setter, which will be
    #            used outside of a simulation context.

    @property
    def value(self):
        return Parameter._get_value(self)

    @value.setter
    def value(self, value):
        Parameter._set_value(self, value)
        self.update_abcd_matrices()


class parameterproperty(property):
    """Descriptor class for declaring a simulation parameter. A simulation parameter is
    one that can be changed during a simulation and affect the resulting outputs. The
    idea is that output dependant variables should be marked as having been changed or
    will be changed during a simulation run. This allows us to then optimise parts of
    the model, as we can determine what will or will not be changing. This descriptor is
    paired with the :class:Parameter.

    Parameters can then be superficially locked once a model has been built so
    accidentally changing some parameter that isn't expected to change can flag a
    warning.
    """

    def __fget(self, x):
        return getattr(x, f"__param_{self.full_name}")

    def __fset(self, x, v):
        return getattr(x, f"__param_{self.full_name}")._set(v)

    def __flocked(self, x):
        getattr(x, f"__param_{self.full_name}").locked

    def __init__(self, full_name, doc=None):
        self.full_name = full_name
        super().__init__(self.__fget, self.__fset, doc=doc)
        self.__doc__ = doc
        self.flocked = self.__flocked

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            return self.fget(obj)

    def __set__(self, obj, value):
        if self.flocked(obj):
            raise ParameterLocked(f"{obj} is locked during this simulation")
        else:
            self.fset(obj, value)

    def __delete__(self, obj):
        raise AttributeError("can't delete parameter")

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)


def float_parameter(
    name, description, units=None, validate=None, post_validate=None,
    is_default=False, is_geometric=False, changeable_during_simulation=True
):
    """A parameter of an element whose value is decribed by a 64-bit floating point
    number."""
    return model_parameter(
        name, description, float, float,
        units=units, validate=validate, post_validate=post_validate,
        is_default=is_default, is_geometric=is_geometric,
        changeable_during_simulation=changeable_during_simulation
    )


def int_parameter(
    name, description, units=None, validate=None, post_validate=None,
    is_default=False, is_geometric=False, changeable_during_simulation=True
):
    """A parameter of an element whose value is decribed by a 64-bit integer number."""
    return model_parameter(
        name, description, int, int,
        units=units, validate=validate, post_validate=post_validate,
        is_default=is_default, is_geometric=is_geometric,
        changeable_during_simulation=changeable_during_simulation
    )

class EnumCaster:
    """Enums are irritating as they don't act like normal types. You need
    to getitem to go from value to key. They also don't cast themselves
    back to themselves as float(1.0) would.
    """

    def __init__(self, enum, validate):
        self.enum = enum
        self.validate = validate

    def __call__(self, value):
        if type(value) is self.enum:
            return value
        else:
            try:
                return self.enum[value]
            except KeyError as e:
                if self.validate:
                    return value
                else:
                    raise ValueError(
                        f"'{value}' is not a valid {self.enum} enum, valid options: "
                        f"{self.enum.__members__.keys()}") from e


def enum_parameter(
    name, description, enum, units=None, validate=None, post_validate=None,
    is_default=False, is_geometric=False, changeable_during_simulation=True
):
    """A parameter of an element whose value is decribed by a Enum definition.

    Enum must only use integer values to describe its members. Unlike a general python
    Enum which can use strings.
    """
    if not issubclass(enum, Enum):
        raise Exception("enum argument should be an enum.Enum type object")

    for _ in enum.__members__.values():
        if type(_.value) is not int:
            raise Exception(f"Value for item {repr(_)} in {enum} must be an integer")

    return model_parameter(
        name, description, int, EnumCaster(enum, validate),
        units=units, validate=validate, post_validate=post_validate,
        is_default=is_default, is_geometric=is_geometric,
        changeable_during_simulation=changeable_during_simulation
    )


def bool_parameter(
    name, description, units=None, validate=None, post_validate=None,
    is_default=False, is_geometric=False, changeable_during_simulation=True
):
    """A parameter of an element whose value is decribed by a True or False value."""
    return model_parameter(
        name, description, bool, bool,
        units=units, validate=validate, post_validate=post_validate,
        is_default=is_default, is_geometric=is_geometric,
        changeable_during_simulation=changeable_during_simulation
    )


class Validator():
    def __init__(self, validate):
        self.validate = validate

    def __call__(self, x, v):
        return getattr(x, self.validate)(v)

class PostValidator():
    def __init__(self, post_validate):
        self.post_validate = post_validate

    def __call__(self, x):
        return getattr(x, self.post_validate)()



cdef object model_parameter(
    str name, str description, type _type, object _type_cast, str units, str validate, str post_validate,
    bint is_default, bint is_geometric, bint changeable_during_simulation
) :
    """Decorator to register a model parameter with a double datatype field in the
    class.

    This shouldn't be called by users. Use the [type]_parameter functions above instead.
    """
    if not issubclass(_type, allowed_datatypes):
        raise Exception(f"Data type {_type} not allowed ({allowed_datatypes})")

    if validate is None:
        vld = None
    else:
        vld = Validator(validate)

    if post_validate is None:
        post_vld = None
    else:
        post_vld = PostValidator(post_validate)


    def func(cls):
        doc = description # use short description if no doc can be found
        try:
            # TODO : numpydoc needs to be changed to use something less heavy on requirements
            from numpydoc.docscrape import ClassDoc
            cdoc = ClassDoc(cls)
            bkp = "\n"
            for p in cdoc["Parameters"]:
                if p.name == name:
                    doc = textwrap.dedent(f"""{p.name} : {p.type}{bkp}{bkp.join(p.desc)}""")
        except ImportError as ex:
            pass

        p = parameterproperty(
            name,
            doc=doc
        )
        cls._param_dict[cls].append(
            ParameterInfo(
                name, description, _type, _type_cast, units, is_geometric, changeable_during_simulation
            )
        )
        cls._validators[cls][name] = vld
        cls._post_validators[cls][name] = post_vld

        if is_default:
            if cls in cls._default_parameter_name:
                raise ValueError(
                    f"is_default cannot be set for more than one model parameter on {cls!r}"
                )

            cls._default_parameter_name[cls] = name

        setattr(cls, name, p)
        return cls

    return func


def info_parameter(name, description, units=None):
    """Decorator to register an info parameter field in the class.

    Info parameters are purely informative properties, and cannot be directly scanned
    using an axis.
    """
    def func(cls):
        cls._info_param_dict[cls][name] = (description, units)
        return cls

    return func


def deref(parameter):
    """Get the :class:`.Parameter` from a :class:`.ParameterRef` or :class:`.Parameter`
    (no-op).

    This is useful in actions which require a parameter but may be passed either a
    parameter or parameter reference.
    """
    if isinstance(parameter, ParameterRef):
        parameter = parameter.parameter

    return parameter

def _operator(A, B, op):
    """Used in operater dunder methods in Parameter class, for compatibility with cython
    0.x, since it handles operator methods and the order of their arguments differently
    from cython3.

    See
    https://cython.readthedocs.io/en/latest/src/userguide/special_methods.html#arithmetic-methods
    for details
    """

    if isinstance(A, Parameter):
        return op(A.value, B)
    else:
        return op(A, B.value)
