from finesse.cymath.cmatrix cimport SubCCSView2DArray
from finesse.simulations.workspace cimport ABCDWorkspace

from cpython.ref cimport PyObject

ctypedef object (*fptr_c_fill)(ConnectorWorkspace)

cpdef enum ConnectorCallbacks:
    FILL_MATRIX = 1,
    FILL_RHS = 2,
    FILL_NOISE = 4
    FILL_INPUT_NOISE = 8


cpdef enum ConnectionSetting:
    DISABLED = 0,
    DIAGONAL = 1,
    MATRIX = 2

cdef class FillFuncWrapper:
    cdef fptr_c_fill func
    @staticmethod
    cdef FillFuncWrapper make_from_ptr(fptr_c_fill f)

cdef struct node_noise_info:
    Py_ssize_t idx

cdef class NoiseInfo:
    cdef:
        int num_nodes
        SubCCSView2DArray nodes
        node_noise_info* node_info
        PyObject*** ptrs


ctypedef struct fill_info_t:
    # All callables should only take workspace as an argument
    PyObject *fn_py # Python callable
    fptr_c_fill fn_c # C callable
    bint refill


ctypedef struct fill_list_t:
    Py_ssize_t size
    Py_ssize_t num_refills # number of refills being done in this fill list
    fill_info_t[10] infos # 10 for now, can make this more adaptable with realloc if we want


cdef class ConnectorMatrixSimulationInfo:
    cdef:
        readonly object connections
        readonly object noise_sources

        fill_list_t matrix_fills

        FillFuncWrapper fn_rhs_c  # C RHS fill function
        object fn_rhs_py  # Python RHS fill function
        FillFuncWrapper fn_quantum_noise_c  # C noise input fill function
        object fn_quantum_noise_py  # Python noise input fill function
        FillFuncWrapper fn_quantum_noise_input_c  # C noise empty node input fill function
        object fn_quantum_noise_input_py  # Python noise empty node input fill function
        readonly ConnectorCallbacks callback_flag # flag stating which fill methods are to be called
        readonly dict connection_settings


cdef class ConnectorWorkspace(ABCDWorkspace):
    cdef readonly:
        ConnectorMatrixSimulationInfo carrier
        ConnectorMatrixSimulationInfo signal
        NoiseInfo input_noise
        NoiseInfo output_noise

    cdef setup_quantum_noise(self)
