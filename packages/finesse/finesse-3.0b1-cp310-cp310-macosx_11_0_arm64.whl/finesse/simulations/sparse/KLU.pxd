from .solver cimport SparseSolver

cdef class KLUSolver(SparseSolver):
    """
    This extends the BaseSolver for using the KLU (Suitesparse) library for solving
    linear sparse systems of equations. It sets the _M member to a :class:`KLUMatrix`.
    """
    cdef double prev_rcond
    cdef double rcond_diff_lim

    cpdef double rcond(self) noexcept
    cpdef double condest(self) noexcept
    cpdef double rgrowth(self) noexcept
