from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj, cexp
from finesse.simulations.base cimport ModelSettings
from finesse.frequency cimport frequency_info_t
from finesse.simulations.simulation cimport BaseSimulation
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.simulations.workspace cimport GouyFuncWrapper
from finesse.element_workspace cimport BaseCValues

import numpy as np
cimport numpy as np
from cpython.ref cimport PyObject

cdef struct laser_connections:
    # 1D array of SubCCSViews
    PyObject*** SIGPWR_P1o
    PyObject*** SIGAMP_P1o
    PyObject*** SIGFRQ_P1o
    PyObject*** SIGPHS_P1o
    PyObject*** dz_P1o
    PyObject*** dx_P1o
    PyObject*** dy_P1o
    PyObject*** xbeta_P1o
    PyObject*** ybeta_P1o

cdef class LaserConnections:
    cdef public:
        int SIGPWR_P1o_idx
        int SIGAMP_P1o_idx
        int SIGFRQ_P1o_idx
        int SIGPHS_P1o_idx
        int dz_P1o_idx
        int dx_P1o_idx
        int dy_P1o_idx
        int ybeta_P1o_idx
        int xbeta_P1o_idx

    cdef readonly:
        SubCCSView2DArray SIGPWR_P1o
        SubCCSView2DArray SIGAMP_P1o
        SubCCSView2DArray SIGFRQ_P1o
        SubCCSView2DArray SIGPHS_P1o
        SubCCSView2DArray dz_P1o
        SubCCSView2DArray dx_P1o
        SubCCSView2DArray dy_P1o
        SubCCSView2DArray xbeta_P1o
        SubCCSView2DArray ybeta_P1o
    cdef:
        laser_connections ptrs

cdef class LaserValues(BaseCValues):
    cdef public:
        double P
        double phase
        double f
        bint signals_only


cdef class LaserWorkspace(ConnectorWorkspace):
    cdef public:
        Py_ssize_t fsrc_car_idx
        Py_ssize_t fcar_sig_sb_idx[2]
        complex_t[::1] power_coeffs # length sim.model_settings.num_HOMs
        complex_t[::1] hom_vector   # length sim.model_settings.num_HOMs
        complex_t[::1] phase_vector # length sim.model_settings.num_HOMs
        Py_ssize_t node_car_id, node_sig_id
        LaserValues cvalues
        LaserConnections lc
        complex_t PIj_2
        Py_ssize_t P1o_id
        KnmMatrix K_yaw_sig, K_pitch_sig
        bint add_gouy_phase


cdef object c_laser_carrier_fill_rhs(ConnectorWorkspace cws)
