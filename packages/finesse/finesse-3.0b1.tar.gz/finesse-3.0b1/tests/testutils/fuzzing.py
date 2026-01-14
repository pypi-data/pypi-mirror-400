"""Fuzzing utilities for tests."""

import os

import numpy as np
from hypothesis import assume
from hypothesis.strategies import (
    characters,
    complex_numbers,
    composite,
    dictionaries,
    floats,
    from_regex,
    integers,
    lists,
    one_of,
    recursive,
    sampled_from,
    text,
)

from finesse import Model
from finesse.script.spec import KATSPEC
from finesse.symbols import OPERATORS

# Deadline setting for fuzzing; see #292.
DEADLINE = None if os.getenv("windows_ci") else 1000


# Min/max sizes for types that get used by numpy integer arrays.
_INT_DTYPE_INFO = np.iinfo(np.int32)
MIN_CINT = _INT_DTYPE_INFO.min
MAX_CINT = _INT_DTYPE_INFO.max


_MODEL = Model()

# Names that cannot be used for elements.
RESERVED_NAMES = {*dir(_MODEL), *KATSPEC.reserved_names}


# FIXME: don't hard-code these.
BINARY_OPERATIONS = (
    "__add__",
    "__sub__",
    "__mul__",
    "__truediv__",
    "__floordiv__",
    "__pow__",
)


# Valid normal fraction for reflectivity etc.
positive_normal_float = floats(min_value=0, max_value=1, allow_nan=False)

# Positive, finite floats.
positive_finite_floats = floats(min_value=0, allow_nan=False, allow_infinity=False)

# Finite integers for use with KLU (see #119).
c_integer = integers(min_value=MIN_CINT, max_value=MAX_CINT)
positive_c_integer = integers(min_value=0, max_value=MAX_CINT)


@composite
def numbers(draw, operations=False):
    """Any type of number."""
    cmplx_kwargs = dict(
        min_magnitude=0, max_magnitude=1, allow_nan=False, allow_infinity=False
    )

    if operations:
        # Wrap complex numbers in Function objects.
        cmplx_strategy = complex_number_operations(**cmplx_kwargs)
    else:
        cmplx_strategy = complex_numbers(**cmplx_kwargs)

    return draw(
        one_of(
            floats(min_value=-1, max_value=1, allow_nan=False, allow_infinity=False),
            integers(min_value=-1, max_value=1),
            cmplx_strategy,
        )
    )


@composite
def rtl_sets(draw):
    """R, T, L adding up to 1."""
    R = draw(positive_normal_float, label="R")
    T = draw(positive_normal_float, label="T")
    L = draw(positive_normal_float, label="L")

    # Don't allow R, T and L to be too small.
    if R != 0:
        assume(R > 1e-3)
    if T != 0:
        assume(T > 1e-3)
    if L != 0:
        assume(L > 1e-3)

    total = R + T + L
    assume(total > 0)
    R /= total
    T /= total
    L /= total
    return R, T, L


@composite
def rtl_sets_two_vals(draw):
    """R, T, L adding up to 1."""
    a = draw(positive_normal_float)
    b = draw(positive_normal_float)

    total = a + b
    assume(total > 0)

    if total > 1.0:
        a /= total
        b /= total

    return a, b


laser_powers = positive_c_integer


@composite
def complex_number_operations(draw, **kwargs):
    number = draw(complex_numbers(**kwargs))
    operation = OPERATORS["__sub__"] if number.imag < 0 else OPERATORS["__add__"]
    return operation(number.real, abs(number.imag))


@composite
def open_expressions(draw, rhs):
    lval = draw(numbers())
    operation = draw(sampled_from(BINARY_OPERATIONS))
    rval = draw(rhs)

    try:
        assume(operation not in ("/", "//") and rhs != 0)
    except TypeError:
        # Input type cannot be compared to zero.
        pass

    return OPERATORS[operation](lval, rval)


# TODO: make an Function for parenthesised expressions
# @composite
# def bracketed_expressions(draw, rhs):
#     return f"({draw(open_expressions(rhs))})"


@composite
def expressions(draw, rhs=None):
    rhs = numbers() if rhs is None else rhs
    # return draw(one_of(open_expressions(rhs), bracketed_expressions(rhs)))
    return draw(open_expressions(rhs))


@composite
def recursive_expressions(draw, max_leaves=25):
    """Generate nested expressions up to max_leaves."""
    return draw(
        recursive(
            expressions(), lambda rhs: expressions(rhs=rhs), max_leaves=max_leaves
        )
    )


@composite
def recursive_arrays(draw, operations=False):
    """Generate nested arrays up to max_leaves."""
    return [draw(recursive(numbers(operations=operations), lists))]


@composite
def line(draw, nonempty=False):
    """A single line of text."""
    # Blacklist control characters.
    return draw(
        text(
            min_size=1 if nonempty else 0,
            alphabet=characters(blacklist_categories=("Cs", "Cc")),
        )
    )


@composite
def kat_name(draw):
    """Valid kat script name."""
    name = draw(from_regex("^[a-zA-Z_][a-zA-Z0-9_]*$", fullmatch=True))
    assume(name not in RESERVED_NAMES)
    return name


@composite
def kat_empty(draw, multiline=False):
    if multiline:
        pattern = "^[ \t]*$"
    else:
        pattern = "^[ \t\n]*$"
    return draw(from_regex(pattern, fullmatch=True))


@composite
def kat_comment(draw):
    # Blacklist control characters.
    comment = draw(line())
    return f"#{comment}"


@composite
def kat_scalar(draw, nonnegative=False):
    """Kat script scalar value, including SI suffices."""
    min_value = 0 if nonnegative else None
    value = draw(floats(min_value=min_value, allow_nan=False, allow_infinity=False))
    items = [value]

    # Can't add a suffix for scientific notation.
    if "e" not in str(value):
        suffix = draw(sampled_from("pnumkMGT"))
        items.append(f"{value}{suffix}")

    return draw(sampled_from(items))


@composite
def kat_laser(draw):
    directive = draw(sampled_from(KATSPEC.elements["laser"].aliases))
    name = draw(kat_name())
    params = draw(
        dictionaries(keys=sampled_from(("P", "f", "phase")), values=kat_scalar())
    )
    paramstr = " ".join([f"{k}={v}" for k, v in params.items()])
    return f"{directive} {name} {paramstr}"


@composite
def kat_mirror(draw):
    directive = draw(sampled_from(KATSPEC.elements["mirror"].aliases))
    name = draw(kat_name())
    R, T, L = draw(rtl_sets())
    return f"{directive} {name} R={R} T={T} L={L}"


@composite
def kat_beamsplitter(draw):
    directive = draw(sampled_from(KATSPEC.elements["beamsplitter"].aliases))
    name = draw(kat_name())
    R, T, L = draw(rtl_sets())
    return f"{directive} {name} R={R} T={T} L={L}"


@composite
def kat_element(draw):
    return draw(one_of(kat_laser(), kat_mirror(), kat_beamsplitter()))


@composite
def kat_script_line(draw):
    """Generate kat script line."""
    return draw(one_of(kat_empty(), kat_comment(), kat_element()))
