from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.element_workspace cimport BaseCValues
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView2DArray
from finesse.knm cimport KnmMatrix
from finesse.simulations.base cimport ModelSettings
from finesse.frequency cimport frequency_info_t
from finesse.components.modal.workspace cimport KnmConnectorWorkspace
from finesse.cymath cimport complex_t
from cpython.ref cimport PyObject
from numpy cimport ndarray
import numpy as np
cimport numpy as np
from finesse.enums cimport ModulatorType


cdef struct modulator_coupling_order:
    Py_ssize_t f1_index
    Py_ssize_t f2_index
    Py_ssize_t order_index
    int order


cdef class ModulatorValues(BaseCValues):
    cdef public:
        double f
        double midx
        double phase
        int mod_type
        int order
        bint positive_only

cdef struct modulator_optical_connections:
    # Couples frequencies
    PyObject*** P1i_P2o
    PyObject*** P2i_P1o

cdef struct modulator_signal_connections:
    # Couples frequencies
    PyObject*** amp_P1o
    PyObject*** amp_P2o
    PyObject*** phs_P1o
    PyObject*** phs_P2o

cdef class ModulatorOpticalConnections:
    cdef public:
        int P1i_P2o_idx
        int P2i_P1o_idx

    cdef readonly:
        SubCCSView2DArray P1i_P2o
        SubCCSView2DArray P2i_P1o
    cdef:
        modulator_optical_connections opt_conn_ptrs


cdef class ModulatorSignalConnections(ModulatorOpticalConnections):
    cdef public:
        int amp_P1o_idx
        int phs_P1o_idx
        int amp_P2o_idx
        int phs_P2o_idx

    cdef readonly:
        SubCCSView2DArray amp_P1o
        SubCCSView2DArray amp_P2o
        SubCCSView2DArray phs_P1o
        SubCCSView2DArray phs_P2o
    cdef:
        modulator_signal_connections sig_conn_ptrs


cdef class ModulatorWorkspace(KnmConnectorWorkspace):
    cdef public:
        # Complete scattering matrices for each propagation direction
        KnmMatrix K12
        KnmMatrix K21

        # Arrays of scattering losses for each mode coupling
        double[::1] K12_loss
        double[::1] K21_loss

        # Refractive indices of adjacent spaces
        double nr1
        double nr2

    cdef readonly:
        dict carrier_frequency_couplings
        dict signal_frequency_couplings
        bint amp_signal_enabled
        bint phs_signal_enabled
    cdef:
        int N_orders
        ndarray orders
        ndarray amps
        ndarray phases
        ndarray factors_12
        ndarray factors_21
        modulator_coupling_order* sig_coupling_orders
        modulator_coupling_order* car_coupling_orders
        Py_ssize_t N_sig_coupling_orders
        Py_ssize_t N_car_coupling_orders
        bint* increment_sig
        ModulatorValues cvalues
        ModulatorOpticalConnections mcc
        ModulatorSignalConnections mcs
        complex_t[:, ::1] eye  # nhom x nhom diagonal matrix for noise coupling filling

    cpdef fill_quantum_matrix(self)
