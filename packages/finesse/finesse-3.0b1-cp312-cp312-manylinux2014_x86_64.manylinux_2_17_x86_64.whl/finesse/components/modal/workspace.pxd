from finesse.components.workspace cimport ConnectorWorkspace
from finesse.knm cimport knm_bh_workspace
from finesse.knm.maps cimport Map, knm_map_workspace
from finesse.simulations.base cimport NodeBeamParam
from finesse.cymath.complex cimport complex_t, DenseZMatrix
from cpython.ref cimport PyObject
from finesse.parameter cimport Parameter
import numpy as np
cimport numpy as np

cdef struct KnmInfo:
    PyObject *ptr_owner
    bint has_been_set # False if component has not set the info for it
    int from_port_idx
    int to_port_idx
    bint is_transmission
    DenseZMatrix *knm_mtx # where final Knm calculations is stored for this connection
    # Refractive indices of adjacent spaces
    double nr_from
    double nr_to
    # C-contiguous ABCD matrix views for this connection: assumes it is a 2x2!!
    double* abcd_x
    double* abcd_y
    # references to the Knm workspaces this information is associated with
    bint use_bh
    knm_bh_workspace *K_ws_x
    knm_bh_workspace *K_ws_y
    DenseZMatrix *bh_mtx # where to store BH calculations
    # misalignment information
    double *beta_x
    double *beta_y
    double *alpha
    double beta_y_factor
    double beta_x_factor
    bint alpha_is_changing
    bint beta_x_is_changing
    bint beta_y_is_changing

    # Pointer to bayerhelms scatter matrix function to use
    # -> see end of set_knm_info definition for details
    void (*bhelms_mtx_func)(
        const knm_bh_workspace*,
        const knm_bh_workspace*,
        const int*,
        complex_t*,
        Py_ssize_t,
        int,
    )
    # Pointer to buffer of knm loss data
    double* loss
    # Map info
    knm_map_workspace map_ws
    bint use_map
    bint map_fliplr
    double map_phase_factor
    DenseZMatrix *map_mtx # where to store map calculations


cdef class KnmConnectorWorkspace(ConnectorWorkspace):
    cdef:
        readonly dict o2o # dict[str, (node, node)] for optical connections
        Py_ssize_t* onode_ids # An array of input, output ordered node ids for each port in index order
        Py_ssize_t* trace_node_indices # An array of input, output ordered indices to access the simulation trace
        knm_bh_workspace* Kws # Array of workspaces for calculating Knm matricies
        double[::1] total_losses  # Temporary array used during loss-induced quantum noise calculations
        int N_opt_ports
        int N_opt_conns
        KnmInfo *oconn_info
        list __knm_matrices # store references to KnmMatrices used

    cdef initialise_knm_workspaces(KnmConnectorWorkspace self)
    cdef void update_changing_knm_workspaces(KnmConnectorWorkspace self) noexcept
    cdef void compute_scattering_matrices(KnmConnectorWorkspace self) noexcept
    cdef void compute_knm_losses(KnmConnectorWorkspace self) noexcept nogil

    cpdef set_knm_info(
        self,
        connection,
        double[:,::1] abcd_x = ?,
        double[:,::1] abcd_y = ?,
        double nr_from=?, double nr_to=?,
        bint is_transmission=?,
        Parameter beta_x = ?,
        double beta_x_factor = ?,
        Parameter beta_y = ?,
        double beta_y_factor = ?,
        Parameter alpha = ?,
        Map apply_map = ?,
        double map_phase_factor = ?,
        bint map_fliplr = ?
    )
