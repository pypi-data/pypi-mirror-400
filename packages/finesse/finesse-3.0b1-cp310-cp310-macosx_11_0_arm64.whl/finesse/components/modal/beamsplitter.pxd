from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.cymath cimport complex_t
from finesse.simulations.base cimport ModelSettings, NodeBeamParam
from finesse.frequency cimport frequency_info_t
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver
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


cdef struct bs_optical_connections:
    PyObject** P1i_P2o
    PyObject** P2i_P1o
    PyObject** P3i_P4o
    PyObject** P4i_P3o
    PyObject** P1i_P3o
    PyObject** P3i_P1o
    PyObject** P2i_P4o
    PyObject** P4i_P2o


cdef struct bs_signal_connections:
    PyObject*** P1i_Fz
    PyObject*** P1o_Fz
    PyObject*** P2i_Fz
    PyObject*** P2o_Fz
    PyObject*** P3i_Fz
    PyObject*** P3o_Fz
    PyObject*** P4i_Fz
    PyObject*** P4o_Fz
    PyObject*** Z_P1o
    PyObject*** Z_P2o
    PyObject*** Z_P3o
    PyObject*** Z_P4o

    PyObject*** P1i_Fyaw
    PyObject*** P1o_Fyaw
    PyObject*** P2i_Fyaw
    PyObject*** P2o_Fyaw
    PyObject*** P3i_Fyaw
    PyObject*** P3o_Fyaw
    PyObject*** P4i_Fyaw
    PyObject*** P4o_Fyaw
    PyObject*** yaw_P1o
    PyObject*** yaw_P2o
    PyObject*** yaw_P3o
    PyObject*** yaw_P4o

    PyObject*** P1i_Fpitch
    PyObject*** P1o_Fpitch
    PyObject*** P2i_Fpitch
    PyObject*** P2o_Fpitch
    PyObject*** P3i_Fpitch
    PyObject*** P3o_Fpitch
    PyObject*** P4i_Fpitch
    PyObject*** P4o_Fpitch
    PyObject*** pitch_P1o
    PyObject*** pitch_P2o
    PyObject*** pitch_P3o
    PyObject*** pitch_P4o

cdef class BeamsplitterOpticalConnections:
    cdef public:
        Py_ssize_t P1i_P2o_idx
        Py_ssize_t P2i_P1o_idx
        Py_ssize_t P3i_P4o_idx
        Py_ssize_t P4i_P3o_idx
        Py_ssize_t P1i_P3o_idx
        Py_ssize_t P3i_P1o_idx
        Py_ssize_t P2i_P4o_idx
        Py_ssize_t P4i_P2o_idx
    cdef readonly:
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
        SubCCSView1DArray P3i_P4o
        SubCCSView1DArray P4i_P3o
        SubCCSView1DArray P1i_P3o
        SubCCSView1DArray P3i_P1o
        SubCCSView1DArray P2i_P4o
        SubCCSView1DArray P4i_P2o
    cdef:
        bs_optical_connections opt_conn_ptrs


cdef class BeamsplitterSignalConnections(BeamsplitterOpticalConnections):
    cdef public:
        Py_ssize_t P1i_Fz_idx
        Py_ssize_t P1o_Fz_idx
        Py_ssize_t P2i_Fz_idx
        Py_ssize_t P2o_Fz_idx
        Py_ssize_t P3i_Fz_idx
        Py_ssize_t P3o_Fz_idx
        Py_ssize_t P4i_Fz_idx
        Py_ssize_t P4o_Fz_idx
        Py_ssize_t Z_P1o_idx
        Py_ssize_t Z_P2o_idx
        Py_ssize_t Z_P3o_idx
        Py_ssize_t Z_P4o_idx

        Py_ssize_t P1i_Fyaw_idx
        Py_ssize_t P1o_Fyaw_idx
        Py_ssize_t P2i_Fyaw_idx
        Py_ssize_t P2o_Fyaw_idx
        Py_ssize_t P3i_Fyaw_idx
        Py_ssize_t P3o_Fyaw_idx
        Py_ssize_t P4i_Fyaw_idx
        Py_ssize_t P4o_Fyaw_idx
        Py_ssize_t yaw_P1o_idx
        Py_ssize_t yaw_P2o_idx
        Py_ssize_t yaw_P3o_idx
        Py_ssize_t yaw_P4o_idx

        Py_ssize_t P1i_Fpitch_idx
        Py_ssize_t P1o_Fpitch_idx
        Py_ssize_t P2i_Fpitch_idx
        Py_ssize_t P2o_Fpitch_idx
        Py_ssize_t P3i_Fpitch_idx
        Py_ssize_t P3o_Fpitch_idx
        Py_ssize_t P4i_Fpitch_idx
        Py_ssize_t P4o_Fpitch_idx
        Py_ssize_t pitch_P1o_idx
        Py_ssize_t pitch_P2o_idx
        Py_ssize_t pitch_P3o_idx
        Py_ssize_t pitch_P4o_idx
    cdef readonly:
        SubCCSView2DArray P1i_Fz
        SubCCSView2DArray P1o_Fz
        SubCCSView2DArray P2i_Fz
        SubCCSView2DArray P2o_Fz
        SubCCSView2DArray P3i_Fz
        SubCCSView2DArray P3o_Fz
        SubCCSView2DArray P4i_Fz
        SubCCSView2DArray P4o_Fz
        SubCCSView2DArray Z_P1o
        SubCCSView2DArray Z_P2o
        SubCCSView2DArray Z_P3o
        SubCCSView2DArray Z_P4o

        SubCCSView2DArray P1i_Fyaw
        SubCCSView2DArray P1o_Fyaw
        SubCCSView2DArray P2i_Fyaw
        SubCCSView2DArray P2o_Fyaw
        SubCCSView2DArray P3i_Fyaw
        SubCCSView2DArray P3o_Fyaw
        SubCCSView2DArray P4i_Fyaw
        SubCCSView2DArray P4o_Fyaw
        SubCCSView2DArray yaw_P1o
        SubCCSView2DArray yaw_P2o
        SubCCSView2DArray yaw_P3o
        SubCCSView2DArray yaw_P4o

        SubCCSView2DArray P1i_Fpitch
        SubCCSView2DArray P1o_Fpitch
        SubCCSView2DArray P2i_Fpitch
        SubCCSView2DArray P2o_Fpitch
        SubCCSView2DArray P3i_Fpitch
        SubCCSView2DArray P3o_Fpitch
        SubCCSView2DArray P4i_Fpitch
        SubCCSView2DArray P4o_Fpitch
        SubCCSView2DArray pitch_P1o
        SubCCSView2DArray pitch_P2o
        SubCCSView2DArray pitch_P3o
        SubCCSView2DArray pitch_P4o
    cdef:
        bs_signal_connections sig_conn_ptrs


cdef class BeamsplitterValues(BaseCValues):
    cdef public:
        double R
        double T
        double L
        double phi
        double Rcx
        double Rcy
        double xbeta
        double ybeta
        double alpha
        double plane
        double misaligned


cdef class BeamsplitterWorkspace(KnmConnectorWorkspace):
    cdef public:
        complex_t field1_to_F
        complex_t field2_to_F
        complex_t z_to_field1
        complex_t z_to_field2

        # Complete scattering matrices for each propagation direction
        KnmMatrix K12
        KnmMatrix K21
        KnmMatrix K13
        KnmMatrix K31
        KnmMatrix K24
        KnmMatrix K42
        KnmMatrix K34
        KnmMatrix K43

        KnmMatrix K_yaw_sig, K_pitch_sig

        # NOTE (sjr) The above should remain as the full scattering matrices
        #            (i.e. composite over each scattering type) whilst extra
        #            KnmMatrix objects should be stored here for the different
        #            types (i.e. K12_map, K12_aperture, etc.)

        # Arrays of scattering losses for each mode coupling
        double[::1] K12_loss
        double[::1] K21_loss
        double[::1] K13_loss
        double[::1] K31_loss
        double[::1] K24_loss
        double[::1] K42_loss
        double[::1] K34_loss
        double[::1] K43_loss

        double cos_alpha
        double cos_alpha_2

        # Refractive indices of adjacent spaces
        double nr1
        double nr2

        # Node indices for the carrier simulation
        Py_ssize_t car_p1i_idx, car_p1o_idx
        Py_ssize_t car_p2i_idx, car_p2o_idx
        Py_ssize_t car_p3i_idx, car_p3o_idx
        Py_ssize_t car_p4i_idx, car_p4o_idx

        # Node RHS index location in the carrier simulation
        Py_ssize_t car_p1o_rhs_idx, car_p1i_rhs_idx
        Py_ssize_t car_p2o_rhs_idx, car_p2i_rhs_idx
        Py_ssize_t car_p3o_rhs_idx, car_p3i_rhs_idx
        Py_ssize_t car_p4o_rhs_idx, car_p4i_rhs_idx
        Py_ssize_t car_p_num_hom

        # ABCD matrix views
        # -> reflection
        double[:, ::1] abcd_p1p2_x
        double[:, ::1] abcd_p1p2_y
        double[:, ::1] abcd_p2p1_x
        double[:, ::1] abcd_p2p1_y
        double[:, ::1] abcd_p3p4_x
        double[:, ::1] abcd_p3p4_y
        double[:, ::1] abcd_p4p3_x
        double[:, ::1] abcd_p4p3_y
        # -> transmission
        double[:, ::1] abcd_p1p3_x
        double[:, ::1] abcd_p1p3_y
        double[:, ::1] abcd_p3p1_x
        double[:, ::1] abcd_p3p1_y
        double[:, ::1] abcd_p2p4_x
        double[:, ::1] abcd_p2p4_y
        double[:, ::1] abcd_p4p2_x
        double[:, ::1] abcd_p4p2_y

        bint z_signal_enabled
        bint yaw_signal_enabled
        bint pitch_signal_enabled
        bint imaginary_transmission
    cdef:
        BeamsplitterValues cvalues
        BeamsplitterOpticalConnections boc
        BeamsplitterSignalConnections bsc

        # Indices (in sim._c_node_info and sim.trace) of nodes
        Py_ssize_t P1i_id
        Py_ssize_t P1o_id
        Py_ssize_t P2i_id
        Py_ssize_t P2o_id
        Py_ssize_t P3i_id
        Py_ssize_t P3o_id
        Py_ssize_t P4i_id
        Py_ssize_t P4o_id

        # Changing expressions of each ABCD matrix
        # -> size 16 as there are 16 different coupling, plane combos
        # -> order of these corresponds exactly to order of matrix views above
        # NOTE (sjr) Elements A, C & D can change so we will just store arrays
        #            of pointers for every element here, rather than singling out
        #            each element, for convenience
        cy_expr** sym_abcd_elements[16]

        # Direct pointer access to beginning of contiguous memory chunk of
        # each ABCD matrix for speed and convenience in updating
        double* abcd_elements[16]

        frequency_info_t *z_mech_freqs
        Py_ssize_t z_mech_freqs_size
        frequency_info_t *yaw_mech_freqs
        Py_ssize_t yaw_mech_freqs_size
        frequency_info_t *pitch_mech_freqs
        Py_ssize_t pitch_mech_freqs_size

    cpdef update_parameter_values(self)


cdef object c_beamsplitter_carrier_fill(ConnectorWorkspace cws)
cdef object c_beamsplitter_signal_fill(ConnectorWorkspace cws)
