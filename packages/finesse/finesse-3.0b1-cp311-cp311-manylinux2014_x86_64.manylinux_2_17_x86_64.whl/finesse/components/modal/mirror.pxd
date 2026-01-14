from finesse.frequency cimport frequency_info_t
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.cymath cimport complex_t
from finesse.simulations.base cimport ModelSettings, NodeBeamParam
from finesse.element_workspace cimport BaseCValues
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.components.modal.workspace cimport KnmConnectorWorkspace

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

cdef class MirrorValues(BaseCValues):
    cdef public:
        double R
        double T
        double L
        double phi
        double Rcx
        double Rcy
        double xbeta
        double ybeta
        double misaligned

cdef struct PyObject1DArray:
    PyObject** ptr
    Py_ssize_t size

cdef struct PyObject2DArray:
    PyObject*** ptr
    Py_ssize_t size1
    Py_ssize_t size2

cdef struct mirror_optical_connections:
    PyObject** P1i_P1o
    PyObject** P1i_P2o
    PyObject** P2i_P1o
    PyObject** P2i_P2o

cdef struct mirror_signal_connections:
    PyObject*** P1i_Fz
    PyObject*** P1o_Fz
    PyObject*** P2i_Fz
    PyObject*** P2o_Fz
    PyObject*** P1i_Fyaw
    PyObject*** P1o_Fyaw
    PyObject*** P2i_Fyaw
    PyObject*** P2o_Fyaw
    PyObject*** P1i_Fpitch
    PyObject*** P1o_Fpitch
    PyObject*** P2i_Fpitch
    PyObject*** P2o_Fpitch
    PyObject*** Z_P1o
    PyObject*** Z_P2o
    PyObject*** yaw_P1o
    PyObject*** yaw_P2o
    PyObject*** pitch_P1o
    PyObject*** pitch_P2o

cdef class MirrorOpticalConnections:
    cdef public:
        int P1i_P1o_idx
        int P2i_P2o_idx
        int P1i_P2o_idx
        int P2i_P1o_idx

    cdef readonly:
        SubCCSView1DArray P1i_P1o
        SubCCSView1DArray P2i_P2o
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
    cdef:
        mirror_optical_connections opt_conn_ptrs

cdef class MirrorSignalConnections(MirrorOpticalConnections):
    cdef public:
        int P1i_Fz_idx, P2i_Fz_idx, P1o_Fz_idx, P2o_Fz_idx
        int P1i_Fyaw_idx, P2i_Fyaw_idx, P1o_Fyaw_idx, P2o_Fyaw_idx
        int P1i_Fpitch_idx, P2i_Fpitch_idx, P1o_Fpitch_idx, P2o_Fpitch_idx
        int Z_P1o_idx, Z_P2o_idx, yaw_P1o_idx, yaw_P2o_idx, pitch_P1o_idx, pitch_P2o_idx

    cdef readonly:
        SubCCSView2DArray P1i_Fz
        SubCCSView2DArray P1o_Fz
        SubCCSView2DArray P2i_Fz
        SubCCSView2DArray P2o_Fz
        SubCCSView2DArray P1i_Fyaw
        SubCCSView2DArray P1o_Fyaw
        SubCCSView2DArray P2i_Fyaw
        SubCCSView2DArray P2o_Fyaw
        SubCCSView2DArray P1i_Fpitch
        SubCCSView2DArray P1o_Fpitch
        SubCCSView2DArray P2i_Fpitch
        SubCCSView2DArray P2o_Fpitch
        SubCCSView2DArray Z_P1o
        SubCCSView2DArray Z_P2o
        SubCCSView2DArray yaw_P1o
        SubCCSView2DArray yaw_P2o
        SubCCSView2DArray pitch_P1o
        SubCCSView2DArray pitch_P2o
    cdef:
        mirror_signal_connections sig_conn_ptrs

cdef class MirrorWorkspace(KnmConnectorWorkspace):
    cdef public:
        complex_t field_to_F
        complex_t z_to_field
        bint imaginary_transmission

        # Complete scattering matrices for each propagation direction
        KnmMatrix K11
        KnmMatrix K12
        KnmMatrix K21
        KnmMatrix K22

        KnmMatrix K_yaw_sig, K_pitch_sig

        # NOTE (sjr) The above should remain as the full scattering matrices
        #            (i.e. composite over each scattering type) whilst extra
        #            KnmMatrix objects should be stored here for the different
        #            types (i.e. K11_map, K11_aperture, etc.)

        # Arrays of scattering losses for each mode coupling
        double[::1] K11_loss
        double[::1] K12_loss
        double[::1] K21_loss
        double[::1] K22_loss

        # Node indices for the carrier simulation
        Py_ssize_t car_p1i_idx, car_p1o_idx
        Py_ssize_t car_p2i_idx, car_p2o_idx

        Py_ssize_t car_p1o_rhs_idx, car_p1i_rhs_idx
        Py_ssize_t car_p2o_rhs_idx, car_p2i_rhs_idx
        Py_ssize_t car_p_num_hom

        # Refractive indices of adjacent spaces
        double nr1
        double nr2

        # ABCD matrix views
        # -> reflection
        double[:, ::1] abcd_p1p1_x
        double[:, ::1] abcd_p1p1_y
        double[:, ::1] abcd_p2p2_x
        double[:, ::1] abcd_p2p2_y
        # -> transmission
        double[:, ::1] abcd_p1p2_x
        double[:, ::1] abcd_p1p2_y
        double[:, ::1] abcd_p2p1_x
        double[:, ::1] abcd_p2p1_y
    cdef:
        MirrorValues mv
        MirrorOpticalConnections mcc
        MirrorValues cvalues
        MirrorSignalConnections mcs
        bint z_signal_enabled, yaw_signal_enabled, pitch_signal_enabled

        # Indices (in sim._c_node_info and sim.trace) of nodes
        Py_ssize_t P1i_id
        Py_ssize_t P1o_id
        Py_ssize_t P2i_id
        Py_ssize_t P2o_id

        # Only elements C of ABCD matrices can change, store pointers
        # to compiled changing expression for these elements here
        # -> size 8 as there are 8 different coupling, plane combos
        # -> order of these corresponds exactly to order of matrix views above
        cy_expr* sym_abcd_Cs[8]

        # Direct pointer access to C element of each ABCD matrix for
        # convenience in updating
        double* abcd_Cs[8]

        frequency_info_t *z_mech_freqs
        Py_ssize_t z_mech_freqs_size
        frequency_info_t *yaw_mech_freqs
        Py_ssize_t yaw_mech_freqs_size
        frequency_info_t *pitch_mech_freqs
        Py_ssize_t pitch_mech_freqs_size

    cpdef update_parameter_values(self)
