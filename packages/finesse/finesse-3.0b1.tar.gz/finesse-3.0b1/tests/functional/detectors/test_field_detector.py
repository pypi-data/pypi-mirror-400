import finesse
import numpy as np


def test_field_detector_conjugate():
    model = finesse.script.parse(
        """
    l l1
    nothing n1
    link(l1.p1, 0, n1.p1)
    sgen sg l1.phs.i
    fsig(10000)
    fd E n1.p1.i 0
    fd U n1.p1.i +fsig
    fd L n1.p1.i -fsig
    gauss g1 l1.p1.o w0=1m z=0
    """
    )

    sol = model.run()
    assert np.allclose(sol["U"], sol["L"], atol=1e-14)


def test_field_detector():
    model = finesse.script.parse(
        """
    l l1
    mirror m1 T=0.09 R=1-m1.T
    link(l1.p1, 0, m1.p1)
    sgen sg l1.phs.i
    fsig(10000)

    fd Ea m1.p1.i 0
    fd ua m1.p1.i +fsig
    fd la m1.p1.i -fsig

    fd Eb m1.p2.o 0
    fd ub m1.p2.o +fsig
    fd lb m1.p2.o -fsig
    gauss g1 l1.p1.o w0=1m z=0
    """
    )

    sol = model.run()
    assert np.allclose(sol["ua"], 0.5j, atol=1e-9)
    assert np.allclose(sol["la"], 0.5j, atol=1e-9)
    assert np.allclose(sol["Ea"], 1, atol=1e-9)
    t = np.sqrt(model.m1.T)
    assert np.allclose(sol["ub"], 1j * 0.5j * t, atol=1e-9)
    assert np.allclose(sol["lb"], 1j * 0.5j * t, atol=1e-9)
    assert np.allclose(sol["Eb"], 1j * 1 * t, atol=1e-9)


def test_field_detector_homs():
    model = finesse.script.parse(
        """
    l l1
    mirror m1 T=0.09 R=1-m1.T
    link(l1.p1, 0, m1.p1)
    sgen sg l1.phs.i
    fsig(10000)

    fd Eb m1.p2.o 0
    fd ub m1.p2.o +fsig
    fd lb m1.p2.o -fsig
    gauss g1 l1.p1.o w0=1m z=0
    modes(maxtem=1)
    """
    )
    model.l1.tem(0, 0, 0, 0)
    model.l1.tem(1, 0, 1, 0)
    model.l1.tem(0, 1, 2, 0)
    sol = model.run()
    t = np.sqrt(model.m1.T)
    scale = np.zeros(model.homs.shape[0])
    scale[model.mode_index_map[(1, 0)]] = np.sqrt(1 / 3)
    scale[model.mode_index_map[(0, 1)]] = np.sqrt(2 / 3)

    assert np.allclose(sol["ub"], 1j * 0.5j * t * scale, atol=1e-9)
    assert np.allclose(sol["lb"], 1j * 0.5j * t * scale, atol=1e-9)
    assert np.allclose(sol["Eb"], 1j * 1 * t * scale, atol=1e-9)
