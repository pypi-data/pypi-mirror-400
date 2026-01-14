# cython: profile=False
"""Sparse matrix math tools.
"""

import numpy as np
cimport numpy as np
from libc.stdlib cimport free, calloc
from finesse.cymath.complex cimport conj


cdef class CSRMatrix:
    """A complex value Compressed Sparse Row (CSR) matrix.
    This is a useful format for storing a sparse matrix for
    fast matrix vector products.

    This class wraps the `csr_matrix` structure which is pure C
    and so can be passed to functions that do not need the GIL.

    Parameters
    ----------
    A : np.ndarray[complex, ndim=2]
        A dense matrix to convert into a sparse format
    """
    def __init__(self, np.ndarray[complex, ndim=2] A):
        self.M.rows = A.shape[0]
        self.M.cols = A.shape[1]
        rows, cols = np.nonzero(A)
        self.M.nnz = len(rows)
        self.M.row_ptr = <unsigned int*> calloc(self.M.rows+1, sizeof(unsigned int))
        if not self.M.row_ptr:
            raise MemoryError()
        self.M.col_index = <unsigned int*> calloc(self.M.nnz, sizeof(unsigned int))
        if not self.M.col_index:
            raise MemoryError()
        self.M.values = <complex*> calloc(self.M.nnz, sizeof(complex))
        if not self.M.values:
            raise MemoryError()

        cdef Py_ssize_t i, j = 0
        for i in range(self.M.nnz):
            self.M.col_index[i] = cols[i]
            self.M.values[i] = A[rows[i], cols[i]]

        self.M.row_ptr[self.M.rows] = self.M.nnz
        for i in range(self.M.rows):
            # what does i-th row start?
            self.row_ptr[i] = j
            if i == self.M.rows-1:
                break
            while j < self.M.nnz and rows[j] <= i:
                j += 1

    def __dealloc__(self):
        if self.M.row_ptr:
            free(self.M.row_ptr)
        if self.M.col_index:
            free(self.M.col_index)
        if self.M.values:
            free(self.M.values)

    @property
    def nnz(self):
        """Number of non-zero elements"""
        return self.M.nnz

    @property
    def rows(self):
        """Number of rows in matrix"""
        return self.M.rows

    @property
    def cols(self):
        """Number of columns in matrix"""
        return self.M.cols

    @property
    def row_ptr(self):
        """Index in values and col_index where each row starts"""
        return np.asarray(<unsigned int[:(self.M.rows+1)]>self.M.row_ptr)

    @property
    def col_index(self):
        """Column index for each non-zero element"""
        return np.asarray(<unsigned int[:(self.M.nnz)]>self.M.col_index)

    @property
    def values(self):
        """Sparse matrix non-zero values"""
        return np.asarray(<np.complex128_t[:(self.M.nnz)]>self.M.values)

    def multiply(self, np.ndarray x):
        """Compute y = M @ x"""
        cdef complex[::1] _x = np.ascontiguousarray(x, dtype=complex)
        cdef complex[::1] y = np.zeros(self.M.rows, dtype=complex)
        rtn = zcsrgemv(&self.M, &_x[0], len(x), &y[0], len(y))
        if rtn != 0:
            raise Exception(f"zcsrgemv error {rtn}")
        return np.asarray(y)

    def zcsrgecmv(self, np.ndarray x, np.ndarray y):
        """Complex (z) valued CSR (csr) general (ge) hermitiain conjugate vector (c) matrix (m) vector (v) product.

        .. math::
            z = y^{\\mathrm{H}} \\cdot M \\cdot x

        Parameters
        ----------
        x : array
            1D, size self.cols
        y : array
            1D, size self.rows
        """
        cdef complex[::1] _x = np.ascontiguousarray(x, dtype=complex)
        cdef complex[::1] _y = np.ascontiguousarray(y, dtype=complex)
        cdef complex z
        rtn = zcsrgecmv(&self.M, &_x[0], len(_x), &_y[0], len(_y), &z)
        if rtn != 0:
            raise Exception(f"zcsrgecmv error {rtn}")
        return z

    def zcsrgevmv(self, np.ndarray x, np.ndarray y):
        """Complex (z) valued CSR (csr) general (ge) transpose vector (v) matrix (m) vector (v) product.

        .. math::
            z = y^{\\mathrm{T}} \\cdot M \\cdot x

        Parameters
        ----------
        x : array
            1D, size self.cols
        y : array
            1D, size self.rows
        """
        cdef complex[::1] _x = np.ascontiguousarray(x, dtype=complex)
        cdef complex[::1] _y = np.ascontiguousarray(y, dtype=complex)
        cdef complex z
        rtn = zcsrgevmv(&self.M, &_x[0], len(_x), &_y[0], len(_y), &z)
        if rtn != 0:
            raise Exception(f"zcsrgevmv error {rtn}")
        return z


cdef inline int zcsrgemv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny) noexcept nogil:
    """Complex (z) valued CSR (csr) general (ge) matrix (m) vector (v) product.

    .. math::
        y  = \\mathbf{M} x

    Parameters
    ----------
    M : csr_matrix struct
        CSR matrix
    x : complex*
        Contiguous memory input vector
    nx : integer
        Size of x array - length of input vector, should equal cols
    y : complex*
        Contiguous memory output vector
    ny : integer
        Size of y arrays - length of output vector, should equals rows

    Returns
    -------
    0 on success
    -1 on wrong vector size or M, x, or y are NULL
    """
    cdef Py_ssize_t i, j, nr, row

    if nx != M.cols or ny != M.rows or M == NULL or x == NULL or y == NULL:
        return -1 # wrong size

    for i in range(ny):
        y[i] = 0 # zero output array

    row = 0
    j = 0
    nr = 0 # number of elements in row

    for row in range(M.rows):
        nr = M.row_ptr[row+1]-M.row_ptr[row]
        # iterate over the number of elements in this row
        for i in range(nr):
            # multiply the matrix value by the colum
            y[row] += x[M.col_index[j+i]] * M.values[j+i]
        j += nr
    return 0


cdef inline int zcsrgecmv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny, complex *z) noexcept nogil:
    """Complex (z) valued CSR (csr) general (ge) hermitiain conjugate vector (c) matrix (m) vector (v) product.

    .. math::
        z = y^{\mathrm{H}} \\cdot \\mathbf{M} \\cdot x

    Parameters
    ----------
    M : csr_matrix struct
        CSR matrix
    x : complex*
        Contiguous memory input vector
    nx : integer
        Size of x array - length of input vector, should equal cols
    y : complex*
        Contiguous memory input vector
    ny : integer
        Size of y arrays - length of intput vector, should equals rows
    z : complex*
        Output complex value

    Returns
    -------
    0 on success
    -1 on wrong vector size or M, x, or y are NULL
    """
    cdef Py_ssize_t i, j, nr, row
    cdef complex a

    if nx != M.cols or ny != M.rows or M == NULL or x == NULL or y == NULL or z == NULL:
        return -1 # wrong size

    z[0] = 0 # initialise output to zero
    row = 0
    j = 0
    nr = 0 # number of elements in row

    for row in range(M.rows):
        nr = M.row_ptr[row+1]-M.row_ptr[row]
        a = 0
        # iterate over the number of elements in this row
        for i in range(nr):
            # multiply the matrix value by the colum
            a += x[M.col_index[j+i]] * M.values[j+i]
        z[0] += a * conj(y[row])
        j += nr
    return 0


cdef inline int zcsrgevmv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny, complex *z) noexcept nogil:
    """Complex (z) valued CSR (csr) general (ge) transpose vector (v) matrix (m) vector (v) product.

    .. math::
        z = y^{\mathrm{T}} \\cdot \\mathbf{M} \\cdot x

    Parameters
    ----------
    M : csr_matrix struct
        CSR matrix
    x : complex*
        Contiguous memory input vector
    nx : integer
        Size of x array - length of input vector, should equal cols
    y : complex*
        Contiguous memory input vector
    ny : integer
        Size of y arrays - length of intput vector, should equals rows
    z : complex*
        Output complex value

    Returns
    -------
    0 on success
    -1 on wrong vector size or M, x, or y are NULL
    """
    cdef Py_ssize_t i, j, nr, row
    cdef complex a

    if nx != M.cols or ny != M.rows or M == NULL or x == NULL or y == NULL or z == NULL:
        return -1 # wrong size

    z[0] = 0 # initialise output to zero
    row = 0
    j = 0
    nr = 0 # number of elements in row

    for row in range(M.rows):
        nr = M.row_ptr[row+1]-M.row_ptr[row]
        a = 0
        # iterate over the number of elements in this row
        for i in range(nr):
            # multiply the matrix value by the colum
            a += x[M.col_index[j+i]] * M.values[j+i]
        z[0] += a * y[row]
        j += nr
    return 0
