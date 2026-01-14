import pytest

from finesse import Model
from finesse.components import Laser, Beamsplitter, Mirror
from finesse.detectors import PowerDetector
from finesse.utilities.network_filter import (
    NetworkFilterBase,
    NetworkType,
    ComponentNetworkFilter,
    OpticalNetworkFilter,
    FullNetworkFilter,
)

from testutils.diff import assert_graphs_match


@pytest.fixture
def michelson():
    m = Model()
    m.link(Laser("l1"), Beamsplitter("bs1", R=0.5, T=0.5))
    m.link(m.bs1.p2, Mirror("ITMy", R=0.5, T=0.5), Mirror("ETMy", R=0.5, T=0.5))
    m.link(m.bs1.p3, Mirror("ITMx", R=0.5, T=0.5), Mirror("ETMx", R=0.5, T=0.5))
    m.add(PowerDetector("out", m.bs1.p4.o))
    return m


def test_network_type(michelson):
    assert_graphs_match(
        NetworkType.COMPONENT.get_network(michelson), michelson.to_component_network()
    )
    assert_graphs_match(
        NetworkType.OPTICAL.get_network(michelson), michelson.optical_network
    )
    assert_graphs_match(NetworkType.FULL.get_network(michelson), michelson.network)


@pytest.mark.parametrize(
    "network_type, expected",
    (
        (NetworkType.COMPONENT, ComponentNetworkFilter),
        (NetworkType.OPTICAL, OpticalNetworkFilter),
        (NetworkType.FULL, FullNetworkFilter),
    ),
)
def test_from_network_type(network_type, expected):
    assert network_type.filter_class is expected


def test_root_str(michelson):
    for root, expected in ((None, "l1"), ("l1", "l1"), (michelson.l1, "l1")):
        component_filter = ComponentNetworkFilter(michelson, root=root)
        assert component_filter.root_str == expected


@pytest.mark.parametrize(
    "filter_class, root",
    (
        (ComponentNetworkFilter, "l1.p1"),
        (OpticalNetworkFilter, "l1"),
        (FullNetworkFilter, "foo"),
    ),
)
def test_root_str_missing(michelson, filter_class, root):
    with pytest.raises(KeyError):
        filter_class(michelson, root=root)


def test_root_type_error(michelson):
    with pytest.raises(TypeError):
        ComponentNetworkFilter(michelson, root=michelson.l1.p1)
    with pytest.raises(TypeError):
        FullNetworkFilter(michelson, root=michelson.l1)


def test_negative_radius(michelson):
    with pytest.raises(ValueError):
        ComponentNetworkFilter(michelson, radius=-1).run()
    with pytest.raises(ValueError):
        ComponentNetworkFilter(michelson, radius=0).run()


@pytest.mark.parametrize(
    "filter_klass, root, radius, add_detectors, undirected, expected_nodes",
    (
        (ComponentNetworkFilter, "l1", 1, False, True, ("l1", "bs1")),
        (ComponentNetworkFilter, "l1", 2, False, True, ("l1", "bs1", "ITMy", "ITMx")),
        (
            ComponentNetworkFilter,
            "bs1",
            1,
            True,
            True,
            ("l1", "bs1", "ITMy", "ITMx", "out"),
        ),
        (OpticalNetworkFilter, "l1.p1.o", 1, False, True, ("l1.p1.o", "bs1.p1.i")),
        (OpticalNetworkFilter, "l1.p1.o", 1, False, False, ("l1.p1.o", "bs1.p1.i")),
        (
            OpticalNetworkFilter,
            "bs1.p2.o",
            1,
            False,
            False,
            ("bs1.p2.o", "ITMy.p1.i"),
        ),
        (
            OpticalNetworkFilter,
            "bs1.p2.o",
            1,
            False,
            True,
            ("bs1.p2.o", "ITMy.p1.i", "bs1.p1.i", "bs1.p4.i"),
        ),
    ),
)
def test_filter(
    michelson,
    filter_klass: type[NetworkFilterBase],
    root,
    radius,
    add_detectors,
    undirected,
    expected_nodes,
):
    result = filter_klass(
        michelson,
        root=root,
        radius=radius,
        add_detectors=add_detectors,
        undirected=undirected,
    ).run()
    assert set(expected_nodes) == set(result.nodes)
