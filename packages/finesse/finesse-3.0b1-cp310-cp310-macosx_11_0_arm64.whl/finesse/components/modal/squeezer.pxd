from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView2DArray
from finesse.cymath.complex cimport complex_t
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.element_workspace cimport BaseCValues
from finesse.cymath.complex cimport DenseZVector

import numpy as np
cimport numpy as np
from cpython.ref cimport PyObject

cdef struct squeezer_noise_sources:
    # 2D array of SubCCSViews
    PyObject*** P1o

cdef struct squeezer_connections:
    # 1D array of SubCCSViews
    PyObject*** UPPER_P1o
    PyObject*** LOWER_P1o

cdef class SqueezerConnections:
    cdef public:
        int UPPER_P1o_idx
        int LOWER_P1o_idx
    cdef readonly:
        SubCCSView2DArray UPPER_P1o
        SubCCSView2DArray LOWER_P1o
    cdef:
        squeezer_connections ptrs


cdef class SqueezerNoiseSources:
    cdef readonly:
        SubCCSView2DArray P1o
    cdef:
        squeezer_noise_sources ptrs


cdef class SqueezerValues(BaseCValues):
    cdef public:
        double db
        double angle
        double f


cdef class SqueezerWorkspace(ConnectorWorkspace):
    cdef public:
        Py_ssize_t fsrc_car_idx
        Py_ssize_t fcar_sig_sb_idx[2]
        Py_ssize_t node_id
        SqueezerValues v
        SqueezerNoiseSources ns
        complex_t[:, ::1] qn_coeffs
        complex_t[::1] qn_coeffs_diag
        complex_t[::1] hom_vector
        SqueezerConnections conns
    cdef:
        DenseZVector c_p1_o


cdef object c_squeezer_fill_rhs(ConnectorWorkspace cws)
