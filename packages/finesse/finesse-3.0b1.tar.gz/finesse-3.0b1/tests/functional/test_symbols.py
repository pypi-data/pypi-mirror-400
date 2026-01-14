import operator
from functools import reduce
from itertools import permutations

import finesse
import numpy as np
import pytest
from finesse.symbols import (
    FUNCTIONS,
    Constant,
    Variable,
    coefficient_and_term,
    collect,
    expand,
    expand_pow,
    operator_add,
    operator_mul,
)


@pytest.fixture(scope="module")
def model():
    model = finesse.script.parse(
        """
    var a 1
    var b 2
    var c 3
    """
    )
    return model


@pytest.fixture(scope="module", params=["variables", "parameter_ref"])
def a_b_variables(request, model):
    if request.param == "variables":
        return Variable("a"), Variable("b")
    else:
        return model.a.ref, model.b.ref


@pytest.fixture(scope="module", params=["variables", "parameter_ref"])
def a_b_c_variables(request, model):
    if request.param == "variables":
        return (
            Variable("a"),
            Variable("b"),
            Variable("c"),
        )
    else:
        return model.a.ref, model.b.ref, model.c.ref


@pytest.fixture(scope="module", params=["variables", "parameter_ref"])
def a(request, model):
    if request.param == "variables":
        return Variable("a")
    else:
        return model.a.ref


@pytest.fixture(scope="module", params=["normal", "pos"])
def a_pos_a(request, a):
    # either `a` or what should act the same `+a`
    if request.param == "normal":
        return a
    else:
        return +a


@pytest.fixture(scope="module", params=["variables", "parameter_ref"])
def b(request, model):
    if request.param == "variables":
        return Variable("b")
    else:
        return model.b.ref


@pytest.fixture(scope="module", params=["variables", "parameter_ref"])
def c(request, model):
    if request.param == "variables":
        return Variable("c")
    else:
        return model.c.ref


def test_simplification_context():
    """Test the simplification context manager."""

    # Ensure _SIMPLIFICATION_ENABLED is False at start
    assert finesse.symbols._SIMPLIFICATION_ENABLED is False

    # Test entering and exiting the context
    with finesse.symbols.simplification():
        assert finesse.symbols._SIMPLIFICATION_ENABLED is True
    assert finesse.symbols._SIMPLIFICATION_ENABLED is False

    # Test entering the context when _SIMPLIFICATION_ENABLED is already True
    with finesse.symbols.simplification():
        assert finesse.symbols._SIMPLIFICATION_ENABLED is True
        with pytest.raises(RuntimeError):
            with finesse.symbols.simplification():
                pass
    assert finesse.symbols._SIMPLIFICATION_ENABLED is False

    # Test entering the context with allow_flagged=True when _SIMPLIFICATION_ENABLED is already True
    with finesse.symbols.simplification():
        assert finesse.symbols._SIMPLIFICATION_ENABLED is True
        with finesse.symbols.simplification(allow_flagged=True):
            assert finesse.symbols._SIMPLIFICATION_ENABLED is True
    assert finesse.symbols._SIMPLIFICATION_ENABLED is False


def test_multiply_reordering(a, b):
    """Ensure multiplying 2,a,b in any order gives the same final result ordering."""
    with finesse.symbols.simplification():
        args = [2, a, b]
        for comb in permutations(args):
            y = reduce(operator.mul, comb)
            assert y == 2 * a * b
            assert y.args == [2, a, b]


def test_multiply_collect(a):
    with finesse.symbols.simplification():
        args = [2, a, 4]
        for comb in permutations(args):
            y = reduce(operator.mul, comb)
            assert y == 8 * a
            assert y.args == [8, a]


def test_sum(a_b_variables):
    a, b = a_b_variables
    y = a + b
    assert str(y) == "(a+b)"
    assert y.args == [a, b]
    y = b + a
    assert str(y) == "(b+a)"
    assert y.args == [b, a]


def test_sub(a_b_variables):
    a, b = a_b_variables
    y = a - b
    assert str(a - b) == "(a-b)"
    assert y.args == [a, b]
    y = b - a
    assert str(b - a) == "(b-a)"
    assert y.args == [b, a]


def test_exp_reduction(a, b):
    with finesse.symbols.simplification():
        z = 2 * a * np.exp(a + b) * np.exp(a - b) * b
    assert z.args == [2, a, b, np.exp(2 * a)]


def test_exp_reduction_cancel(a):
    with finesse.symbols.simplification():
        z = np.exp(a) * np.exp(-a)
    assert z.value == 1, z


def test_mul_pow(a):
    with finesse.symbols.simplification():
        z = a**0.5 * a**0.5
    assert z == a


def test_mul_pow_2(a):
    with finesse.symbols.simplification():
        z = a**0.5 * a**1.5
    assert z == a**2


def test_mul(a_b_variables):
    a, b = a_b_variables
    assert str(a * b) == "(a*b)"
    assert str(2 * a * b) == "((2*a)*b)"


def test_pow(a):
    with finesse.symbols.simplification():
        z = (a**0.5) ** 2
    assert z == a


def test_pow_2(a):
    with finesse.symbols.simplification():
        z = (a**0.5) ** 4
    assert z == a**2
    assert z.op == operator.pow


def test_numpy_fn(a_b_variables):
    a, _ = a_b_variables
    assert str(np.cos(a)) == "cos(a)"


def test_lambdify(a_b_c_variables):
    a, b, c = a_b_c_variables
    y = a + 2 * b + 3 * c
    f = y.lambdify(a, b, c)
    assert f(1, 2, 3) == y.eval(subs={a: 1, b: 2, c: 3})
    f = y.lambdify(b, c, a)
    assert f(2, 3, 1) == y.eval(subs={a: 1, b: 2, c: 3})


def test_lambdify_default_variables():
    a = Variable("a")
    b = Variable("b")
    y = a + b
    f = y.lambdify()
    assert f() == a + b


def test_lambdify_default_parameter_refs():
    model = finesse.script.parse(
        """
    var a 1
    var b 2
    var c 3
    """
    )
    y = model.a.ref + model.b.ref + model.c.ref
    f = y.lambdify()
    assert f() == 6


def test_lambdify_default_mix():
    model = finesse.script.parse(
        """
    var a 1
    var b 2
    var c 3
    """
    )

    a = Variable("a")
    b = Variable("b")
    y = a + b / 2 + model.a * 3
    f = y.lambdify()
    assert f() == a + b / 2 + 3


def test_lambdify_functions(a_b_c_variables):
    a, b, c = a_b_c_variables
    y = a + np.cos(b) / c**b
    f = y.lambdify(a, b, c)
    assert f(1, 2, 3) == y.eval(subs={a: 1, b: 2, c: 3})


def test_lamdify_wrong_arguments(model):
    c = model.a.ref
    d = model.b.ref

    a = Variable("a")
    b = Variable("b")

    with pytest.raises(NameError):
        (a + b).lambdify(c, d)


def test_lambdify_expand_symbols():
    model = finesse.script.parse(
        """
    var a 1.3
    var b 2*a
    var c (10*b + cos(a))
    """
    )

    f = model.c.ref.lambdify(expand_symbols=True)
    assert f.__code__.co_argcount == 0  # only a should be present
    assert f() == 20 * 1.3 + np.cos(1.3)

    with pytest.raises(NameError):
        model.c.ref.lambdify(model.b.ref, expand_symbols=True)
        model.c.ref.lambdify(model.c.ref, expand_symbols=True)

    f = model.c.ref.lambdify(model.a.ref, expand_symbols=True)
    assert f(1) == 20 * 1 + np.cos(1)


def test_substitute(a_b_c_variables):
    a, b, c = a_b_c_variables
    assert (a).substitute({a: a}) == a
    assert (a + b).substitute({a: a}) == a + b
    assert (2 * a + b).substitute({a: a}) == 2 * a + b

    assert (a + b).substitute({a: a, b: b}) == a + b
    assert (a + b).substitute({a: a + b, b: a}) == (a + b) + a

    assert (2 * a + 3 * b).substitute({a: b, b: a}) == 2 * b + 3 * a
    assert (np.cos(2 * a) + 3 * b).substitute({a: b, b: a}) == np.cos(2 * b) + 3 * a

    assert (a + b).substitute({a: a, b: 1}) == a + 1
    assert (2 * a + 3 * b).substitute({a: b, b: 1}) == 2 * 1 + 3 * 1
    assert (np.cos(2 * a) + 3 * b).substitute({a: b, b: 1}).eval() == np.cos(2) + 3

    assert (a + b).substitute({a: a + b, b: 1}) == (a + 1) + 1
    assert (a + b).substitute({a: c, b: c + 1}) == c + (c + 1)


def test_substitute_expression_mix():
    model = finesse.Model()
    model.parse(
        """
    var c 1
    """
    )

    a = Variable("a")
    b = Variable("b")
    c = model.c.ref
    y = a + b + c
    assert y.substitute(dict(a=y)) == (a + b + c) + b + c


def test_self_eval(a_b_variables):
    a, _ = a_b_variables
    y = (a).eval({a: a})
    if hasattr(a, "parameter"):
        assert y == 1  # parameteref
    else:
        assert y == a  # variables


def test_eval_symbol_numeric(a_b_variables):
    a, b = a_b_variables
    y = a + b
    z = y.eval(subs={a: b, b: 2})
    assert z == 4


def test_parameter_ref_eval():
    model = finesse.script.parse(
        """
    var a b+2
    var b 10
    """
    )
    a, b = model.a.ref, model.b.ref
    assert a.eval() == 12
    assert b.eval() == 10
    assert (2 * a - b / 2).eval() == 19


def test_parameter_ref_eval_subs_override():
    model = finesse.script.parse(
        """
    var a 5
    var b 10
    """
    )
    a, b = model.a.ref, model.b.ref
    assert (a + b).eval() == 15
    assert (a + b).eval(subs={b: 5}) == 10


def test_parameter_ref_eval_subs_override_2():
    model = finesse.script.parse(
        """
    var a b+1
    var b 10
    """
    )
    a, b = model.a.ref, model.b.ref
    assert a.eval() == model.b.value + 1
    assert a.eval(subs={b: 5}) == 6
    assert (a + b).eval() == 21
    assert (a + b).eval(subs={b: 5}) == 11


def test_sub_and_sub(a_b_variables):
    a, b = a_b_variables
    y = (a + b).substitute({a: b, b: 1})
    assert 2 == float(y)


def test_extra_zero_equality(a_pos_a):
    ONE = Constant(1)
    ZERO = Constant(0)
    y = a_pos_a + ONE
    z = a_pos_a + ZERO + ONE
    assert y == z


def test_same_name_variables_equality():
    # Define two variables with the same name but different Python names
    var1 = Variable("x")
    var2 = Variable("x")
    var3 = Variable("y")
    assert var1 == var2
    assert var1 != var3
    assert var2 != var3


def test_simple_equality(a, a_pos_a):
    with finesse.symbols.simplification():
        assert 2 * (+a) == 2 * a_pos_a
        assert a == a_pos_a

        assert a != -a_pos_a
        assert -a != a_pos_a
        assert +a != -a_pos_a
        assert -a != a_pos_a
        assert -a == -a_pos_a

        assert 1 * a == a_pos_a
        assert a == 1 * a_pos_a
        assert a == a_pos_a / 1
        assert 1 * a == a_pos_a / 1

        assert a**1 == a_pos_a**1
        assert a**1 == a_pos_a**2 / a_pos_a

        assert 1 * a == 3 * a_pos_a / (1 + 2)
        assert 2 * a / a == 2
        assert (a - a) == 0
        assert (2 * a - a) == a_pos_a
        assert 2 * (1 * a / 1) / 2 == 2 * a_pos_a / 2


def test_equality_checks_functions(a, b, c):
    from itertools import combinations

    y = []
    # generate a bunch of different
    for op1 in ["+", "-"]:
        for op2, op3 in combinations(["+", "-", "*", "/"], 2):
            for _a, _b, _c in combinations(["a", "cos(b)", "exp(a+c)"], 3):
                y.append(
                    eval(
                        f"{op1}{_a}{op2}{_b}{op3}{_c}",
                        {"a": a, "b": b, "c": c, "cos": np.cos, "exp": np.exp},
                    )
                )

    # Each expression should equal itself and not the others
    for i in range(len(y)):
        for j in range(len(y)):
            if i == j:
                assert y[i] == y[j]
            else:
                assert y[i] != y[j]
                assert y[j] != y[i]


def test_not_equality_checks(a, b, c):
    from itertools import combinations

    y3 = []
    # generate a bunch of different
    for op1 in ["+", "-"]:
        for op2, op3 in combinations(["+", "-", "*", "/"], 2):
            for _a, _b, _c in combinations(["a", "b", "c"], 3):
                y3.append(
                    eval(f"{op1}{_a}{op2}{_b}{op3}{_c}", {"a": a, "b": b, "c": c})
                )

    y2 = []
    # generate a bunch of different
    for op1 in ["+", "-"]:
        for op2 in ["+", "-", "*", "/"]:
            for _i, _j in combinations(["a", "b", "c", "cos(a)", "exp(b)"], 2):
                y2.append(
                    eval(
                        f"{op1}{_i}{op2}{_j}",
                        {"a": a, "b": b, "c": c, "cos": np.cos, "exp": np.exp},
                    )
                )

    # these should never equal
    for i in y3:
        for j in y2:
            assert i != j


def test_equality_sum(a_b_variables):
    a, b = a_b_variables
    with finesse.symbols.simplification():
        args = [2, a, b]
        for comb in permutations(args):
            assert np.sum(comb) == 2 + a + b


def test_sub_then_sub(a_b_variables):
    a, b = a_b_variables
    if hasattr(a, "parameter"):
        assert a.parameter is not None
        assert b.parameter is not None
        assert a.parameter._model is not None
        assert b.parameter._model is not None
        assert b.parameter._model is a.parameter._model

    y = (a + b).substitute({a: b})
    assert 2 == y.substitute({b: 1})


def test_equality_mul(a_b_variables):
    a, b = a_b_variables
    with finesse.symbols.simplification():
        args = [2, a, b]
        for comb in permutations(args):
            assert np.prod(comb) == 2 * a * b


def test_simplify(a_b_variables):
    a, _ = a_b_variables
    with finesse.symbols.simplification():
        assert (
            3 / a - 2 * (4 * 1 / a - (-5 * 1 / a + 1.0))
        ).expand().collect() == 2 - 15 / a


def test_simplification(a_pos_a):
    a = a_pos_a
    with finesse.symbols.simplification():
        assert (a - a) == 0
        assert (2 * a - a) == a
        assert (a - 2 * a) == -a
        assert (a + a) == 2 * a
        # should simplify the outer terms not expand bracket
        assert a * (2 + a) * a == (2 + a) * a**2


def test_collect_pos_neg(a):
    # some more explcit tests of pos/neg being collected

    y = (+(+a)).collect()  # noqa: B002
    # collect to -> a
    assert y is a

    y = (+(-a)).collect()
    # collect to -> -a
    assert y.args == [-1, a] and y.op is operator_mul

    y = (-(+a)).collect()
    # collect to -> -a
    assert y.args == [-1, a] and y.op is operator_mul

    y = (-(-a)).collect()
    # collect to -> a
    assert y is a

    y = (+(-(-a))).collect()
    # collect to -> a
    assert y is a


def test_collect(a_pos_a):
    a = a_pos_a
    with finesse.symbols.simplification():
        assert collect(a * a) == a**2
        assert collect(a * a**-1) == 1
        assert collect(a - a) == 0
        assert collect(a + (-a)) == 0
        assert collect(a + a) == 2 * a
        assert collect(2 / a - 2 / a) == 0
        assert collect(-2 / a - 3 / a) == -5 / a
        assert collect(2 * 2 / a) == 4 / a
        assert collect(2 * (2 / a)) == 4 / a
        assert collect((1 + 2 / a) + (1 - 2 / a)) == 2
        assert collect(2 * a - a) == a
        assert collect(4 * a - 4 * a) == 0
        assert collect(-2 * a + a) == -a
        assert collect(a + a + 4) == 4 + 2 * a
        assert collect(a + 2 * a) == 3 * a
        assert collect(1.5 * a + 1.5 * a) == 3 * a
        assert collect(np.cos(a) + np.cos(a)) == 2 * np.cos(a)


def test_expand(a_b_variables):
    a, b = a_b_variables
    with finesse.symbols.simplification():
        assert -2 * a * b == -2 * a * b
        assert 2 * a * b == -2 * a * -b
        assert 2 * a * b == 2 * a * b
        assert a * 2 * b == 2 * a * b
        assert a * b * 2 == 2 * a * b
        assert expand(2 * a * (1 + b)) == 2 * a + 2 * a * b
        assert expand(2 * np.cos(a + b)) == 2 * np.cos(a + b)
        assert (
            expand(10 * np.cos(a) * (a + b)) == 10 * np.cos(a) * a + 10 * np.cos(a) * b
        )
        assert expand(3 * (1 + a) ** 2 * (2 + a) ** 2).collect() == (
            12 + 36 * a + 39 * (a) ** (2) + 18 * (a) ** (3) + 3 * (a) ** (4)
        )
        assert expand(2 / a - 6 / (3 * a)).collect() == 0


def test_expand_symbols():
    model = finesse.script.parse(
        """
    var a b+2
    var b 10
    """
    )
    a, b = model.a.ref, model.b.ref
    assert (1 + a).expand_symbols() == (1 + b + 2)
    assert (b + a).expand_symbols() == (b + b + 2)
    assert np.cos(1 + a).expand_symbols() == np.cos(1 + b + 2)
    assert np.cos(b + a).expand_symbols() == np.cos(b + b + 2)


def test_expand_mul(a_b_variables):
    a, b = a_b_variables
    from finesse.symbols import expand_mul

    # Shouldn't do anything to the expression here
    assert expand_mul(4 * a).args == [4, a]

    y = expand_mul((4 + b) * a)
    assert y.args[0].args == [4, a]
    assert y.args[1].args == [a, b]


def test_coefficient_and_term(a_b_variables):
    a, b = a_b_variables
    pi = finesse.symbols.CONSTANTS["pi"]
    assert coefficient_and_term(a) == (1, a)
    assert coefficient_and_term(2 * a) == (2, a)
    assert coefficient_and_term(a * b) == (1, a * b)
    assert coefficient_and_term(a + b) == (1, a + b)
    assert coefficient_and_term(Constant(3.3)) == (3.3, None)
    assert coefficient_and_term(np.cos(a)) == (1, np.cos(a))
    assert coefficient_and_term(3.3 * np.cos(a)) == (3.3, np.cos(a))
    assert coefficient_and_term(pi) == (pi, None)
    assert coefficient_and_term(2 * pi) == (2 * pi, None)
    assert coefficient_and_term(pi * a) == (pi, a)


def test_expand_pow(a_b_variables):
    a, _ = a_b_variables
    with finesse.symbols.simplification():
        assert expand_pow((2 * a) ** 2) == 4 * a**2
        assert (
            expand_pow(1 + (2 * a) ** 2 + 2 * (4 * a) ** 2).collect() == 1 + 36 * a**2
        )


def test_matrix_prods(a_b_variables):
    a, _ = a_b_variables
    from finesse.symbols import Matrix

    with finesse.symbols.simplification():
        A = Matrix("A")
        B = Matrix("B")
        assert (a * B * A * 2).args == [2, a, B, A]
        assert (a * B * A * 2 - 2 * a * B * A).collect() == 0


def test_nary_add_to_binary_add(a_b_c_variables):
    from operator import add

    a, b, c = a_b_c_variables

    with finesse.symbols.simplification():
        d = a + b + c

    assert d.op is operator_add
    assert d.args == [a, b, c]

    e = d.to_binary_add_mul()
    assert e.op is add
    assert e.args == [add(a, b), c]
    assert e.args[0].op is add
    assert e.args[0].args == [a, b]


def test_nary_mul_to_binary_add(a_b_c_variables):
    from operator import mul

    from finesse.symbols import operator_mul

    a, b, c = a_b_c_variables

    with finesse.symbols.simplification():
        d = a * b * c

    assert d.op is operator_mul
    assert d.args == [a, b, c]

    e = d.to_binary_add_mul()
    assert e.op is mul
    assert e.args == [mul(a, b), c]
    assert e.args[0].op is mul
    assert e.args[0].args == [a, b]


def test_binary_to_nary_mul(a_b_c_variables):
    from operator import mul

    from finesse.symbols import operator_mul

    a, b, c = a_b_c_variables
    d = a * b * c

    assert d.op is mul
    assert d.args == [mul(a, b), c]

    e = d.to_nary_add_mul()
    assert e.op is operator_mul
    assert e.args == [a, b, c]


def test_binary_to_nary_add(a_b_c_variables):
    from operator import add

    a, b, c = a_b_c_variables
    d = a + b + c

    assert d.op is add
    assert d.args == [add(a, b), c]

    e = d.to_nary_add_mul()
    assert e.op is operator_add
    assert e.args == [a, b, c]


def test_equality_add(a_b_c_variables):
    a, b, c = a_b_c_variables
    d = a + 20 + b + c
    assert (d.collect() - 10).collect() == (10 + a + b + c)


def test_constant():
    y = Constant(1) + Constant(4)
    assert y == 5
    # should retain operator without simplification
    assert y.op == operator.add

    y = Constant(1) * Constant(4)
    assert y == 4
    assert y.op == operator.mul

    with finesse.symbols.simplification():
        # Results should be the same but more simplification
        # should happen, end up with a reduced constant
        y = Constant(1) + Constant(4)
        assert y == 5
        assert isinstance(y, Constant)

        y = Constant(1) * Constant(4)
        assert y == 4
        assert isinstance(y, Constant)


def test_named_constant_collect():
    pi = finesse.symbols.CONSTANTS["pi"]
    y = pi + pi
    assert y.collect() == 2 * pi


def test_nary_keep_named_constants_add(a, b):
    pi = finesse.symbols.CONSTANTS["pi"]
    y = 2 + pi + pi + a * pi + 2 * b
    z = y.to_nary_add_mul()
    assert z.op is operator_add
    assert z.args == [2, 2 * b, pi, pi, pi * a]


def test_nary_keep_named_constants_add_duplicate(a):
    pi = finesse.symbols.CONSTANTS["pi"]
    y = a * pi + a * pi
    z = y.to_nary_add_mul()
    assert z.op is operator_mul
    assert z.args == [2, pi, a]


def test_nary_keep_named_constants_mul(a):
    pi = finesse.symbols.CONSTANTS["pi"]
    y = 2 * pi * a
    z = y.to_nary_add_mul()
    assert z.op is operator_mul
    assert z.args == [2, pi, a]


def test_nary_keep_named_constants_pow():
    pi = finesse.symbols.CONSTANTS["pi"]
    y = pi * 2 * pi
    assert y.to_nary_add_mul() == 2 * pi**2


def test_param_ref_equality():
    # issue 514
    model = finesse.script.parse("var test 1e-3")
    assert (model.test.ref == model.test.ref) is True
    assert (-model.test.ref == model.test.ref) is False
    assert (model.test.ref == -model.test.ref) is False
    assert (model.test.ref == -(-model.test.ref)) is True
    assert (-(-model.test.ref) == model.test.ref) is True


def test_function_arg_expand_collect(a):
    with finesse.symbols.simplification():
        assert np.cos(2 * (a + a)).collect().args == [4 * a]


def test_function_arg_expand_collect_zero(a):
    with finesse.symbols.simplification():
        z = np.cos(2 * (a + a) - 4 * a).expand().collect()
        assert z.args == [0]


def test_aligo_path_eval():
    # Seems that some complicated expressions don't eval fully. This tests that
    # this case does.
    model = finesse.Model()
    model.parse(
        """
    variable f1 9099471
    variable f2 5*f1
    variable nsilica 1.45
    variable Mloss 30u

    ###############################################################################
    ###   length definitions
    ###############################################################################
    variable Larm 3994.47
    variable LPR23 16.164  # distance between PR2 and PR3
    variable LSR23 15.443  # distance between SR2 and SR3
    variable LPR3BS 19.538 # distance between PR3 and BS
    variable LSR3BS 19.366 # distance between SR3 and BS
    variable lmich 5.342   # average length of MICH
    variable lschnupp 0.08 # double pass schnupp length
    variable lPRC (3+0.5)*c0/(2*f1) # T1000298 Eq2.1, N=3
    variable lSRC (17)*c0/(2*f2) # T1000298 Eq2.2, M=3

    ###############################################################################
    ###   PRC
    ###############################################################################

    m PRMAR R=0 L=40u xbeta=PRM.xbeta ybeta=PRM.ybeta phi=PRM.phi
    s sPRMsub1 PRMAR.p2 PRM.p1 L=0.0737 nr=nsilica
    m PRM T=0.03 L=8.5u Rc=11.009
    s lp1 PRM.p2 PR2.p1 L=lPRC-LPR3BS-LPR23-lmich
    bs PR2 T=250u L=Mloss alpha=-0.79 Rc=-4.545
    s lp2 PR2.p2 PR3.p1 L=LPR23
    bs PR3 T=0 L=Mloss alpha=0.615 Rc=36.027
    s lp3 PR3.p2 BS.p1 L=LPR3BS

    ###############################################################################
    ###   BS
    ###############################################################################
    bs BS R=0.5 L=Mloss alpha=45
    s BSsub1 BS.p3 BSAR1.p1 L=60m/cos(radians(BSAR1.alpha)) nr=nsilica
    s BSsub2 BS.p4 BSAR2.p2 L=60m/cos(radians(BSAR1.alpha)) nr=nsilica
    bs BSAR1 L=50u R=0 alpha=-29.186885954108114
    bs BSAR2 L=50u R=0 alpha=BSAR1.alpha

    ###############################################################################
    ###   Xarm
    ###############################################################################
    # Distance from beam splitter to X arm input mirror
    s lx1 BSAR1.p3 ITMXlens.p1 L=lmich+lschnupp/2-ITMXsub.L*ITMXsub.nr-BSsub1.L*BSsub1.nr
    lens ITMXlens f=34500
    s lx2 ITMXlens.p2 ITMXAR.p1
    m ITMXAR R=0 L=20u xbeta=ITMX.xbeta ybeta=ITMX.ybeta phi=ITMX.phi
    s ITMXsub ITMXAR.p2 ITMX.p1 L=0.2 nr=nsilica
    m ITMX T=0.014 L=Mloss Rc=-1934
    s LX ITMX.p2 ETMX.p1 L=Larm
    m ETMX T=5u L=Mloss Rc=2245
    s ETMXsub ETMX.p2 ETMXAR.p1 L=0.2 nr=nsilica
    m ETMXAR 0 500u xbeta=ETMX.xbeta ybeta=ETMX.ybeta phi=ETMX.phi
    """
    )
    path = model.path("PRM.p2.o", "ITMX.p1.i")
    y = sum(s.L * s.nr for s in path.spaces)
    # just check that indeed a float is returned when eval'd
    assert type(y.eval()) == np.float64


def test_jv(a, b):
    f = FUNCTIONS["jv"](a, b)
    assert f.op == finesse.cymath.ufuncs.jv
    assert f.args == [a, b]


def test_jv_eval():
    from scipy.special import jv

    a, b = Variable("a"), Variable("b")
    f = FUNCTIONS["jv"](a, b)
    assert f.eval() == FUNCTIONS["jv"](a, b)
    f = FUNCTIONS["jv"](a, 1.23)
    assert f.eval() == FUNCTIONS["jv"](a, 1.23)
    f = FUNCTIONS["jv"](2, 1.23)
    assert f.eval() == jv(2, 1.23)


def test_single_paramref_lambda_eval():
    model = finesse.script.parse("l l1 P=pi")
    y = model.l1.P.ref
    z = y.lambdify()
    assert z() == model.l1.P.value

    y = 10 + model.l1.P.ref
    z = y.lambdify()
    assert z() == 10 + model.l1.P.value

    y = 10 + model.l1.P.ref + model.l1.f.ref
    z = y.lambdify(model.l1.f.ref)

    assert z(0) == 10 + model.l1.P.value
    assert z(-10) == 10 + model.l1.P.value - 10
