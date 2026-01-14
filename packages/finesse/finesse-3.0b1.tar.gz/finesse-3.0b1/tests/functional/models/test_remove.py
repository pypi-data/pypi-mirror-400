import pytest

from finesse.components import Mirror, ReadoutDC, ReadoutRF
from finesse import BeamParam


def test_remove_mirror(model):
    model.parse("mirror m1")
    assert "m1" in model.elements
    model.remove(model.m1)
    assert "m1" not in model.elements


def test_remove_space(model):
    model.parse("mirror m1")
    model.parse("mirror m2")
    model.parse("space s1 portA=m1.p2 portB=m2.p1")
    assert "s1" in model.elements
    model.remove(model.elements["s1"])
    assert "s1" not in model.elements


def test_string(model):
    model.parse("mirror m1")
    assert "m1" in model.elements
    model.remove("m1")
    assert "m1" not in model.elements


def test_error_on_unrecognised(model):
    with pytest.raises(TypeError, match=r".*not recongised.*"):
        model.remove(10)


def test_remove_readout(model):
    model.add(Mirror("M", T=0, L=0))
    model.add(ReadoutDC("ReadoutDC", model.M.p1.o))
    model.add(ReadoutRF("ReadoutRF", model.M.p1.o))
    model.M.p1.i.q = BeamParam(w0=1e-3, z=0)
    readouts = [f"ReadoutRF{suf}" for suf in ["", "_DC", "_I", "_Q"]]
    readouts += ["ReadoutDC", "ReadoutDC_DC"]
    for readout in readouts:
        assert readout in model.elements
    model.remove(model.ReadoutDC)
    model.remove(model.ReadoutRF)
    for readout in readouts:
        assert readout not in model.elements
    model.beam_trace()
