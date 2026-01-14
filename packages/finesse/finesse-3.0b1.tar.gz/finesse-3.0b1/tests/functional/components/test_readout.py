import pytest

from finesse import Model
from finesse.exceptions import FinesseException
from finesse.components import ReadoutDC, ReadoutRF, Mirror
from finesse.components.readout import _Readout
from finesse.components.node import Port, Node


# https://gitlab.com/ifosim/finesse/finesse3/-/issues/654
def test_double_connection_raises():
    m = Model()
    m1 = m.add(Mirror("m1"))
    readout = m.add(ReadoutDC(name="readout", optical_node=m1.p2.o))
    with pytest.raises(FinesseException):
        m.connect(m1.p2, readout.p1)


def test_implicit_connection_raises():
    m = Model()
    m1 = m.add(Mirror("m1"))
    readout = m.add(ReadoutDC(name="readout", optical_node=m1.p2.o))
    with pytest.raises(FinesseException):
        m.connect(m1.p1, readout.p1)


@pytest.fixture(
    params=(ReadoutDC, ReadoutRF),
)
def readout_cls(request) -> _Readout:
    return request.param


def test_optical_node(readout_cls):
    model = Model()
    m1 = Mirror("m1")
    model.add(m1)
    readout = readout_cls("readout", optical_node=m1.p2.o)
    assert readout.p1.i is m1.p2.o
    assert readout.p1.o is m1.p2.i


def test_optical_node_with_port(readout_cls):
    model = Model()
    m1 = Mirror("m1")
    model.add(m1)
    with pytest.warns():
        readout = readout_cls("readout", optical_node=m1.p2)
    # when passing in a port, should grab the first node, which is input
    assert readout.p1.i is m1.p2.i
    assert readout.p1.o is m1.p2.o


def test_optical_node_none(readout_cls):
    readout = readout_cls("readout")
    assert isinstance(readout.p1, Port)
    assert isinstance(readout.p1.i, Node)
    assert isinstance(readout.p1.o, Node)


def test_optical_wrong_type(readout_cls):
    model = Model()
    m1 = Mirror("m1")
    model.add(m1)
    with pytest.raises(TypeError):
        readout_cls("readout", optical_node=m1)
