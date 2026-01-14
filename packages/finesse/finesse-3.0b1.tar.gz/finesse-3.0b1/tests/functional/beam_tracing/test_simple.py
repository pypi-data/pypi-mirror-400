"""Simple beam tracing tests - i.e. single cavities, no beam splitters."""

from collections import OrderedDict
import pytest
import finesse
import numpy as np
import networkx as nx

import finesse.components
from finesse.cymath.gaussbeam import transform_q
from finesse.components import Cavity, Laser, Mirror
from finesse.exceptions import BeamTraceException
from finesse.gaussian import BeamParam
from finesse.tracing.tree import get_tracing_tree


def test_dont_trace_through():
    model = finesse.Model()
    laser1 = model.add(finesse.components.Laser("laser1"))
    mirror = model.add(finesse.components.Mirror("mirror"))
    laser2 = model.add(finesse.components.Laser("laser2"))
    mirror._trace_through = False
    model.link(laser1, mirror, laser2)
    graph_view = get_tracing_tree(model.optical_network)
    graph = nx.bfs_tree(graph_view, laser1.p1.o.full_name)

    assert (
        "mirror.p2.o" not in graph.nodes
    ), "Should be no connection to mirror.p2.o from laser1"
    assert (
        "mirror.p2.i" not in graph.nodes
    ), "Should be no connection to mirror.p1.i from laser1"

    graph = nx.bfs_tree(graph_view, laser2.p1.o.full_name)
    assert (
        "mirror.p1.o" not in graph.nodes
    ), "Should be no connection to mirror.p1.o from laser2"
    assert (
        "mirror.p1.i" not in graph.nodes
    ), "Should be no connection to mirror.p2.i from laser2"


def test_laser_to_mirror_trace(model):
    """Test beam tracing for a laser -> mirror configuration with a beam parameter set
    at the laser."""
    m_roc = 2.5
    L0_q = -0.5 + 1j
    model.chain(Laser("L0"), 1, Mirror("M", Rc=m_roc))

    # First check that we get an exception when no beam parameters are set anywhere.
    with pytest.raises(BeamTraceException):
        model.beam_trace()

    model.L0.p1.o.q = L0_q
    result = model.beam_trace().data_qx

    # TODO: write generic function to compute the target trace results for any given simple config.
    target = OrderedDict()
    target[model.L0.p1.o] = BeamParam(q=L0_q)
    target[model.L0.p1.i] = -target[model.L0.p1.o].conjugate()
    target[model.M.p1.i] = transform_q(
        model.L0.p1.o.space.ABCD(model.L0.p1.o, model.M.p1.i),
        target[model.L0.p1.o],
        1,
        1,
    )
    target[model.M.p1.o] = -target[model.M.p1.i].conjugate()
    target[model.M.p2.o] = transform_q(
        model.M.ABCD(model.M.p1.i, model.M.p2.o),
        target[model.M.p1.i],
        1,
        1,
    )
    target[model.M.p2.i] = -target[model.M.p2.o].conjugate()

    for node, q in target.items():
        assert q == result[node]


def test_fabry_perot_no_cav_trace(model):
    """Test beam tracing for a laser -> mirror -> space -> mirror configuration with a
    beam parameter set at the laser and no cavity object added."""
    m_roc = 2.5
    L0_q = -0.9 + 1.3j
    model.chain(Laser("L0"), 0.5, Mirror("ITM", Rc=-m_roc), 1, Mirror("ETM", Rc=m_roc))
    model.L0.p1.o.q = L0_q
    result = model.beam_trace().data_qx

    # TODO: write generic function to compute the target trace results for any given simple config.
    target = OrderedDict()
    # L0 p1
    target[model.L0.p1.o] = BeamParam(q=L0_q)
    target[model.L0.p1.i] = -target[model.L0.p1.o].conjugate()
    # ITM p1
    target[model.ITM.p1.i] = transform_q(
        model.L0.p1.o.space.ABCD(model.L0.p1.o, model.ITM.p1.i),
        target[model.L0.p1.o],
        1,
        1,
    )
    target[model.ITM.p1.o] = -target[model.ITM.p1.i].conjugate()
    # ITM p2
    target[model.ITM.p2.o] = transform_q(
        model.ITM.ABCD(model.ITM.p1.i, model.ITM.p2.o),
        target[model.ITM.p1.i],
        1,
        1,
    )
    target[model.ITM.p2.i] = -target[model.ITM.p2.o].conjugate()
    # ETM p1
    target[model.ETM.p1.i] = transform_q(
        model.ITM.p2.o.space.ABCD(model.ITM.p2.o, model.ETM.p1.i),
        target[model.ITM.p2.o],
        1,
        1,
    )
    target[model.ETM.p1.o] = -target[model.ETM.p1.i].conjugate()
    # ETM p2
    target[model.ETM.p2.o] = transform_q(
        model.ETM.ABCD(model.ETM.p1.i, model.ETM.p2.o),
        target[model.ETM.p1.i],
        1,
        1,
    )
    target[model.ETM.p2.i] = -target[model.ETM.p2.o].conjugate()

    for node, q in target.items():
        assert q == result[node]


def test_fabry_perot_cav_trace(model):
    """Test beam tracing for a laser -> mirror -> space -> mirror configuration with a
    cavity object added."""
    m_roc = 2.5
    model.chain(Laser("L0"), 0.5, Mirror("ITM", Rc=-m_roc), 1, Mirror("ETM", Rc=m_roc))
    model.add(Cavity("FPC", model.ITM.p2.o, model.ITM.p2.i))
    result = model.beam_trace().data_qx

    # TODO: write generic function to compute the target trace results for any given simple config.
    target = OrderedDict()
    # ITM p2
    target[model.ITM.p2.o] = model.FPC.qx
    target[model.ITM.p2.i] = -target[model.ITM.p2.o].conjugate()
    # ETM p1
    target[model.ETM.p1.i] = transform_q(
        model.ITM.p2.o.space.ABCD(model.ITM.p2.o, model.ETM.p1.i),
        target[model.ITM.p2.o],
        1,
        1,
    )
    target[model.ETM.p1.o] = -target[model.ETM.p1.i].conjugate()
    # ETM p2
    target[model.ETM.p2.o] = transform_q(
        model.ETM.ABCD(model.ETM.p1.i, model.ETM.p2.o),
        target[model.ETM.p1.i],
        1,
        1,
    )
    target[model.ETM.p2.i] = -target[model.ETM.p2.o].conjugate()
    # ITM p1
    target[model.ITM.p1.o] = transform_q(
        model.ITM.ABCD(model.ITM.p2.i, model.ITM.p1.o),
        target[model.ITM.p2.i],
        1,
        1,
    )
    target[model.ITM.p1.i] = -target[model.ITM.p1.o].conjugate()
    # L0 p1
    target[model.L0.p1.i] = transform_q(
        model.ITM.p1.o.space.ABCD(model.ITM.p1.o, model.L0.p1.i),
        target[model.ITM.p1.o],
        1,
        1,
    )
    target[model.L0.p1.o] = -target[model.L0.p1.i].conjugate()

    for node, q in target.items():
        assert q == result[node]


def test_fabry_perot_cav_and_manual_trace(model):
    """Test beam tracing for a laser -> mirror -> space -> mirror configuration with a
    cavity object added and a beam parameter set at the laser."""
    m_roc = 2.5
    L0_q = -1.1 + 1.6j
    model.chain(Laser("L0"), 0.5, Mirror("ITM", Rc=-m_roc), 1, Mirror("ETM", Rc=m_roc))
    model.L0.p1.o.q = L0_q
    model.add(Cavity("FPC", model.ITM.p2.o, model.ITM.p2.i))
    result = model.beam_trace().data_qx

    # TODO: write generic function to compute the target trace results for any given simple config.
    target = OrderedDict()
    # L0 p1
    target[model.L0.p1.o] = BeamParam(q=L0_q)
    target[model.L0.p1.i] = -target[model.L0.p1.o].conjugate()
    # ITM p2
    target[model.ITM.p2.o] = model.FPC.qx
    target[model.ITM.p2.i] = -target[model.ITM.p2.o].conjugate()
    # ETM p1
    target[model.ETM.p1.i] = transform_q(
        model.ITM.p2.o.space.ABCD(model.ITM.p2.o, model.ETM.p1.i),
        target[model.ITM.p2.o],
        1,
        1,
    )
    target[model.ETM.p1.o] = -target[model.ETM.p1.i].conjugate()
    # ETM p2
    target[model.ETM.p2.o] = transform_q(
        model.ETM.ABCD(model.ETM.p1.i, model.ETM.p2.o),
        target[model.ETM.p1.i],
        1,
        1,
    )
    target[model.ETM.p2.i] = -target[model.ETM.p2.o].conjugate()
    # ITM p1
    target[model.ITM.p1.i] = transform_q(
        model.L0.p1.o.space.ABCD(model.L0.p1.o, model.ITM.p1.i),
        target[model.L0.p1.o],
        1,
        1,
    )
    target[model.ITM.p1.o] = -target[model.ITM.p1.i].conjugate()

    for node, q in target.items():
        assert q == result[node]


def test_issue_505():
    script = """
    laser i1 P=20.0
    m m1 R=0.1 T=.9 Rc=10
    m m2 R=0.1 T=.9 Rc=-1
    link(i1, 1, m1, 1, m2)
    gauss g1 m1.p1.i w0=0.01 z=1300
    gauss g2 m2.p1.i w0=0.02 z=1300
    """

    ifo = finesse.Model()
    ifo.parse(script)
    ifo.modes(maxtem=0)
    ifo.run()


def test_change_gauss():
    model = finesse.script.parse(
        """
    l l1
    mirror n1 T=1 R=0
    link(l1, n1)
    gauss g1 l1.p1.o w0x=1 zx=0 w0y=1 zy=0
    gauss g2 n1.p2.o w0x=1 zx=0 w0y=1 zy=0
    pd P n1.p2.o
    modes(even, maxtem=2)
    """
    )

    model.run("change(g1.w0x=2)")

    assert model.l1.p1.o.qx.w0 == 2
    assert model.l1.p1.o.qy.w0 == 1
    assert model.l1.p1.o.qx.z == 0
    assert model.l1.p1.o.qy.z == 0

    sol = model.run()

    assert sol["P"] < 1


def test_optimize_gauss():
    model = finesse.script.parse(
        """
    l l1
    mirror n1 T=1 R=0
    link(l1, n1)
    gauss g1 l1.p1.o w0x=2 zx=0 w0y=2 zy=0
    gauss g2 n1.p2.o w0x=1 zx=0 w0y=1 zy=0
    pd P n1.p2.o
    modes(even, maxtem=2)
    """
    )
    model.run("maximize(P, [g1.w0x, g1.w0y])")
    sol = model.run()
    assert np.allclose(sol["P"], 1)
