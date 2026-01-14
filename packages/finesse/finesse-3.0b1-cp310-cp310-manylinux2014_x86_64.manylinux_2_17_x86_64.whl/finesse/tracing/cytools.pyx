#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Internal Cythonised tools for performing the calculations required by each
function in :mod:`.tracing.tools`.

Note that the functions documented here are typically only to be used as
a developer reference. Users should instead refer to :mod:`.tracing.tools`
for the Python functions which provide beam propagation tools which return
useful solution objects.
"""

cimport numpy as np
import numpy as np

from finesse.cymath cimport complex_t
from finesse.cymath.math cimport degrees
from finesse.cymath.gaussbeam cimport (
    transform_q,
    abcd_multiply,
    gouy,
)
from finesse.tracing.tree cimport TraceTree
from finesse.symbols import eval_symbolic_numpy, simplify_symbolic_numpy, simplification
from finesse.gaussian import transform_beam_param
from finesse.utilities import refractive_index # For getting symbolic nr at a node

### Composite ABCD matrices ###


cpdef np.ndarray[double, ndim=2] compute_numeric_abcd(TraceTree last_branch, unicode direction):
    cdef:
        np.ndarray[double, ndim=2] M = np.eye(2)
        double[:, ::1] M_view = M

        bint is_x_plane = direction == "x"

        TraceTree t = last_branch.parent

    while t is not None:
        if is_x_plane:
            abcd_multiply(
                M_view, t.left_abcd_x, out=M_view,
            )
        else:
            abcd_multiply(
                M_view, t.left_abcd_y, out=M_view,
            )

        t = t.parent

    return M

def extract_symbols_to_keep(symbols):
    return tuple(s if isinstance(s, str) else s.full_name for s in symbols)

cpdef np.ndarray[object, ndim=2] compute_symbolic_abcd(
    TraceTree last_branch,
    unicode direction,
    bint simplify,
    tuple symbols_to_keep=None,
):
    cdef:
        np.ndarray[object, ndim=2] M = np.eye(2, dtype=object)
        object[:, ::1] M2

        bint is_x_plane = direction == "x"

        TraceTree t = last_branch.parent

    if symbols_to_keep is not None:
        symbols_to_keep = extract_symbols_to_keep(symbols_to_keep)

    while t is not None:
        if is_x_plane:
            M2 = t.sym_left_abcd_x
        else:
            M2 = t.sym_left_abcd_y

        if symbols_to_keep is not None:
            M2 = eval_symbolic_numpy(M2, *symbols_to_keep)

        np.matmul(M, M2, out=M)
        if simplify:
            M = simplify_symbolic_numpy(M)

        if t.is_left_surf_refl:
            np.multiply(M, -1, out=M)

        t = t.parent
    return M


### Accumulated Gouy phases ###


cpdef double compute_numeric_acc_gouy(
    TraceTree t,
    complex_t q_in,
    unicode direction,
    bint deg=True,
) noexcept:
    cdef:
        # Total accumulated Gouy phase
        double agouy = 0.0
        # Gouy phase at start, end of a space
        double gouy_start = 0.0
        double gouy_end = 0.0
        # Beam parameter at current node
        complex_t q = q_in

        bint is_x_plane = direction == "x"

    if t is None:
        return agouy

    if t.node.is_input:
        if t.left is None:
            return agouy

        if is_x_plane:
            q = transform_q(t.left_abcd_x, q, t.nr, t.left.nr)
        else:
            q = transform_q(t.left_abcd_y, q, t.nr, t.left.nr)

        t = t.left

    while t is not None:
        if t.node.is_input:
            gouy_end = gouy(q)

            agouy += gouy_end - gouy_start
        else:
            gouy_start = gouy(q)

        if t.left is not None:
            if is_x_plane:
                q = transform_q(t.left_abcd_x, q, t.nr, t.left.nr)
            else:
                q = transform_q(t.left_abcd_y, q, t.nr, t.left.nr)

        t = t.left

    if deg:
        return degrees(agouy)

    return agouy

cpdef object compute_symbolic_acc_gouy(
    TraceTree t,
    object q_in,
    unicode direction,
    bint deg=True,
) :
    cdef:
        # Total accumulated Gouy phase
        object agouy = 0.0
        # Gouy phase at start, end of a space
        object gouy_start = 0.0
        object gouy_end = 0.0
        # Beam parameter at current node
        object q = q_in

        bint is_x_plane = direction == "x"

    if t is None:
        return agouy

    if t.node.is_input:
        if t.left is None:
            return agouy

        if is_x_plane:
            q = transform_beam_param(t.sym_left_abcd_x.base, q, t.nr, t.left.nr)
        else:
            q = transform_beam_param(t.sym_left_abcd_y.base, q, t.nr, t.left.nr)

        t = t.left

    while t is not None:
        if t.node.is_input:
            gouy_end = q.gouy()

            agouy += gouy_end - gouy_start
        else:
            gouy_start = q.gouy()

        if t.left is not None:
            if is_x_plane:
                q = transform_beam_param(t.sym_left_abcd_x.base, q, t.nr, t.left.nr)
            else:
                q = transform_beam_param(t.sym_left_abcd_y.base, q, t.nr, t.left.nr)

        t = t.left

    if deg:
        return np.degrees(agouy)

    return agouy


### Arbitrary beam propagations ###


cpdef tuple propagate_beam_numeric(
    TraceTree t,
    q_in,
    unicode direction,
) :
    cdef:
        bint is_x_plane = direction == "x"
        object q = q_in
        # Beam parameters for computing Gouy phases over spaces
        complex_t q1, q2

        # Propagated distance (geometric)
        double distance = 0.0
        # Propagated distance (optical)
        double opt_distance = 0.0

        dict node_info = {}
        dict comp_info = {}

        dict info_at_node, info_at_space, info_at_comp

    while t is not None:
        space = t.node.space
        info_at_space = comp_info.get(space, {})
        comp = t.node.component
        info_at_comp = comp_info.get(comp, {})

        if t.node.is_input:
            # Space was traversed so compute the accumulated Gouy over it
            if info_at_space:
                q1 = complex(info_at_space["q_in"])
                q2 = complex(q)

                info_at_space["acc_gouy"] = degrees(gouy(q2) - gouy(q1))

                distance += space.L.value
                opt_distance += space.L.value * t.nr

            info_at_space["q_out"] = q
        else:
            info_at_space["q_in"] = q

        info_at_comp[t.node] = q
        comp_info[comp] = info_at_comp
        comp_info[space] = info_at_space

        info_at_node = {
            "q": q,
            "z": distance,
            "z_optical": opt_distance,
            "ABCD": compute_numeric_abcd(t, direction)
        }
        node_info[t.node] = info_at_node

        if t.left is not None:
            if is_x_plane:
                q = transform_beam_param(t.left_abcd_x.base, q, t.nr, t.left.nr)
            else:
                q = transform_beam_param(t.left_abcd_y.base, q, t.nr, t.left.nr)

        t = t.left

    return node_info, comp_info

def propagate_beam_symbolic(
    TraceTree t,
    q_in,
    unicode direction,
    bint simplify=False,
    tuple symbols_to_keep=None
):
    cdef:
        bint is_x_plane = direction == "x"
        object q = q_in
        # Beam parameters for computing Gouy phases over spaces
        object q1, q2

        # Propagated distance (geometric)
        object distance = 0.0
        # Propagated distance (optical)
        object opt_distance = 0.0

        dict node_info = {}
        dict comp_info = {}

        dict info_at_node, info_at_space, info_at_comp

    # enables low level simplification of some basic symbols, eg. a*a => a**2
    # simplify = True, means symbol.simplify() is called on the final result
    with simplification():
        if symbols_to_keep is not None:
            symbols_to_keep = extract_symbols_to_keep(symbols_to_keep)

        while t is not None:
            space = t.node.space
            info_at_space = comp_info.get(space, {})
            comp = t.node.component
            info_at_comp = comp_info.get(comp, {})

            if t.node.is_input:
                # Space was traversed so compute the accumulated Gouy over it
                if info_at_space:
                    q1 = info_at_space["q_in"]
                    q2 = q

                    info_at_space["acc_gouy"] = np.degrees(q2.gouy() - q1.gouy())

                    distance += space.L.ref
                    opt_distance += space.L.ref * refractive_index(t.node, symbolic=True)

                info_at_space["q_out"] = q
            else:
                info_at_space["q_in"] = q

            info_at_comp[t.node] = q
            comp_info[comp] = info_at_comp
            comp_info[space] = info_at_space

            info_at_node = {
                "q": q,
                "z": distance,
                "z_optical": opt_distance,
                "ABCD": compute_symbolic_abcd(t, direction, simplify, symbols_to_keep)
            }
            node_info[t.node] = info_at_node

            if is_x_plane:
                M = np.asarray(t.sym_left_abcd_x)
            else:
                M = np.asarray(t.sym_left_abcd_y)

            if symbols_to_keep is not None:
                M = eval_symbolic_numpy(M, *symbols_to_keep)

            if t.left is not None:
                q = transform_beam_param(M, q, t.nr, t.left.nr)

            t = t.left

    return node_info, comp_info


### Debugging tools ###

cpdef generate_rt_abcd_str(TraceTree tree) :
    cdef TraceTree t = tree
    src_node = t.node

    # Find the bottom first as round-trip matrix is
    # computed from multiplying each ABCD "upwards"
    # in the internal tree
    while t.left is not None:
        if t.left is None:
            break

        t = t.left

    M_str = f"{t.node.component.name}__{t.node.port.name}_{src_node.port.name} @"
    t = t.parent
    while t is not None:
        if t.node.is_input:
            comp = t.node.component
        else:
            comp = t.node.space

        M_str += f" {comp.name}__{t.left.node.port.name}_{t.node.port.name} "
        if t.parent is not None:
            M_str += "@"

        t = t.parent

    return M_str
