"""Tree data structure."""

from functools import reduce
import networkx as nx

cdef class TreeNode:
    """Container for tree-like structures.

    Tree nodes can contain other tree nodes, allowing these objects to be built into a
    tree-like hierarchy useful for representing connections between components, nested
    data sets, etc.

    Parameters
    ----------
    name : str
        The node name.

    parent: :class:`.TreeNode`, optional
        The parent tree node, if not the root.

    empty : bool, optional
        Whether this node is considered "empty", which determines which character to use
        to represent the node in the tree; defaults to True.

    edge_info : str, optional
        String information on how this node is connected to its parent node. Will be used
        in :meth:`TreeNode.draw_tree`
    """
    def __init__(self, str name, TreeNode parent=None, bint empty=True, str edge_info=None):
        self.__name = name
        self.children = []
        self.empty = empty
        self.edge_info = edge_info
        if parent:
            parent.add(self)
        self.parent = parent

    @classmethod
    def from_network(cls, network, root):
        """Create a tree node hierarchy from an acyclic network.

        Notes
        -----
        Cyclic networks are handled by
        :func:`networkx.algorithms.traversal.depth_first_search.dfs_tree`, so this method does not
        need to detect and avoid such cycles.

        Parameters
        ----------
        network : :class:`networkx.Graph`
            The network that is to be represented as a tree.

        root : hashable
            The network node to use as the root of the tree.

        Raises
        ------
        ValueError
            When the specified network is not a forest.
        """
        # Use networkx to convert the network into tree form.
        tree = nx.dfs_tree(network, root)

        if not nx.is_forest(tree):
            raise ValueError("Network must be a forest (no undirected cycles).")

        def add_children(tree_node, node_name):
            for child in tree.successors(node_name):
                # Verbose component networks store edge information here
                edge_info = network.nodes[child].get(node_name, None)
                child_tree_node = cls(child, parent=tree_node, edge_info=edge_info)
                add_children(child_tree_node, child)

        head_node = cls(root)
        add_children(head_node, root)

        return head_node

    def add(self, child):
        if child is self:
            raise Exception("Can't add self as a node")

        if child in self.children:
            raise Exception(
                f"Child {repr(child)} has already been added to {repr(self)}"
            )
        self.children.append(child)
        child.parent = self

    def get_all_children(self):
        rtn = [*self.children]
        for child in self.children:
            rtn.extend(child.get_all_children())
        return rtn

    def get_all_parents(self):
        rtn = []
        curr = self

        while curr.parent is not None:
            rtn.append(curr.parent)
            curr = curr.parent

        return rtn

    @property
    def name(self):
        return self.__name

    def get_path(self):
        return reduce(
            lambda a, b: (b.name if b.name is not None else "") + "/" + a,
            self.get_all_parents(),
            self.name,
        )

    def get(self, ipath):
        els = ipath.strip("/").split("/")
        curr = self

        for i, el in enumerate(els):
            names = tuple(child.name for child in curr.children)
            try:
                idx = names.index(el)
            except ValueError:
                idx = -1

            if idx > -1:
                curr = curr.children[idx]
            else:
                path = "/".join(els[:(i+1)])
                raise Exception(f"Could not find '{path}'")

        return curr

    def ls(self, ipath="/"):
        me = self.get_path()
        if me is None:
            me = ""
        me = me.strip("/")

        if ipath == "/":
            print(list(c.get_path()[(len(me) + 1) :] for c in self.children))
        else:
            print(list(c.get_path()[(len(me) + 1) :] for c in self.get(ipath).children))

    def draw_tree(self, fn_name=None, title=None, show_max_children=None):
        """Draws the solution tree in text form.

        Based on https://stackoverflow.com/a/49638425/2251982.

        Parameters
        ----------
        fn_name : callable, optional
            Function to return the name of a :class:`.TreeNode` given the :class:`.TreeNode` itself.
            Defaults to using :attr:`.TreeNode.name`.

        title : str, optional
            The tree title. If not specified, no title is printed.

        show_max_children : int, optional
            Maximum number of children to show in the tree; defaults to showing all children.

        Returns
        -------
        str
            The tree in textual form.
        """
        branch = "├─"
        pipe = "│"
        end = "╰─"
        dash = "─"

        def format_name(t: TreeNode) -> str:
            if t.edge_info is None:
                return t.name
            else:
                return f"{t.name} ({t.edge_info})"

        fn_name = fn_name or format_name

        if show_max_children is not None:
            show_max_children = int(show_max_children)

            if show_max_children < 0:
                raise ValueError("show_max_children must be >= 0 or None")

        first = fn_name(self) if self.name is not None else None
        char_empty = lambda x: "○" if x.empty else "●"

        lines = [char_empty(self) + " " + (first or "/")]

        def fill_tree(this, lpad):
            maxed_out = False
            for i, child in enumerate(this.children):
                if (
                    show_max_children
                    and i >= show_max_children
                    and i < (len(this.children) - show_max_children)
                ):
                    if not maxed_out:
                        lines.append(lpad + "·")
                        lines.append(lpad + "·")
                        maxed_out = True
                    continue

                if i == len(this.children) - 1:
                    s = end + dash
                    pad = "   "
                else:
                    s = branch + dash
                    pad = pipe + "  "

                lines.append(str(lpad) + str(s) + str(char_empty(child)) + " " + str(fn_name(child)))
                fill_tree(child, str(lpad) + str(pad))

        fill_tree(self, "")

        treestr = ""
        if title is not None:
            treestr += f"- {title}\n"
        treestr += "\n".join(lines)

        return treestr

    def __str__(self):
        return self.draw_tree()
