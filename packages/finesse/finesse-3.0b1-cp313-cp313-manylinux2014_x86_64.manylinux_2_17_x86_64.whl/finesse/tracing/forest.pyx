#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""The TraceForest data structure used for representing propagating beams in a model.

Details on each class, method and function in this sub-module are provided mostly for
developers. Users should refer to :ref:`tracing_manual` for details on beam tracing,
:meth:`.Model.beam_trace` for the main method through which beam traces can be performed
on a model and :mod:`.tracing.tools` for the various beam propagation tools which the
beam tracing library provides.
"""

from finesse.cymath.math cimport float_eq
from finesse.cymath.gaussbeam cimport is_abcd_changing
from finesse.tracing.tree import get_tracing_tree
from finesse.tracing.tree cimport is_surface_refl
from finesse.components.node import NodeDirection

from itertools import chain
import logging
import numbers

from finesse.exceptions import BeamTraceException, TotalReflectionError, NoCouplingError
from finesse.utilities import refractive_index
from finesse.utilities.collections cimport OrderedSet
from finesse.utilities.collections import OrderedSet

LOGGER = logging.getLogger(__name__)


cdef class tree_container:
    """A container of TraceTree objects.

    Consists of a wrapper around a list of trees and a set of all
    the OpticalNode instances covered by this tree list. All of
    these attributes are read-only in the sense that they can only
    be accessed via C code.
    """
    def __init__(self, list trees=None):
        self.trees = []
        self.size = 0
        self.node_coverage = OrderedSet()

        # Support for creating a tree_container from pre-existing list of trees
        if trees:
            self.trees = trees.copy()
            self.size = len(self.trees)
            for tree in self.trees:
                self.node_coverage.update(tree.get_all_nodes())

    @property
    def trees(self):
        return self.trees[:]

    cdef clear(self) :
        self.trees.clear()
        self.node_coverage.clear()
        self.size = 0

    cdef append(self, TraceTree tree) :
        if tree is None:
            return

        self.trees.append(tree)
        self.size += 1
        self.node_coverage.update(tree.get_all_nodes())

    cdef remove(self, TraceTree tree) :
        if tree is None:
            return

        self.trees.remove(tree)
        self.size -= 1
        self.node_coverage.difference_update(tree.get_all_nodes())

    cdef _update_after_sub_remove(self, TraceTree sub_tree) :
        """Method to be called after removing sub-trees from the forest (via
        remove_left, remove_right on forest trees). Ensures that node_coverage
        remains consistent with forest state."""
        if sub_tree is None:
            return

        self.node_coverage.difference_update(sub_tree.get_all_nodes())

    def __getitem__(self, index):
        return self.trees[index]

    def __len__(self):
        return self.size




cdef class TraceForest:
    """A container structure which stores multiple :class:`.TraceTree` instances.

    The :class:`.Model` stores a TraceForest object which then represents the current
    tracing state of the configuration. Each time a :meth:`.Model.beam_trace` is called,
    either directly or indirectly, the TraceForest of the Model will be used to perform
    the tracing via propagation of the beam parameters through each tree. This is also
    detailed in :ref:`tracing_manual`.

    Determination of the ordering and overall structure of the TraceForest happens through
    the "planting" of the forest. By calling :meth:`.TraceForest.plant`, the forest is cleared
    and re-planted according to the ordered list of trace dependencies passed to this method.
    This is a step which is performed automatically in :meth:`.Model.beam_trace`, where this
    re-planting process only occurs under the following condition:

     * a connector has been added or removed since the last call,
     * the type of beam tracing has been switched from symmetric to
       asymmetric or vice-verase,
     * or the tracing priority (i.e. ordered list of trace dependencies)
       has changed in any way.

    In the initialisation process of building a simulation, a specialised version of a TraceForest
    is constructed from the model TraceForest using the ``TraceForest.make_changing_forest`` method.
    This inspects the model forest and selects only those trees, and branches of trees, which will
    have changing beam parameters during the simulation; i.e. due to some :class:`.GeometricParameter`
    being scanned. This new, "changing TraceForest" is then the optimised structure via which
    simulation-time beam traces (on changing beam parameter paths) are performed. More details on
    this, including additional powerful features that this changing forest provides, can be found
    in :ref:`tracing_manual`.

    .. rubric:: Special method support

    This class implements the following special methods: ``__getitem__``, ``__len__``, ``__iter__``,
    ``__next__`` and ``__contains__``, providing the following behaviour (assuming `forest` is an
    instance of this class):

      * ``tree = forest[x]`` - either get the :class:`.TraceTree` at index ``x`` (i.e. the x-th tree to be
        traced when performing a beam trace on the forest), OR if ``x`` is a :class:`.TraceDependency` get
        a list of all the trees in the forest which are associated with that dependency.
      * ``N_trees = len(forest)`` - the number of trees in the forest, equivalent to :meth:`.TraceForest.size`.
      * ``for tree in forest:`` - iteration support over the forest, in order of tracing priority.
      * ``flag = x in forest`` - check whether some object ``x`` is in the forest. This can be a :class:`.TraceTree`,
        an :class:`.OpticalNode`, a :class:`.Space` or a :class:`.Connector`. Equivalent to :meth:`.TraceForest.contains`.
    """
    def __init__(self, object model, bint symmetric, list trees=None):
        self.model = model
        self.symmetric = symmetric

        self.forest = tree_container(trees)
        self.dependencies = []

    def __deepcopy__(self, memo):
        raise RuntimeError("TraceForest instances cannot be copied.")

    ### Planting and clearing ###

    def plant(self, list trace_order):
        """Constructs and stores all the trace trees according to
        the order of dependencies in `trace_order`.

        Parameters
        ----------
        trace_order : list
            List of the dependency objects by priority of tracing.
        """
        from finesse.components import Cavity, Gauss

        self.clear()
        self.dependencies = trace_order.copy()

        # Always make the internal cavity trees first, these
        # will be generated in the order in which each cavity
        # appears in the trace_order dependency list
        cavities = list(filter(lambda x: isinstance(x, Cavity), self.dependencies))
        self._add_internal_cavity_trees(cavities)
        LOGGER.debug("TraceForest with internal Cavity trees: %s", self)

        # Handle ordering of internal cavity trees which overlap
        self._handle_overlapping_cavities()
        LOGGER.debug("TraceForest after overlapping cavities handled: %s", self)

        cdef OrderedSet internal_cav_nodes = self.forest.node_coverage.copy()
        cdef list gauss_nodes = []
        # Iterate through all dependencies by tracing order
        # and generate their associated trees
        for dep in self.dependencies:
            if isinstance(dep, Cavity):
                self._add_external_cavity_tree(dep)
            elif isinstance(dep, Gauss):
                mnode = next((n for n in gauss_nodes if n.space is dep.node.space), None)
                if mnode is not None:
                    mgauss = self.model.gausses[mnode]
                    # Cannot allow mismatches across spaces so explicitly ban
                    # separate Gauss objects at opposite ends of a space
                    if mnode.port is not dep.node.port:
                        raise BeamTraceException(
                            f"Gauss object {dep.name} is at the opposite end of a space to a "
                            f"previously defined Gauss ({mgauss.name}). Mode mismatches must occur "
                            "at connectors, not spaces, so disable or remove one of "
                            "these Gausses to propagate the intended beam.",
                        )
                    # Also prevent Gauss objects at opposite node of a port
                    # where a Gauss has already been defined
                    else:
                        raise BeamTraceException(
                            f"Gauss object {dep.name} is at the opposite node of a port with a "
                            f"previously defined Gauss ({mgauss.name}). Disable, or remove, one of "
                            "these Gausses to propagate the intended beam.",
                        )
                if dep.node in internal_cav_nodes:
                    raise BeamTraceException(
                        f"Gauss object {dep.name} is at an internal Cavity node "
                        f"({dep.node.full_name}). Disable, or remove, either the Gauss "
                        "or the corresponding Cavity to propagate the intended beam.",
                    )

                self._add_gauss_tree(dep)
                gauss_nodes.append(dep.node)
            else:
                raise TypeError(f"Unrecognised trace dependency type: {type(dep)}")
        LOGGER.debug(
            "TraceForest with internal, external Cavity trees and Gauss trees: %s",
            self,
        )

        # Remove common sub-trees sequentially
        self.trim()
        LOGGER.debug("TraceForest after trimming: %s", self)

        # Add branch trees at beam splitters where the nodes weren't
        # reachable from a previous trace tree
        cdef int missing = self._add_beamsplitter_branch_trees()
        LOGGER.debug("TraceForest after branch trees planted: %s", self)

        # If tracing is asymmetric and there are nodes which we can't
        # reach because of this (i.e. no path leading back to these
        # nodes), then we need to rectify this
        if not self.symmetric and missing:
            self._add_backwards_nonsymm_trees()
            # It's possible that there are still some branch nodes from beam splitters
            # that we couldn't reach at this point in asymmetric traces (e.g. a typical PDH
            # setup with a pick-off BS and one cav command), so we need to repeat the above
            # all over again to catch these trees
            if self._add_beamsplitter_branch_trees():
                self._add_backwards_nonsymm_trees()
            LOGGER.debug("TraceForest after backwards asymmetric trees added: %s", self)

        cdef OrderedSet diff = self.find_untraversed_nodes()
        if len(diff):
            raise BeamTraceException(
                f"The following optical nodes were not traced to. Ensure that a cavity or gaussian beam parameter is set that can reach them:\n{diff}"
            )

    cpdef void clear(self) noexcept:
        """Clears the trace forest, removing all trace trees."""
        self.forest.clear()

    cdef void trim(self) noexcept:
        cdef:
            Py_ssize_t i, j
            TraceTree tree1, tree2

            OrderedSet tree1_nodes
            OrderedSet trees_to_remove = OrderedSet()

        for i in range(self.forest.size):
            tree1 = self.forest[i]
            tree1_nodes = tree1.get_all_nodes()

            for j in range(i + 1, self.forest.size):
                tree2 = self.forest[j]
                # Don't attempt to trim common nodes for internal cavity trees
                if not tree2.is_source or tree2.dep_type == DependencyType.GAUSS:
                    # If any parts of tree2 overlap with tree1 then trim off
                    # these branches of tree2 to ensure uniqueness of trees
                    tree2.trim_at_nodes(tree1_nodes, self.symmetric)

                    if not tree2.is_source:
                        # Tree has no branches left so can be removed entirely
                        if tree2.left is None and tree2.right is None:
                            trees_to_remove.add(tree2)

        for tree in trees_to_remove:
            self.forest.remove(tree)

    cdef int _add_internal_cavity_trees(self, list cavities) except -1:
        cdef:
            Py_ssize_t Ncavs = len(cavities)
            Py_ssize_t cav_idx
            object cav

        for cav_idx in range(Ncavs):
            cav = cavities[cav_idx]

            self.forest.append(TraceTree.from_cavity(cav))

        return 0

    cdef int _handle_overlapping_cavities(self) except -1:
        cdef:
            Py_ssize_t i, j
            TraceTree tree1, tree2

            OrderedSet tree1_nodes
            list overlaps = []

        # Gather all the overlapping cavity combinations
        for i in range(self.forest.size):
            tree1 = self.forest[i]
            tree1_nodes = tree1.get_all_nodes()
            for j in range(i + 1, self.forest.size):
                tree2 = self.forest[j]
                for node in tree1_nodes:
                    if tree2._contains_node(node) or tree2._contains_node(node.opposite):
                        overlaps.append((tree1, tree2))
                        break

        # If there are no overlaps then nothing to do here
        if not overlaps:
            return 0

        # Make a flattened list of the overlapping tree combinations
        merged = list(chain.from_iterable(overlaps))
        # and merge the column slices of these combinations to get
        # the correct ordering before the operations below
        merged = merged[::2] + merged[1::2]

        # From this, create a list of these unique trees with the order
        # reversed such that trees which were added first from the cavity
        # trace order will overwrite the branches of the later trees which
        # intersect with them. This then guarantees that the trace_order given
        # to TraceForest.plant will be preserved for overlapping cavities.
        new_inner_order = list(dict.fromkeys(reversed(merged)))

        # Remove the internal cavity trees which are present in this
        # overlapping trees container...
        self.forest = tree_container(
            [tree for tree in self.forest.trees if tree not in new_inner_order]
        )
        # ... and then add them back in the order as outlined above
        for tree in new_inner_order:
            self.forest.append(tree)

        return 0

    cdef int _add_external_cavity_tree(self, object cav) except -1:
        cdef:
            dict exit_nodes
            object source, target

        exit_nodes = cav.get_exit_nodes()
        for source, target in exit_nodes.items():
            self.forest.append(
                TraceTree.from_node(
                    target,
                    cav,
                    self.symmetric,
                    pre_node=source,
                    exclude=self.forest.node_coverage,
                )
            )

        return 0

    cdef int _add_gauss_tree(self, object gauss) except -1:
        cdef:
            object gauss_node = gauss.node

            Py_ssize_t tree_idx
            TraceTree tree, new_tree, found, fp, fpp
            TraceTree rm_tree, tmp_tree
            OrderedSet trees_to_remove = OrderedSet()

        # Find branches in trees already planted that contain the gauss node
        # or its opposite direction
        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            found = tree.find_tree_at_node(gauss_node, include_opposite=True)
            if found is not None: # found a tree at the gauss node
                fp = found.parent
                if fp is not None: # this tree has a parent
                    # the parent node is an output i.e. a space exists between
                    # parent and the gauss -> so we want to remove parent too
                    if not fp.node.is_input:
                        fpp = fp.parent
                        if fpp is None: # parent has no parent so just remove the whole tree
                            trees_to_remove.add(tree)
                        else: # parent has a parent
                            if fp == fpp.left:
                                tmp_tree = fpp.remove_left()
                                self.forest._update_after_sub_remove(tmp_tree)
                            else:
                                tmp_tree = fpp.remove_right()
                                self.forest._update_after_sub_remove(tmp_tree)

                            # if the parent of parent has no remaining connections
                            # just remove the whole tree
                            if not fpp.is_source:
                                if fpp.left is None and fpp.right is None and fpp.parent is None:
                                    trees_to_remove.add(tree)
                    else: # parent node is an input (no space between parent -> gauss)
                        if found == fp.left:
                            tmp_tree = fp.remove_left()
                            self.forest._update_after_sub_remove(tmp_tree)
                        else:
                            tmp_tree = fp.remove_right()
                            self.forest._update_after_sub_remove(tmp_tree)

                        if not fp.is_source:
                            if fp.left is None and fp.right is None and fp.parent is None:
                                trees_to_remove.add(tree)
                else: # found tree has no parent so just remove the whole tree
                    trees_to_remove.add(tree)

        for rm_tree in trees_to_remove:
            self.forest.remove(rm_tree)

        new_tree = TraceTree.from_node(
            gauss_node,
            gauss,
            self.symmetric,
            is_source=True,
            exclude=self.forest.node_coverage,
        )
        self.forest.append(new_tree)

        # If the opposite direction of gauss node is not in the forward propagated
        # gauss tree then we need to make a tree from gauss.opposite too
        if (
            self.symmetric or
            (
                new_tree is not None and
                new_tree.find_tree_at_node(gauss_node.opposite) is None
            )
        ):
            # Backwards tree is not from the gauss node itself now
            # so leave is_source as False otherwise there would be
            # two sources from the same gauss node leading to problems
            back_new_tree = TraceTree.from_node(
                gauss_node.opposite,
                gauss,
                self.symmetric,
                exclude=self.forest.node_coverage - OrderedSet([gauss_node]),
            )

            if (
                back_new_tree is not None and
                (back_new_tree.left is not None or back_new_tree.right is not None)
            ):
                self.forest.append(back_new_tree)

        return 0

    cdef int _add_beamsplitter_branch_trees(self) except -1:
        cdef:
            double node_nr, pre_node_nr
            OrderedSet diff = self.find_untraversed_nodes()
            dict branch_start_nodes = {}

        from finesse.components.general import InteractionType

        if not diff:
            return 0

        tree = get_tracing_tree(self.model.optical_network)

        for node in diff:
            pre = list(tree.predecessors(node.full_name))
            node_nr = refractive_index(node)
            for pre_node_name in pre:
                pre_node = self.node_from_name(pre_node_name)
                pre_node_nr = refractive_index(pre_node)
                # If predecessor node is also in the set of unreachable nodes OR
                # the interaction type from pre_node -> node is a reflection and
                # the refractive indices at these ports are not the same (total
                # internal reflection) then skip it
                if (
                    pre_node in diff
                    or (
                        node.component.interaction_type(pre_node, node) == InteractionType.REFLECTION
                        and not float_eq(node_nr, pre_node_nr)
                    )
                ):
                    continue

                # Otherwise we want to store the predecessor node and its associated
                # dependency in a dict to make trees from later
                branch_start_nodes[node] = pre_node, self.find_dependency_from_node(pre_node)
                break

        if len(branch_start_nodes) == 0:
            # Shouldn't ever have a case where a branched node does not have
            # a predecessor (when doing symmetric planting), so if this
            # happens a bug has been encountered
            if self.symmetric:
                raise BeamTraceException(
                    f"These nodes were not reachable by the tracer and their beam parameter could not be set: {tuple(n.full_name for n in diff)}. "
                    "Ensure that you have set a cavity or gaussian beam parameter that can reach them."
                )
            # But if we're not a symmetric forest, then this will occur in
            # most cases as (for anything but extremely simple files) there
            # will be nodes which can't be reached directly, so inform on
            # return that this is the case
            else:
                return 1

        for node, (pre_node, dependency) in branch_start_nodes.items():
            self.forest.append(
                TraceTree.from_node(
                    node,
                    dependency,
                    self.symmetric,
                    pre_node=pre_node,
                    exclude=self.forest.node_coverage,
                )
            )

        return self._add_beamsplitter_branch_trees()

    cdef int _add_backwards_nonsymm_trees(self) except -1:
        cdef:
            TraceTree tree
            # twisted tree root and branch
            TraceTree ttr, ttb

            object comp
            bint is_dependency_changing

        # Get all the nodes we can't reach due to the asymmetric trace
        unreachable_nodes = self.find_untraversed_nodes()
        for node in unreachable_nodes:
            tree = self.find_tree_from_node(node.opposite)
            if tree is None:
                continue

            is_dependency_changing = tree.dependency.is_changing
            # Here we begin the process of making a "twisted tree" where
            # the left sub-tree node is actually a pre-coupling of the
            # parent tree node, this will allow us to apply the inverse
            # ABCD law transformation to left sub-tree node during tracing
            ttr = TraceTree.initialise(
                tree.node, tree.dependency, &is_dependency_changing
            )
            ttb = TraceTree.initialise(
                node, tree.dependency, &is_dependency_changing
            )

            if ttb.node.is_input:
                comp = ttb.node.component
            else:
                comp = ttb.node.space

            ttr.left = ttb
            ttb.parent = ttr

            try:
                # Check that there is a coupling from unreachable node -> opposite
                comp.check_coupling(ttb.node, ttr.node)

                try:
                    # Just to re-iterate, here we get the ABCD matrix coupling from
                    # the left tree to the parent tree (opposite to usual) in order
                    # to use this matrix in the inverse ABCD law transformation
                    ttr.set_left_abcd_x_memory(
                        comp.ABCD, ttb.node, ttr.node, direction="x", copy=False, retboth=True
                    )
                    ttr.set_left_abcd_y_memory(
                        comp.ABCD, ttb.node, ttr.node, direction="y", copy=False, retboth=True
                    )
                except TotalReflectionError:
                    raise

                ttr.is_left_surf_refl = is_surface_refl(comp, ttb.node, ttr.node)

                ttb.is_x_changing |= (
                    ttr.sym_left_abcd_x is not None
                    and is_abcd_changing(ttr.sym_left_abcd_x)
                )
                ttb.is_y_changing |= (
                    ttr.sym_left_abcd_y is not None
                    and is_abcd_changing(ttr.sym_left_abcd_y)
                )

                # Now mark the twisted tree root as an inverse transformation tree
                ttr.do_inv_transform = True
            except NoCouplingError:
                # No coupling exists from ttb.node -> ttr.node (typically means no
                # reflection coupling) so mark the root as needing a -q* operation
                # instead now as there is no other way to set the node q otherwise
                ttr.do_nonsymm_reverse = True

            self.forest.append(ttr)

    cpdef OrderedSet find_untraversed_nodes(self) :
        """Finds all the optical nodes in the model which are not
        covered by the trace forest."""
        cdef:
            OrderedSet nodes_traversed = self.forest.node_coverage
            OrderedSet nominal_diff = OrderedSet(self.model.optical_nodes).difference(nodes_traversed)
            OrderedSet real_diff = OrderedSet()

        if not self.symmetric:
            return nominal_diff

        for node in nominal_diff:
            if node.opposite not in nodes_traversed:
                real_diff.add(node)

        return real_diff

    ### Searching and attributes ###

    cpdef Py_ssize_t size(self) noexcept:
        """The number of trees in the forest."""
        return self.forest.size

    cpdef bint empty(self) noexcept:
        """Whether the forest is empty (no trees) or not."""
        return not self.forest.size

    def __getitem__(self, x):
        from finesse.components.trace_dependency import TraceDependency

        if isinstance(x, numbers.Integral):
            return self.forest[x]
        if isinstance(x, TraceDependency):
            return self.trees_of_dependency(x)

        raise TypeError(
            "Expected sub-script of type: Integral or TraceDependency, but "
            f"received {x} of type {type(x)}"
        )

    def __len__(self):
        return self.forest.size

    def __iter__(self):
        return iter(self.forest.trees)

    def __next__(self):
        return next(self.forest.trees)

    def __contains__(self, o):
        return self.contains(o)

    cpdef bint contains(self, object o) noexcept:
        """Whether the forest contains the specified object, determined recursively for
        each tree within the forest.

        Parameters
        ----------
        o : [:class:`.TraceTree` | :class:`.OpticalNode` | :class:`.Space` | :class:`.Connector`]
            The object to search for in the forest.

        Returns
        -------
        flag : bool
            True if `o` is in the forest, False otherwise.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            if tree.contains(o):
                return True

        return False

    cdef list _get_trees_upred(self, bint (*predicate)(TraceTree)):
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            list trees = []

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            if predicate(tree):
                trees.append(tree)

        return trees

    cdef list _get_trees_bpred(self, bint (*predicate)(TraceTree, object), object o):
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            list trees = []

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            if predicate(tree, o):
                trees.append(tree)

        return trees

    cpdef list trees_of_dependency(self, object dependency) :
        """Get a list of all the :class:`.TraceTree` instances with the
        associated trace `dependency` object.

        Parameters
        ----------
        dependency : :class:`.TraceDependency`
            A trace dependency object.

        Returns
        -------
        trees : list
            A list of all trace trees with dependency equal to above object.
        """
        return self._get_trees_bpred(dep_match_pred, dependency)

    cdef list get_internal_cavity_trees(self) :
        return self._get_trees_upred(internal_cav_pred)

    @property
    def internal_cavity_trees(self):
        return self.get_internal_cavity_trees()

    cdef list get_external_cavity_trees(self) :
        return self._get_trees_upred(external_cav_pred)

    @property
    def external_cavity_trees(self):
        return self.get_external_cavity_trees()

    cdef list get_gauss_trees(self) :
        return self._get_trees_upred(gauss_pred)

    @property
    def gauss_trees(self):
        return self.get_gauss_trees()

    cpdef TraceTree find_tree_from_node(self, object node) :
        """Given an optical node, this finds the :class:`.TraceTree` instance
        corresponding to this node (if one exists).

        Parameters
        ----------
        node : :class:`.OpticalNode`
            An optical node.

        Returns
        -------
        tree : :class:`.TraceTree`
            The tree corresponding to `node`, or ``None`` if none found.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree, found

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            found = tree.find_tree_at_node(node, self.symmetric)
            if found is not None:
                return found

        return None

    cpdef object find_dependency_from_node(self, object node, bint raise_not_found=True) :
        """Finds the dependency object associated with the optical `node`.

        If no tree is found associated with this node, and `raise_not_found` is true,
        then a ``BeamTraceException`` is raised. Otherwise `None` is returned.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            An optical node.

        raise_not_found : bool, optional; default: True
            Raises a BeamTraceException if no dependency found. Returns `None` if False.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree, found

        for tree_idx in range(self.forest.size, 0, -1):
            tree = self.forest[tree_idx - 1]

            found = tree.find_tree_at_node(node, self.symmetric)
            if found is not None:
                return found.dependency

        if raise_not_found:
            raise BeamTraceException(
                f"Could not find a dependency object associated with node {node.full_name} in the trace forest."
            )
        else:
            return None

    cdef object node_from_name(self, name) :
        return self.model.network.nodes[name]["weakref"]()

    ### Changing geometric parameter forest algorithms ###

    cpdef TraceForest make_changing_forest(self) :
        """Constructs a new TraceForest from this forest, consisting
        of only the trees which will have changing beam parameters.

        This method is called in BaseSimulation._initialise for setting
        up the simulation trace forest used for efficient beam tracing.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree, chtree

            list changing_trees = []
            bint branch_added = False

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]
            branch_added = False
            # For branched beamsplitter trees, need to see if the root
            # node opposite is already present in the changing trees
            # list --- if so then add the branch tree as this will also
            # be changing
            for chtree in changing_trees:
                if chtree.find_tree_at_node(tree.node.opposite) is not None:
                    changing_trees.append(tree)
                    branch_added = True
                    break

            if not branch_added:
                # From this tree, obtain the broadest sub-trees which
                # will have changing beam parameters
                changing_trees.extend(tree.get_broadest_changing_subtrees())

        cdef Py_ssize_t Nchanging_nominal = len(changing_trees)
        cdef OrderedSet roots = OrderedSet() # Parents of changing trees
        cdef OrderedSet trees_to_remove = OrderedSet()
        for tree_idx in range(Nchanging_nominal):
            tree = changing_trees[tree_idx]
            # Now set each changing tree to the parent tree so that
            # the root is used in beam tracing...
            if tree.parent is not None:
                # ... but only do this for parents not yet added
                # otherwise could get duplicate trees
                if tree.parent not in roots:
                    changing_trees[tree_idx] = tree.parent
                    roots.add(tree.parent)
                else:
                    # This tree will already be encapsulated by the previous
                    # parent so just mark it to be removed
                    trees_to_remove.add(tree)

        for tree in trees_to_remove:
            changing_trees.remove(tree)

        cdef TraceForest changing_forest = TraceForest(self.model, self.symmetric, changing_trees)

        return changing_forest

    ### Automatic mode mismatch coupling determination ###

    cpdef tuple find_potential_mismatch_couplings(self, TraceForest other=None) :
        """Retrieves the node couplings which are potentially mode mismatched. If
        `other` is not given then the couplings which are local to this forest only
        will be found, otherwise couplings between this forest and `other` will
        be retrieved.

        If this forest is asymmetric, then calling this method is equivalent to
        calling :meth:`.TraceForest.find_intersection_couplings`.

        This method is used internally for obtaining all the possible mode mismatch
        couplings between a changing trace forest (held by a modal simulation) and
        the main model trace forest.

        Parameters
        ----------
        other : :class:`.TraceForest`
            Find dependencies from a different trace forest than this one
            when checking for mode mismatch couplings.

        Returns
        -------
        couplings : tuple
            A tuple of the node couplings where each element is ``(from_node, to_node)``.
        """
        from finesse.components.general import InteractionType

        intersect_couplings = self.find_intersection_couplings(other)

        cdef list refls = []
        cdef list fake_refl_mismatches = []
        cdef tuple other_mrefls
        cdef object[:, ::1] refl_abcd_sym_x
        cdef object[:, ::1] refl_abcd_sym_y
        # If we're doing a symmetric trace then self-reflections from mirror-type components
        # can be potential mode mismatch couplings so need to add these too
        if self.symmetric:
            refls.extend(self.get_mirror_reflection_couplings())
            for node1, node2 in refls:
                opp_surface_onode = None
                # Find the output node on the other side of the surface
                for n1s_name in list(self.model.optical_network.successors(node1.full_name)):
                    n1s = self.node_from_name(n1s_name)
                    if node1.component.interaction_type(node1, n1s) == InteractionType.TRANSMISSION:
                        opp_surface_onode = n1s
                        break

                # If none found then nothing else needs to be done for this coupling
                if opp_surface_onode is None:
                    continue

                # Reflection coupling on other side of surface is in the potential
                # mismatch couplings so this one can remain too
                if (opp_surface_onode.opposite, opp_surface_onode) in refls:
                    continue

                # Get the dependencies associated with the two sides of the surface
                dep1 = self.find_dependency_from_node(node1)
                dep2 = self.find_dependency_from_node(opp_surface_onode, raise_not_found=False)
                if dep2 is None and other is not None:
                    dep2 = other.find_dependency_from_node(opp_surface_onode)

                # Finally, if the dependencies of the trees on both sides are the same
                # then this isn't really a mismatch coupling (as beam params on both sides
                # are guaranteed to be mode matched in such a case) so mark it to be removed
                if dep1 is dep2:
                    fake_refl_mismatches.append((node1, node2))

            for fnodes in fake_refl_mismatches:
                refls.remove(fnodes)

            # In addition, if the model trace forest is specified via other
            # then we need to check for reflection couplings here which
            # impinge against connectors with changing ABCDs as these will
            # also be potential mode mismatch couplings
            if other is not None:
                other_mrefls = other.get_mirror_reflection_couplings(
                    skip_dependencies=self.dependencies,
                )

                for node1, node2 in other_mrefls:
                    # Don't add the coupling if we already determined that it
                    # was a "fake" mismatch coupling (see above)
                    if (node1, node2) in fake_refl_mismatches:
                        continue

                    comp = node1.component
                    # Get the symbolic ABCDs upon reflection from the surface...
                    refl_abcd_sym_x = comp.ABCD(
                        node1, node2, "x", copy=False, symbolic=True
                    )
                    refl_abcd_sym_y = comp.ABCD(
                        node1, node2, "y", copy=False, symbolic=True
                    )

                    # ... and check if they're changing, if so we have another
                    # possible mode mismatch coupling which needs to be added
                    if is_abcd_changing(refl_abcd_sym_x) or is_abcd_changing(refl_abcd_sym_y):
                        refls.append((node1, node2))

        return intersect_couplings + tuple(OrderedSet(refls))


    cpdef tuple find_intersection_couplings(self, TraceForest other=None) :
        """Finds the node couplings at which trees with differing trace dependencies intersect.

        Parameters
        ----------
        other : :class:`.TraceForest`
            Find dependencies from a different trace forest than this one
            when checking for intersections.

        Returns
        -------
        couplings : tuple
            A tuple of the node couplings where each element is ``(from_node, to_node)``.
        """
        cdef:
            Py_ssize_t otree_idx
            TraceTree tree

            list couplings = []

        if not self.forest.size:
            return ()

        for otree_idx in range(self.forest.size):
            tree = self.forest[otree_idx]

            # An internal cavity trace can have intersection couplings
            # from any input node in the cavity path
            if tree.is_source and tree.dep_type == DependencyType.CAVITY:
                last_nodes = [n for n in tree.get_all_nodes() if n.is_input]
            else:
                # Get the final *input* nodes at the end of the tree, across all branches
                last_nodes = tree.get_last_input_nodes()
                # Need to also add the reverse node of the tree if it's a source
                # tree so that intersections are checked in the other propagation
                if tree.is_source and tree.node.opposite not in last_nodes:
                    last_nodes.append(tree.node.opposite)

            for node in last_nodes:
                # Obtain the successor nodes of this (if any) from the network
                succ_nodes = list(self.model.optical_network.successors(node.full_name))

                for snode_name in succ_nodes:
                    snode = self.node_from_name(snode_name)
                    # Then for each successor node find its TraceTree in the forest
                    # and obtain the dependency that this relies upon
                    if other is None:
                        snode_dep = self.find_dependency_from_node(snode)
                    else:
                        snode_dep = other.find_dependency_from_node(snode)

                    # If this dependency is not the same object as the original tree's
                    # dependency then we've found an intersection so add this coupling
                    if snode_dep is not tree.dependency:
                        # Here we do some sanity checks on the coupling we've found
                        node.component
                        snode.component
                        if node.component is not snode.component:
                            raise BeamTraceException(
                                "Found an intersection coupling "
                                f"{node.full_name} -> {snode.full_name} which "
                                "does not occur across the same connector. Mode "
                                "mismatches must not occur across Spaces in Finesse."
                            )
                        node.component.check_coupling(node, snode)

                        couplings.append((node, snode))
                        # Add the reverse coupling too if it exists
                        try:
                            node.component.check_coupling(snode.opposite, node.opposite)
                            couplings.append((snode.opposite, node.opposite))
                        except:
                            pass

        return tuple(OrderedSet(couplings))

    cpdef tuple get_mirror_reflection_couplings(
        self,
        bint ignore_internal_cavities=True,
        list skip_dependencies=None,
    ) :
        """Get the node couplings in the forest which correspond to self-reflections
        from mirror-like components.

        Parameters
        ----------
        ignore_internal_cavities : bool, default: True
            Ignore the node couplings inside cavities.

        skip_dependencies : list
            Optional list of trees to skip based on their dependencies.

        Returns
        -------
        couplings : tuple
            A sequence of tuples consisting of the node1 -> node2 self
            reflection couplings.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            list couplings = []

        if skip_dependencies is None:
            skip_dependencies = []

        # Gather the nodes which are part of any cavity cycle
        cdef OrderedSet internal_cav_nodes = OrderedSet()
        for tree in self.get_internal_cavity_trees():
            internal_cav_nodes.update(tree.get_all_nodes())

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]

            if tree.dependency in skip_dependencies:
                continue

            if ignore_internal_cavities:
                # The tree is an internal cavity tree itself so skip the whole thing
                if tree.is_source and tree.dep_type == DependencyType.CAVITY:
                    continue

                # If it's a tree coming directly from an internal cavity tree then
                # get the reflection couplings only from the second node onwards
                if tree.node in internal_cav_nodes:
                    if tree.left is not None:
                        couplings.extend(tree.left.get_mirror_reflection_couplings())
                else:
                    couplings.extend(tree.get_mirror_reflection_couplings())
            else:
                couplings.extend(tree.get_mirror_reflection_couplings())

        return tuple(OrderedSet(couplings))

    def get_nodes_with_changing_q(self):
        """For a given TraceForest this method will determine which optical nodes in a
        model will have a changing complex beam parameter.

        This relies on element Parameters having their ``is_tunable`` or ``is_changing``
        being set as ``True``. In such cases the Model will construct a simulation where
        the calculations dependent on these parameters will be recomputed at multiple
        steps.

        Returns
        -------
        q_changing_nodes : set{OpticalNode}
            Set of of OpticalNodes which will have a changing complex beam parameter
            during a simulation.
        """
        model = self.model
        q_changing_nodes = OrderedSet()
        # 1) Get changing geometric parameters
        changing_geometric = [p for el in model.elements.values() for p in el.parameters if p.is_geometric and p.is_changing]
        # 2) Get elements with changing geometric parameters
        changing_geometric_elements = {p.owner for p in changing_geometric}
        # 3) Can't tell yet which changing geometric parameter will affect which
        #    coupling, so grab all output nodes which might carry new q away
        output_nodes = [n for el in changing_geometric_elements for n in el.optical_nodes if n.direction == NodeDirection.OUTPUT]
        if len(output_nodes) == 0:
            return q_changing_nodes

        # 4) Are any nodes in a cavity trace? If so they will propgate to other intersecting tree
        affected_cavities = {tree.dependency for n in output_nodes for tree in model.trace_forest.internal_cavity_trees if tree.contains(n)}

        if len(affected_cavities) == 0:
            # Changing nodes are not part of a cavity, but can still have
            # downstream affects.
            # For each node, find the downstream tree to see which nodes it will effect
            output_trees = tuple(model.trace_forest.find_tree_from_node(n) for n in output_nodes)
            if len(output_trees) > 0:
                # Merge all the nodes into one unique set
                q_changing_nodes = OrderedSet.union(*(t.get_all_nodes() for t in output_trees))
        else:
            # otherwise get all the nodes in each of the cavities being affected
            q_changing_nodes = OrderedSet.union(*(tree.get_all_nodes() for tree in chain.from_iterable(model.trace_forest.trees_of_dependency(c) for c in affected_cavities)))

        if model.trace_forest.symmetric and len(q_changing_nodes) > 0:
            # If it's symmetric tracing we need to make
            # sure pairs of nodes are marked
            q_changing_nodes = OrderedSet.union(q_changing_nodes, {n.opposite for n in q_changing_nodes})

        return q_changing_nodes

    ### Drawing ###

    cpdef draw_by_dependency(self) :
        """Draws the forest as a string representation.

        All the trees in the forest are sorted by their dependency and
        stored in the resultant string by these dependency sub-headings. Each
        tree also has its index (i.e. tracing priority) stored in the string
        above the drawn tree.

        Returns
        -------
        forest_str : str
            A string representation of the forest, sorted by dependency with
            tracing priority indices displayed for each tree.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            list dependencies = []

            all_trees_str = ""

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]
            if tree.dependency not in dependencies:
                dependencies.append(tree.dependency)

        for dependency in dependencies:
            # Make sub-heading for each dependency, giving its name and type name
            all_trees_str += f"\nDependency: {dependency.name} [{type(dependency).__name__}]\n\n"
            for tree_idx in range(self.forest.size):
                tree = self.forest[tree_idx]
                if tree.dependency == dependency:
                    # Give the index of the tree in the forest before drawing each tree
                    # -> indicates tracing order of the tree
                    all_trees_str += (
                        f"  (Index: {tree_idx})\n" + tree.draw(left_pad="    ") + "\n\n"
                    )

        return all_trees_str

    cpdef draw(self) :
        """Draws the forest, by trace priority, as a string representation.

        The order in which trees appear in this string represents the order in which
        they will be traced during the beam tracing algorithm.

        In the rare cases where a subsequent tree contains a duplicate node (from an
        earlier tree), the latter tree trace will overwrite the former. This is only
        applicable to configurations with overlapping cavities, and this overwriting
        behaviour will take account of the desired cavity ordering given by the user.

        Returns
        -------
        forest_str : str
            A string representation of the ordered forest.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            object last_dep = None
            all_trees_str = ""

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]
            dep = tree.dependency

            if dep is not last_dep:
                all_trees_str += f"\nDependency: {dep.name} [{type(dep).__name__}]\n\n"
            else:
                all_trees_str += "\n"

            all_trees_str += tree.draw(left_pad="  ") + "\n"

            last_dep = dep

        return all_trees_str

    def __str__(self):
        return self.draw()

    ### Propagating beams ###

    cpdef dict trace_beam(self) :
        """Performs a "model-time" beam trace on all trace trees.

        This method is called internally by :meth:`.Model.beam_trace`. One should
        use that method to get a more complete representation of the tracing of
        the beam through a model.

        Returns
        -------
        trace : dict
            Dictionary of `node: (qx, qy)` mappings where `node` is each
            :class:`.OpticalNode` instance and `qx, qy` are the beam
            parameters in the tangential and sagittal planes, respectively,
            at these nodes.
        """
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            double lambda0 = self.model.lambda0

            dict trace = {}

        for tree_idx in range(self.forest.size):
            tree = self.forest[tree_idx]
            if tree.is_source:
                trace.update(tree.trace_beam(lambda0, self.symmetric))
            else:
                tree.propagate(trace, lambda0, self.symmetric)

        return trace


### Useful low-level predicates for TraceTree filtering ###

cdef bint dep_match_pred(TraceTree tree, object dependency) noexcept:
    return tree.dependency is dependency

cdef bint internal_cav_pred(TraceTree tree) noexcept:
    return tree.is_source and tree.dep_type == DependencyType.CAVITY

cdef bint external_cav_pred(TraceTree tree) noexcept:
    return not tree.is_source and tree.dep_type == DependencyType.CAVITY

cdef bint gauss_pred(TraceTree tree) noexcept:
    return tree.is_source and tree.dep_type == DependencyType.GAUSS
