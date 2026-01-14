from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.cymath cimport complex_t
from finesse.simulations.base cimport ModelSettings
from finesse.frequency cimport frequency_info_t
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.simulations.workspace cimport GouyFuncWrapper
from finesse.element_workspace cimport BaseCValues

from finesse.cyexpr cimport (
    cy_expr,
    cy_expr_new,
    cy_expr_init,
    cy_expr_free,
    cy_expr_eval,
)

from cpython.ref cimport PyObject

import numpy as np
cimport numpy as np


cdef struct space_optical_connections:
    PyObject** P1i_P2o
    PyObject** P2i_P1o


cdef struct space_signal_connections:
    PyObject*** SIGAMP_P1o
    PyObject*** SIGAMP_P2o
    PyObject*** SIGPHS_P1o
    PyObject*** SIGPHS_P2o
    PyObject*** H_P1o
    PyObject*** H_P2o


cdef class SpaceOpticalConnections:
    cdef public:
        int P1i_P2o_idx
        int P2i_P1o_idx
    cdef readonly:
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
    cdef:
        space_optical_connections opt_ptrs


cdef class SpaceSignalConnections(SpaceOpticalConnections):
    cdef public:
        int SIGPHS_P1o_idx
        int SIGPHS_P2o_idx
        int SIGAMP_P1o_idx
        int SIGAMP_P2o_idx
        int H_P1o_idx
        int H_P2o_idx
    cdef readonly:
        SubCCSView2DArray SIGPHS_P1o
        SubCCSView2DArray SIGPHS_P2o
        SubCCSView2DArray SIGAMP_P1o
        SubCCSView2DArray SIGAMP_P2o
        SubCCSView2DArray H_P1o
        SubCCSView2DArray H_P2o
    cdef:
        space_signal_connections sig_ptrs


cdef class SpaceValues(BaseCValues):
    cdef public:
        double L
        double nr

        # Holds user and bt gouy values
        double user_gouy_x
        double user_gouy_y
        double computed_gouy_x
        double computed_gouy_y


cdef class SpaceWorkspace(ConnectorWorkspace):
    cdef public:
        # Indices (in sim._c_node_info and sim.trace) of nodes
        Py_ssize_t P1i_id
        Py_ssize_t P1o_id
        Py_ssize_t P2i_id
        Py_ssize_t P2o_id

        Py_ssize_t car_p1o_idx
        Py_ssize_t car_p2o_idx

        # ABCD matrix view (note same for all couplings)
        double[:, ::1] abcd

        # Flags to use user or bt gouy phase
        bint use_user_gouy_x
        bint use_user_gouy_y
    cdef:
        SpaceOpticalConnections sco
        SpaceSignalConnections scs
        SpaceValues sv

        # Only element B of ABCD matrix can change, store pointer
        # to compiled changing expression for this element here
        cy_expr* sym_abcd_B
        complex_t* couplings

        Py_ssize_t car_p1o_rhs_idx
        Py_ssize_t car_p2o_rhs_idx
        Py_ssize_t car_p_num_hom
        bint strain_signal_enabled
        bint phase_signal_enabled
        bint amp_signal_enabled

    cpdef update_parameter_values(self)


cdef object c_space_carrier_fill(ConnectorWorkspace cws)
cdef void space_fill_optical_2_optical(
        space_optical_connections *conn,
        SpaceWorkspace ws,
        frequency_info_t *freq,
        double pre_factor,
        double gouy_x,
        double gouy_y,
        bint zero_tem00_gouy,
        int[:, ::1] homs_view
    ) noexcept
