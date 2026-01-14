"""Test cases for model component tree generation."""

import pytest


def test_component_tree_contains_network_nodes(network_model_michelson):
    """Test that all branches of the tree contain network nodes, regardless of starting
    node."""
    model, network = network_model_michelson

    for start in (model.L0, model.BS, model.IMX, model.IMY, model.EMX, model.EMY):
        tree = model.component_tree(start)
        assert tree.parent is None
        assert tree.name == start.name
        assert set([child.name for child in tree.get_all_children()]).issubset(
            set(network.nodes)
        )


@pytest.mark.parametrize(
    "root, radius, expected",
    (
        ("L0", 1, {"BS"}),
        ("L0", 2, {"BS", "IMX", "IMY"}),
        ("L0", 3, {"BS", "IMX", "IMY", "EMX", "EMY"}),
        ("BS", 1, {"L0", "IMX", "IMY"}),
    ),
)
def test_component_tree_radius(network_model_michelson, root, radius, expected):
    """Test that all branches of the tree contain network nodes, regardless of starting
    node."""
    model, network = network_model_michelson

    tree = model.component_tree(root=root, radius=radius)
    assert set([child.name for child in tree.get_all_children()]) == expected


def test_component_tree_flattens_cyclic_network(network_model_sagnac):
    """Test that component tree contains a flattened, acyclic version of a cyclic
    component network.

    Note: cyclic networks are handled by :meth:`networkx.dfs_tree`, so
    :meth:`.TreeNode.from_network` does not need to detect and avoid such cycles.
    """
    model, _ = network_model_sagnac

    for start in (model.L0, model.BS, model.M1, model.M2, model.M3):
        tree = model.component_tree(root=start)
        assert len(tree.get_all_children()) + 1 == len(model.components)


def test_component_tree_show_detectors(network_model_michelson):
    model, _ = network_model_michelson
    tree = model.component_tree(show_detectors=True)
    children = tree.get_all_children()
    names = [node.name for node in children]
    refl = children[names.index("refl")]
    assert refl.parent.name == "IMX"


@pytest.mark.parametrize(
    "show_detectors, show_ports, ref",
    (
        (
            False,
            False,
            # fmt:off
            (
                "○ L0\n"
                "╰──○ BS\n"
                "   ├──○ IMY\n"
                "   │  ╰──○ EMY\n"
                "   ╰──○ IMX\n"
                "      ╰──○ EMX"
            )
            # fmt:on
        ),
        (
            True,
            False,
            # fmt:off
            (
                "○ L0\n"
                "╰──○ BS\n"
                "   ├──○ IMY\n"
                "   │  ╰──○ EMY\n"
                "   ╰──○ IMX\n"
                "      ├──○ EMX\n"
                "      ╰──○ refl"
            )
            # fmt:on
        ),
        (
            False,
            True,
            # fmt:off
            (
                "○ L0\n"
                "╰──○ BS (L0.p1 ↔ BS.p1)\n"
                "   ├──○ IMY (BS.p2 ↔ IMY.p1)\n"
                "   │  ╰──○ EMY (IMY.p2 ↔ EMY.p1)\n"
                "   ╰──○ IMX (BS.p3 ↔ IMX.p1)\n"
                "      ╰──○ EMX (IMX.p2 ↔ EMX.p1)"
            )
            # fmt:on
        ),
        (
            True,
            True,
            # fmt:off
            (
                "○ L0\n"
                "╰──○ BS (L0.p1 ↔ BS.p1)\n"
                "   ├──○ IMY (BS.p2 ↔ IMY.p1)\n"
                "   │  ╰──○ EMY (IMY.p2 ↔ EMY.p1)\n"
                "   ╰──○ IMX (BS.p3 ↔ IMX.p1)\n"
                "      ├──○ EMX (IMX.p2 ↔ EMX.p1)\n"
                "      ╰──○ refl (IMX.p1.o)"
            )
            # fmt:on
        ),
    ),
)
def test_component_tree_draw(network_model_michelson, show_detectors, show_ports, ref):
    # can not use pregenerated component tree because we want to parameterize the args
    model, _ = network_model_michelson
    assert (
        model.component_tree(
            show_detectors=show_detectors, show_ports=show_ports
        ).draw_tree()
        == ref
    )
