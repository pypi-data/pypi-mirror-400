import importlib
import importlib.resources
import itertools
import os
import re
import shutil
import subprocess
from pathlib import Path

import networkx
import pygraphviz

from finesse.components.general import ModelElement

FINESSE_ROOT = Path(str(importlib.resources.files("finesse"))).parent.parent
SCRIPTS = FINESSE_ROOT / "scripts"
FINESSE_SRC = FINESSE_ROOT / "src" / "finesse"
SVG_FOLDER = SCRIPTS / "class_svgs"

os.chdir(SCRIPTS)


def get_git_commit() -> str:
    return subprocess.run(
        "git rev-parse HEAD",
        cwd=FINESSE_ROOT,
        check=True,
        text=True,
        shell=True,
        capture_output=True,
    ).stdout.strip()


def parse_classname(line: str) -> str | None:
    """
    Extract class name from the following statements:

    class Foo:
    class Foo(Bar):
    cdef class Foo:
    cdef class Foo(Bar):

    Parameters
    ----------
    line : str
        Line of source code

    Returns
    -------
    str | None
        Class name
    """
    match = re.search(
        r"""
                        ^              # only top-level class statements
                        (?:cdef\ )?    # optional non-capturing 'cdef' cython statement
                        class\ (\w+?)  # capture the class name
                        [:\(]          # until we reach : or (
                        """,
        line,
        re.VERBOSE,
    )
    return match if match is None else match.group(1)


def create_supergraph() -> networkx.DiGraph:
    """Creates a graph of all classes in the Finesse codebase, with directed edges
    pointing from child classes to parent classes.

    This is achieved by scanning the source code for class statements, importing the
    module that contains the class (may have side-effects!) and extracting the base
    classes from the __bases__ class attribute

    Returns
    -------
    networkx.DiGraph
        Directed graph containing all the classes defined in Finesse
    """
    supergraph = networkx.DiGraph()
    # skip .pxd files to not add duplicate classes
    src_files = itertools.chain(FINESSE_SRC.rglob("*.py"), FINESSE_SRC.rglob("*.pyx"))
    for src_file in src_files:
        # __init__ files can not be imported directly and hopefully no-one would put
        # important class definitions there
        if src_file.stem == "__init__":
            continue
        src = src_file.read_text()
        mod_name = "." + ".".join(
            src_file.relative_to(FINESSE_SRC).with_suffix("").parts
        )
        mod = importlib.import_module(name=mod_name, package="finesse")
        for i, line in enumerate(src.splitlines(keepends=True)):
            class_name = parse_classname(line)
            if class_name is None:
                continue
            f_class = getattr(mod, class_name)

            supergraph.add_node(
                f_class, line_no=i + 1, source_file=src_file.relative_to(FINESSE_SRC)
            )
            for base in f_class.__bases__:
                if base.__module__.startswith("finesse"):
                    supergraph.add_edge(f_class, base)
    return supergraph


def create_svg_folder() -> None:
    if SVG_FOLDER.exists():
        shutil.rmtree(SVG_FOLDER)
    SVG_FOLDER.mkdir()


def render_subgraphs(supergraph: networkx.DiGraph) -> None:
    """Splits up the supergraph of all classes in separate subgraphs, discards
    everything with size 1, and renders an svg with pygraphviz.

    Parameters
    ----------
    supergraph : networkx.DiGraph
        Graph containing all classes in Finesse
    """
    for _g in networkx.weakly_connected_components(supergraph):
        g = supergraph.subgraph(_g)
        line_numbers = networkx.get_node_attributes(g, "line_no")
        source_files = networkx.get_node_attributes(g, "source_file")
        if len(g) == 1:
            continue

        # find node that has no outgoing edges (hopefully uppermost base class)
        # to use as the file name
        base = None
        for node, out_deg in g.out_degree:
            if out_deg == 0:
                base = node

        assert base is not None
        # this hierarchy has multiple upper base classes
        if ModelElement in g.nodes:
            base = ModelElement
        A = pygraphviz.AGraph(directed=True)
        for node in g.nodes():
            if source_files[node].suffix == ".py":
                color = "lightyellow"
            else:
                color = "lightblue"
            A.add_node(
                node.__name__,
                tooltip=f"{node.__module__}.{node.__name__}",
                fillcolor=color,
                style="filled",
                URL=f"https://gitlab.com/ifosim/finesse/finesse3/-/blob/{get_git_commit()}/src/finesse/{source_files[node]}#L{line_numbers[node]}",
                target="_blank",
                shape="rect",
                margin="0",
            )

        for u, v in g.edges():
            A.add_edge(u=u.__name__, v=v.__name__)
        A.graph_attr["overlap"] = "prism"
        # large separation between nodes makes images too large
        A.graph_attr["sep"] = "+2"
        A.graph_attr["base"] = base.__name__
        A.draw(path=SVG_FOLDER / f"{base.__name__}.svg", format="svg", prog="twopi")


def main():
    supergraph = create_supergraph()
    create_svg_folder()
    render_subgraphs(supergraph)


if __name__ == "__main__":
    main()
