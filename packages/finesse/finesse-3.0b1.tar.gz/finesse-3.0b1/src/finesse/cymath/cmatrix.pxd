cimport numpy as np
from cpython.ref cimport PyObject
from finesse.cymath cimport complex_t
from cython cimport view

from finesse.cymath.complex cimport DenseZVector, DenseZMatrix

ctypedef np.npy_intp SIZE_t

cdef extern from "klu.h":
    cdef int KLU_OK = 0
    cdef int KLU_SINGULAR = 1
    cdef int KLU_OUT_OF_MEMORY = -2
    cdef int KLU_INVALID = -3
    cdef int KLU_TOO_LARGE = -4

    ctypedef long SuiteSparse_long

    ctypedef struct klu_l_symbolic:
        double symmetry, est_flops, lnz, unz
        double *Lnz
        SuiteSparse_long n, nz, nzoff, nblocks, maxblock, ordering, do_btf, structural_rank
        SuiteSparse_long *P
        SuiteSparse_long *Q
        SuiteSparse_long *R

    ctypedef struct klu_l_numeric:
        SuiteSparse_long n, nblocks, lnz, unz, max_lnz_block, max_unz_block
        SuiteSparse_long *Pnum
        SuiteSparse_long *Pinv
        SuiteSparse_long *Lip
        SuiteSparse_long *Uip
        SuiteSparse_long *Llen
        SuiteSparse_long *Ulen
        void **LUbx
        size_t *LUsize
        void *Udiag
        double *Rs
        size_t worksize
        void *Work
        void *Xwork
        SuiteSparse_long *Iwork
        SuiteSparse_long *Offp
        SuiteSparse_long *Offi
        void *Offx
        SuiteSparse_long nzoff

    ctypedef struct klu_l_common:
        int ordering
        int scale
        int btf
        int maxwork
        int status
        double tol
        double rcond
        double condest
        double rgrowth

    cdef int klu_l_defaults(klu_l_common* Common) noexcept
    cdef klu_l_symbolic *klu_l_analyze(SuiteSparse_long num_eqs,
                                       SuiteSparse_long *col_ptr,
                                       SuiteSparse_long *row_idx,
                                       klu_l_common* Common) noexcept

    cdef klu_l_numeric *klu_zl_factor(SuiteSparse_long *col_ptr,
                                      SuiteSparse_long *row_idx,
                                      double *values,
                                      klu_l_symbolic *Symbolic,
                                      klu_l_common *Common) noexcept


    cdef void        klu_zl_refactor(SuiteSparse_long *col_ptr,
                                     SuiteSparse_long *row_idx,
                                     double *values,
                                     klu_l_symbolic *Symbolic,
                                     klu_l_numeric *Numeric,
                                     klu_l_common *Common) noexcept


    cdef int klu_zl_sort(klu_l_symbolic *Symbolic, klu_l_numeric *Numeric, klu_l_common* Common) noexcept

    cdef int klu_zl_free_numeric(klu_l_numeric **Numeric, klu_l_common *Common) noexcept
    cdef int klu_l_free_symbolic(klu_l_symbolic **Symbolic, klu_l_common *Common) noexcept

    cdef SuiteSparse_long klu_zl_solve (klu_l_symbolic *, klu_l_numeric *, SuiteSparse_long, SuiteSparse_long, double *, klu_l_common *) noexcept
    cdef SuiteSparse_long klu_zl_tsolve(klu_l_symbolic *, klu_l_numeric *, SuiteSparse_long, SuiteSparse_long, double *, SuiteSparse_long, klu_l_common * ) noexcept

    SuiteSparse_long klu_zl_rgrowth (SuiteSparse_long *, SuiteSparse_long *, double *, klu_l_symbolic *, klu_l_numeric *, klu_l_common *)
    SuiteSparse_long klu_zl_condest (SuiteSparse_long *, double *, klu_l_symbolic *, klu_l_numeric *, klu_l_common *)
    SuiteSparse_long klu_zl_rcond (klu_l_symbolic *, klu_l_numeric *, klu_l_common *)

cdef class CCSMatrix:
    cdef:
        unicode __name
        dict __indexes

        SuiteSparse_long num_eqs
        int allocated
        int num_nodes
        unsigned num_rhs

        SuiteSparse_long   *row_idx
        SuiteSparse_long   *col_ptr
        complex_t *values
        complex_t *rhs
        readonly complex_t[:, ::1] rhs_view

        SuiteSparse_long nnz
        readonly dict sub_columns
        dict diag_map
        list __callbacks
        object __weakref__

    cpdef declare_equations(
        self,
        SuiteSparse_long Neqs,
        SuiteSparse_long index,
        unicode name,
        is_diagonal = ?,
        add_view = ?
    )
    cpdef _declare_submatrix(self, SuiteSparse_long _from, SuiteSparse_long _to,
                        unicode name, callback=?, type_=?)
    cpdef set_rhs(self, SuiteSparse_long index, complex_t value, unsigned rhs_index=?)
    cdef int c_set_rhs(self, SuiteSparse_long index, complex_t value, Py_ssize_t rhs_index) except -1
    cdef unsigned request_rhs_view(self) noexcept
    cpdef complex_t[::1] get_rhs_view(self, unsigned index) noexcept
    cpdef construct(self, complex_t diagonal_fill=?)
    cdef np.ndarray get_numpy_array_view(self, SuiteSparse_long _from, SuiteSparse_long _to, complex_t** start_ptr, SuiteSparse_long* from_rhs_index)
    cpdef clear_rhs(self, unsigned rhs_index=?)
    cpdef factor(self)
    cpdef refactor(self)
    cpdef const complex_t[::1] solve(self, int transpose=?, bint conjugate=?, unsigned rhs_index=?) noexcept
    cpdef void solve_extra_rhs(self, int transpose=?, bint conjugate=?) noexcept
    cdef void zgemv(self, complex_t[::1] out, unsigned rhs_index=?) noexcept


cdef class SubCCSView:
    cdef:
        readonly str name
        readonly object M
        readonly Py_ssize_t _from, _to
        readonly bint conjugate_fill
        readonly int stride1 # in units of 16 bytes
        readonly int stride2 # in units of 16 bytes
        readonly int size1
        readonly int size2
        readonly SuiteSparse_long start_idx
        readonly SuiteSparse_long from_rhs_index
        complex_t* ptr
        np.ndarray A
        readonly complex_t[:, ::1] from_rhs_view # rhs[rhs index, rhs values]
        readonly Py_ssize_t from_rhs_view_size
        complex_t[::1] prop_za_zm_workspace

    cdef void fill_za(self, complex_t a) noexcept
    cdef void fill_zd(self, complex_t[::1] D) noexcept
    cdef void fill_dv(self, double[::1] D) noexcept
    cdef void fill_za_dv(self, complex_t a, double[::1] D) noexcept
    cdef void fill_zd_2(self, const complex_t* D, int s1) noexcept nogil
    cdef void fill_za_zd_2(self, complex_t a, const complex_t* D, int stride) noexcept nogil
    cdef void fill_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept
    cdef void fill_za_zm_2(self, complex_t a, const complex_t* M, int s1, int s2) noexcept
    cdef void fill_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept


    cdef void fill_zm(self, complex_t[:, ::1] M) noexcept
    cdef void fill_negative_za(self, complex_t a) noexcept
    cdef void fill_negative_zd(self, complex_t[::1] D) noexcept
    cdef void fill_negative_dd(self, double[::1] D) noexcept
    cdef void fill_negative_za_dd(self, complex_t a, double[::1] D) noexcept
    cdef void fill_negative_zd_2(self, const complex_t* D, int s1) noexcept nogil
    cdef void fill_negative_za_zd_2(self, complex_t a, const complex_t* D, int stride) noexcept nogil

    cdef void fill_negative_za_zv(self, complex_t a, DenseZVector* V) noexcept

    cdef void fill_negative_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept
    cdef void fill_negative_za_zm_2(self, complex_t a, DenseZMatrix* M) noexcept
    cdef void fill_negative_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept
    cdef void fill_negative_zm(self, complex_t[:, ::1] M) noexcept

    cdef void fill_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept
    cdef void fill_negative_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept
    cdef void fill_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept
    cdef void fill_negative_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept

    cdef void fill_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept
    cdef void fill_prop_za(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept
    cdef void fill_neg_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept
    cdef void fill_neg_prop_za(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept


cdef class SubCCSView1DArray:
    cdef PyObject** views
    cdef readonly Py_ssize_t size


cdef class SubCCSView2DArray:
    cdef PyObject*** views
    cdef readonly (Py_ssize_t, Py_ssize_t) shape
    cdef readonly Py_ssize_t rows
    cdef readonly Py_ssize_t cols


cdef class KLUMatrix(CCSMatrix):
    cdef:
        klu_l_common Common
        klu_l_numeric* Numeric
        klu_l_symbolic* Symbolic

    cpdef factor(self)
    cpdef refactor(self)
    cpdef const complex_t[::1] solve(self, int transpose=?, bint conjugate=?, unsigned rhs_index=?) noexcept
    cpdef void solve_extra_rhs(self, int transpose=?, bint conjugate=?) noexcept
    cpdef double rgrowth(self) noexcept
    cpdef double rcond(self) noexcept
    cpdef double condest(self) noexcept
    cpdef void zgemv(self, complex_t[::1] out, unsigned rhs_index=?) noexcept
