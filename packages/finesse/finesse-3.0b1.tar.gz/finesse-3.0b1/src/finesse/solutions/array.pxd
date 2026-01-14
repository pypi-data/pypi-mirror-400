from finesse.solutions.base import BaseSolution
from finesse.solutions.base cimport BaseSolution
from cpython.ref cimport PyObject

import numpy as np
cimport numpy as np


cdef class ArraySolution(BaseSolution):
    cdef:
        readonly dict trace_info
        readonly dict axis_info
        readonly np.ndarray _data
        readonly np.dtype dtype
        readonly int _axes
        readonly int _num
        readonly tuple shape
        readonly tuple x
        readonly tuple params
        readonly tuple detectors
        readonly bint masked
        PyObject** workspaces
        Py_ssize_t num_workspaces
        bint enabled
        readonly np.ndarray flatiters

    cpdef int update(self, int index, bint mask) except -1
    cpdef enable_update(self, detector_workspaces)
