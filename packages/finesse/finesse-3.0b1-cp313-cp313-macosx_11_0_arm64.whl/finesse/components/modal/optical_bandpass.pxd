from finesse.frequency cimport frequency_info_t
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.cymath cimport complex_t
from finesse.simulations.base cimport ModelSettings, NodeBeamParam
from finesse.element_workspace cimport BaseCValues
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.components.modal.workspace cimport KnmConnectorWorkspace
from cpython.ref cimport PyObject

import numpy as np
cimport numpy as np


cdef class OpticalBandpassValues(BaseCValues):
    cdef public:
        double fc
        double bandwidth


cdef struct optical_bandpass_connections:
    PyObject** P1i_P2o
    PyObject** P2i_P1o


cdef class OpticalBandpassConnections:
    cdef public:
        int P1i_P2o_idx
        int P2i_P1o_idx

    cdef readonly:
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
    cdef:
        optical_bandpass_connections ptrs


cdef class OpticalBandpassWorkspace(KnmConnectorWorkspace):
    cdef public:
        KnmMatrix K12
        KnmMatrix K21
        double[::1] K12_loss
        double[::1] K21_loss
        complex_t[:, ::1] M # HOM transmission matrix
        double nr1
        double nr2
    cdef:
        OpticalBandpassValues cvalues
        OpticalBandpassConnections signal_opt_conns
        OpticalBandpassConnections carrier_opt_conns
