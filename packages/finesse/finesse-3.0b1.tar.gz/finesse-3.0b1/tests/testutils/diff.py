""""Finesse object comparison utilities for tests.

There is a lot going on in this module. We cannot compare some Finesse objects by
implementing `__eq__` methods directly (doing so would interfere with how they behave in
lists, dicts, etc.), so special checks are instead implemented here. Furthermore, in
order to provide useful error messages for tests, special set operations are provided
that use the special equivalence functions here instead of hashing.
"""

from io import BytesIO

import networkx as nx
import numpy as np
from numpy.testing import assert_array_equal

from finesse.components import Cavity, Gauss
from finesse.detectors.general import Detector


def assert_models_equivalent(model_a, model_b):
    """Check :class:`.Model` equality.

    This checks that the two specified models are identical in a shallow way, i.e. they
    have elements with the same properties, equivalent networks, actions, etc.

    This is implemented here and not as `Model.__eq__` because :class:`.Model` must be
    hashable.
    """
    if model_a.analysis is not None and model_b.analysis is not None:
        assert_actions_equivalent(model_a.analysis, model_b.analysis)
    elif (model_a.analysis is None) != (model_b.analysis is None):
        raise AssertionError("analyses don't match")

    assert set(model_a.elements) == set(model_b.elements)
    assert_array_equal(model_a.homs, model_b.homs, "HOMs don't match")

    for el_a, el_b in zip(sorted(model_a.elements), sorted(model_b.elements)):
        assert_model_elements_equivalent(model_a.elements[el_a], model_b.elements[el_b])


def assert_model_elements_equivalent(element_a, element_b):
    """Check :class:`.ModelElement` equality.

    This is implemented here and not as `ModelElement.__eq__` because `ModelElement`
    must be hashable.
    """

    assert type(element_a) == type(element_b)  # noqa: E721
    assert element_a.name == element_b.name
    for param_a, param_b in zip(element_a.parameters, element_b.parameters):
        assert_parameters_equivalent(param_a, param_b)


def assert_nodes_equivalent(node_a, node_b):
    """Check node equality.

    This is implemented here and not as `Node.__eq__` because `Node` must be hashable.
    """
    assert node_a.name == node_b.name, f"{node_a!r} name != {node_b!r} name"
    assert_model_elements_equivalent(node_a.component, node_b.component)


def assert_parameters_equivalent(param_a, param_b, expected=None):
    """Check model parameter equality.

    This is implemented here and not as `ModelParameter.__eq__` because `ModelParameter`
    must be hashable.
    """
    assert type(param_a) == type(param_b)  # noqa:E721

    val_a = param_a.eval()
    val_b = param_b.eval()

    assert val_a == val_b

    if expected is not None:
        assert val_a == expected
        assert val_b == expected


# FIXME: make this check far more than just the name of the top action...
def assert_actions_equivalent(act_a, act_b):
    """Check action equality."""
    # TODO: compare more things.
    assert str(act_a.plan()) == str(act_b.plan())


def assert_cavities_equivalent(cav_a, cav_b):
    """Check cavity equality."""
    if not isinstance(cav_b, cav_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(cav_a, cav_b)
    assert isinstance(cav_a, Cavity), f"{cav_a!r} is not a Cavity"
    assert isinstance(cav_b, Cavity), f"{cav_b!r} is not a Cavity"
    assert (
        cav_a.round_trip_optical_length == cav_b.round_trip_optical_length
    ), f"{cav_a!r} round trip length != {cav_b!r} round trip length"
    assert np.all(
        cav_a.gouy == cav_b.gouy
    ), f"{cav_a!r} round trip gouy != {cav_b!r} round trip gouy"
    assert cav_a.FSR == cav_b.FSR, f"{cav_a!r} FSR != {cav_b!r} FSR"
    assert cav_a.loss == cav_b.loss, f"{cav_a!r} loss != {cav_b!r} loss"
    assert cav_a.finesse == cav_b.finesse, f"{cav_a!r} finesse != {cav_b!r} finesse"
    assert cav_a.FWHM == cav_b.FWHM, f"{cav_a!r} FWHM != {cav_b!r} FWHM"
    assert cav_a.pole == cav_b.pole, f"{cav_a!r} pole != {cav_b!r} pole"
    assert np.all(
        cav_a.mode_separation == cav_b.mode_separation
    ), f"{cav_a!r} mode separation != {cav_b!r} mode separation"
    assert np.all(cav_a.S == cav_b.S), f"{cav_a!r} resolution != {cav_b!r} resolution"
    assert np.all(cav_a.ABCDx == cav_b.ABCDx), f"{cav_a!r} ABCDx != {cav_b!r} ABCDx"
    assert np.all(cav_a.ABCDy == cav_b.ABCDy), f"{cav_a!r} ABCDy != {cav_b!r} ABCDy"
    assert np.all(cav_a.q == cav_b.q), f"{cav_a!r} q != {cav_b!r} q"
    assert np.all(cav_a.g == cav_b.g), f"{cav_a!r} g != {cav_b!r} g"


def assert_gauss_commands_equivalent(gauss_a, gauss_b):
    """Check gauss command equality.

    This is implemented here and not as `Gauss.__eq__` because `Gauss` must be hashable.
    """
    if not isinstance(gauss_b, gauss_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(gauss_a, gauss_b)
    assert isinstance(gauss_a, Gauss), f"{gauss_a!r} is not a Gauss"
    assert isinstance(gauss_b, Gauss), f"{gauss_b!r} is not a Gauss"
    # TODO: add more gauss command comparisons.


def assert_detectors_equivalent(det_a, det_b):
    """Check detector equality.

    This is implemented here and not as `Detector.__eq__` because `Detector` must be
    hashable.
    """
    if not isinstance(det_b, det_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(det_a, det_b)
    assert isinstance(det_a, Detector), f"{det_a!r} is not a Detector"
    assert isinstance(det_b, Detector), f"{det_b!r} is not a Detector"
    # TODO: add more detector comparisons.


def assert_trace_trees_equal(t1, t2):
    """Check TraceTree equality."""
    # Both t1 and t2 must be None or not None.
    if t1 is None and t2 is None:
        # Nothing to test.
        return
    elif (t1 is None and t2 is not None) or (t1 is not None and t2 is None):
        raise AssertionError

    assert t1.node == t2.node, f"{t1} node {t1.node} != {t2} node {t2.node}"
    assert (
        t1.dependency == t2.dependency
    ), f"{t1} dependency {t1.dependency} != {t2} dependency {t2.dependency}"

    assert_trace_trees_equal(t1.left, t2.left)
    assert_trace_trees_equal(t1.right, t2.right)


def assert_graph_matches_def(graph, ref_definition):
    """Assert specified graph has GML representation equivalent to specified
    definition."""
    ref_graph = nx.read_gml(BytesIO(ref_definition.encode()))
    assert_graphs_match(graph, ref_graph)


def assert_graphs_match(graph, ref_graph):
    """Assert graphs match."""

    def stringify(item):
        """Convert graph item to string form."""
        if isinstance(item, list):
            return f"[{', '.join(stringify(i) for i in item)}]"
        return str(item)

    nodes = sorted([node for node in graph.nodes], key=lambda node: str(node))
    ref_nodes = sorted([node for node in ref_graph.nodes], key=lambda node: str(node))

    # Node names.
    assert [stringify(node) for node in nodes] == [
        stringify(node) for node in ref_nodes
    ], "Node names in graph don't match those in reference graph"

    # Node attributes.
    for node, ref_node in zip(nodes, ref_nodes):
        data = {
            stringify(key): stringify(value) for key, value in graph.nodes[node].items()
        }
        ref_data = {
            stringify(key): stringify(value)
            for key, value in ref_graph.nodes[ref_node].items()
        }
        assert (
            data == ref_data
        ), f"{node!r} attributes in graph don't match those in reference graph"

    edges = sorted(
        [edge for edge in graph.edges],
        key=lambda edge: (stringify(edge[0]), stringify(edge[1])),
    )
    ref_edges = sorted(
        [edge for edge in ref_graph.edges],
        key=lambda edge: (stringify(edge[0]), stringify(edge[1])),
    )

    # Edges.
    assert list(edges) == list(ref_edges)

    # Edge attributes.
    for edge, ref_edge in zip(edges, ref_edges):
        data = {
            stringify(key): stringify(value) for key, value in graph.edges[edge].items()
        }
        ref_data = {
            stringify(key): stringify(value)
            for key, value in ref_graph.edges[ref_edge].items()
        }
        assert (
            data == ref_data
        ), f"{edge!r} attributes in graph don't match those in reference graph"
