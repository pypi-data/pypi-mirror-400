from pathlib import Path

import pygraphviz

from finesse.components.general import Connector, NodeType, Port
from finesse.components.node import Node
from finesse.components import ReadoutDC


def make_component_graph(
    comp: Connector, path: str | Path, port_type: NodeType | None = None
):
    A = pygraphviz.AGraph(directed=True, strict=True, rankdir="LR", newrank=True)
    A.node_attr["style"] = "filled"
    A.node_attr["fillcolor"] = "lightcoral"

    comp_cluster = A.add_subgraph(
        name=f"cluster_{comp.name}", label=comp.__class__.__name__, bgcolor="lightblue"
    )
    for port in sorted(comp.ports, key=lambda c: c.name):
        port: Port
        if port_type is not None and port.type is not port_type:
            continue
        port_cluster = comp_cluster.add_subgraph(
            name=f"cluster_{port.name}",
            label=port.name,
            bgcolor="lightyellow",
            rank="same",
        )
        for node in port.nodes:
            node: Node
            port_cluster.add_node(node.full_name, label=node.name)

    for n1, n2 in comp._registered_connections.values():
        if A.has_node(n1) and A.has_node(n2):
            A.add_edge(n1, n2)

    A.draw(path, format="svg", prog="dot")


# for i in range(50):
# make_component_graph(Mirror("m1"), "mirror.svg")
make_component_graph(ReadoutDC("readout"), "readoutdc.svg")
