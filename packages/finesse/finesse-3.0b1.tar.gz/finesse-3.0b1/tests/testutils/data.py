"""Data for use in tests.

Most data contains tuples with 3 values: the input (parsed) string, the output
(generated) string and the Python representation. This allows the same data to be used
for both parser and generator tests.
"""

from itertools import combinations
import numpy as np
from . import BINARY_OPERATORS, CONSTANTS, EXPRESSION_FUNCTIONS

# Some macros for internal use.
_ADD = BINARY_OPERATORS["+"]
_SUB = BINARY_OPERATORS["-"]
_MUL = BINARY_OPERATORS["*"]
_DIV = BINARY_OPERATORS["/"]
_FLOORDIV = BINARY_OPERATORS["//"]
_POW = BINARY_OPERATORS["**"]
_POS = EXPRESSION_FUNCTIONS["pos"]
_NEG = EXPRESSION_FUNCTIONS["neg"]
_ABS = EXPRESSION_FUNCTIONS["abs"]
_COS = EXPRESSION_FUNCTIONS["cos"]
_SIN = EXPRESSION_FUNCTIONS["sin"]
_TAN = EXPRESSION_FUNCTIONS["tan"]
_ACOS = EXPRESSION_FUNCTIONS["arccos"]
_ASIN = EXPRESSION_FUNCTIONS["arcsin"]
_ATAN2 = EXPRESSION_FUNCTIONS["arctan2"]
_EXP = EXPRESSION_FUNCTIONS["exp"]
_SQRT = EXPRESSION_FUNCTIONS["sqrt"]
_PI = CONSTANTS["pi"]

SI_PREFICES = {
    # Taken from lexer NUMBER tokeniser.
    "p": -12,
    "n": -9,
    "u": -6,
    "m": -3,
    "k": 3,
    "M": 6,
    "G": 9,
    "T": 12,
}

NONE = (("none", "none", None),)

BOOLEANS = (
    ("false", "false", False),
    ("true", "true", True),
)

STRINGS = (
    # Single quotes.
    (r"'my string'", "'my string'", "my string"),
    (r"' my string'", "' my string'", " my string"),
    (r"'  my   string  '", "'  my   string  '", "  my   string  "),
    (r"'\"my string'", "'\"my string'", '"my string'),
    (r"'\"\"my \'string'", r"""'""my \'string'""", '""my \'string'),
    # Double quotes.
    (r'"my string"', "'my string'", "my string"),
    (r'" my string"', "' my string'", " my string"),
    (r'"  my   string  "', "'  my   string  '", "  my   string  "),
    (r'"\"my string"', "'\"my string'", '"my string'),
    (r'"\"\"my \'string"', r"""'""my \'string'""", '""my \'string'),
)

# No signs allowed!
INTEGERS = (
    ("0", "0", 0),
    ("1", "1", 1),
    ("100", "100", 100),
    ("50505", "50505", 50505),
    ("1234567890", "1234567890", 1234567890),
    ("123141242151251616110", "123141242151251616110", 123141242151251616110),
    # Separation of digits with `_`.
    ("1_0", "10", 10),
    ("1_00", "100", 100),
    ("1_000", "1000", 1000),
    ("1_000_000", "1000000", 1000000),
    ("1_0_0_0_0_0_0", "1000000", 1000000),
)

# Unary literals are eagerly evaluated.
UNARY_INTEGERS = (
    ("+0", +0),
    ("-0", +0),
    ("+15", +15),
    ("-15", -15),
    ("+50505", +50505),
    ("-50505", -50505),
)
UNARY_FLOATS = (
    ("+0.", +0.0),
    ("-0.", -0.0),
    ("+0.0", +0.0),
    ("-0.0", -0.0),
    ("+50505.0112", +50505.0112),
    ("-50505.0112", -50505.0112),
    # Scientific.
    ("+0.e7", +0e7),
    ("+0.0e7", +0e7),
    ("-0.e7", -0e7),
    ("-0.0e7", -0e7),
    ("+1.23e7", +1.23e7),
    ("+1.23e+7", +1.23e7),
    ("+1.23e-7", +1.23e-7),
    ("-1.23e7", -1.23e7),
    ("-1.23e+7", -1.23e7),
    ("-1.23e-7", -1.23e-7),
    # Infinities.
    ("+inf", float("+inf")),
    ("-inf", float("-inf")),
)
UNARY_IMAGINARIES = (
    ("+0j", +0j),
    ("+0.j", +0j),
    ("+0.0j", +0j),
    ("-0j", -0j),
    ("-0.j", -0j),
    ("-0.0j", -0j),
    ("+1.32j", +1.32j),
    ("-1.32j", -1.32j),
    # Scientific.
    ("+0e7j", +0e7j),
    ("+0.e7j", +0e7j),
    ("+0.0e7j", +0e7j),
    ("-0e7j", -0e7j),
    ("-0.e7j", -0e7j),
    ("-0.0e7j", -0e7j),
    ("+1.23e7j", +1.23e7j),
    ("+1.23e+7j", +1.23e7j),
    ("+1.23e-7j", +1.23e-7j),
    ("-1.23e7j", -1.23e7j),
    ("-1.23e+7j", -1.23e7j),
    ("-1.23e-7j", -1.23e-7j),
    # Infinities.
    ("+infj", complex("+infj")),
    ("-infj", complex("-infj")),
)
UNARY_COMPLEX = (
    ("+0+0j", +0 + 0j),
    ("+0-0j", +0 - 0j),
    ("+0+1.23j", +0 + 1.23j),
    ("+0-1.23j", +0 - 1.23j),
    ("+0.+0j", +0.0 + 0j),
    ("+0.-0j", +0.0 - 0j),
    ("+0.+1.23j", +0.0 + 1.23j),
    ("+0.-1.23j", +0.0 - 1.23j),
    ("+0.0+0j", +0.0 + 0j),
    ("+0.0-0j", +0.0 - 0j),
    ("+0.0+1.23j", +0.0 + 1.23j),
    ("+0.0-1.23j", +0.0 - 1.23j),
    ("-0+0j", -0 + 0j),
    ("-0-0j", -0 - 0j),
    ("-0+1.23j", -0 + 1.23j),
    ("-0-1.23j", -0 - 1.23j),
    ("-0.+0j", -0.0 + 0j),
    ("-0.-0j", -0.0 - 0j),
    ("-0.+1.23j", -0.0 + 1.23j),
    ("-0.-1.23j", -0.0 - 1.23j),
    ("-0.0+0j", -0.0 + 0j),
    ("-0.0-0j", -0.0 - 0j),
    ("-0.0+1.23j", -0.0 + 1.23j),
    ("-0.0-1.23j", -0.0 - 1.23j),
    ("+1.23+10j", +1.23 + 10j),
    ("+1.23-10j", +1.23 - 10j),
    ("+1.23+1.23j", +1.23 + 1.23j),
    ("+1.23-1.23j", +1.23 - 1.23j),
    ("-1.23+10j", -1.23 + 10j),
    ("-1.23-10j", -1.23 - 10j),
    ("-1.23+1.23j", -1.23 + 1.23j),
    ("-1.23-1.23j", -1.23 - 1.23j),
    # Scientific.
    ("+1.23e7+10j", +1.23e7 + 10j),
    ("+1.23e+7+10j", +1.23e7 + 10j),
    ("+1.23e-7+10j", +1.23e-7 + 10j),
    ("+1.23e7-10j", +1.23e7 - 10j),
    ("+1.23e+7-10j", +1.23e7 - 10j),
    ("+1.23e-7-10j", +1.23e-7 - 10j),
    ("+1.23e7+1.23j", +1.23e7 + 1.23j),
    ("+1.23e+7+1.23j", +1.23e7 + 1.23j),
    ("+1.23e-7+1.23j", +1.23e-7 + 1.23j),
    ("+1.23e7-1.23j", +1.23e7 - 1.23j),
    ("+1.23e+7-1.23j", +1.23e7 - 1.23j),
    ("+1.23e-7-1.23j", +1.23e-7 - 1.23j),
    ("-1.23e7+10j", -1.23e7 + 10j),
    ("-1.23e+7+10j", -1.23e7 + 10j),
    ("-1.23e-7+10j", -1.23e-7 + 10j),
    ("-1.23e7-10j", -1.23e7 - 10j),
    ("-1.23e+7-10j", -1.23e7 - 10j),
    ("-1.23e-7-10j", -1.23e-7 - 10j),
    ("-1.23e7+1.23j", -1.23e7 + 1.23j),
    ("-1.23e+7+1.23j", -1.23e7 + 1.23j),
    ("-1.23e-7+1.23j", -1.23e-7 + 1.23j),
    ("-1.23e7-1.23j", -1.23e7 - 1.23j),
    ("-1.23e+7-1.23j", -1.23e7 - 1.23j),
    ("-1.23e-7-1.23j", -1.23e-7 - 1.23j),
    # Infinities.
    ("+1.23+infj", +1.23 + complex("infj")),
    ("+1.23-infj", -1.23 - complex("infj")),
    ("-1.23+infj", -1.23 + complex("infj")),
    ("-1.23-infj", -1.23 - complex("infj")),
    ("+inf+infj", float("+inf") + complex("infj")),
    ("+inf-infj", float("+inf") - complex("infj")),
    ("-inf+infj", float("-inf") + complex("infj")),
    ("-inf-infj", float("-inf") - complex("infj")),
    # Infinities with scientific.
    ("+1.23e7+infj", +1.23e7 + complex("infj")),
    ("+1.23e7-infj", +1.23e7 - complex("infj")),
    ("+1.23e+7+infj", +1.23e7 + complex("infj")),
    ("+1.23e+7-infj", +1.23e7 + complex("infj")),
    ("+1.23e-7+infj", +1.23e-7 + complex("infj")),
    ("+1.23e-7-infj", +1.23e-7 - complex("infj")),
    ("-1.23e7+infj", -1.23e7 + complex("infj")),
    ("-1.23e7-infj", -1.23e7 - complex("infj")),
    ("-1.23e+7+infj", -1.23e7 + complex("infj")),
    ("-1.23e+7-infj", -1.23e7 - complex("infj")),
    ("-1.23e-7+infj", -1.23e-7 + complex("infj")),
    ("-1.23e-7-infj", -1.23e-7 - complex("infj")),
    ("+inf+1.23e7j", float("+inf") + 1.23e7j),
    ("+inf-1.23e7j", float("+inf") - 1.23e7j),
    ("+inf+1.23e+7j", float("+inf") + 1.23e7j),
    ("+inf-1.23e+7j", float("+inf") - 1.23e7j),
    ("+inf+1.23e-7j", float("+inf") + 1.23e-7j),
    ("+inf-1.23e-7j", float("+inf") - 1.23e-7j),
    ("-inf+1.23e7j", float("-inf") + 1.23e7j),
    ("-inf-1.23e7j", float("-inf") - 1.23e7j),
    ("-inf+1.23e+7j", float("-inf") + 1.23e7j),
    ("-inf-1.23e+7j", float("-inf") - 1.23e7j),
    ("-inf+1.23e-7j", float("-inf") + 1.23e-7j),
    ("-inf-1.23e-7j", float("-inf") - 1.23e-7j),
)

# No signs allowed!
FLOATS_STD = (
    ("0.", "0.0", 0.0),
    ("0.0", "0.0", 0.0),
    ("0.00000", "0.0", 0.0),
    ("0.00000000000001", "1e-14", 0.00000000000001),
    ("1.", "1.0", 1.0),
    ("1.0", "1.0", 1.0),
    ("1.10", "1.1", 1.1),
    ("1.10000", "1.1", 1.1),
    ("15.151", "15.151", 15.151),
    # Separation of digits with `_`.
    ("1_0.", "10.0", 10.0),
    ("1_00.", "100.0", 100.0),
    ("1_000.", "1000.0", 1000.0),
    ("1_000_000.", "1000000.0", 1000000.0),
    ("1_0_0_0_0_0_0.", "1000000.0", 1000000.0),
)
FLOATS_SCIENTIFIC = (
    ("0.e7", "0.0", 0e7),
    ("0.0e7", "0.0", 0e7),
    ("1.23e7", "12300000.0", 1.23e7),
    ("1.23e+7", "12300000.0", 1.23e7),
    ("1.23e-7", "1.23e-07", 1.23e-7),
    # Separation of digits with `_`.
    ("1_0e3", "10000.0", 10000.0),
    ("1_00e3", "10000.0", 10000.0),
    ("1_000e3", "1000000.0", 1000000.0),
    ("1_000_000e-3", "1000.0", 1000.0),
    ("1_0_0_0_0_0_0e-3", "1000.0", 1000.0),
    ("1_0.e3", "10000.0", 10000.0),
    ("1_00.e3", "10000.0", 10000.0),
    ("1_000.e3", "1000000.0", 1000000.0),
    ("1_000_000.e-3", "1000.0", 1000.0),
    ("1_0_0_0_0_0_0.e-3", "1000.0", 1000.0),
    ("1_0.0e3", "10000.0", 10000.0),
    ("1_00.0e3", "10000.0", 10000.0),
    ("1_000.0e3", "1000000.0", 1000000.0),
    ("1_000_000.0e-3", "1000.0", 1000.0),
    ("1_0_0_0_0_0_0.0e-3", "1000.0", 1000.0),
    ("1_0.1_2e3", "10000.12", 10000.12),
    ("1_00.1_2e3", "10000.12", 10000.12),
    ("1_000.1_2e3", "1000000.12", 1000000.12),
    ("1_000_000.1_2e-3", "1000.12", 1000.12),
    ("1_0_0_0_0_0_0.1_2e-3", "1000.12", 1000.12),
)
FLOATS_INF = (("inf", "inf", float("inf")),)
FLOATS = (*FLOATS_STD, *FLOATS_SCIENTIFIC, *FLOATS_INF)

# No signs allowed!
# NOTE: the middle (generator) forms may seem counter-intuitive in places but match that
# of Python's repr() for complex numbers.
IMAGINARIES = (
    ("0j", "0j", 0j),
    ("0.j", "0j", 0.0j),
    ("0.0j", "0j", 0.0j),
    ("10j", "10j", 10j),
    ("1.32j", "1.32j", 1.32j),
    # Scientific.
    ("0e7j", "0j", 0e7j),
    ("0.e7j", "0j", 0.0e7j),
    ("0.0e7j", "0j", 0.0e7j),
    ("1.23e7j", "12300000j", 1.23e7j),
    ("1.23e+7j", "12300000j", 1.23e7j),
    ("1.23e-7j", "1.23e-07j", 1.23e-7j),
    # Infinities.
    ("infj", "infj", complex("infj")),
    # Separation of digits with `_`.
    ("1_0j", "10j", 10j),
)

ARRAYS_STD = (
    ("[]", []),
    ("[[]]", [[]]),
    ("[[[]]]", [[[]]]),
    ("[1]", [1]),
    ("[[1]]", [[1]]),
    ("[[[1]]]", [[[1]]]),
    ("[1, 2]", [1, 2]),
    ("[[1], 2]", [[1], 2]),
    ("[[[1], 2], 3]", [[[1], 2], 3]),
    (
        "[1, 2, [3, 4], [5, 6, [7, 8, [9, 10, [11]]]]]",
        [1, 2, [3, 4], [5, 6, [7, 8, [9, 10, [11]]]]],
    ),
    ("[[[1, 2]], [[3, 4]]]", [[[1, 2]], [[3, 4]]]),
)
ARRAYS_WHITESPACE = (
    ("[ ]", []),
    ("[[ ]]", [[]]),
    ("[ [ [ ]]]", [[[]]]),
    ("[[ []] ]", [[[]]]),
    ("[ 1 ]", [1]),
    ("[[1 ]]", [[1]]),
    ("[[ [1 ]] ]", [[[1]]]),
    ("[1,   2 ]", [1, 2]),
    ("[[1 ]  ,   2  ]", [[1], 2]),
    ("[ [ [1], 2  ] ,   3 ]", [[[1], 2], 3]),
    ("[ [[1   , 2  ] ], [[ 3 , 4 ] ]   ]", [[[1, 2]], [[3, 4]]]),
)
ARRAYS = (*ARRAYS_STD, *ARRAYS_WHITESPACE)

NUMBER_EXPRESSIONS = (
    ("2+3", 2 + 3),
    ("2-3", 2 - 3),
    ("2*3", 2 * 3),
    ("2/3", 2 / 3),
    ("2//3", 2 // 3),
    ("2**3", 2 ** 3),
    ("2+3*4", 2 + 3 * 4),
    ("3*4+2", 3 * 4 + 2),
    ("3+5**2", 3 + 5 ** 2),
    ("3*5**2", 3 * 5 ** 2),
    ("sqrt(1+3)+5", (_SQRT(1 + 3) + 5).eval()),
    ("4**3**2", 4 ** 3 ** 2),
    ("10/5/2", 10 / 5 / 2),
)

COMPLEX_NUMBER_EXPRESSIONS = (
    ("0+0j", 0 + 0j),
    ("0-0j", 0 - 0j),
    ("0+1.23j", 0 + 1.23j),
    ("0-1.23j", 0 - 1.23j),
    ("0.+0j", 0.0 + 0j),
    ("0.-0j", 0.0 - 0j),
    ("0.+1.23j", 0.0 + 1.23j),
    ("0.-1.23j", 0.0 - 1.23j),
    ("0.0+0j", 0.0 + 0j),
    ("0.0-0j", 0.0 - 0j),
    ("0.0+1.23j", 0.0 + 1.23j),
    ("0.0-1.23j", 0.0 - 1.23j),
    ("1.23+10j", 1.23 + 10j),
    ("1.23-10j", 1.23 - 10j),
    ("1.23+1.23j", 1.23 + 1.23j),
    ("1.23-1.23j", 1.23 - 1.23j),
    # Scientific.
    ("1.23e7+10j", 1.23e7 + 10j),
    ("1.23e+7+10j", 1.23e7 + 10j),
    ("1.23e-7+10j", 1.23e-7 + 10j),
    ("1.23e7-10j", 1.23e7 - 10j),
    ("1.23e+7-10j", 1.23e7 - 10j),
    ("1.23e-7-10j", 1.23e-7 - 10j),
    ("1.23e7+1.23j", 1.23e7 + 1.23j),
    ("1.23e+7+1.23j", 1.23e7 + 1.23j),
    ("1.23e-7+1.23j", 1.23e-7 + 1.23j),
    ("1.23e7-1.23j", 1.23e7 - 1.23j),
    ("1.23e+7-1.23j", 1.23e7 - 1.23j),
    ("1.23e-7-1.23j", 1.23e-7 - 1.23j),
    # Infinities.
    ("1.23+infj", 1.23 + complex("infj")),
    ("1.23-infj", 1.23 - complex("infj")),
    ("inf+infj", float("inf") + complex("infj")),
    ("inf-infj", float("inf") - complex("infj")),
    # Infinities with scientific.
    ("1.23e7+infj", 1.23e7 + complex("infj")),
    ("1.23e7-infj", 1.23e7 - complex("infj")),
    ("1.23e+7+infj", 1.23e7 + complex("infj")),
    ("1.23e+7-infj", 1.23e7 - complex("infj")),
    ("1.23e-7+infj", 1.23e-7 + complex("infj")),
    ("1.23e-7-infj", 1.23e-7 - complex("infj")),
    ("inf+1.23e7j", float("inf") + 1.23e7j),
    ("inf-1.23e7j", float("inf") - 1.23e7j),
    ("inf+1.23e+7j", float("inf") + 1.23e7j),
    ("inf-1.23e+7j", float("inf") - 1.23e7j),
    ("inf+1.23e-7j", float("inf") + 1.23e-7j),
    ("inf-1.23e-7j", float("inf") - 1.23e-7j),
)

FUNCTION_EXPRESSIONS_EAGER = (
    # Single argument.
    ("cos(0)", _COS(0).eval()),
    ("cos(3.141)", _COS(3.141).eval()),
    (
        "cos(1.8446744073709552923592595329252523523e+19)",
        _COS(1.8446744073709552923592595329252523523e19).eval(),
    ),
    # Multiple arguments.
    ("arctan2(0, 0)", _ATAN2(0, 0).eval()),
    ("arctan2(1, 1)", _ATAN2(1, 1).eval()),
    (
        "arctan2(1.23e-5, 6.43e-7)",
        _ATAN2(1.23e-5, 6.43e-7).eval(),
    ),
    # Nested functions.
    (
        "(1-cos(2*8.8))/2",
        ((1 - _COS(2 * 8.8)) / 2).eval(),
    ),
    # Compound expressions.
    ("3.141*sin(3.141)", (3.141 * _SIN(3.141)).eval()),
    ("-3.141*tan(3.141)", (-3.141 * _TAN(3.141)).eval()),
    ("-10*abs(1.82)*pos(3.141)", (-10 * _ABS(1.82) * 3.141).eval()),
)

FUNCTION_EXPRESSIONS_LAZY = (
    # Single argument.
    ("cos(pi)", _COS(_PI)),
    ("cos(pi/2)", _COS(_PI / 2)),
    ("cos(3*pi/2)", _COS(3 * _PI / 2)),
    ("exp(1j*pi)", _EXP(1j * _PI)),
    # Multiple arguments.
    ("arctan2(pi, pi)", _ATAN2(_PI, _PI)),
    # Nested functions.
    (
        "arccos(cos(pi))",
        _ACOS(_COS(_PI)),
    ),
    ("arcsin(sin(pi/2))", _ASIN(_SIN(_PI / 2))),
)

PARENTHESISED_EXPRESSIONS_EAGER = (
    ("(3*5)**2", (3 * 5) ** 2),
    ("(2+3)*4", (2 + 3) * 4),
    ("(4**3)**2", (4 ** 3) ** 2),
    ("10/(5/2)", 10 / (5 / 2)),
    # With whitespace.
    ("(1 + 1)", (1 + 1)),
    ("((1 + 1))", ((1 + 1))),
    ("(((1 + 1)))", (((1 + 1)))),
    ("(1+ 1)", (1 + 1)),
    ("(1 +1)", (1 + 1)),
    ("( 1 + 1)", (1 + 1)),
    ("(1 + 1 )", (1 + 1)),
    ("( 1 + 1 )", (1 + 1)),
    ("(1   +  1 )", (1 + 1)),
    ("( 1   +  1)", (1 + 1)),
    ("(  (1 + (2 - 3) ) * 5)", ((1 + (2 - 3)) * 5)),
)

PARENTHESISED_EXPRESSIONS_LAZY = (
    # The 10//4 branch gets eagerly evaluated, but the rest is left as symbolic because of `pi`.
    ("(cos(pi)+(10//4)-3)*5", _MUL(_SUB(_ADD(_COS(_PI), 2), 3), 5)),
    # With whitespace.
    (
        "((( cos(  pi ) + (10//4) - 3) ) * 5)",
        _MUL(_SUB(_ADD(_COS(_PI), 2), 3), 5),
    ),
)

# Expressions that are eagerly evaluated by the compiler.
# Note: we separate out complex/imaginary numbers here; they're not allowed as model element values
# so we apply a separate test.
EAGER_EXPRESSIONS = (
    UNARY_INTEGERS
    + UNARY_FLOATS
    + NUMBER_EXPRESSIONS
    + FUNCTION_EXPRESSIONS_EAGER
    + PARENTHESISED_EXPRESSIONS_EAGER
)
EAGER_EXPRESSIONS_COMPLEX = (
    UNARY_IMAGINARIES + UNARY_COMPLEX + COMPLEX_NUMBER_EXPRESSIONS
)

# Expressions that are kept as symbols due to dependencies on other symbols.
LAZY_EXPRESSIONS = (
    tuple(CONSTANTS.items())
    + FUNCTION_EXPRESSIONS_LAZY
    + PARENTHESISED_EXPRESSIONS_LAZY
)

# Reflectivity, transmissivity and loss sets (all add up to 1).
RTL_SETS = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0.5, 0.5, 0),
    (0.5, 0, 0.5),
    (0, 0.5, 0.5),
    (0.1, 0.1, 0.8),
    (0.9, 0.09, 0.01),
)

# Laser powers.
LASER_POWERS = tuple(np.linspace(0, 1000, 10))

RADII_OF_CURVATURES = (
    np.inf,
    -np.inf,
    1,
    -1,
    3.141,
    -3.141,
    6.282,
    -6.282,
    1e9,
    -1e9,
)

# Rcx and Rcy pairs.
RADII_OF_CURVATURE_PAIRS = tuple(combinations(RADII_OF_CURVATURES, 2))
