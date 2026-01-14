"""Test if math detector type casting works."""

import pytest
import numpy as np
from finesse import Model
from finesse.detectors import MathDetector
from finesse.symbols import Constant


@pytest.fixture
def model():
    m = Model()
    m.parse(
        """
        modes(maxtem=2)
        l L0
        gauss g1 L0.p1.o q=1+1j
        m Mirr R=0.5 L=0
        link(L0,Mirr)

        ad ad_Aout Mirr.p2.o f=0
        fd fd_Aout Mirr.p2.o f=0

        xaxis(L0.P, lin, 0, 10, 10)
        """
    )
    return m


def test_math_detector_complex_init(model):
    model.add(MathDetector("md_Aout", Constant(model.ad_Aout), dtype=np.complex128))
    sol = model.run()
    assert sol["md_Aout"].dtype == np.complex128
    assert np.all(np.isclose(sol["md_Aout"], sol["ad_Aout"]))


def test_math_detector_complex_set_expression(model):
    model.parse("mathd md_Aout ad_Aout")
    model.md_Aout.set_expression(model.md_Aout.expression, dtype=np.complex128)
    sol = model.run()
    assert sol["md_Aout"].dtype == np.complex128
    assert np.all(np.isclose(sol["md_Aout"], sol["ad_Aout"]))


def test_math_detector_shape_init(model):
    model.add(
        MathDetector(
            "md_Aout",
            Constant(model.fd_Aout),
            dtype=np.complex128,
            dtype_shape=(len(model.modes()),),
        )
    )
    sol = model.run()
    assert sol["md_Aout"].shape == (len(sol.x1), len(model.modes()))
    assert np.all(np.isclose(sol["md_Aout"], sol["fd_Aout"]))


def test_math_detector_shape_set_expression(model):
    model.parse("mathd md_Aout fd_Aout")
    model.md_Aout.set_expression(
        model.md_Aout.expression, dtype=np.complex128, dtype_shape=(len(model.modes()),)
    )
    sol = model.run()
    assert sol["md_Aout"].shape == (len(sol.x1), len(model.modes()))
    assert np.all(np.isclose(sol["md_Aout"], sol["fd_Aout"]))


def test_math_detector_label_init(model):
    model.add(MathDetector("md", Constant(2), label="a label"))
    sol = model.run()
    assert sol.trace_info["md"]["label"] == "a label"


def test_math_detector_label_set_expression(model):
    model.parse("mathd md 2")
    model.md.set_expression(model.md.expression, label="a label")
    sol = model.run()
    assert sol.trace_info["md"]["label"] == "a label"


def test_math_detector_unit_init(model):
    model.add(MathDetector("md", Constant(2), unit="a unit"))
    sol = model.run()
    assert sol.trace_info["md"]["unit"] == "a unit"


def test_math_detector_unit_set_expression(model):
    model.parse("mathd md 2")
    model.md.set_expression(model.md.expression, unit="a unit")
    sol = model.run()
    assert sol.trace_info["md"]["unit"] == "a unit"
