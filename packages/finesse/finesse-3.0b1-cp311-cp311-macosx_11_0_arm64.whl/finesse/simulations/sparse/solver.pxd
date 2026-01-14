from finesse.cymath.cmatrix cimport CCSMatrix
from ..homsolver cimport HOMSolver
from finesse.cymath cimport complex_t

cdef class SparseSolver(HOMSolver):
    """
    This class represents a sparse solver for a given system. It inherits from
    HOMSolver.

    Attributes
    ----------
    _M : CCSMatrix
        The compressed column sparse matrix representing the system
    """
    cdef:
        readonly CCSMatrix _M
