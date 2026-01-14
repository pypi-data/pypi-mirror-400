"""A bunch of tests for serialisation of models.

Writing tests for every combination might be a bit overkill, so we'll just test a few
different complicated cases and probably copy issues in when we find them.
"""

import finesse
import finesse.components as fc
import finesse.detectors as fd
import numpy as np
import pytest
from pathlib import Path
from finesse.utilities.maps import circular_aperture


@pytest.fixture(params=[True, False])
def model(request):
    use_map = request.param

    model = finesse.Model()
    model.add_parameter("test", 2245)
    model.modes("even", maxtem=2)
    LASER = model.add(fc.Laser("LASER", P=1))
    PRM = model.add(fc.Mirror("PRM", T=0.031, L=0, Rc=-10.948))
    PR2 = model.add(fc.Beamsplitter("PR2", T=230.0e-6, L=0, Rc=-4.543, alpha=0))
    PR3 = model.add(fc.Beamsplitter("PR3", T=4.0e-6, L=0, Rc=36.021, alpha=0))
    LENS = model.add(fc.Lens("LENS", f=50e3))
    ITM = model.add(fc.Mirror("ITM", T=0.015, L=0, Rc=1940))
    ETM = model.add(fc.Mirror("ETM", T=0, L=75e-6, Rc=model.test.ref))
    model.add(fc.ReadoutDC("DC", optical_node=PRM.p2.o))

    model.link(
        LASER.p1,
        PRM.p2,
        PRM.p1,
        16608.6e-3,
        PR2.p1,
        PR2.p2,
        16093e-3,
        PR3.p1,
        PR3.p2,
        19537.4e-3 + 4829.6e-3 + 40.0e-3,
        LENS,
        ITM.p2,
        ITM.p1,
        3994.485,
        ETM.p1,
    )

    model.add(fc.Cavity("ARM", ITM.p1.o))
    model.add(fc.Cavity("PRC", ITM.p2.o, via=PRM.p1.o))

    model.add(fd.PowerDetector("P_in", PRM.p2.i))
    model.add(fd.PowerDetector("P_prc", ITM.p2.i))
    model.add(fd.PowerDetector("P_itm", ITM.p1.o))
    model.add(fd.FieldDetector("E_itm", ITM.p1.i, f=0))
    model.add(fd.PowerDetector("P_etm", ETM.p1.i))
    model.add(fd.BeamPropertyDetector("q_in", PRM.p2.i, "q"))
    model.add(fd.BeamPropertyDetector("q_prc", ITM.p2.i, "q"))
    model.add(fd.BeamPropertyDetector("q_itm", ITM.p1.o, "q"))
    model.add(fd.BeamPropertyDetector("q_etm", ETM.p1.o, "q"))

    if use_map:
        x = np.linspace(-0.16, 0.16, 100)
        y = np.linspace(-0.16, 0.16, 101)
        ITM.surface_map = finesse.knm.Map(x, y, amplitude=circular_aperture(x, y, 0.16))

    model.add(
        fd.FieldScanLine(
            "beam_itm",
            ITM.p1.o,
            100,
            xlim=[-0.16, 0.16],
            w0_scaled=False,
        )
    )
    model.add(
        fd.FieldScanLine(
            "beam_prc",
            ITM.p2.i,
            100,
            xlim=[-0.16, 0.16],
            w0_scaled=False,
        )
    )
    model.add(fd.MathDetector("Rc_ITM", ITM.Rcx.ref))
    model.add(fd.MathDetector("Rc_ETM", ETM.Rcx.ref))
    model.add(fd.MathDetector("f_ITM", LENS.f.ref))

    model.parse(
        """
    mathd PRG P_prc/P_in
    mathd ARG P_itm/P_prc
    # rescale to rough unitary values for optimisation as we know what the arm and
    # prc gains should be in the ideal case
    mathd cost ARG/260+PRG/50
    """
    )
    return model


@pytest.fixture
def test_save_load(model, tmpdir: Path):
    filepath: Path = tmpdir + "model.pkl"
    model.save(filepath)
    loaded = finesse.model.load(filepath)
    return model.deepcopy(), loaded.deepcopy()


def test_coupled_cavity_homs(test_save_load):
    model, loaded = test_save_load

    for a in model.all_parameters:
        b = loaded.get(a)
        assert a is not b
        if a.is_symbolic or b.is_symbolic:
            assert str(a.value) == str(b.value)
        else:
            assert a.value == b.value
        assert a.name == b.name
        assert a.__class__ == b.__class__

    for a, b in zip(loaded.elements.values(), model.elements.values()):
        assert a is not b
        assert a.name == b.name
        assert a.__class__ == b.__class__

    model.ITM.Rc = 1980
    loaded.ITM.Rc = 1980
    assert np.all(model.ITM.Rc == loaded.ITM.Rc)
    assert np.all(loaded.ARM.g == model.ARM.g)
    assert np.all(loaded.PRC.g == model.PRC.g)


def test_noxaxis(test_save_load):
    model, loaded = test_save_load

    A = model.run()
    B = loaded.run()

    for output in A.outputs:
        assert np.allclose(A[output], B[output], rtol=1e-10), output


@pytest.mark.parametrize(
    "action",
    [
        "xaxis(ITM.Rcx, lin, -10, 10, 2, True)",  # change geometry, makes sure ABCDs are all updating correctly
        "xaxis(test, lin, -10, 10, 2, True)",  # change model var
        "xaxis(LASER.P, lin, 0, 1, 2, True)",  # change element var
    ],
)
def test_xaxis(test_save_load, action):
    model, loaded = test_save_load
    A = model.run(action)
    B = loaded.run(action)

    for output in A.outputs:
        if A[output].dtype == object:
            assert np.allclose(
                A[output].astype(complex), B[output].astype(complex), rtol=1e-14
            ), output
        else:
            assert np.allclose(A[output], B[output], rtol=1e-14), output


def test_dcfields(test_save_load):
    model, loaded = test_save_load
    action = "dc_fields()"
    A = model.run(action)
    B = loaded.run(action)

    assert np.allclose(A.fields, B.fields, rtol=1e-14)


def test_frequency_response(test_save_load):
    model, loaded = test_save_load
    action = "frequency_response([1, 10, 100], ITM.mech.z, ETM.mech.F_z)"
    model.fsig.f = loaded.fsig.f = 1
    A = model.run(action)
    B = loaded.run(action)
    assert np.allclose(A.out, B.out, rtol=1e-14)
