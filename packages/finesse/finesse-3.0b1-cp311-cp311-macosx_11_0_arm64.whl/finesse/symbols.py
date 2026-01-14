"""Symbolic manipulations (`expand`, `collect`, etc.) are based on the book:

Cohen JS. Computer algebra and symbolic computation: mathematical methods. First
edition, 2003.
"""

import abc
import logging
import operator
import warnings
from contextlib import contextmanager
from functools import reduce
from numbers import Number

import numpy as np
from packaging.version import parse

from collections import defaultdict

from finesse import constants
from finesse.exceptions import FinesseException, EvaluateResolvingSymbolError
from finesse.utilities import is_iterable
from finesse.utilities import OrderedSet
import finesse.cymath.ufuncs as ufuncs

LOGGER = logging.getLogger(__name__)

MAKE_LOP = lambda name, opfn: lambda self, other: Function(name, opfn, self, other)
MAKE_ROP = lambda name, opfn: lambda self, other: Function(name, opfn, other, self)

# Default no simplification happens, must wrap symbol code that needs it
# with the context manager below. When flagged symbols will attempt to simplify
# themselves, using a standardised ordering of arguments. Only +, *, and ** operators
# are used in simplified symbols which allow various symbolic simplification
# algorithms to be used.
_SIMPLIFICATION_ENABLED = False  # Global flag to state if simplification will happen


@contextmanager
def simplification(allow_flagged=False):
    """When used any symbolic operations will apply various simplification rules rather
    than recording everything symbolic operation, to preserve intent. This is useful
    when you want situations like 0*a -> 0, or a*a -> a**2. A complete simplification is
    not applied but it will generally yeild more efficient symbolic expressions. Intent
    preservation is required by KatScript so that it can serialise and deserialise
    (unparse and parse) a model into a script form without losing specific equations.
    For example, it often useful to record how many minus signs or factors of two have
    been used in an expression, rather than cancelling them out for record keeping.

    Parameters
    ----------
    allow_flagged : bool, optional
        When True, it will not throw an error if already in a simplification state.
    """
    global _SIMPLIFICATION_ENABLED

    if allow_flagged and _SIMPLIFICATION_ENABLED:
        yield
    else:
        if _SIMPLIFICATION_ENABLED is True:
            raise RuntimeError("Simplification has already been enabled")

        try:
            _SIMPLIFICATION_ENABLED = True
            yield
        finally:
            _SIMPLIFICATION_ENABLED = False


def base_exponent(y):
    try:
        if y.op is operator.pow:
            return y.args[0], y.args[1]
        else:
            return y, Constant(1)
    except AttributeError:
        return y, Constant(1)


def operator_add(*args):
    return reduce(operator.add, args)


def operator_mul(*args):
    return reduce(operator.mul, args)


def operator_sub(*args):
    return reduce(operator.sub, args)


def add_sort_key(a):
    try:
        # chr(58) is the character after 9 so
        # numerical numbers come first.
        if a.op is operator_add:
            return chr(58)
        elif a.op is operator.pow:
            return chr(58) + str(a.args[0]) + str(a.args[1])
        else:
            return str(a)
    except AttributeError:
        if hasattr(a, "name"):
            return a.name
        else:
            return str(a)


def MAKE_simplify_add(dir):
    def simplify_add(self, other):
        if not _SIMPLIFICATION_ENABLED:
            if dir == "LOP":
                return Function("+", operator.add, self, other)
            else:
                return Function("+", operator.add, other, self)

        if isinstance(self, Number) and np.all(self == 0):
            return other
        elif isinstance(other, Number) and np.all(other == 0):
            return self
        elif type(self) is Constant and type(other) is Constant:
            if self.is_named and other.is_named:
                if self == other:
                    return 2 * self
                else:
                    return self + other
            elif self.is_named ^ other.is_named:
                if dir == "LOP":
                    return Function("+", operator_add, self, other)
                else:
                    return Function("+", operator_add, other, self)
            else:
                return Constant(self.value + other.value)
        else:

            def process(a):
                try:
                    if a.op is operator_add:
                        a = a.args
                    else:
                        a = (a,)
                except AttributeError:
                    a = (a,)
                return a

            a = process(self)
            b = process(other)

            args = [*a, *b]
            # Collect all the terms together. Whilst `collect` could be used
            # it has the potential for infinite loops and extra steps not needed
            terms = defaultdict(list)  # each of the terms and its multiplier

            for x in args:
                c, t = coefficient_and_term(x)
                terms[t].append(c)

            collected_args = []
            for k, v in terms.items():
                if k is None:  # constants
                    # append indvidually and avoid using `sum` to stop infinite loops
                    # don't include zeros in simplification
                    for k in v:
                        if k != 0:
                            collected_args.append(k)
                else:
                    s = sum(v)
                    if s != 0:
                        collected_args.append(s * k)

            if len(collected_args) == 0:
                rtn = Constant(0)
            elif len(collected_args) == 1:
                rtn = collected_args[0]
            else:
                collected_args.sort(key=add_sort_key)
                rtn = Function("+", operator_add, *collected_args)
            return rtn

    return simplify_add


def mul_sort_key(a):
    """Sorting key for multiplication arguments. Puts constants first then others"""
    if isinstance(a, (Number, Constant)):
        return chr(0) + str(a)
    else:
        try:
            if a.op is operator_add:
                return str(a)
            elif a.op is operator.pow:
                return str(a.args[0]) + str(a.args[1])
            elif hasattr(a, "name"):
                return a.name
        except AttributeError:
            return str(a)


def reduce_mul_args(args):
    """Sorts and reduces a multiply operation arguments.

    Collect constants and sort variables by their `str`.
    """

    def _reduce_mul_args(a, b):
        b = as_symbol(b)  # need this in case arg is a float/int type
        # Assumes first element is a numeric constant and
        # store all constants there
        if type(b) is Constant:
            if len(a) >= 1:
                if b.is_named:
                    a[0].append(b)
                else:
                    a[0][0] = Constant(a[0][0].value * b.value)
            else:
                a[0].append(b)
        elif type(b) is Matrix:
            a[1].append(b)
        else:
            a[0].append(b)
        return a

    def _reduce_exp_args(a, b):
        if hasattr(b, "op") and b.op == np.exp:
            a[1] += b.args[0]
        else:
            a[0].append(b)
        return a

    def _reduce_mul_args_pows(a, b):
        base, exp = base_exponent(b)
        if np.all(a[-1][0] == base):
            a[-1][1] += exp
        else:
            a.append([base, exp])
        return a

    if len(args) > 1:
        scalars, matrices = reduce(_reduce_mul_args, args, ([Constant(1)], []))
        if np.all(scalars[0] == 1):
            if len(scalars) == 1:
                return [1]
            else:
                scalars.pop(0)
        # Exp function is an unusual one because it is actually a power function
        # so we need to collect it as if it was
        non_exp_args, exp_arg = reduce(_reduce_exp_args, scalars, [[1], 0])
        scalars = non_exp_args
        if exp_arg != 0:
            # if there is an exp arg then it needs to be added to the list
            # of non exp args
            scalars.append(np.exp(exp_arg))

        # Sort arguments alphabetically using str form of symbols
        scalars.sort(key=mul_sort_key)
        # Now it's ordered, powers will be grouped
        # together so we can reduce them too
        pow_args = reduce(
            _reduce_mul_args_pows, scalars[1:], [list(base_exponent(scalars[0]))]
        )
        # any 0**n or 1**n simplify out
        args = list(b**e for b, e in pow_args if e != 0 and b != 1)
        args.extend(matrices)

    return args


def MAKE_simplify_mul(dir):
    def simplify_mul(self, other):
        if not _SIMPLIFICATION_ENABLED:
            if dir == "LOP":
                return Function("*", operator.mul, self, other)
            else:
                return Function("*", operator.mul, other, self)

        # Check if an obvious simplication can be made here when 0 or 1 are used
        if isinstance(self, np.ndarray):
            if np.all(self == 0):
                return 0
            elif np.all(self == 1):
                return other

        if isinstance(other, np.ndarray):
            if np.all(other == 0):
                return 0
            elif np.all(other == 1):
                return self

        if isinstance(self, (Number, Constant)):
            if self == 0:
                return 0
            elif self == 1:
                return other

        if isinstance(other, (Number, Constant)):
            if other == 0:
                return 0
            elif other == 1:
                return self

        # If not extract out the arguments and sort them depending on whether it
        # is a LOP or ROP
        def process(a):
            try:
                if a.op is operator_mul:
                    a = a.args
                elif a.op is operator.pos:
                    a = [+1, *a.args]
                elif a.op is operator.neg:
                    a = [-1, *a.args]
                else:
                    a = (a,)
            except AttributeError:
                a = (a,)
            return a

        a = process(self)
        b = process(other)

        if dir == "LOP":
            args = [*a, *b]
        else:
            args = [*b, *a]

        args = reduce_mul_args(args)
        if len(args) > 1:
            # Create a n-arg multiplication
            return Function("*", operator_mul, *args)
        elif len(args) == 1:
            return args[0]  # reduced to a single argument
        else:
            # 0 arguments left then it's cancelled out the args
            return Constant(1)

    return simplify_mul


def MAKE_simplify_sub(dir):
    _simplify_sub = MAKE_simplify_add(dir)

    def simplify_sub(self, other):
        if not _SIMPLIFICATION_ENABLED:
            if dir == "LOP":
                return Function("-", operator.sub, self, other)
            else:
                return Function("-", operator.sub, other, self)
        else:
            if dir == "LOP":
                return _simplify_sub(self, -other)
            else:
                return _simplify_sub(-self, other)

    return simplify_sub


def MAKE_simplify_neg():
    def simplify_neg(self):
        if not _SIMPLIFICATION_ENABLED:
            return Function("-", operator.neg, self)
        else:
            # converts to a multiplication to make simplifying easier
            return -1 * self

    return simplify_neg


def MAKE_simplify_pos():
    def simplify_pos(self):
        if not _SIMPLIFICATION_ENABLED:
            return Function("+", operator.pos, self)
        else:
            # no need for any extra operation here
            return self

    return simplify_pos


def MAKE_simplify_pow(dir):
    def simplify_pow(self, exp):
        if dir == "ROP":
            self, exp = exp, self
        if not _SIMPLIFICATION_ENABLED:
            return Function("**", operator.pow, self, exp)

        if hasattr(self, "op"):
            # If we're doing a power of a power then we can do some obvious
            # multiplication of the power terms. We override self and exp
            # so that the other simplification logic can then take place
            # i.e. (x**0.5)**2 -> x
            if self.op is operator.pow:
                z = self.args[0]
                exp = self.args[1] * exp
                self = z

        if np.all(exp == 0):
            return Constant(1)
        elif np.all(exp == 1):
            return self
        elif (
            type(self) is Constant
            and type(exp) is Constant
            and not (self.is_named ^ exp.is_named)
        ):
            return Constant(self.value**exp.value)
        else:
            return Function("**", operator.pow, self, exp)

    return simplify_pow


def MAKE_LOP_simplify_truediv():
    def simplify_truediv(self, other):
        if not _SIMPLIFICATION_ENABLED:
            return Function("/", operator.truediv, self, other)

        if np.all(self == 0):
            return 0
        elif np.all(other == 0):
            raise ZeroDivisionError()
        elif isinstance(self, Function) and self.op is operator.neg:
            return -self.args[0] * Function("**", operator.pow, other, -1)
        elif isinstance(other, Function) and other.op is operator.neg:
            return -self * Function("**", operator.pow, other.args[0], -1)
        else:
            return self * Function("**", operator.pow, other, -1)

    return simplify_truediv


def MAKE_ROP_simplify_truediv():
    def simplify_truediv(self, other):
        if not _SIMPLIFICATION_ENABLED:
            return Function("/", operator.truediv, other, self)

        if np.all(other == 0):
            return 0
        elif self == 0:
            raise ZeroDivisionError()
        elif isinstance(self, Function) and self.op is operator.neg:
            return -other * Function("**", operator.pow, self.args[0], -1)
        elif isinstance(other, Function) and other.op is operator.neg:
            return -other.args[0] * Function("**", operator.pow, self, -1)
        else:
            return other * Function("**", operator.pow, self, -1)

    return simplify_truediv


# Supported operators.
OPERATORS = {
    "__add__": MAKE_simplify_add("LOP"),
    "__sub__": MAKE_simplify_sub("LOP"),
    "__mul__": MAKE_simplify_mul("LOP"),
    "__radd__": MAKE_simplify_add("ROP"),
    "__rsub__": MAKE_simplify_sub("ROP"),
    "__rmul__": MAKE_simplify_mul("ROP"),
    "__neg__": MAKE_simplify_neg(),
    "__pos__": MAKE_simplify_pos(),
    "__pow__": MAKE_simplify_pow("LOP"),
    "__rpow__": MAKE_simplify_pow("ROP"),
    "__truediv__": MAKE_LOP_simplify_truediv(),
    "__rtruediv__": MAKE_ROP_simplify_truediv(),
    "__floordiv__": MAKE_LOP("//", operator.floordiv),
    "__rfloordiv__": MAKE_ROP("//", operator.floordiv),
    "__matmul__": MAKE_LOP("@", operator.matmul),
    "__mod__": MAKE_LOP("%", operator.mod),
    "__rmod__": MAKE_ROP("%", operator.mod),
}


# Maps function names to actual functions called,
# this is used for lambdifying symbolics as you
# can't grab the underlying function from the lambdas
# stored in FUNCTIONS below
PYFUNCTION_MAP = {
    "abs": operator.abs,
    "neg": operator.neg,
    "pos": operator.pos,
    "pow": operator.pow,
    "conj": np.conj,
    "real": np.real,
    "imag": np.imag,
    "exp": np.exp,
    "log10": np.log10,
    "log": np.log,
    "sin": np.sin,
    "arcsin": np.arcsin,
    "cos": np.cos,
    "arccos": np.arccos,
    "tan": np.tan,
    "arctan": np.arctan,
    "arctan2": np.arctan2,
    "sqrt": np.sqrt,
    "std": np.std,
    "sum": np.sum,
    "dot": np.dot,
    "radians": np.radians,
    "degrees": np.degrees,
    "deg2rad": np.deg2rad,
    "rad2deg": np.rad2deg,
    "arange": np.arange,
    "linspace": np.linspace,
    "logspace": np.logspace,
    "geomspace": np.geomspace,
    "jv": ufuncs.jv,
}


# Built-in symbolic functions: maps string names of functions to acutal functions
FUNCTIONS = {
    "abs": lambda x: Function("abs", operator.abs, x),
    "neg": lambda x: Function("neg", operator.neg, x),
    "pos": lambda x: Function("pos", operator.pos, x),
    "pow": lambda x: Function("pow", operator.pow, x),
    "conj": lambda x: Function("conj", np.conj, x),
    "real": lambda x: Function("real", np.real, x),
    "imag": lambda x: Function("imag", np.imag, x),
    "exp": lambda x: Function("exp", np.exp, x),
    "log": lambda x: Function("log", np.log, x),
    "log10": lambda x: Function("log10", np.log10, x),
    "sin": lambda x: Function("sin", np.sin, x),
    "arcsin": lambda x: Function("arcsin", np.arcsin, x),
    "cos": lambda x: Function("cos", np.cos, x),
    "arccos": lambda x: Function("arccos", np.arccos, x),
    "tan": lambda x: Function("tan", np.tan, x),
    "arctan": lambda x: Function("arctan", np.arctan, x),
    "arctan2": lambda y, x: Function("arctan2", np.arctan2, y, x),
    "sqrt": lambda x: Function("sqrt", np.sqrt, x),
    "std": lambda x: Function("std", np.std, x),
    "sum": lambda x: Function("sum", np.sum, x),
    "dot": lambda x, y: Function("dot", np.dot, x, y),
    "radians": lambda x: Function("radians", np.radians, x),
    "degrees": lambda x: Function("degrees", np.degrees, x),
    "deg2rad": lambda x: Function("deg2rad", np.deg2rad, x),
    "rad2deg": lambda x: Function("rad2deg", np.rad2deg, x),
    "arange": lambda a, b, c: Function("arange", np.arange, float(a), float(b), int(c)),
    "linspace": lambda a, b, c: Function(
        "linspace", np.linspace, float(a), float(b), int(c)
    ),
    "logspace": lambda a, b, c: Function(
        "logspace", np.logspace, float(a), float(b), int(c)
    ),
    "geomspace": lambda a, b, c: Function(
        "geomspace", np.geomspace, float(a), float(b), int(c)
    ),
    "jv": lambda v, x: Function("jv", ufuncs.jv, v, x),
}


op_repr = {
    operator_add: lambda *args: "({})".format("+".join(args)),
    operator.add: "({}+{})".format,
    operator.sub: lambda *args: "({})".format("-".join(args)),
    operator_mul: lambda *args: "*".join(args),
    operator.mul: "({}*{})".format,
    operator.pow: "({})**({})".format,
    operator.truediv: "({}/{})".format,
    operator.floordiv: "({}//{})".format,
    operator.mod: "({}%{})".format,
    operator.matmul: "({}@{})".format,
    operator.neg: "-{}".format,
    operator.pos: "+{}".format,
    operator.abs: "abs({})".format,
    np.conj: "conj({})".format,
    np.sqrt: "sqrt({})".format,
}


def display(a, dunder=()):
    """For a given Symbol this method will return a human readable string representing
    the various operations it contains.

    Parameters
    ----------
    a : :class:`.Symbol`
        Symbol to print
    dunder : tuple
        Names of variables to display with double underscores pre- and suf-fixing
        the names.

    Returns
    -------
    String form of Symbol
    """
    if hasattr(a, "op"):
        # Check if operation has a predefined string format
        if a.op in op_repr:
            sop = op_repr[a.op]
        else:  # if not just treat it as a function
            sop = (a.op.__name__ + "(" + ("{}," * len(a.args)).rstrip(",") + ")").format

        sargs = (display(_, dunder=dunder) for _ in a.args)

        return sop(*sargs).replace("-1*", "-").replace("+-", "-").replace("*1/", "/")
    elif hasattr(a, "name"):  # Anything with a name attribute just display that
        if a in dunder:
            return "__" + a.name + "__"
        else:
            return a.name
    elif type(a) is Symbol:
        return f"<Symbol @ {hex(id(a))}>"
    else:
        return str(a)


def finesse2sympy(expr, iter_num=0):
    """
    Notes
    -----
    It might be common for this this function to throw a NotImplementedError.
    This function maps, by hand, various operator and numpy functions to sympy.
    If you come across this error, you'll need to update the if-statement to
    include the missing operations. Over time this should get fixed for most
    use cases.
    """
    import sympy

    from finesse.parameter import ParameterRef

    iter_num += 1
    if isinstance(expr, Constant):
        return expr.value
    elif isinstance(expr, (ParameterRef, Variable)):
        return sympy.Symbol(expr.name)
    elif isinstance(expr, Function):
        sympy_args = [finesse2sympy(arg, iter_num) for arg in expr.args]
        if expr.op == operator_mul or expr.op == operator.mul:
            op = sympy.Mul
        elif expr.op == operator_add or expr.op == operator.add:
            op = sympy.Add
        elif expr.op == operator.truediv:
            op = lambda a, b: sympy.Mul(a, sympy.Pow(b, -1))
        elif expr.op == operator.mod:
            op = sympy.Mod
        elif expr.op == operator.pow:
            op = sympy.Pow
        elif expr.op == operator.sub:
            op = lambda x, y: sympy.Add(x, -y)
        elif expr.op == np.conj:
            op = sympy.conjugate
        elif expr.op == np.radians:
            op = sympy.rad
        elif expr.op == np.exp:
            op = sympy.exp
        elif expr.op == np.cos:
            op = sympy.cos
        elif expr.op == np.sin:
            op = sympy.sin
        elif expr.op == np.tan:
            op = sympy.tan
        elif expr.op == np.sqrt:
            op = sympy.sqrt
        elif expr.op == operator.abs:
            op = sympy.Abs
        elif expr.op == operator.neg:
            op = lambda x: sympy.Mul(-1, x)
        elif expr.op == operator.pos:
            op = lambda x: sympy.Mul(+1, x)
        elif expr.op == np.imag:
            op = sympy.im
        elif expr.op == np.real:
            op = sympy.re
        else:
            try:
                op = getattr(sympy, expr.op.__name__)
            except AttributeError:
                raise NotImplementedError(
                    f"undefined Function {expr.op} in {expr}. {finesse2sympy} needs to be updated."
                )
        return op(*sympy_args)
    else:
        raise NotImplementedError(
            f"{expr} undefined. {finesse2sympy} needs to be updated."
        )


def sympy2finesse(expr, symbol_dict=None, iter_num=0):
    import sympy

    symbol_dict = {} if symbol_dict is None else symbol_dict

    iter_num += 1
    if isinstance(expr, sympy.Mul):
        return np.prod(
            [sympy2finesse(arg, symbol_dict, iter_num=iter_num) for arg in expr.args]
        )
    elif isinstance(expr, sympy.Add):
        return np.sum(
            [sympy2finesse(arg, symbol_dict, iter_num=iter_num) for arg in expr.args]
        )
    elif isinstance(expr, sympy.conjugate):
        return np.conj(sympy2finesse(*expr.args, symbol_dict))
    elif isinstance(expr, sympy.exp):
        return np.exp(sympy2finesse(*expr.args, symbol_dict))
    elif isinstance(expr, sympy.Pow):
        return np.power(
            sympy2finesse(expr.args[0], symbol_dict),
            sympy2finesse(expr.args[1], symbol_dict),
        )
    elif isinstance(expr, sympy.Mod):
        return np.mod(
            sympy2finesse(expr.args[0], symbol_dict),
            sympy2finesse(expr.args[1], symbol_dict),
        )
    elif (
        expr.is_NumberSymbol
    ):  # sympy class for named symbols (eg Pi, golden ratio, ...)
        if str(expr) == "pi":
            return CONSTANTS["pi"]
        else:
            return complex(expr)
    elif expr.is_number:
        if expr.is_integer:
            return int(expr)
        elif expr.is_real:
            return float(expr)
        else:
            return complex(expr)
    elif expr.is_symbol:
        return symbol_dict[str(expr)]
    else:
        raise Exception(f"{expr} undefined")


simplify_symbolic_numpy = np.vectorize(
    lambda x: collect(expand(x)) if isinstance(x, Symbol) else x, otypes="O"
)


def np_eval_symbolic_numpy(a, *keep):
    if isinstance(a, Symbol):
        return a.eval(keep=keep)
    else:
        return a


__eval_symbolic_numpy = np.vectorize(np_eval_symbolic_numpy, otypes="O")


def eval_symbolic_numpy(a, *keep):
    return __eval_symbolic_numpy(a, *keep)


def as_symbol(x):
    if isinstance(x, Symbol):
        return x
    return Constant(x)


def evaluate(x):
    """Evaluates a symbol or N-dimensional array of symbols.

    Parameters
    ----------
    x : :class:`.Symbol` or array-like
        A symbolic expression or an array of symbolic expressions.

    Returns
    -------
    out : float, complex, :class:`numpy.ndarray`
        A single value for the evaluated expression if `x` is not
        array-like, otherwise an array of the evaluated expressions.
    """
    if is_iterable(x):
        y = np.array(x, dtype=np.complex128)
        if not np.any(y.imag):  # purely real symbols in array
            with warnings.catch_warnings():
                if parse(np.__version__) < parse("1.25"):
                    category = np.ComplexWarning
                else:
                    category = np.exceptions.ComplexWarning
                # suppress 'casting to float discards imag part' warning
                # as we know that all imag parts are zero here anyway
                warnings.simplefilter("ignore", category=category)
                y = np.array(y, dtype=np.float64)

        return y

    if isinstance(x, Symbol):
        return x.eval()

    # If not a symbol then just return x directly
    return x


class Symbol(abc.ABC):
    __add__ = OPERATORS["__add__"]
    __sub__ = OPERATORS["__sub__"]
    __mul__ = OPERATORS["__mul__"]
    __radd__ = OPERATORS["__radd__"]
    __rsub__ = OPERATORS["__rsub__"]
    __rmul__ = OPERATORS["__rmul__"]
    __pow__ = OPERATORS["__pow__"]
    __rpow__ = OPERATORS["__rpow__"]
    __truediv__ = OPERATORS["__truediv__"]
    __rtruediv__ = OPERATORS["__rtruediv__"]
    __floordiv__ = OPERATORS["__floordiv__"]
    __rfloordiv__ = OPERATORS["__rfloordiv__"]
    __matmul__ = OPERATORS["__matmul__"]
    __neg__ = OPERATORS["__neg__"]
    __pos__ = OPERATORS["__pos__"]
    __mod__ = OPERATORS["__mod__"]
    __rmod__ = OPERATORS["__rmod__"]
    __abs__ = FUNCTIONS["abs"]
    conjugate = FUNCTIONS["conj"]
    conj = FUNCTIONS["conj"]
    exp = FUNCTIONS["exp"]
    sin = FUNCTIONS["sin"]
    arcsin = FUNCTIONS["arcsin"]
    cos = FUNCTIONS["cos"]
    arccos = FUNCTIONS["arccos"]
    tan = FUNCTIONS["tan"]
    arctan = FUNCTIONS["arctan"]
    arctan2 = FUNCTIONS["arctan2"]
    sqrt = FUNCTIONS["sqrt"]
    radians = FUNCTIONS["radians"]
    degrees = FUNCTIONS["degrees"]
    deg2rad = FUNCTIONS["deg2rad"]
    rad2deg = FUNCTIONS["rad2deg"]
    log = FUNCTIONS["log"]
    log10 = FUNCTIONS["log10"]

    @property
    def real(self):
        return FUNCTIONS["real"](self)

    @property
    def imag(self):
        return FUNCTIONS["imag"](self)

    @abc.abstractmethod
    def eval(self) -> float | complex | int:
        pass

    def __eq__(self, obj):
        """Inheriting classes should implement __symeq__ and do any symbol specific
        equality checks there.

        This top level handles initial n-arg conversion before symbolic comparison.
        """
        # Need to convert any symbolic expressions (Functions)
        # to nary form for equality checks
        if isinstance(obj, Function) and not obj._is_narg_expression_tree:
            obj = obj.to_nary_add_mul()
        if isinstance(self, Function) and not self._is_narg_expression_tree:
            self = self.to_nary_add_mul()
            # Might have been simplified to a number
            if isinstance(self, Number):
                return self == obj

        return self.__symeq__(obj)

    def __symeq__(self, obj):
        if isinstance(obj, Function):
            return obj == self
        else:
            return id(self) == id(obj)

    def __float__(self):
        v = self.eval()
        if np.isscalar(v):
            return float(v)
        else:
            raise TypeError(f"Can't cast {type(v)} ({v}) into a single float value")

    def __complex__(self):
        v = self.eval()
        if np.isscalar(v):
            return complex(v)
        else:
            raise TypeError(f"Can't cast {type(v)} ({v}) into a single complex value")

    def __int__(self):
        v = self.eval()
        if np.isscalar(v):
            return int(v)
        else:
            raise TypeError(f"Can't cast {type(v)} into a single int value")

    @property
    def value(self):
        """The current value of this symbol"""
        return self.eval()

    def __str__(self):
        return display(self)

    def __repr__(self):
        return f"<Symbolic='{display(self)}' @ {hex(id(self))}>"

    def __bool__(self):
        return bool(self.eval())

    @property
    def is_changing(self):
        """Returns True if one of the arguements of this symbolic object is varying
        whilst a :class:`` is running."""
        res = False

        if hasattr(self, "op"):
            res = any([_.is_changing for _ in self.args])
        elif hasattr(self, "parameter"):
            res = self.parameter.is_tunable or self.parameter.is_changing

        return res

    def parameters(self, memo=None):
        """Returns all the parameters that are present in this symbolic expression.

        Parameters are symbols whose values are attached to a model
        """
        if memo is None:
            memo = OrderedSet()

        if hasattr(self, "op"):
            for _ in self.args:
                _.parameters(memo)
        elif hasattr(self, "parameter"):
            memo.add(self)

        return list(memo)

    def all(self, predicate, memo=None):
        """Returns all the symbols that are present in this expression which satisify
        the predicate.

        Parameters
        ----------
        predicate : callable
            Method which takes in an argument and returns True if it matches.

        Examples
        --------
        To select all `Constant`s and `Variable`s from an expression `y`:

        >>> y.all(lambda a: isinstance(a, (Constant, Variable)))
        """
        if memo is None:
            memo = OrderedSet()

        if hasattr(self, "op"):
            for _ in self.args:
                _.all(predicate, memo)

        if predicate(self):
            memo.add(self)

        return list(memo)

    def changing_parameters(self):
        p = np.array(self.parameters())
        return list(p[list(map(lambda x: x.is_changing, p))])

    def to_sympy(self):
        """Converts a Finesse symbolic expression into a Sympy expression.

        Warning: for large functions this can be quite slow.
        """
        return finesse2sympy(self)

    def sympy_simplify(self):
        """Converts this expression into a Sympy symbol."""
        refs = {
            _.name: _ for _ in self.parameters()
        }  # get a list of symbols we're using
        sympy = finesse2sympy(self)
        return sympy2finesse(sympy.simplify(), refs)

    def collect(self):
        """Collects like terms in the expressions."""
        return collect(self)

    def expand(self):
        """Performs a basic expansion of the symbolic expression."""
        return expand(self)

    def expand_symbols(self):
        """A method that expands any symbolic parameter references that are themselves
        symbolic. This can be used to get an expression that only depends on references
        that are numeric.

        Examples
        --------
        >>> import finesse
        >>> model = finesse.Model()
        >>> model.parse(
        ...     '''
        ...     var d 300
        ...     var c 6000
        ...     var b c+d
        ...     var a b+1
        ...     '''
        ... )
        >>> model.a.value.expand_symbols()
        <Symbolic='((c+d)+1)' @ 0x7faa4d351c10>

        Parameters
        ----------
        sym : Symbolic
            Symbolic equation to expand
        """

        def process(p):
            if p.parameter.is_symbolic:
                return p.parameter.value
            else:
                return p

        def _expand(sym):
            params = sym.parameters()
            if len(params) == 0:
                return None
            elif not any(p.parameter.is_symbolic for p in params):
                return None
            else:
                subs = {p: process(p) for p in params if p.parameter.is_symbolic}
                return sym.substitute(subs)

        sym = self
        while True:
            res = _expand(sym)
            if res is None:
                return sym
            else:
                sym = res

    def to_binary_add_mul(self):
        """Converts a symbolic expression to use binary forms of operator.add and
        operator.mul operators, rather than the n-ary operator_add and operator_mul.

        Returns
        -------
        Symbol
        """
        if hasattr(self, "op"):
            return self.op(*(_.to_binary_add_mul() for _ in self.args))
        else:
            return self

    def to_nary_add_mul(self):
        """Converts a symbolic expression to use n-ary forms of operator_add and
        operator_mul operators, rather than the binary-ary operator.add and
        operator.mul.

        Returns
        -------
        Symbol
        """
        if hasattr(self, "op"):
            with simplification(allow_flagged=True):
                if self.op is operator.pos:
                    return self.args[0].to_nary_add_mul()
                elif self.op is operator.neg:
                    return -1 * self.args[0].to_nary_add_mul()
                else:
                    # calling to_nary_add_mul here as it's basically the same but
                    # just won't keep opening a new context manager each time
                    return self.op(*(_.to_nary_add_mul() for _ in self.args))
        else:
            return self

    def lambdify(self, *args, expand_symbols=False, ignore_unused_symbols=False):
        """Converts this symbolic expression into a function that can be called.

        Parameters
        ----------
        args : Symbols
            Symbols to use to make up the arguments of the generated function. If
            none are provided then the current values of `ParameterRef`s are used
            and `Variables` are left as they are.

        expand_symbols : bool, optional
            If True, the expression will first have any dependent variables expanded.
            See `.expand_symbols`.
        """
        from finesse.parameter import ParameterRef

        # Convert to a string form, which is in a python evaluatable format, then
        # run eval on it to get a lambda function
        if expand_symbols:
            expr = self.expand_symbols()
        else:
            expr = self

        # We dunder the arugments so we can easily find and string replace them
        # later with the lambda function argument. This has to be done as `.`
        # can't be used in variable name (i.e. l1.P). This should stop clashes
        # with other names.
        sym_str = display(expr, dunder=args)
        params = expr.all(lambda x: isinstance(x, (Variable, ParameterRef)))

        fix_curly = lambda x: x.replace("{", "Ç").replace("}", "ç")
        ARGS = []
        for arg in args:
            if not ignore_unused_symbols and arg not in params:
                raise NameError(
                    f"`{arg}` is not a valid symbol to make as an argument to this the lambda function in this expression: {sym_str}"
                )
            if hasattr(arg, "full_name"):
                ARGS.append(arg.full_name.replace(".", "__"))
                ARGS[-1] = fix_curly(ARGS[-1])
                sym_str = sym_str.replace("__" + arg.full_name + "__", ARGS[-1])
            else:
                ARGS.append(arg.name.replace(".", "__"))
                ARGS[-1] = fix_curly(ARGS[-1])
                sym_str = sym_str.replace("__" + arg.name + "__", ARGS[-1])

        _globals = {}

        for arg in params:
            if arg not in args:
                if isinstance(arg, Variable):
                    _globals[arg.name] = arg
                elif hasattr(arg, "owner") and hasattr(arg.owner, "name"):
                    _globals[arg.owner.name] = arg.owner
                else:
                    # for model parameters
                    _globals[arg.name] = arg.owner.get(arg.name)

        # get functions used so that they can be exposed to the eval
        for func in expr.all(lambda x: isinstance(x, Function)):
            if func.__class__.__module__ != "__builtin__":
                _globals[func.name] = func.op

        s = f"lambda {','.join(ARGS)}: {sym_str}"
        return eval(s, _globals)

    @staticmethod
    def _check_substitution(subs):
        if "__checked__" not in subs:
            # Need this check to pre-subsitute any constants back into
            constants = {k: v for k, v in subs.items() if not hasattr(v, "substitute")}
            if len(constants) > 0:
                for key in list(subs.keys()):
                    if hasattr(subs[key], "substitute"):
                        subs[key] = subs[key].substitute(constants)
            subs["__checked__"] = True

    def substitute(self, mapping):
        """Uses a dictionary to substitute terms in this expression with another. This
        does not perform any evaluation of any terms, unlike `eval(subs=...)`.

        Notes
        -----
        The symbolic substitution implemented here is not recursive, consider:

        >>> y = a + b
        >>> y.subs({a:a+b, b:a}) # results in => a+b+a

        Here `b` is not replaced in the substitutions. The only time this happens
        is if one mapping is purely numeric:

        >>> y.subs({a:a+b, b:1}) # results in => a+2

        Parameters
        ----------
        mapping : dict
            Dictionary of substitutions/mappings to make. Keys can be the actual symbol
            or the name of the symbol in string form. Values must all be proper symbols.
        """
        self._check_substitution(mapping)

        if self.name in mapping:
            return mapping[self.name]
        elif self in mapping:
            return mapping[self]
        else:
            return self


class Matrix(Symbol):
    """A Matrix symbol."""

    def __init__(self, name):
        self.name = str(name)

    def __hash__(self):
        return hash((self.name,))

    def eval(self, **kwargs):
        return self


class Constant(Symbol):
    """Defines a constant symbol that can be used in symbolic math.

    Parameters
    ----------
    value : float, int
        Value of constant

    name : str, optional
        Name of the constant to use when printing
    """

    def __init__(self, value, name=None):
        self.__value = value
        self.__name = name

    def __str__(self):
        return self.__name or str(self.__value)

    def __repr__(self):
        return str(self.__name or self.__value)

    def __symeq__(self, obj):
        if isinstance(obj, Function):
            return obj == self.value
        elif isinstance(obj, Constant):
            return obj.value == self.value
        else:
            return obj == self.value

    def __hash__(self):
        """Constant hash.

        This is used by the tokenizer. Constants are by definition immutable.
        """
        # Add the class to reduce chance of hash collisions.
        return hash((type(self), self.value))

    def substitute(self, subs):
        """Uses a dictionary to substitute terms in this expression with another. This
        does not perform any evaluation of any terms, unlike `eval(subs=...)`.

        Parameters
        ----------
        subs : dict
            Dictionary of substitutions to make. Keys can be the actual symbol or
            the name of the symbol in string form. Values must all be proper symbols.
        """
        self._check_substitution(subs)

        if subs and self in subs:
            return subs[self]
        else:
            return self

    def eval(self, subs=None, **kwargs):
        """Evaluate this constant.

        If a substitution is available the value of that will be used instead of
        `self.value`
        """
        if subs and self in subs:
            return subs[self]
        elif hasattr(self.__value, "eval"):
            return self.__value.eval()
        else:
            return self.__value

    @property
    def is_named(self):
        """Was this constant given a specific name."""
        return self.__name is not None

    @property
    def name(self):
        return str(self.value) if self.__name is None else self.__name


# Constants.
# NOTE: The keys here are used by the parser to recognise constants in kat script.
CONSTANTS = {
    "pi": Constant(constants.PI, name="π"),
    "c0": Constant(constants.C_LIGHT, name="c"),
}


class Resolving(Symbol):
    """A special symbol that represents a symbol that is not yet resolved.

    This is used in the parser to support self-referencing parameters.

    An error is thrown if the value is attempted to be read.
    """

    def eval(self, **kwargs):
        raise EvaluateResolvingSymbolError(
            "an attempt has been made to read the value of a resolving symbol (hint: "
            "symbols should not be evaluated until parsing has fully finished)"
        )

    @property
    def name(self):
        return "RESOLVING"


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Variable(Symbol):
    """Makes a variable symbol that can be used in symbolic math. Values must be
    substituted in when evaluating an expression.

    Examples
    --------
    Using some variables to make an expression and evaluating it:

    >>> import numpy as np
    >>> x = Variable('x')
    >>> y = Variable('y')
    >>> z = 4*x**2 - np.cos(y)
    >>> print(f"{z} = {z.eval(subs={x:2, y:3})} : x={2}, y={3}")
    (4*x**2-y) = 13 : x=2, y=3

    Parameters
    ----------
    value : float, int
        Value of constant

    name : str, optional
        Name of the constant to use when printing
    """

    def __init__(self, name):
        if name is None:
            raise ValueError("Name must be provided")
        self.__name = str(name)

    def __hash__(self):
        return hash((Variable, self.name))

    @property
    def name(self):
        return self.__name

    def __symeq__(self, obj):
        if isinstance(obj, Variable):
            return self.name == obj.name
        else:
            return False

    def eval(self, subs=None, keep=None, **kwargs):
        """Evaluates this variable and returns either itself or a substituted value.

        Parameters
        ----------
        subs : dict
            Dictionary of object
        keep : iterable, str
            A collection of names of variables to keep as variables when
            evaluating. Keep will override any substitution.
        """
        if keep:
            if self.name == keep:
                return self
            elif is_iterable(keep):
                if self.name in keep or self in keep:
                    return self

        if subs is not None:
            return self.substitute(subs)
        else:
            return self


class Function(Symbol):
    """This is a symbol to represent a mathematical function. This could be a simple
    addition, or a more complicated multi-argument function.

    It supports creating new mathematical operations::

        import math
        import cmath

        cos   = lambda x: finesse.symbols.Function("cos", math.cos, x)
        sin   = lambda x: finesse.symbols.Function("sin", math.sin, x)
        atan2 = lambda y, x: finesse.symbols.Function("atan2", math.atan2, y, x)

    Complex math can also be used::

        import numpy as np
        angle = lambda x: finesse.symbols.Function("angle", np.angle, x)
        print(f"{angle(1+1j)} = {angle(1+1j).eval()}")

    Parameters
    ----------
    name : str
        The operation name. This is used for dumping operations to kat script.

    operation : callable
        The function to pass the arguments of this operation to.

    Other Parameters
    ----------------
    *args
        The arguments to pass to `operation` during a call.
    """

    def __init__(self, name, operation, *args):
        self.__simplified_expr_tree = _SIMPLIFICATION_ENABLED
        self.name = str(name)
        self.args = list(as_symbol(_) for _ in args)
        self.op = operation

    def substitute(self, subs):
        """Uses a dictionary to substitute terms in this expression with another. This
        does not perform any evaluation of any terms, unlike `eval(subs=...)`.

        Parameters
        ----------
        subs : dict
            Dictionary of substitutions to make. Keys can be the actual symbol or
            the name of the symbol in string form. Values must all be proper symbols.
        """
        try:
            args = tuple(_.substitute(subs) for _ in self.args)
            return self.op(*args)
        except ZeroDivisionError:
            return np.nan  # return
        except TypeError as ex:
            msg = f"Whilst evaluating {self.op}{self.args} this error was raised:\n`    {ex}`"
            for _ in self.args:
                if _.value is None:
                    msg += f"\nHint: {_} is `None` make sure it is defined before being used."
                    if _.parameter.full_name == "fsig.f":
                        msg += " if using KatScript use `fsig(f)` before this line."
            raise FinesseException(msg)

    def eval(self, **kwargs):
        """Evaluates the operation.

        Parameters
        ----------
        subs : dict, optional
            Parameter substitutions can be given via an optional
            ``subs`` dict (mapping parameters to substituted values).
        keep : iterable, str
            A collection of names of variables to keep as variables when
            evaluating.

        Notes
        -----
        A division by zero will return a NaN, rather than raise an exception.

        Returns
        -------
        result : number or array-like
            The single-valued result of evaluation of the operation (if no
            substitutions given, or all substitutions are scalar-valued). Otherwise,
            if any parameter substitution was a :class:`numpy.ndarray`, then a corresponding array
            of results.
        """
        try:
            args = tuple(_.eval(**kwargs) for _ in self.args)
            return self.op(*args)
        except ZeroDivisionError:
            return np.nan  # return
        except TypeError as ex:
            msg = f"Whilst evaluating {self.op}{self.args} this error was raised:\n`    {ex}`"
            for _ in self.args:
                if _.value is None:
                    msg += f"\nHint: {_} is `None` make sure it is defined before being used."
                    if _.parameter.full_name == "fsig.f":
                        msg += " if using KatScript use `fsig(f)` before this line."
            raise FinesseException(msg)

    @property
    def _is_narg_expression_tree(self):
        """Was this expressions built with the global `_SIMPLIFICATION_ENABLED` set to
        `False`."""
        return self.__simplified_expr_tree

    @property
    def contains_unresolved_symbol(self):
        """Whether the operation contains any unresolved symbols.

        :`getter`: Returns true if any symbol in the operation is an instance
                   of :class:`.Resolving`, false otherwise. Read-only.
        """
        try:
            self.eval()
        except EvaluateResolvingSymbolError:
            return True

        return False

    def __symeq__(self, obj):
        if not isinstance(obj, Symbol) and (obj == 0 or obj == 1):
            # Some dumb checks for common comparisons for things like 0
            return False

        if self is obj:
            return True

        # Need to simplify functions first before comparisons
        A = self
        B = obj

        if not isinstance(A, Function):
            # A might not be a function anymore if simplified away to variable
            # 2*a/2 -> a
            return A == obj

        if isinstance(B, Function):
            if A.op == B.op:
                if len(A.args) != len(B.args):
                    return False
                else:
                    return all([a == b for a, b in zip(A.args, B.args)])
            if B.op is operator.pos:
                return A == B.args[0]
            elif B.op is operator.neg:
                return A == -1 * B.args[0]
            else:
                return False
        else:
            # pos and neg comparisons are some what annoying, if we
            # convert them to multiply it becomes a simple product arg
            # comparison
            if A.op is operator.pos:
                return A.args[0] == B
            elif A.op is operator.neg:
                return (-1) * A.args[0] == B
            else:
                return False

    def __hash__(self):
        return hash((Function, self.op, *(hash(_) for _ in self.args)))


class LazySymbol(Symbol):
    """A generic way to make some lazily evaluated symbol.

    The value is dependant on a lambda function and some arbitrary arguments
    which will be called when the symbol is evaluated.

    Parameters
    ----------
    name : str
        Human readable string name for the symbol
    function : callable
        Function to call when evaluating the symbol
    *args : objects
        Arguments to pass to `function` when evaluating

    Examples
    --------
    >>> a = LazyVariable('a', lambda x: x**2, 10)
    >>> print(a)
    <Symbolic='(a*10)' @ 0x7fd6587e6760>
    >>> print((a*10).eval())
    1000
    """

    def __init__(self, name, function, *args):
        self.__name = name
        self.function = function
        self.args = args

    def eval(self, **kwargs):
        return self.function(*self.args)

    @property
    def name(self):
        return self.__name


def collect(y):
    if hasattr(y, "op"):
        if not y._is_narg_expression_tree:
            y = y.to_nary_add_mul()  # simplification happens on nary trees
            if not hasattr(y, "op"):
                return y
        with simplification(allow_flagged=True):
            if y.op is operator_add:
                args = {}
                out = 0
                for x in y.args:
                    c, t = coefficient_and_term(x)
                    if t is None:  # just a coefficient/constant
                        out += x
                    else:
                        if t in args:
                            args[t] += c
                        else:
                            args[t] = c
                for k, v in args.items():
                    out += k * v
                return out

            elif len(y.args) > 0:
                # y is some other operator, which may have args that need collecting
                # pos and neg we can simplify here to just return itself, or
                # by multiplying by -1
                if y.op is operator.pos:
                    return collect(y.args[0])
                elif y.op is operator.neg:
                    return -1 * collect(y.args[0])
                else:
                    return y.op(*(collect(_) for _ in y.args))
            else:
                return y
    else:
        return y


def coefficient_and_term(y):
    try:
        if y.op is operator_mul or y.op is operator.mul:
            if not y._is_narg_expression_tree:
                y = y.to_nary_add_mul()  # simplification happens on nary trees
            args = y.args
            if all(type(_) is Constant for _ in args):
                # if all constants then probably a named constant time other
                # like 2*pi
                coeff = y
                term = None
            elif type(args[0]) is not Constant:
                # There are no constant values so just variables/functions/etc
                coeff = Constant(1)
                term = np.prod(args)
            else:
                coeff = args[0]  # Just the constants at the start
                term = np.prod(
                    args[1:]
                )  # then the rest of the args should be variables/etc
            return coeff, term
        elif y.op is operator.pos:
            return Constant(1), y.args[0]
        elif y.op is operator.neg:
            return Constant(-1), y.args[0]
        else:
            return Constant(1), y
    except AttributeError:
        # Not an operator...
        if type(y) is Constant:
            return y, None
        else:
            return Constant(1), y


def expand_mul(y):
    with simplification(allow_flagged=True):
        if not hasattr(y, "op"):
            return y
        elif not y._is_narg_expression_tree:
            y = y.to_nary_add_mul()  # simplification happens on nary trees

        if y.op is operator_mul:
            terms = np.array([1], dtype="O")
            for x in y.args:
                try:
                    if x.op is operator_add:
                        terms = np.outer(terms, x.args)
                    else:
                        terms *= x
                except AttributeError:
                    terms *= x

            res = np.sum(terms)

            return res
        elif y.op is operator_add:
            return sum(expand_mul(_) for _ in y.args)
        else:
            return y


def is_integer(n):
    """Checks if `n` is an integer.

    Parameters
    ----------
    n : str, float
        Input to check
    """
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def expand_pow(y):
    with simplification(allow_flagged=True):
        if not hasattr(y, "op"):
            return y
        elif not y._is_narg_expression_tree:
            y = y.to_nary_add_mul()  # simplification happens on nary trees

        if y.op is operator.pow:
            z = 1
            exp = y.args[1]
            base = y.args[0]

            try:
                if base.op is operator_mul:
                    for _ in base.args:
                        z *= _**exp
                    return z
                elif base.op is operator_add:
                    if type(exp) is Constant and is_integer(exp.value):
                        n = int(exp.value)
                        if n == 0:
                            return 1
                        terms = np.array([1], dtype="O")
                        for _ in range(abs(n)):
                            terms = np.outer(terms, base.args)
                        if n > 0:
                            return terms.sum().collect()
                        else:
                            return (terms.sum().collect()) ** -1
                    else:
                        return y
                else:
                    return y
            except AttributeError:
                return y
        elif y.op is operator_add:
            return sum(expand_pow(_) for _ in y.args)
        elif y.op is operator_mul:
            return np.prod(tuple(expand_pow(_) for _ in y.args))
        else:
            return y


def expand(y):
    with simplification(allow_flagged=True):
        if not isinstance(y, Function):
            return y  # Nothing to expand
        else:
            if not y._is_narg_expression_tree:
                y = y.to_nary_add_mul()  # simplification happens on nary trees
                if not isinstance(y, Function):
                    return y  # Nothing to expand
            if y.op is operator_mul:
                # Run through and expand any pows before the
                # full mul expansion
                y = Function(y.name, y.op, *[expand_pow(_) for _ in y.args])
                y = expand_mul(y)
                # Nothing left to expand as no add operator
                if not isinstance(y, Function):
                    return y
                elif y.op is operator_mul:
                    return y
            elif y.op is operator.pow:
                y = expand_pow(y)
                # Nothing left to expand as no add operator
                if y.op is operator.pow:
                    return y

            if y.op is not operator_add:
                # some other type of operator expand it's args
                if len(y.args) > 0:
                    return y.op(*(expand(_) for _ in y.args))
                else:
                    return y
            else:
                # We have a summation of terms from the initial expansion
                # so expand each term
                out = []
                for x in y.args:
                    try:
                        if x.op is operator_mul:
                            x = Function(x.name, x.op, *[expand_pow(_) for _ in x.args])
                            z = expand_mul(x)
                        elif x.op is operator.pow:
                            z = expand_pow(x)
                        else:
                            z = x

                        if hasattr(z, "op") and z.op is operator_add:
                            out.extend(z.args)
                        else:
                            out.append(z)
                    except AttributeError:
                        out.append(x)

                z = Function(y.name, y.op, *out)
                if y == z:
                    return z
                else:
                    return expand(z)
