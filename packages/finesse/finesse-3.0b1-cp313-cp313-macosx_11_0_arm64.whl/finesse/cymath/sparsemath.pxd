cdef struct csr_matrix:
    unsigned int nnz
    unsigned int rows
    unsigned int cols
    unsigned int *row_ptr # size rows + 1
    unsigned int *col_index # size nnz
    complex *values # size nnz


cdef class CSRMatrix:
    cdef:
        csr_matrix M

cdef int zcsrgemv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny) noexcept nogil
cdef int zcsrgecmv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny, complex *z) noexcept nogil
cdef int zcsrgevmv(csr_matrix *M, complex *x, Py_ssize_t nx, complex *y, Py_ssize_t ny, complex *z) noexcept nogil
