from finesse.utilities.collections cimport OrderedSet

cdef enum DependencyType:
    CAVITY,
    GAUSS,
    NONE

cdef class TraceTree:
    cdef readonly:
        TraceTree parent
        TraceTree left
        TraceTree right

        # The TraceDependency object that the tree relies on
        object dependency
        object node

        bint is_x_changing
        bint is_y_changing

        # Flag for whether tree is directly from a TraceDependency source
        # (this is True when the tree is an internal cavity tree or a tree
        #  from a Gauss node)
        bint is_source

        # Numeric views on the component ABCD matrices - the initial
        # numeric ABCD memory for each component is only ever modified,
        # never re-allocated, so these views will always be valid
        double[:, ::1] left_abcd_x
        double[:, ::1] left_abcd_y
        double[:, ::1] right_abcd_x
        double[:, ::1] right_abcd_y
        # Is the left tree a reflection from a surface? Important for
        # computing composite / round-trip ABCDs so co-ordinate transformation
        # in x plane can be taken into account
        bint is_left_surf_refl

        # Symbolic ABCD views - only to be used for utility beam tracing code
        # such as computing a composite ABCD matrix over a path
        object[:, ::1] sym_left_abcd_x
        object[:, ::1] sym_left_abcd_y
        object[:, ::1] sym_right_abcd_x
        object[:, ::1] sym_right_abcd_y

        double nr

        object left_abcd_x_target
        object left_abcd_x_args
        object left_abcd_x_kwargs
        object left_abcd_y_target
        object left_abcd_y_args
        object left_abcd_y_kwargs
        object right_abcd_x_target
        object right_abcd_x_args
        object right_abcd_x_kwargs
        object right_abcd_y_target
        object right_abcd_y_args
        object right_abcd_y_kwargs

    cdef:
        DependencyType dep_type

        # Indices of the node (and opposite for symmetric tracing) to be
        # set and used by a BaseSimulation
        Py_ssize_t node_id
        Py_ssize_t opp_node_id

        # Only used for non-symmetric traces on trees which couldn't be
        # reached from any other dependency branch. This flag indicates
        # the next (left) tree node is a reverse coupling so need to
        # apply the inverse abcd law transform when tracing.
        bint do_inv_transform

        # Again, only used for non-symmetric traces on trees which couldn't
        # be reached from any other dependency branch AND for which the node
        # doesn't have a reverse coupling; e.g. reverse node at a Laser. This
        # flag indicates that the next tree node needs -q* applied during tracing
        # as there is really no other option for setting it at this point.
        bint do_nonsymm_reverse

    @staticmethod
    cdef TraceTree initialise(
        object node, object dependency, bint* is_dependency_changing=?
    )

    ### Modifying the tree ###

    cpdef TraceTree add_left(self, TraceTree sub_tree)
    cpdef TraceTree add_right(self, TraceTree sub_tree)

    cpdef TraceTree remove_left(self)
    cpdef TraceTree remove_right(self)

    cpdef trim_at_nodes(self, nodes, bint include_opposite=?)

    ### Tree searching ###

    cdef _get_all_nodes(self, OrderedSet nodes)
    cpdef OrderedSet get_all_nodes(self)

    cpdef bint contains(self, object o) noexcept
    cdef bint _contains_tree(self, TraceTree tree) noexcept
    cdef bint _contains_node(self, object node) noexcept
    cdef bint _contains_space(self, object space) noexcept
    cdef bint _contains_comp(self, object comp) noexcept
    cpdef TraceTree find_tree_at_node(self, object node, bint include_opposite=?)

    ### Retrieving specific nodes, couplings etc. ###

    cdef _get_last_input_nodes(self, list last_nodes)
    cpdef list get_last_input_nodes(self)

    cpdef TraceTree get_last_left_branch(self)

    cdef __append_mirror_refl_coupling(self, list couplings)
    cdef _get_mirror_refl_couplings(self, list couplings)
    cpdef list get_mirror_reflection_couplings(self)

    ### Changing geometric parameter tree algorithms ###

    cpdef bint is_changing(self, bint recursive=?) noexcept
    cdef _get_broadest_changing_subtrees(self, list trees)
    cpdef list get_broadest_changing_subtrees(self)

    ### Drawing trees ###

    cdef _draw_tree(self, unicode lpad, list lines)
    cpdef draw(self, unicode left_pad=?)

    ### Propagating beams ###

    cdef void c_compute_rt_abcd(self, double* abcdx, double* abcdy) noexcept
    cpdef compute_rt_abcd(self, double[:, ::1] abcdx=?, double[:, ::1] abcdy=?)

    cpdef dict trace_beam(self, double lambda0, bint symmetric)
    cpdef propagate(self, dict trace, double lambda0, bint symmetric)


cdef bint is_surface_refl(comp, parent_node, sub_node) noexcept
