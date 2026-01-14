import pytest
from finesse.components import Mirror
from finesse.components.gauss import Gauss
from finesse.script import KATSPEC, unparse


@pytest.mark.parametrize(
    "beam_params,argument_defaults,prefer_keywords,expected",
    (
        # Non-astigmatic.
        ({"w0": 10e-3, "z": -1200}, False, False, "gauss g1 m1.p1.o w0=0.01 z=-1200.0"),
        (
            {"w0": 10e-3, "z": -1200},
            False,
            True,
            "gauss g1 node=m1.p1.o w0=0.01 z=-1200.0",
        ),
        (
            {"w0": 10e-3, "z": -1200},
            True,
            False,
            "gauss g1 m1.p1.o 0 w0=0.01 z=-1200.0",
        ),
        (
            {"w0": 10e-3, "z": -1200},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 w0=0.01 z=-1200.0",
        ),
        ({"z": 100, "zr": 10000}, False, False, "gauss g1 m1.p1.o z=100.0 zr=10000.0"),
        (
            {"z": 100, "zr": 10000},
            False,
            True,
            "gauss g1 node=m1.p1.o z=100.0 zr=10000.0",
        ),
        ({"z": 100, "zr": 10000}, True, False, "gauss g1 m1.p1.o 0 z=100.0 zr=10000.0"),
        (
            {"z": 100, "zr": 10000},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 z=100.0 zr=10000.0",
        ),
        (
            {"w": 1e-3, "Rc": -1},
            False,
            False,
            "gauss g1 m1.p1.o w=0.001 Rc=-1.0",
        ),
        (
            {"w": 1e-3, "Rc": -1},
            False,
            True,
            "gauss g1 node=m1.p1.o w=0.001 Rc=-1.0",
        ),
        (
            {"w": 1e-3, "Rc": -1},
            True,
            False,
            "gauss g1 m1.p1.o 0 w=0.001 Rc=-1.0",
        ),
        (
            {"w": 1e-3, "Rc": -1},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 w=0.001 Rc=-1.0",
        ),
        (
            {"w": 1e-3, "Rc": float("inf")},
            False,
            False,
            "gauss g1 m1.p1.o w=0.001 Rc=inf",
        ),
        (
            {"w": 1e-3, "Rc": float("inf")},
            False,
            True,
            "gauss g1 node=m1.p1.o w=0.001 Rc=inf",
        ),
        (
            {"w": 1e-3, "Rc": float("inf")},
            True,
            False,
            "gauss g1 m1.p1.o 0 w=0.001 Rc=inf",
        ),
        (
            {"w": 1e-3, "Rc": float("inf")},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 w=0.001 Rc=inf",
        ),
        # Astigmatic.
        (
            {"w0x": 10e-3, "w0y": 11e-3, "zx": -1200, "zy": -1250},
            False,
            False,
            "gauss g1 m1.p1.o w0x=0.01 w0y=0.011 zx=-1200.0 zy=-1250.0",
        ),
        (
            {"w0x": 10e-3, "w0y": 11e-3, "zx": -1200, "zy": -1250},
            False,
            True,
            "gauss g1 node=m1.p1.o w0x=0.01 w0y=0.011 zx=-1200.0 zy=-1250.0",
        ),
        (
            {"w0x": 10e-3, "w0y": 11e-3, "zx": -1200, "zy": -1250},
            True,
            False,
            "gauss g1 m1.p1.o 0 w0x=0.01 w0y=0.011 zx=-1200.0 zy=-1250.0",
        ),
        (
            {"w0x": 10e-3, "w0y": 11e-3, "zx": -1200, "zy": -1250},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 w0x=0.01 w0y=0.011 zx=-1200.0 zy=-1250.0",
        ),
        (
            {"zx": 100, "zy": 110, "zrx": 10000, "zry": 10100},
            False,
            False,
            "gauss g1 m1.p1.o zx=100.0 zy=110.0 zrx=10000.0 zry=10100.0",
        ),
        (
            {"zx": 100, "zy": 110, "zrx": 10000, "zry": 10100},
            False,
            True,
            "gauss g1 node=m1.p1.o zx=100.0 zy=110.0 zrx=10000.0 zry=10100.0",
        ),
        (
            {"zx": 100, "zy": 110, "zrx": 10000, "zry": 10100},
            True,
            False,
            "gauss g1 m1.p1.o 0 zx=100.0 zy=110.0 zrx=10000.0 zry=10100.0",
        ),
        (
            {"zx": 100, "zy": 110, "zrx": 10000, "zry": 10100},
            True,
            True,
            "gauss g1 node=m1.p1.o priority=0 zx=100.0 zy=110.0 zrx=10000.0 zry=10100.0",
        ),
    ),
)
@pytest.mark.xfail(
    reason="See issue https://gitlab.com/ifosim/finesse/finesse3/-/issues/494"
)
def test_gauss(model, beam_params, argument_defaults, prefer_keywords, expected):
    adapter = KATSPEC.elements["gauss"]
    model.add(Mirror("m1"))
    model.add(Gauss("g1", model.m1.p1.o, **beam_params))
    dump = next(iter(adapter.getter(adapter, model)))
    script = unparse(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
