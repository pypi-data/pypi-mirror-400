"""Kat file parser reference syntax tests."""

import pytest
from finesse.script import parse
from finesse.script.exceptions import KatScriptError
from finesse.symbols import Constant
from testutils.text import dedent_multiline, escape_full


@pytest.fixture
def model_with_references(model):
    model.parse(
        """
        var L 1
        pd P ITM.p1.o

        l L0 P=1
        s s1 L0.p1 ITM.p1
        m ITM R=1-ETM.T L=0
        s sCAV ITM.p2 ETM.p1 L=L
        m ETM R=0.99 T=0.01
        """
    )

    return model


@pytest.fixture
def model_with_references_second_parse(model_with_references):
    model_with_references.parse("xaxis(L0.P, lin, 0, 100, 10)")
    return model_with_references


def test_first_run(model_with_references):
    model_with_references.run()


def test_second_parse_run(model_with_references_second_parse):
    model_with_references_second_parse.run()


def test_symbolic_references(model_with_references):
    assert model_with_references.ITM.R.eval() == 1 - model_with_references.ETM.T.eval()
    assert model_with_references.spaces.sCAV.L.eval() == 1


def test_reference():
    model = parse(
        """
        l l1
        l l2 P=l1.P
        """
    )
    assert model.l2.P.value == model.l1.P.ref


def test_self_reference__mirror():
    model = parse("m m1 R=1-m1.T T=0.5")
    assert model.m1.T.value == 0.5
    assert model.m1.R.value == Constant(1) - model.m1.T.ref


def test_self_reference__gauss():
    model = parse(
        """
        l l1
        gauss g1 l1.p1.o w0x=0.01 w0y=g1.w0x zx=100 zy=g1.zx
        """
    )
    assert model.g1.w0y.value == model.g1.w0x.ref
    assert model.g1.zy.value == model.g1.zx.ref


def test_default_reference():
    """Test that references to elements (and not their model parameters) return their
    default."""
    model = parse(
        """
        var myvar 180
        l l1
        l l2 P=l1.P phase=myvar
        """
    )
    assert model.l2.phase.eval() == 180


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "l l1 P=l2.P",
            (
                "\nline 1: model has no attribute 'l2'\n"
                "\nNo suggestions found for 'l2'\n"
                "-->1: l l1 P=l2.P\n"
                "             ^^^^"
            ),
            id="ref-to-non-existent-element-1",
        ),
        pytest.param(
            dedent_multiline(
                """
                m m1
                l l1 P=m1.
                """
            ),
            (
                "\nline 2: 'm1.' should not end with a '.'\n"
                "   1: m m1\n"
                "-->2: l l1 P=m1.\n"
                "             ^^^"
            ),
            id="ref-to-non-existent-element-2",
        ),
        pytest.param(
            "l l1 P=l1.P",
            (
                "\nline 1: cannot set l1.P to self-referencing value l1.P\n"
                "-->1: l l1 P=l1.P\n"
                "             ^^^^"
            ),
            id="ref-to-self",
        ),
        pytest.param(
            "l l1 P=l1.A",
            (
                "\nline 1: model has no attribute 'l1.A'\n"
                "\nDid you mean: 'l1.P' or 'l1.f'?\n"
                "-->1: l l1 P=l1.A\n"
                "             ^^^^"
            ),
            id="ref-to-nonexistent-same-element-arg",
        ),
        pytest.param(
            # this used to suggest '__dict__', because it is a an attribute of Model
            "l l1 P=__dic__",
            (
                "\nline 1: model has no attribute '__dic__'\n"
                "\nNo suggestions found for '__dic__'\n"
                "-->1: l l1 P=__dic__\n"
                "             ^^^^^^^"
            ),
            id="ref-to-dunder-attribute-no-suggestion",
        ),
        # Make sure class attributes are not accepted as valid references
        pytest.param(
            # this used to suggest '__dict__', because it is a an attribute of Model
            "l l1 P=__dict__",
            (
                "\nline 1: Forbidden word '__dict__' in this context (python class attribute)\n"
                "\nNo suggestions found for '__dict__'\n"
                "-->1: l l1 P=__dict__\n"
                "             ^^^^^^^^"
            ),
            id="ref-to-class-attribute",
        ),
        # Components with constructors that contain **kwargs should also be handled.
        pytest.param(
            dedent_multiline(
                """
                l l1
                gauss g1 l1.p1.o w0x=0.01 w0y=0.01 zx=100 zy=g1.zz
                """
            ),
            (
                "\nline 2: model has no attribute 'g1.zz'\n"
                "\nDid you mean: 'g1.zx' or 'g1.zy'?\n"
                "   1: l l1\n"
                "-->2: gauss g1 l1.p1.o w0x=0.01 w0y=0.01 zx=100 zy=g1.zz\n"
                "                                                   ^^^^^"
            ),
            id="ref-to-nonexistent-same-element-arg--component-with-kwargs",
        ),
        # see https://gitlab.com/ifosim/finesse/finesse3/-/issues/622
        pytest.param(
            dedent_multiline(
                """
                m m1 L=1 T=0
                m m2 L=1 T=0
                s s1 m1.p2 m2.p1
                l l1 P=qqq.P
                """
            ),
            (
                "\nline 4: model has no attribute 'qqq'\n"
                "\nNo suggestions found for 'qqq'\n"
                "   3: s s1 m1.p2 m2.p1\n"
                "-->4: l l1 P=qqq.P\n"
                "             ^^^^^"
            ),
            id="ref-to-non-existent-element-with-spaces",
        ),
    ),
)
def test_invalid_reference(script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        parse(script)


def test_geometric_parameters_as_references():
    """Test a model containing a geometric model parameter referencing another element's
    value.

    See #172.
    """
    model = parse(
        """
        l L0 P=1

        s s0 L0.p1 ITM.p1

        m ITM R=0.99 T=0.01 Rc=-10
        s CAV ITM.p2 ETM.p1 L=L    # <-------
        m ETM R=0.99 T=0.01 Rc=10

        cav FP ITM.p2.o

        var L 1
        """
    )

    # Check reference.
    assert model.spaces.CAV.L == model.L
    assert model.spaces.CAV.L.value == model.L
    # Check value.
    assert model.spaces.CAV.L.eval() == 1


def test_illegal_self_reference():
    match = """
line 1: DegreeOfFreedom does not support self-referencing.
-->1: dof mirror_1 mirror_1.DC +1
                   ^^^^^^^^^^^"""
    with pytest.raises(KatScriptError, match=escape_full(match)):
        parse("dof mirror_1 mirror_1.DC +1")
