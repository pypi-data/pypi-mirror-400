"""Parse function tests."""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings

from finesse.model import Model
from finesse.script import parse, parse_file
from finesse.script.parser import KatParser
from finesse.script.exceptions import KatParsingInputSizeWarning
from testutils.diff import assert_models_equivalent
from testutils.fuzzing import DEADLINE, kat_script_line
from testutils.text import dedent_multiline


@pytest.fixture
def model_kat_script():
    """Some uneventful kat model."""
    return dedent_multiline(
        """
        laser l0 P=1
        space s1 l0.p1 itm.p1
        mirror itm R=0.99 T=0.01
        space scav itm.p2 etm.p1 L=1
        mirror etm R=itm.R T=itm.T phi=itm.phi
        pd pdcav itm.p1.o
        """
    )


@pytest.fixture
def model_via_string(model_kat_script):
    return parse(model_kat_script)


@pytest.fixture
def model_via_file(tmp_path, model_kat_script):
    """Test that parsing a string with kat script is the same as via a file."""
    tmpfile = tmp_path / "script.kat"
    with tmpfile.open(mode="w") as fp:
        fp.write(model_kat_script)
    with tmpfile.open(mode="r") as fp:
        return parse_file(fp)


def test_parse_function_is_same_as_model_parse_method(
    model_via_string, model, model_kat_script
):
    """Test that parsing directly with :meth:`.parse` results in the same model as
    :meth:`.Model.parse`."""
    model.parse(model_kat_script)
    assert_models_equivalent(model_via_string, model)


def test_parse_is_same_as_parse_file(tmp_path, model_via_string, model_via_file):
    """Test that parsing a string with kat script is the same as via a file."""
    assert_models_equivalent(model_via_string, model_via_file)


@given(line=kat_script_line())
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
def test_script_line_fuzzing(line):
    parse(line)


def test_pythonic_names(model):
    """Test that defining elements and analyses via their python class names is
    identical to using their katscript names.

    https://gitlab.com/ifosim/finesse/finesse3/-/issues/554
    """
    m_kat = Model()
    m_pythonic = Model()
    m_kat.parse(
        """
        laser laser1 P=1
        """
    )
    m_pythonic.parse(
        """
        Laser laser1 P=1
        """
    )
    assert_models_equivalent(m_kat, m_pythonic)
    out_kat = m_kat.run("xaxis(laser1.P, lin, 0, 1, 10)")
    out_pythonic = m_pythonic.run("Xaxis(laser1.P, lin, 0, 1, 10)")
    np.testing.assert_equal(out_kat.data, out_pythonic.data)


@pytest.mark.parametrize(
    "n_lines, warns",
    (
        (1, False),
        (10, True),
    ),
)
def test_unreasonable_input_size(n_lines, warns, monkeypatch):
    monkeypatch.setattr(KatParser, "_script_size_limit", 0.1)
    script = "\n".join(f"m m{i} R=0.99 T=0.01" for i in range(n_lines))
    m = Model()
    if warns:
        with pytest.warns(KatParsingInputSizeWarning):
            m.parse(script)
    else:
        m.parse(script)


@pytest.mark.parametrize(
    "n_words, warns",
    (
        (1, False),
        (20, True),
    ),
)
def test_unreasonable_line_length(n_words, warns, monkeypatch):
    monkeypatch.setattr(KatParser, "_script_line_limit", 10)
    m = Model()
    m.parse("m m1 R=0.9 T=0.1")
    if warns:
        with pytest.warns(KatParsingInputSizeWarning):
            m.parse(f"sweep(m1.phi, {[i for i in range(n_words)]}, True)")
    else:
        m.parse(f"sweep(m1.phi, {[i for i in range(n_words)]}, True)")
