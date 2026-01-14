"""Graph plotting."""

from __future__ import annotations

import logging
import pathlib
import tempfile
import warnings
import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm
from matplotlib.colors import rgb2hex
from matplotlib.patches import ArrowStyle, BoxStyle

import finesse
from finesse.components.general import Connector
from finesse.components.node import Node, NodeType, Port
from finesse.env import has_pygraphviz

from ..utilities import class_to_url, graph_layouts, option_list
from ..utilities.graph import remove_orphans
from .tools import _in_ipython

if TYPE_CHECKING:
    import pygraphviz


plot_format = Literal["png", "svg"]

LOGGER = logging.getLogger(__name__)


def plot_graph(
    network,
    layout,
    graphviz=False,
    path=None,
    show=True,
    format: plot_format = "svg",
    **kwargs,
):
    if graphviz and not has_pygraphviz():
        raise ModuleNotFoundError(
            "The graphviz option requires pygraphviz and graphviz to be installed"
        )
    if format not in ("svg", "png"):
        raise ValueError(f"Format must be 'svg' or 'png', received {repr(format)}")
    if graphviz:
        return graphviz_draw(
            network=network,
            layout=layout,
            path=path,
            show=show,
            format=format,
            **kwargs,
        )
    else:
        return plot_nx_graph(
            network, layout, path=path, show=show, format=format, **kwargs
        )


def plot_nx_graph(
    network,
    layout,
    node_labels=True,
    node_attrs=False,
    edge_attrs=False,
    node_color_key=None,
    edge_color_key=None,
    label_font_size=12,
    attr_font_size=6,
    edge_font_size=6,
    bounding_ellipses=True,
    format: plot_format = "svg",
    path: pathlib.Path | None = None,
    show=True,
    **kwargs,
):
    """Plot graph with NetworkX.

    Parameters
    ----------
    network : :class:`networkx.Graph`
        The network to plot.

    layout : str
        The layout type to use. Any layout algorithm provided by
        :mod:`networkx.drawing.layout` is supported.

    node_labels : :class:`bool`, optional
        Show node names; defaults to True.

    node_attrs : :class:`bool` or :class:`list`, optional
        Show node data. This can be `True`, in which case all node data is shown, or a
        list, in which case only the specified keys are shown. Defaults to `True`.

    edge_attrs : :class:`bool` or :class:`list`, optional
        Show edge data. This can be `True`, in which case all edge data is shown, or a
        list, in which case only the specified keys are shown. Defaults to `True`.

    node_color_key : callable, optional
        Key function accepting a node and its attribute :class:`dict` and returning a
        group. Each group is assigned a unique color. If not specified, nodes are not
        colored.

    edge_color_key : callable, optional
        Key function accepting an edge (u, v) and its attribute :class:`dict` and
        returning a group. Each group is assigned a unique color. If not specified,
        edges are not colored.

    label_font_size, attr_font_size, edge_font_size : :class:`int`, optional
        Font size for node labels, attributes and edges. Defaults to 12, 6 and 6,
        respectively.

    bounding_ellipses: bool, optional
        Hijack the node label bounding boxes to draw the node labels inside of an
        ellipse (similar to graphviz neato layout). This guarantees the label is
        readable, but the arrow direction might not always be clear and might not
        combine well with `node_color_key`. Defaults to `True`.

    path : Path or None
        Save the resulting image to the given path. Defaults to None, which saves in
        a temporary file that is displayed if 'show' is set to True.

    show : bool, optional
        Whether to show the resulting image. In Jupyter environments, shows the plot
        inline, otherwise opens a webbrowser for svgs and PIL for pngs. Defaults to
        True.

    Other Parameters
    ----------------
    kwargs
        Anything else supported by :func:`networkx.drawing.nx_pylab.draw`.

    Raises
    ------
    ValueError
        If the specified layout is not supported.

    Exception
        If the graph cannot be represented with the specified layout.
    """
    from ..utilities import stringify

    if node_color_key is not None:
        if "node_color" in kwargs:
            raise ValueError(
                "cannot specify both 'node_color' and 'node_color_key' arguments"
            )
        if bounding_ellipses:
            warnings.warn(
                "'node_color_key' might not work as intended with 'bounding_ellipses'!",
                stacklevel=2,
            )
        # Assign node colors.
        cycler = iter(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        group_colors = defaultdict(lambda: next(cycler))
        kwargs["node_color"] = [
            group_colors[node_color_key(node, data)]
            for node, data in network.nodes(data=True)
        ]

    if edge_color_key is not None:
        if "edge_color" in kwargs:
            raise ValueError(
                "cannot specify both 'edge_color' and 'edge_color_key' arguments"
            )

        # Assign edge colors.
        cycler = iter(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        group_colors = defaultdict(lambda: next(cycler))
        kwargs["edge_color"] = [
            group_colors[edge_color_key((u, v), data)]
            for u, v, data in network.edges(data=True)
        ]

    layouts = graph_layouts()

    try:
        posfunc = layouts[layout.casefold()]
    except KeyError:
        choices = option_list(layouts)

        raise ValueError(
            f"Layout '{layout}' is not available in NetworkX (choose from {choices})."
        )

    try:
        pos = posfunc(network)
    except nx.NetworkXException as e:
        if "G is not planar" in str(e):
            raise Exception(
                "Graph cannot be represented with a planar layout. Try a different layout."
            ) from e

    bbox_kwargs = {}
    if bounding_ellipses:
        bbox_kwargs = {
            # We draw an ellipsoid bounding box over the node name, so the name is always
            # readable (like in pygraphviz) neato layout
            "bbox": {
                "facecolor": "white",
                "edgecolor": "black",
                "alpha": 1.0,
                "boxstyle": BoxStyle.Ellipse(pad=0.1),
            },
            # we need to make the arrow head longer, so it is not obscured by the bounding
            # box
            "arrowstyle": ArrowStyle("-|>", head_length=2.0, head_width=0.3),
        }

    nx.draw(
        network,
        pos,
        with_labels=node_labels,
        font_size=label_font_size,
        **bbox_kwargs,
        **kwargs,
    )

    if node_attrs:
        data = network.nodes(data=True)

        if node_attrs is not True:  # Needs to be like this!
            # Show only certain data.
            data = [
                (
                    node,
                    {
                        key: value
                        for key, value in node_data.items()
                        if key in node_attrs
                    },
                )
                for node, node_data in data
            ]

        node_labels = {
            node: "\n".join(
                [f"{key}={stringify(value)}" for key, value in node_attrs.items()]
            )
            for node, node_attrs in data
        }
        nx.draw_networkx_labels(
            network,
            pos,
            labels=node_labels,
            verticalalignment="top",
            font_size=attr_font_size,
        )

    if edge_attrs:
        data = network.edges(data=True)

        if edge_attrs is not True:  # Needs to be like this!
            # Show only certain data.
            data = (
                (
                    u,
                    v,
                    {
                        key: value
                        for key, value in edge_data.items()
                        if key in edge_attrs
                    },
                )
                for u, v, edge_data in data
            )

        edge_labels = {
            (u, v): "\n".join(
                [f"{key}={stringify(value)}" for key, value in edge_attrs.items()]
            )
            for u, v, edge_attrs in data
        }
        nx.draw_networkx_edge_labels(
            network,
            pos,
            edge_labels=edge_labels,
            font_size=edge_font_size,
        )
    if show:
        plt.show()
    if path:
        plt.savefig(pathlib.Path(path).with_suffix(f".{format}"))
    return plt.gcf()


def plot_graphviz(network, layout):
    """Plot graph with graphviz.

    The `pygraphviz` Python package must be installed and available on the current
    Python path, and `graphviz` must be available on the system path.

    Parameters
    ----------
    network : :class:`networkx.Graph`
        The network to plot.

    layout : str
        The layout type to use. Any layout algorithm provided by graphviz is supported.

    Raises
    ------
    ValueError
        If the specified layout is not supported.

    ImportError
        If graphviz or pygraphviz is not installed.
    """
    from networkx.drawing.nx_agraph import view_pygraphviz

    layouts = ("neato", "dot", "fdp", "sfdp", "circo")
    gvlayout = layout.casefold()

    if gvlayout not in layouts:
        choices = option_list(layouts)

        raise ValueError(
            f"Layout '{layout}' is not available in graphviz (choose from {choices})."
        )

    view_pygraphviz(network, prog=gvlayout)


def graphviz_draw(
    model=None,
    network=None,
    draw_labels=True,
    angle=0,
    overlap=True,
    ratio=0.45,
    edge_len=1.0,
    size=(13, 7),
    pad=(0.0, 0.0),
    format: plot_format = "svg",
    maxiter=500,
    layout="neato",
    mode="sgd",
    path=None,
    show=True,
):
    """This should get merged with plot_graphviz at some point.

    Draws a ``graphviz`` figure using ``neato`` layout.
    The default settings are tested to produce a passable drawing of the
    aLIGO DRMI graph.

    Parameters
    ----------
    angle : float or bool
        The angle parameter rotates the graph by ``angle`` degrees relative to the
        first edge in the graph, which most of the time is the edge coming out
        of the laser. Set ``angle=False`` to disable rotation and let graphviz
        decide how to rotate the graph.

    overlap : bool or str
        Setting for how graphviz deals with node overlaps. Set to False for
        graphviz to attempt to remove overlaps. Note that overlap removal runs as
        a post-processing step after initial layout and usually makes the graph look
        worse.

    ratio : float
        Post processing step to stretch the graph. Used for stretching horizontally
        to compoensate for wider nodes to fit node labels.

    path : Path or None
        Save the resulting image to the given path. Defaults to None, which saves in
        a temporary file that is displayed if 'show' is set to True.

    show : bool, optional
        Whether to show the resulting image. In Jupyter environments, shows the plot
        inline, otherwise opens a webbrowser for svgs and PIL for pngs. Defaults to
        True.

    Notes
    -----
    The svg format sometimes crops the image too hard, which results in clipped
    nodes or edges, if that happens increase the ``pad`` graph_attr or use the
    ``png`` format.
    """
    if network is None:
        network = model.optical_network

    G = remove_orphans(network, inplace=False)
    A = nx.drawing.nx_agraph.to_agraph(G)

    # remove unnecessary metadata from DOT file
    for node in A.nodes():
        for k in node.attr.keys():
            node.attr[k] = ""
    for edge in A.edges():
        for k in edge.attr.keys():
            edge.attr[k] = ""

    A.graph_attr["mode"] = mode
    A.graph_attr["maxiter"] = maxiter
    A.graph_attr["size"] = f"{size[0]},{size[1]}"
    A.graph_attr["pad"] = f"{pad[0]},{pad[1]}"
    A.graph_attr["margin"] = 1
    A.graph_attr["normalize"] = angle
    A.graph_attr["overlap"] = overlap
    A.edge_attr["len"] = edge_len

    if draw_labels:
        A.node_attr["shape"] = "oval"
        A.graph_attr["ratio"] = ratio
    else:
        A.node_attr["shape"] = "circle"
        A.node_attr["style"] = "filled"
        A.node_attr["label"] = " "

    show_graphviz(A, format=format, path=path, layout=layout, show=show)


def plot_dcfields_graph(
    model: finesse.Model,
    path: Path | str | None = None,
    show: bool = True,
    add_fields: bool = True,
    add_operators: bool = False,
) -> pathlib.Path:
    """Visualize the values of the DC fields in a model in a graph representation.
    Will run a :class:`finesse.analysis.actions.dc.DCFields` action under the hood.

    Parameters
    ----------
    model : finesse.Model
        Model to visualize
    path : Path | str | None, optional
        Save the resulting image to the given path. Defaults to None, which saves in
        a temporary file that is displayed if 'show' is set to True.
    show : bool, optional
        Whether to show the resulting image. In Jupyter environments, shows the plot
        inline, otherwise opens a webbrowser. Defaults to True.
    add_fields : bool, optional
        Whether to show the DC fields values in the nodes of the graph, by default True
    add_operators : bool, optional
        Whether to show the couplings between nodes as edge tooltips, by default False.
        Only supported for plane-wave single frequency models for now.

    Returns
    -------
    pathlib.Path
        Path where the svg was saved

    Raises
    ------
    ModuleNotFoundError
        If pygraphviz is not installed
    NotImplementedError
        When ``add_operators`` is True, but the model is not plane-wave single frequency
    """
    import pygraphviz

    # prevent circular import
    from finesse.analysis.actions.dc import DCFields, DCFieldsSolutions
    from finesse.analysis.actions.operator import Operator, OperatorSolution

    # don't modify the original model
    model = model.deepcopy()

    dc_sol: DCFieldsSolutions = model.run(DCFields())

    A = pygraphviz.AGraph(directed=True, strict=True, rankdir="LR", newrank=True)
    A.node_attr["style"] = "filled"
    A.node_attr["fillcolor"] = "lightyellow"

    kat = model.unparse()

    for n1, n2 in model.optical_network.edges:
        tooltip_suffix = ""
        if add_operators:
            if len(dc_sol.homs) == 1 and len(dc_sol.frequencies) == 1:
                # TODO this is very slow for large models, the operator action
                # should have an option to return all operators as a dictionary?
                op_sol = model.run(Operator(n1, n2))
                # just for the type hint
                assert isinstance(op_sol, OperatorSolution)
                tooltip_suffix = f": {op_sol.operator.squeeze():2.2f}"
            else:
                # TODO not sure how to visualize all the different coupling matrices
                raise NotImplementedError(
                    "add_operators only supported for plane-wave single-frequency models"
                )

        A.add_edge(
            u=n1,
            v=n2,
            label="",
            # will show the coupling on mouseover
            edgetooltip=f"{n1}->{n2}{tooltip_suffix}",
            penwidth=2,
        )

    # we sort the components in the order they appear in the katscript
    def comp_sorter(key: Connector) -> int:
        return kat.index(key.name)

    # create a graphviz cluster for every component and every port
    # port clusters go into the component cluster and nodes go into the port clusters
    for comp in sorted(model.components, key=comp_sorter):
        comp: Connector
        comp_cluster = A.add_subgraph(
            name=f"cluster_{comp.name}",
            label=comp.name,
            bgcolor="lightblue",
            fontsize=20,
            URL=class_to_url(type(comp)),
        )
        for port in sorted(comp.ports, key=lambda c: c.name):
            port: Port
            if port.type is not NodeType.OPTICAL:
                continue
            port_cluster = comp_cluster.add_subgraph(
                name=f"cluster_{port.name}",
                label=port.name,
                bgcolor="lightpink",
                rank="same",
            )
            for node in port.nodes:
                node: Node
                if node.type is NodeType.OPTICAL:
                    DC = dc_sol[node]

                    DC_formatted = create_graphviz_table(
                        DC, dc_sol.frequencies, dc_sol.homs
                    )
                    lines = DC_formatted.splitlines()
                    if len(lines) > 5:
                        label = "\n".join(lines[:5])
                        label += "\n..."
                        tooltip = DC_formatted
                    else:
                        label = DC_formatted
                        tooltip = node.full_name
                    node_label = node.name
                    if add_fields:
                        node_label = node.name + "\n" + label

                    port_cluster.add_node(
                        node.full_name,
                        label=node_label,
                        tooltip=tooltip,
                        shape="box",
                    )
    if len(dc_sol.frequencies) > 1:
        A.add_node(
            n="f_legend",
            shape="box",
            style="",
            label="FREQUENCY LEGEND\n"
            + "\n".join(f"f{i}: {f:3.1f}hz" for i, f in enumerate(dc_sol.frequencies)),
        )

    return show_graphviz(A=A, format="svg", path=path, layout="dot", show=show)


def create_graphviz_table(fields, frequencies, homs):
    table = ""
    for i, _ in enumerate(frequencies):
        for j, (n, m) in enumerate(homs):
            label = ""
            if len(frequencies) > 1:
                label += f"f{i}"
                if len(homs) > 1:
                    label += " "
            if len(homs) > 1:
                label += f"{n}{m}"
            if len(label) > 0:
                label += ": "
            value = f"{fields[:, i, j].squeeze():2.2f}"
            table += label + value + "\n"
    return table


def show_graphviz(
    A: pygraphviz.AGraph, format: str, path: str | Path | None, layout: str, show: bool
) -> pathlib.Path:
    suffix = f".{format}"
    if path is None:
        path = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        fullpath = path.name
    else:
        path = pathlib.Path(path).absolute().with_suffix(suffix)
        fullpath = path

    if _in_ipython():
        A.draw(path=fullpath, format=format, prog=layout)
        from IPython.display import SVG, Image, display

        with open(fullpath, "rb") as f:
            byt = f.read()

        if show:
            if format == "svg":
                display(SVG(byt))
            else:
                display(Image(byt))

    else:
        A.draw(path=path, format=format, prog=layout)
        LOGGER.debug(f"Network graph written to {path}")

        if show:
            if format == "svg":
                webbrowser.open(f"file://{fullpath}")
            else:
                from PIL import Image

                if isinstance(path, tempfile._TemporaryFileWrapper):
                    path.close()
                Image.open(path.name).show()
    return pathlib.Path(fullpath)


def graphviz_draw_beam_trace(
    model=None,
    network=None,
    draw_labels=True,
    angle=0,
    overlap=True,
    ratio=0.45,
    edge_len=1.0,
    size=(13, 7),
    pad=(0.5, 0.5),
    format: plot_format = "svg",
    maxiter=500,
    layout="neato",
    mode="sgd",
    cmap=cm.tab10,
):
    colors = {
        dep: rgb2hex(cmap.colors[i])
        for i, dep in enumerate(model.trace_forest.dependencies)
    }
    node_colors = {
        n.full_name: colors[model.trace_forest.find_dependency_from_node(n)]
        for n in model.optical_nodes
    }
    network = model.optical_network

    G = remove_orphans(network, inplace=False)
    A = nx.drawing.nx_agraph.to_agraph(G)

    # remove unnecessary metadata from DOT file
    for node in A.nodes():
        for k in node.attr.keys():
            node.attr[k] = ""
        node.attr["fillcolor"] = node_colors[node]
        node.attr["tooltip"] = model.get(node).q

    for edge in A.edges():
        for k in edge.attr.keys():
            edge.attr[k] = ""

    A.graph_attr["mode"] = mode
    A.graph_attr["maxiter"] = maxiter
    A.graph_attr["size"] = f"{size[0]},{size[1]}"
    A.graph_attr["pad"] = f"{pad[0]},{pad[1]}"
    A.graph_attr["normalize"] = angle
    A.graph_attr["overlap"] = overlap
    A.edge_attr["len"] = edge_len

    if draw_labels:
        A.node_attr["shape"] = "oval"
        A.node_attr["style"] = "filled"
        A.graph_attr["ratio"] = ratio
    else:
        A.node_attr["shape"] = "circle"
        A.node_attr["style"] = "filled"
        A.node_attr["label"] = " "

    for dep in model.trace_forest.dependencies:
        A.add_node(dep.name)
        A.add_edge(dep.name, dep.node.full_name)
        A.add_edge(dep.name, dep.node.opposite.full_name)
        node = A.get_node(dep.name)
        node.attr["fillcolor"] = colors[dep]
        node.attr["shape"] = "rectangle"

    byt = A.draw(format=format, prog=layout)

    from IPython.display import SVG, Image

    if format == "svg":
        out = SVG(byt)
    elif format in ["png"]:
        out = Image(byt)
    else:
        raise ValueError(f"unknown {format}")

    return out
