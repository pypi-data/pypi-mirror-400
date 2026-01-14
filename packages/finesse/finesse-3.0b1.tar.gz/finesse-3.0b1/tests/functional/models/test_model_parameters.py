import finesse
import numpy as np


def test_add_parameter():
    model = finesse.Model()
    A = model.add_parameter("A", 1)
    B = model.add_parameter("B", 10)
    C = model.add_parameter("C", model.A.ref * model.B.ref)

    assert model.A in tuple(model.parameters)
    assert model.B in tuple(model.parameters)
    assert model.C in tuple(model.parameters)

    assert model.A == 1
    assert model.A.value == 1

    assert model.B == 10
    assert model.B.value == 10

    # assert(model.C == model.A.ref * model.B.ref) # doesn't pass, should it?
    assert model.C.value == model.A.ref * model.B.ref

    assert model.get("A") is A
    assert model.get("B") is B
    assert model.get("C") is C


def test_set_parameter():
    model = finesse.Model()
    _ = model.add_parameter("R", 1)
    model.parse(
        """
    l l1
    m m1 R=R T=1-R
    link(l1, m1)
    pd P m1.p2.o
    """
    )

    assert model.m1.R.value == model.R
    assert model.m1.R.value == model.R.ref
    # assert(model.m1.T.value == 1-model.R) # doesn't pass, should it?
    assert model.m1.T.value == 1 - model.R.ref


def test_change_parameter():
    model = finesse.Model()
    _ = model.add_parameter("R", 1)
    model.parse(
        """
    l l1
    m m1 R=R T=1-R
    link(l1, m1)
    pd P m1.p2.o
    """
    )

    model.R = 0.9
    assert model.m1.R.value == model.R
    assert model.m1.R.value == model.R.ref
    # assert(model.m1.T.value == 1-model.R) # doesn't pass, should it?
    assert model.m1.T.value == 1 - model.R.ref


def test_sweep_parameter():
    model = finesse.Model()
    _ = model.add_parameter("R", 1)
    model.parse(
        """
    l l1
    m m1 R=R T=1-R
    link(l1, m1)
    pd P m1.p2.o
    """
    )
    from finesse.analysis.actions import Xaxis

    sol = model.run(Xaxis(model.R, "lin", 0, 1, 10))
    assert np.allclose(sol["P"], 1 - sol.x1)


def test_sweep_parameter_str():
    model = finesse.Model()
    _ = model.add_parameter("R", 1)
    model.parse(
        """
    l l1
    m m1 R=R T=1-R
    link(l1, m1)
    pd P m1.p2.o
    """
    )
    from finesse.analysis.actions import Xaxis

    sol = model.run(Xaxis("R", "lin", 0, 1, 10))
    assert np.allclose(sol["P"], 1 - sol.x1)


def test_xaxis_reset():
    model = finesse.Model()
    model.parse("laser l1")
    model.add_parameter("A", 1)
    model.run("xaxis(A, lin, 10, 10, 1)")
    assert model.A.value == 1


def test_deepcopy():
    model = finesse.Model()
    model.add_parameter("X", 1)
    model.add_parameter("Y", model.X.ref)

    assert model.X == 1
    assert model.Y.value.parameter._model is model
    assert model.Y.value.parameter is model.X

    _model = model.deepcopy()

    assert _model.X == 1
    assert _model.Y.value.parameter._model is _model
    assert _model.Y.value.parameter is _model.X
    assert _model.Y.value.parameter is not model.X
