#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""The TraceTree data structure and associated algorithms.

Details on each class, method and function in this sub-module are provided mostly for
developers. Users should refer to :ref:`tracing_manual` for details on beam tracing,
:meth:`.Model.beam_trace` for the main method through which beam traces can be performed
on a model and :mod:`.tracing.tools` for the various beam propagation tools which the
beam tracing library provides.
"""

import networkx

from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj
from finesse.cymath.gaussbeam cimport (
    transform_q,
    inv_transform_q,
    c_abcd_multiply,
    is_abcd_changing,
)
from finesse.gaussian import BeamParam
from finesse.exceptions import TotalReflectionError
from finesse.utilities import refractive_index


def get_tracing_tree(optical_network: networkx.DiGraph) -> networkx.DiGraph:
    """Creates a view of an optical network that removes edges that should
    not be ABCD traced. These are determined by checking the objects
    Connector._trace_through flag.
    """
    def criteria(edge_data: dict):
        if len(edge_data) == 0:
            return False
        owner = edge_data["owner"]()
        return not owner._trace_through

    # Here we search through and find any elements that we should not trace through
    edges_to_remove = [
        edge
        for edge in optical_network.edges
        if criteria(optical_network.get_edge_data(*edge))
    ]

    # Create subgraph view without those edges
    def edge_filter(u, v):
        return (u, v) not in edges_to_remove and (v, u) not in edges_to_remove

    return networkx.subgraph_view(optical_network, filter_edge=edge_filter)


cdef class TraceTree:
    """A binary tree data structure representing all the beam tracing
    paths from some root optical node of a model.

    Each instance of this class has a `left` and `right` sub-tree (of the
    class type) and a parent tree. These linked tree attributes can be None. If
    the tree has a left / right sub-tree then the memoryviews `left_abcd_x`,
    `left_abcd_y` etc. will be initialised from the numerical ABCD matrix from
    the tree's optical node to the next tree's optical node.

    Every sub-tree has a `dependency` attribute which is the object that the
    trace tree depends on - either a :class:`.Cavity` or a :class:`.Gauss`
    instance."""
    def __init__(self, object node, object dependency):
        from finesse.components import Cavity, Gauss

        self.parent = None
        self.left = None
        self.right = None

        self.dependency = dependency # the source object (a cavity or gauss)
        if self.dependency is None:
            self.dep_type = DependencyType.NONE
        elif isinstance(self.dependency, Cavity):
            self.dep_type = DependencyType.CAVITY
        elif isinstance(self.dependency, Gauss):
            self.dep_type = DependencyType.GAUSS
        else:
            raise TypeError("Unrecognised trace dependency type.")

        self.node = node # the optical node

        self.is_source = False

        # These will get set in TraceTree.initialise afterwards anyway
        self.is_x_changing = False
        self.is_y_changing = False

        self.left_abcd_x = None
        self.left_abcd_y = None
        self.right_abcd_x = None
        self.right_abcd_y = None

        self.is_left_surf_refl = False

        self.sym_left_abcd_x = None
        self.sym_left_abcd_y = None
        self.sym_right_abcd_x = None
        self.sym_right_abcd_y = None

        self.nr = refractive_index(self.node)

        self.node_id = 0
        self.opp_node_id = 0

        self.do_inv_transform = False
        self.do_nonsymm_reverse = False

    def __deepcopy__(self, memo):
        raise RuntimeError("TraceTree instances cannot be copied.")

    def __getstate__(self):
        state = {}
        state["parent"] = self.parent
        state["left"] = self.left
        state["right"] = self.right
        state["node"] = self.node
        state["dependency"] = self.dependency
        state["is_source"] = self.is_source
        state["is_x_changing"] = self.is_x_changing
        state["is_y_changing"] = self.is_y_changing
        state["is_left_surf_refl"] = self.is_left_surf_refl
        state["nr"] = self.nr
        state["dep_type"] = self.dep_type
        state["node_id"] = self.node_id
        state["opp_node_id"] = self.opp_node_id
        state["do_inv_transform"] = self.do_inv_transform
        state["do_nonsymm_reverse"] = self.do_nonsymm_reverse
        # We don't store the memoryviews, just where to get them from
        state["left_abcd_x_target"] = self.left_abcd_x_target
        state["left_abcd_x_args"] = self.left_abcd_x_args
        state["left_abcd_x_kwargs"] = self.left_abcd_x_kwargs
        state["left_abcd_y_target"] = self.left_abcd_y_target
        state["left_abcd_y_args"] = self.left_abcd_y_args
        state["left_abcd_y_kwargs"] = self.left_abcd_y_kwargs
        state["right_abcd_x_target"] = self.right_abcd_x_target
        state["right_abcd_x_args"] = self.right_abcd_x_args
        state["right_abcd_x_kwargs"] = self.right_abcd_x_kwargs
        state["right_abcd_y_target"] = self.right_abcd_y_target
        state["right_abcd_y_args"] = self.right_abcd_y_args
        state["right_abcd_y_kwargs"] = self.right_abcd_y_kwargs

        return state

    def __setstate__(self, state):
        self.parent = state["parent"]
        self.left = state["left"]
        self.right = state["right"]
        self.node = state["node"]
        self.dependency = state["dependency"]
        self.is_source = state["is_source"]
        self.is_x_changing = state["is_x_changing"]
        self.is_y_changing = state["is_y_changing"]
        self.is_left_surf_refl = state["is_left_surf_refl"]
        self.nr = state["nr"]
        self.dep_type = state["dep_type"]
        self.node_id = state["node_id"]
        self.opp_node_id = state["opp_node_id"]
        self.do_inv_transform = state["do_inv_transform"]
        self.do_nonsymm_reverse = state["do_nonsymm_reverse"]

        # We need to get the memory-views back from any new components so
        # here we call the set functions again to do that. The Pickling
        # should unpickle the dependency object first so that the memory
        # can be referenced
        if state["left_abcd_x_target"] is not None:
            self.set_left_abcd_x_memory(
                state["left_abcd_x_target"],
                *state["left_abcd_x_args"],
                **state["left_abcd_x_kwargs"]
            )
        if state["left_abcd_y_target"] is not None:
            self.set_left_abcd_y_memory(
                state["left_abcd_y_target"],
                *state["left_abcd_y_args"],
                **state["left_abcd_y_kwargs"]
            )
        if state["right_abcd_x_target"] is not None:
            self.set_right_abcd_x_memory(
                state["right_abcd_x_target"],
                *state["right_abcd_x_args"],
                **state["right_abcd_x_kwargs"]
            )
        if state["right_abcd_y_target"] is not None:
            self.set_right_abcd_y_memory(
                state["right_abcd_y_target"],
                *state["right_abcd_y_args"],
                **state["right_abcd_y_kwargs"]
            )

    @staticmethod
    cdef TraceTree initialise(
        object node, object dependency, bint* is_dependency_changing=NULL
    ) :
        cdef TraceTree tree = TraceTree(node, dependency)

        cdef bint is_dep_changing
        if is_dependency_changing == NULL:
            if dependency is None:
                is_dep_changing = False
            else:
                is_dep_changing = dependency.is_changing
        else:
            is_dep_changing = is_dependency_changing[0]

        tree.is_x_changing = is_dep_changing
        tree.is_y_changing = is_dep_changing

        return tree

    @classmethod
    def from_cavity(cls, cavity):
        """Construct a TraceTree from a cavity instance.

        The resulting tree decays to a linked list as it
        just includes the internal path of the cavity.

        Parameters
        ----------
        cavity : :class:`.Cavity`
            The cavity object.

        Returns
        -------
        tree : :class:`.TraceTree`
            The tree representing the internal cavity path.
        """
        cdef:
            list path = cavity.path.nodes
            Py_ssize_t num_nodes = len(path)
            TraceTree parent = None
            TraceTree root

            object node

            bint cav_is_changing = cavity.is_changing

        root = TraceTree.initialise(path[0], cavity, &cav_is_changing)
        root.is_source = True
        parent = root

        cdef Py_ssize_t i
        for i in range(1, num_nodes):
            node = path[i]

            parent = parent.add_left(TraceTree.initialise(node, cavity, &cav_is_changing))

        # Add the final reflection ABCDs for last tree node back to source
        # so that round-trip ABCD can be efficiently computed from root
        parent.set_left_abcd_x_memory(
            parent.node.component.ABCD,
            parent.node,
            root.node,
            direction="x",
            copy=False,
            retboth=True,
        )
        parent.set_left_abcd_y_memory(
            parent.node.component.ABCD,
            parent.node,
            root.node,
            direction="y",
            copy=False,
            retboth=True,
        )

        # co-ordinate system transformation on reflection due
        # to rotation around vertical axis (inversion)
        parent.is_left_surf_refl = is_surface_refl(
            parent.node.component, parent.node, root.node
        )

        return root

    @staticmethod
    def from_path(list path):
        """Construct a TraceTree from a list of optical nodes.

        The resulting tree decays to a linked list as the path
        is 1D - no branches will occur.

        Parameters
        ----------
        path : list
            A list of optical nodes representing the node path. This
            can be obtained from a :class:`.OpticalPath` instance
            by invoking :attr:`.OpticalPath.nodes`.

        Returns
        -------
        tree : :class:`.TraceTree`
            The tree representing the node path.
        """
        cdef:
            Py_ssize_t num_nodes = len(path)
            TraceTree parent = None
            TraceTree root

            object node

        if not num_nodes:
            return None

        root = TraceTree.initialise(path[0], None)
        parent = root

        cdef Py_ssize_t i
        for i in range(1, num_nodes):
            node = path[i]

            parent = parent.add_left(TraceTree.initialise(node, None))

        return root

    @classmethod
    def from_node(
        cls,
        node,
        object dependency,
        bint symmetric,
        pre_node=None,
        bint is_source=False,
        exclude=None,
    ):
        """Construct a TraceTree from an optical node root.

        The resulting tree includes all optical node paths traced
        forward from `node`.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            The root node.

        dependency : :class:`.Cavity` or :class:`.Gauss`
            The dependency object - i.e. what the trace sub-trees depend on.

        symmetric : bool
            Flag indicating whether the tree should be constructed assuming
            that opposite node beam parameters will be set via the reverse
            of the original node beam parameter (true indicates this will be
            the case). In practice, this means that the resultant tree will
            not include any duplicate ports.

        pre_node : :class:`.OpticalNode`, optional; default: None
            An optional node to add before the root for the root sub-tree.

        is_source : bool, optional; default: False
            Whether the root node is the source node of a TraceDependency.

        exclude : set, optional
            Set of optical nodes to avoid branching to.

        Returns
        -------
        tree : :class:`.TraceTree`
            The tree of all paths from `node`.
        """
        cdef:
            object model = node._model

            TraceTree new_root = None
            TraceTree root = None
            TraceTree parent

            dict sub_trees = {}

            unicode n_name
            unicode nbr_name
            dict nbrsdict

            OrderedSet excl = OrderedSet()

            bint is_dependency_changing = dependency.is_changing

        if pre_node is not None:
            new_root = TraceTree.initialise(pre_node, dependency, &is_dependency_changing)

        if exclude is not None:
            excl = OrderedSet(exclude)

        node_from_name = lambda n: model.network.nodes[n]["weakref"]()

        tree = networkx.bfs_tree(get_tracing_tree(model.optical_network), node.full_name)
        sub_trees = {}
        cdef Py_ssize_t i, j

        for i, (n_name, nbrsdict) in enumerate(tree.adjacency()):
            n = node_from_name(n_name)

            if n in excl or (symmetric and n.opposite in excl):
                if not i:
                    break

                continue

            excl.add(n)

            if i == 0:
                # Initialise first round and store as the parent
                root = TraceTree.initialise(n, dependency, &is_dependency_changing)
                parent = root
            else:
                parent = sub_trees.get(n_name, None)
                if parent is None:
                    continue

            for j, nbr_name in enumerate(nbrsdict.keys()):
                nbr = node_from_name(nbr_name)

                if nbr in excl or (symmetric and nbr.opposite in excl):
                    continue

                if j == 0:
                    sub_trees[nbr_name] = parent.add_left(
                        TraceTree.initialise(nbr, dependency, &is_dependency_changing)
                    )
                else:
                    sub_trees[nbr_name] = parent.add_right(
                        TraceTree.initialise(nbr, dependency, &is_dependency_changing)
                    )

        if root is None:
            return None

        if new_root is not None:
            new_root.add_left(root)
            new_root.is_source = is_source
        else:
            root.is_source = is_source

        return new_root or root

    ### Modifying the tree ###

    cpdef TraceTree add_left(self, TraceTree sub_tree) :
        """Add a left sub-tree to the tree.

        Parameters
        ----------
        sub_tree : :class:`.TraceTree`
            The tree to add to the left.

        Returns
        -------
        sub_tree : :class:`.TraceTree`
            The same tree that was added. This is useful for
            looping over a single branch of the tree as a parent
            tree can be set to the return of this method on each iteration.
        """
        cdef:
            object comp
            object parent_node = self.node

        self.left = sub_tree
        sub_tree.parent = self

        if parent_node.is_input:
            comp = parent_node.component
        else:
            comp = parent_node.space

        try:
            self.set_left_abcd_x_memory(
                comp.ABCD,
                parent_node,
                sub_tree.node,
                direction="x",
                copy=False,
                retboth=True,
                allow_reverse=True,
            )
            self.set_left_abcd_y_memory(
                comp.ABCD,
                parent_node,
                sub_tree.node,
                direction="y",
                copy=False,
                retboth=True,
                allow_reverse=True,
            )
        except TotalReflectionError:
            raise

        # co-ordinate system transformation on reflection due
        # to rotation around vertical axis (inversion)
        self.is_left_surf_refl = is_surface_refl(comp, parent_node, sub_tree.node)

        sub_tree.is_x_changing |= (
            self.sym_left_abcd_x is not None
            and is_abcd_changing(self.sym_left_abcd_x)
        )
        sub_tree.is_y_changing |= (
            self.sym_left_abcd_y is not None
            and is_abcd_changing(self.sym_left_abcd_y)
        )

        return sub_tree

    cpdef TraceTree add_right(self, TraceTree sub_tree) :
        """Add a right sub-tree to the tree.

        Parameters
        ----------
        sub_tree : :class:`.TraceTree`
            The tree to add to the right.

        Returns
        -------
        sub_tree : :class:`.TraceTree`
            The same tree that was added. This is useful for
            looping over a single branch of the tree as a parent
            tree can be set to the return of this method on each iteration.
        """
        cdef:
            object comp
            object parent_node = self.node

        self.right = sub_tree
        sub_tree.parent = self

        if parent_node.is_input:
            comp = parent_node.component
        else:
            comp = parent_node.space

        try:
            self.set_right_abcd_x_memory(
                comp.ABCD,
                parent_node,
                sub_tree.node,
                direction="x",
                copy=False,
                retboth=True,
                allow_reverse=True,
            )
            self.set_right_abcd_y_memory(
                comp.ABCD,
                parent_node,
                sub_tree.node,
                direction="y",
                copy=False,
                retboth=True,
                allow_reverse=True,
            )
        except TotalReflectionError:
            raise

        sub_tree.is_x_changing |= (
            self.sym_right_abcd_x is not None
            and is_abcd_changing(self.sym_right_abcd_x)
        )
        sub_tree.is_y_changing |= (
            self.sym_right_abcd_y is not None
            and is_abcd_changing(self.sym_right_abcd_y)
        )

        return sub_tree

    cpdef TraceTree remove_left(self) :
        """Removes the left sub-tree and returns it.

        Sets the ``left`` trace tree attribute to None, and nullifies
        left ABCD memory-views and pointers.

        Returns
        -------
        ltree : :class:`.TraceTree`
            The removed left sub-tree.
        """
        if self.left is None:
            return None

        tree = self.left
        self.left = None
        self.left_abcd_x = None
        self.sym_left_abcd_x = None
        self.left_abcd_y = None
        self.sym_left_abcd_y = None
        self.is_left_surf_refl = False

        return tree

    cpdef TraceTree remove_right(self) :
        """Removes the right sub-tree and returns it.

        Sets the ``right`` trace tree attribute to None, and nullifies
        right ABCD memory-views and pointers.

        Returns
        -------
        rtree : :class:`.TraceTree`
            The removed right sub-tree.
        """
        if self.right is None:
            return None

        tree = self.right
        self.right = None
        self.right_abcd_x = None
        self.sym_right_abcd_x = None
        self.right_abcd_y = None
        self.sym_right_abcd_y = None

        return tree

    def set_left_abcd_x_memory(self, target, *args, **kwargs):
        """Set the left ABCD matrix memory-views from the target function.
        Stores where this ABCD matrix came from for later retrieval and
        recreation if copied or pickled."""
        self.left_abcd_x_target = target
        self.left_abcd_x_args = args
        self.left_abcd_x_kwargs = kwargs

        cdef tuple Ms = target(*args, **kwargs)
        self.sym_left_abcd_x, self.left_abcd_x = Ms

    def set_left_abcd_y_memory(self, target, *args, **kwargs):
        """Set the left ABCD matrix memory-views from the target function.
        Stores where this ABCD matrix came from for later retrieval and
        recreation if copied or pickled."""
        self.left_abcd_y_target = target
        self.left_abcd_y_args = args
        self.left_abcd_y_kwargs = kwargs

        cdef tuple Ms = target(*args, **kwargs)
        self.sym_left_abcd_y, self.left_abcd_y = Ms

    def set_right_abcd_x_memory(self, target, *args, **kwargs):
        """Set the right ABCD matrix memory-views from the target function.
        Stores where this ABCD matrix came from for later retrieval and
        recreation if copied or pickled."""
        self.right_abcd_x_target = target
        self.right_abcd_x_args = args
        self.right_abcd_x_kwargs = kwargs

        cdef tuple Ms = target(*args, **kwargs)
        self.sym_right_abcd_x, self.right_abcd_x = Ms

    def set_right_abcd_y_memory(self, target, *args, **kwargs):
        """Set the right ABCD matrix memory-views from the target function.
        Stores where this ABCD matrix came from for later retrieval and
        recreation if copied or pickled."""
        self.right_abcd_y_target = target
        self.right_abcd_y_args = args
        self.right_abcd_y_kwargs = kwargs

        cdef tuple Ms = target(*args, **kwargs)
        self.sym_right_abcd_y, self.right_abcd_y = Ms

    cpdef trim_at_nodes(self, nodes, bint include_opposite=False) :
        """Trims branches from the tree starting at any optical node in `nodes`."""
        if self.left is not None:
            if self.left.node in nodes or (include_opposite and self.left.node.opposite in nodes):
                self.remove_left()
            else:
                self.left.trim_at_nodes(nodes, include_opposite)

        if self.right is not None:
            if self.right.node in nodes or (include_opposite and self.right.node.opposite in nodes):
                self.remove_right()
            else:
                self.right.trim_at_nodes(nodes, include_opposite)

    ### Tree searching ###

    cdef _get_all_nodes(self, OrderedSet nodes) :
        nodes.add(self.node)

        if self.left is not None:
            self.left._get_all_nodes(nodes)

        if self.right is not None:
            self.right._get_all_nodes(nodes)

    cpdef OrderedSet get_all_nodes(self) :
        """Retrieve a set consisting of all the :class:`.OpticalNode` objects
        covered by this tree.

        Returns
        -------
        nodes : set
            A set of all the optical nodes in the tree.
        """
        cdef OrderedSet nodes = OrderedSet()
        self._get_all_nodes(nodes)
        return nodes

    cpdef bint contains(self, object o) noexcept:
        """Whether the tree contains the specified object, determined recursively.

        Parameters
        ----------
        o : [:class:`.TraceTree` | :class:`.OpticalNode` | :class:`.Space` | :class:`.Connector`]
            The object to search for in the trace tree.

        Returns
        -------
        flag : bool
            True if `o` is in the tree, False otherwise.
        """
        from finesse.components import Space, Connector
        from finesse.components.node import OpticalNode

        if isinstance(o, TraceTree):
            return self._contains_tree(o)

        if isinstance(o, OpticalNode):
            return self._contains_node(o)

        if isinstance(o, Space):
            return self._contains_space(o)
        if isinstance(o, Connector):
            return self._contains_comp(o)

    cdef bint _contains_tree(self, TraceTree tree) noexcept:
        if self is tree:
            return True

        cdef bint left_contains = False
        if self.left is not None:
            left_contains = self.left._contains_tree(tree)

        cdef bint right_contains = False
        if self.right is not None:
            right_contains = self.right._contains_tree(tree)

        return left_contains or right_contains

    cdef bint _contains_node(self, object node) noexcept:
        return self.find_tree_at_node(node) is not None

    cdef bint _contains_space(self, object space) noexcept:
        if not self.node.is_input:
            tspace = self.node.space
            if tspace is space:
                return True

        cdef bint left_contains_space = False
        if self.left is not None:
            left_contains_space = self.left._contains_space(space)

        cdef bint right_contains_space = False
        if self.right is not None:
            right_contains_space = self.right._contains_space(space)

        return left_contains_space or right_contains_space

    cdef bint _contains_comp(self, object comp) noexcept:
        for node in comp.optical_nodes:
            if self._contains_node(node):
                return True

        return False

    cpdef TraceTree find_tree_at_node(self, object node, bint include_opposite=False) :
        """Recursively search for the TraceTree corresponding to the optical `node`."""
        if self.node is node or (include_opposite and self.node.opposite is node):
            return self

        if self.left is not None:
            ltree = self.left.find_tree_at_node(node, include_opposite)
            if ltree is not None:
                return ltree

        if self.right is not None:
            rtree = self.right.find_tree_at_node(node, include_opposite)
            if rtree is not None:
                return rtree

        return None

    ### Retrieving specific nodes, couplings etc. ###

    cdef _get_last_input_nodes(self, list last_nodes) :
        if self.left is None and self.right is None:
            if self.node.is_input:
                last_nodes.append(self.node)
            else:
                # TODO : ddb : this was causing segfaults when self.parent is None
                # Don't really get what this should be doing, should it throw an
                # error is such a case? Should everything have a parent?
                if self.parent is not None:
                    last_nodes.append(self.parent.node)
                    # If we're at a beamsplitter-type interface then get opposite node
                    # of reflection to last node so that both transmission
                    # intersections can be picked up properly
                    # TODO (sjr) Not sure if this is appropriate for asymmetric
                    #            tracing yet, need to think about it
                    if self.node.port is not self.parent.node.port:
                        last_nodes.append(self.node.opposite)

        if self.left is not None:
            self.left._get_last_input_nodes(last_nodes)

        if self.right is not None:
            self.right._get_last_input_nodes(last_nodes)

    cpdef list get_last_input_nodes(self) :
        """Retrieves a list of the final input optical nodes within the tree."""
        cdef list last_nodes = []
        self._get_last_input_nodes(last_nodes)
        return last_nodes

    cpdef TraceTree get_last_left_branch(self) :
        """Finds the final left sub-tree from this tree node."""
        cdef TraceTree t = self
        while t.left is not None:
            if t.left is None:
                break

            t = t.left

        return t

    cdef __append_mirror_refl_coupling(self, list couplings) :
        from finesse.components.surface import Surface

        opp_node = self.node.opposite
        comp = self.node.component
        if opp_node.port is self.node.port and isinstance(comp, Surface):
            # Make sure both sides of the surface get included if encountered
            if self.node.is_input:
                node1 = self.node
                node2 = opp_node
            else:
                node1 = opp_node
                node2 = self.node

            # Check that the reflection coupling makes sense
            if comp.is_valid_coupling(node1, node2):
                couplings.append((node1, node2))

    cdef _get_mirror_refl_couplings(self, list couplings) :
        self.__append_mirror_refl_coupling(couplings)

        if self.left is not None:
            self.left._get_mirror_refl_couplings(couplings)

        if self.right is not None:
            self.right._get_mirror_refl_couplings(couplings)

    cpdef list get_mirror_reflection_couplings(self) :
        """Obtain a list of all the node couplings corresponding to self-reflections."""
        cdef list couplings = []
        self._get_mirror_refl_couplings(couplings)
        return couplings

    ### Changing geometric parameter tree algorithms ###

    cpdef bint is_changing(self, bint recursive=True) noexcept:
        if not recursive:
            return self.is_x_changing or self.is_y_changing

        return (
            self.is_x_changing or self.is_y_changing
            or (self.left is not None and self.left.is_changing())
            or (self.right is not None and self.right.is_changing())
        )

    cdef _get_broadest_changing_subtrees(self, list trees) :
        if self.is_changing(recursive=False):
            trees.append(self)
            return

        if self.left is not None:
            self.left._get_broadest_changing_subtrees(trees)

        if self.right is not None:
            self.right._get_broadest_changing_subtrees(trees)

    cpdef list get_broadest_changing_subtrees(self) :
        """Retrieve a list of each TraceTree, from here, which is changing."""
        cdef list trees = []
        self._get_broadest_changing_subtrees(trees)
        return trees

    ### Drawing trees ###

    cdef _draw_tree(self, unicode lpad, list lines) :
        cdef:
            unicode pad
            unicode branch = "├─"
            unicode pipe = "│"
            unicode end = "╰─"
            unicode dash = "─"

            TraceTree ltree = self.left
            TraceTree rtree = self.right

        if ltree is not None:
            s = branch + dash
            if rtree is None:
                s = end + dash
                pad = "   "
            else:
                s = branch + dash
                pad = pipe + "   "
            lines.append(lpad + s + "o" + " " + ltree.node.full_name)
            ltree._draw_tree(lpad + pad, lines)

        if rtree is not None:
            s = end + dash
            pad = "   "
            lines.append(lpad + s + "o" + " " + rtree.node.full_name)
            rtree._draw_tree(lpad + pad, lines)

    cpdef draw(self, unicode left_pad="") :
        cdef:
            unicode first = self.node.full_name
            list lines = [left_pad + "o" + " " + first]

        self._draw_tree("", lines)
        treestr = f"\n{left_pad}".join(lines)

        return treestr

    def __str__(self):
        return self.draw()

    ### Propagating beams ###

    cdef void c_compute_rt_abcd(self, double* abcdx, double* abcdy) noexcept:
        cdef Py_ssize_t i
        # Reset ABCDs to identity matrices
        for i in range(4):
            if not i or i == 3:
                if abcdx != NULL:
                    abcdx[i] = 1.0
                if abcdy != NULL:
                    abcdy[i] = 1.0
            else:
                if abcdx != NULL:
                    abcdx[i] = 0.0
                if abcdy != NULL:
                    abcdy[i] = 0.0

        cdef TraceTree t = self
        while t is not None:
            if abcdx != NULL:
                c_abcd_multiply(abcdx, &t.left_abcd_x[0][0], out=abcdx)
            if abcdy != NULL:
                c_abcd_multiply(abcdy, &t.left_abcd_y[0][0], out=abcdy)

            t = t.parent

    cpdef compute_rt_abcd(self, double[:, ::1] abcdx=None, double[:, ::1] abcdy=None) :
        cdef:
            double* _abcdx = NULL
            double* _abcdy = NULL

        if not self.is_source or self.dep_type != DependencyType.CAVITY:
            raise RuntimeError("The tree is not an internal cavity tree, cannot compute round-trip matrix.")

        if abcdx is not None:
            _abcdx = &abcdx[0][0]
        if abcdy is not None:
            _abcdy = &abcdy[0][0]

        # Find the bottom first as round-trip matrix is
        # computed from multiplying each ABCD "upwards"
        # in the internal tree
        cdef TraceTree t = self.get_last_left_branch()
        t.c_compute_rt_abcd(_abcdx, _abcdy)

    cpdef dict trace_beam(self, double lambda0, bint symmetric) :
        """Trace the beam through the source tree."""
        if not self.is_source:
            raise RuntimeError(
                "TraceTree is not a source tree! Use TraceTree.propagate "
                "for non-source trees."
            )

        # Holds the tracing results as {node: qx, qy}
        cdef dict trace = {}

        # First q value will correspond to qx, qy of trace dependency
        qx = self.dependency.qx
        qy = self.dependency.qy
        trace[self.node] = qx, qy
        if symmetric:
            trace[self.node.opposite] = qx.reverse(), qy.reverse()

        self.propagate(trace, lambda0, symmetric)
        return trace

    cpdef propagate(self, dict trace, double lambda0, bint symmetric) :
        cdef:
            TraceTree ltree = self.left
            TraceTree rtree = self.right

            # Beam parameter(s) at the current optical node
            tuple q1 = trace[self.node]
            complex_t qx1_q = q1[0].q
            complex_t qy1_q = q1[1].q

            # Propagated beam parameters (re-used for both ltree, rtree)
            complex_t qx2_q, qy2_q

        if ltree is not None:
            # For non-symmetric traces we have some special checks
            # to do on trees which couldn't be reached from the
            # other dependency trees. Note these are only performed
            # on the left tree; see TraceForest._add_backwards_nonsymm_trees
            # for details.
            if symmetric or (not self.do_nonsymm_reverse and not self.do_inv_transform):
                qx2_q = transform_q(self.left_abcd_x, qx1_q, self.nr, ltree.nr)
                qy2_q = transform_q(self.left_abcd_y, qy1_q, self.nr, ltree.nr)
            elif self.do_inv_transform:
                # Can't reach tree directly but there is a coupling from ltree.node
                # to tree.node so apply the inverse abcd law to get correct q
                qx2_q = inv_transform_q(self.left_abcd_x, qx1_q, self.nr, ltree.nr)
                qy2_q = inv_transform_q(self.left_abcd_y, qy1_q, self.nr, ltree.nr)
            else:
                # Really is no way to get to the node (no coupling from ltree.node to
                # tree.node) so only option now is to reverse q for ltree node entry
                qx2_q = -conj(qx1_q)
                qy2_q = -conj(qy1_q)

            qx2 = BeamParam(q=qx2_q, wavelength=lambda0, nr=ltree.nr)
            qy2 = BeamParam(q=qy2_q, wavelength=lambda0, nr=ltree.nr)

            trace[ltree.node] = qx2, qy2
            if symmetric:
                trace[ltree.node.opposite] = qx2.reverse(), qy2.reverse()

            ltree.propagate(trace, lambda0, symmetric)

        if rtree is not None:
            qx2_q = transform_q(self.right_abcd_x, qx1_q, self.nr, rtree.nr)
            qy2_q = transform_q(self.right_abcd_y, qy1_q, self.nr, rtree.nr)

            qx2 = BeamParam(q=qx2_q, wavelength=lambda0, nr=rtree.nr)
            qy2 = BeamParam(q=qy2_q, wavelength=lambda0, nr=rtree.nr)

            trace[rtree.node] = qx2, qy2
            if symmetric:
                trace[rtree.node.opposite] = qx2.reverse(), qy2.reverse()

            rtree.propagate(trace, lambda0, symmetric)


# NOTE (sjr) Can get rid of this (and is_left_surf_refl flag in TraceTree) if
#            convention for reflections at surfaces is changed in ABCD methods
cdef bint is_surface_refl(comp, parent_node, sub_node) noexcept:
    # TODO (sjr) Want to move these imports to module level but we are
    #            losing the war against circular dependencies right now
    from finesse.components.general import InteractionType
    from finesse.components.surface import Surface

    return (
        isinstance(comp, Surface) and
        comp.interaction_type(parent_node, sub_node) == InteractionType.REFLECTION
    )
