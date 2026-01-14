"""A collection of methods to compute overlap integrals for modal scattering matrices.
Essentially this involves solving the following integral

.. math::
    K_{abnm} = \iint^{\infty}_{-\infty} U_{nm}(x,y,q_i) M(x,y) U^*_{ab}(x,y,q_o) \, dy \, dx

:math:`U_nm` is the initial modes in the basis :math:`q_i` we are converting from and
:math:`U_ab` are the target modes in a basis :math:`q_o` we are projecting into.

TODO
----
Should explore if decomposing compute_map_knm_matrix_riemann_optimised into real and imaginary
integrals might be faster. In cases where q_in == q_out then integrals are real, apart from
the map component which can be complex.

Explore use of zgemm3m which is 25% faster than zgemm

Probably look into using CUDA if necessary for more speed.
"""
import cython
import numpy as np
cimport numpy as np
from finesse.cymath cimport complex_t
from scipy.linalg.cython_blas cimport zgemm
from scipy.integrate import newton_cotes
from ..cymath.homs cimport unm_workspace, unm_factor_store, u_n__fast, u_m__fast


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef void outer_conj_product(complex_t[:,::1] U, complex_t[:,:,::1] result) except *:
    """Computes U * U^C and returns the output into the result array.
    Result array must be of shape (N,N,M) where U is shape (N,M).
    """
    cdef:
        Py_ssize_t i, j, k
        double a, b, c, d

    A = U.shape[0]
    B = U.shape[1]
    if not (result.shape[0] == result.shape[1] == A) or not (result.shape[2] == B):
        raise RuntimeError(f"result array wrong shape should be ({A,A,B})")

    for i in range(A):
        for j in range(A):
            for k in range(B):
                a = U[i, k].real
                b = U[i, k].imag
                c = U[j, k].real
                d = U[j, k].imag
                result[i, j, k] = a*c + b*d + 1j*(b*c - a*d) # U[i, k] * conj(U[j, k])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_outer_conj_product(
        Py_ssize_t Nm,
        Py_ssize_t Ns,
        complex_t *U, # complex[Nm, Ns] C-ordered
        complex_t *result  # complex[Nm, Nm, Ns] C-ordered
    ) noexcept nogil:
    """Computes U * U^C and returns the output into the result array.
    Result array must be of shape (Nm,Nm,Ns) where U is shape (Nm,Ns).
    """
    cdef:
        Py_ssize_t i, j, k
        double a, b, c, d

    for i in range(Nm):
        for j in range(Nm):
            for k in range(Ns):
                a = U[i*Ns + k].real #U[i, k].real
                b = U[i*Ns + k].imag
                c = U[j*Ns + k].real
                d = U[j*Ns + k].imag
                result[i*Nm*Ns + j*Ns + k] = a*c + b*d + 1j*(b*c - a*d) # U[i, k] * conj(U[j, k])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef void outer_conj_product_2(complex_t[:,::1] U1, complex_t[:,::1] U2, complex_t[:,:,::1] result) except *:
    """Computes U1 * U2**C and returns the output into the result array.
    Result array must be of shape (N,N,M) where U is shape (N,M).
    """
    cdef:
        Py_ssize_t i, j, k
        double a, b, c, d

    A = U1.shape[0]
    B = U1.shape[1]
    if not (result.shape[0] == result.shape[1] == A) or not (result.shape[2] == B):
        raise RuntimeError(f"result array wrong shape should be ({A,A,B})")

    for i in range(A):
        for j in range(A):
            for k in range(B):
                a = U1[i, k].real
                b = U1[i, k].imag
                c = U2[j, k].real
                d = U2[j, k].imag
                result[i, j, k] = a*c + b*d + 1j*(b*c - a*d) # U1[i, k] * conj(U2[j, k])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_outer_conj_product_2(
        Py_ssize_t Nm,
        Py_ssize_t Ns,
        complex_t* U1,
        complex_t* U2,
        complex_t* result
    ) noexcept nogil:
    """Computes U1 * U2**C and returns the output into the result array.
    Result array must be of shape (N,N,M) where U is shape (N,M).
    """
    cdef:
        Py_ssize_t i, j, k
        double a, b, c, d

    for i in range(Nm):
        for j in range(Nm):
            for k in range(Ns):
                a = U1[i*Ns + k].real
                b = U1[i*Ns + k].imag
                c = U2[j*Ns + k].real
                d = U2[j*Ns + k].imag
                result[i*Ns*Nm + j*Ns + k] = a*c + b*d + 1j*(b*c - a*d) # U1[i, k] * conj(U2[j, k])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void update_U_xy_array(
        double *x, Py_ssize_t Nx, double *y, Py_ssize_t Ny,
        complex_t *Un, complex_t *Um, Py_ssize_t Nm,
        unm_workspace *ws, unm_factor_store *store
    ) noexcept nogil:
    """Method to fill Un and Um arrays up to some mode index Nm
    Parameters
    ----------
    x : *double
        Pointer to start of contiguous x array
    Nx : int
        Size of x array
    y : *double
        Pointer to start of contiguous y array
    Ny : int
        Size of y array
    Nm : int
        Max number of modes to calculate up to
    ws
        Pointer to allocated and initialised unm_workspace
    store
        Pointer to allocated and initialised unm_factor_store
    """
    cdef Py_ssize_t i, j
    for i in range(Nm):
        for j in range(Nx):
            Un[i*Nx + j] = u_n__fast(ws, store, i, x[j])

    for i in range(Nm):
        for j in range(Ny):
            Um[i*Ny + j] = u_m__fast(ws, store, i, y[j])


cpdef compute_map_scattering_coeffs_riemann_optimised(
            double dA,
            complex_t[:,::1] Z,
            complex_t[:,:,::1] Unn_,
            complex_t[:,:,::1] Umm_,
            complex_t[:,:,::1] tmp,
            complex_t[:,:,:,::1] result,
        ) :
    """Calculates a mode scattering matrix using a Riemann sum. This method
    uses an computationally optimised approach making use of fast BLAS
    functions. This requires the input modes to be specified in specific
    formats and memory layouts. What this functions computes is the following
    via a Riemann
    sum:

    .. math::
        K_{abnm} = \int^{\infty}_{-\infty}  u_{m}(y,q^y_i) u^*_{b}(y,q^y_o) \Bigg[ \int^{\infty}_{-\infty} Z(x,y) u_{n}(x,q^x_i) u^*_{a}(x,q^x_o) \, dx \Bigg] \, dy

    This integral is not actually performed to infinity, it is bound by the
    dimensions of the discretised map :math:`Z`. The map bound and uniform
    discretisation must be chosen to effciently sample the size of any of
    the beams and maximum mode order being used.

    Due to the optimised calculation method, the result indexing is not
    [a,b,n,m] but [m,a,n,b]. To convert it back to a more usable
    indexing use:

    >>> result = np.transpose(result, (2,1,0,3))

    Notes
    -----
    Nx - number of x samples
    Ny - number of y samples
    Nm - number of modes (n, m) being calculated

    Parameters
    ----------
    dA : double
        Area of discrete integral, dx * dy

    Z : array[complex]
        2D map of size [Ny, Nx]

    Unn_ : array[complex]
        3D array of size [Nm, Nm, Nx]. This should contain the
        Un(x) * Un'(x)**C products

    Umm_ : array[complex]
        3D array of size [Nm, Nm, Ny]. This should contain the
        Um(x) * Um'(x)**C products

    tmp : array[complex]
        Temporary storage that can be used to compute the dot
        products between Z and Unn\\_.
        Should be of size (Nm, Nm, Ny)

    result : array[complex]
        Resulting Knmnm output of size [Nm, Nm, Nm, Nm].
        IMPORTANT: Note output indexing of result K[m,a,n,b]
    """
    if not (Z.ndim == 2):
        raise RuntimeError("Z.ndim != 2")
    if not (result.ndim == 4):
        raise RuntimeError("result.ndim != 2")
    cdef:
        int Nx = Z.shape[1]
        int Ny = Z.shape[0]
        int Nm = result.shape[0]
    if not (result.shape[0] == Nm and result.shape[1] == Nm and result.shape[2] == Nm and result.shape[3] == Nm):
        raise RuntimeError("result.shape != (Nm, Nm, Nm, Nm)")
    if not (Unn_.shape[0] == Nm and Unn_.shape[1] == Nm and Unn_.shape[2] == Nx):
        raise RuntimeError("Unn_.shape != (Nm, Nm, Nx)")
    if not (Umm_.shape[0] == Nm and Umm_.shape[1] == Nm and Umm_.shape[2] == Ny):
        raise RuntimeError("Umm_.shape != (Nm, Nm, Ny)")
    if not (tmp.shape[0] == Nm and tmp.shape[1] == Nm and tmp.shape[2] == Ny):
        raise RuntimeError("tmp.shape != (Nm, Nm, Ny)")
    c_riemann_optimised(
        Nx, Ny, Nm, dA,
        &Z[0,0],
        &Unn_[0,0,0],
        &Umm_[0,0,0],
        &tmp[0,0,0],
        &result[0,0,0,0],
    )


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_riemann_optimised(
            int Nx,
            int Ny,
            int Nm,
            double dA,
            complex_t* Z, # [Ny, Nx]
            complex_t* Unn_, # [Nm, Nm, Nx]
            complex_t* Umm_, # [Nm, Nm, Ny]
            complex_t* tmp,  # [Nm, Nm, Ny]
            complex_t* result, # [Nm, Nm, Nm, Nm]
        ) noexcept nogil:
    """Raw interface that can be accessed via a Python interface using
    `compute_map_scattering_coeffs_riemann_optimised`, see that function
    for more details.

    Parameters
    ----------
    Nx : int
        Number of x samples

    Ny : int
        Number of y samples

    Nm : int
        Number of 1D modes

    dA : double
        Area of discrete integral, dx * dy

    Z : array[complex]
        2D map of size [Ny, Nx]

    Unn_ : array[complex]
        3D array of size [Nm, Nm, Nx]. This should contain the
        Un(x) * Un'(x)**C products

    Umm_ : array[complex]
        3D array of size [Nm, Nm, Ny]. This should contain the
        Um(x) * Um'(x)**C products

    tmp : array[complex]
        Temporary storage that can be used to compute the dot
        products between Z and Unn_.
        Should be of size (Nm, Nm, Ny)

    result : array[complex]
        Resulting Knmnm output of size [Nm, Nm, Nm, Nm].
        IMPORTANT: Note output indexing of result K[m,a,n,b]
    """
    cdef:
        Py_ssize_t i, k
        int lda, ldb, ldc, M, N, K
        complex_t alpha = dA
        complex_t beta = 0
        complex_t *A
        complex_t *B
        complex_t *C

    # setup blas zgemm variables for map product with x-modes
    # store this in a temporary memory and then apply the
    M = Ny
    N = Nm
    K = Nx
    lda = K
    ldb = K
    ldc = M
    A = Z

    for i in range(Nm):
        B = Unn_ + i*Nm*Nx # &Unn_[i,0,0]
        C = tmp + i*Nm*Ny #&tmp[i,0,0]
        zgemm("T", "N",
            &M, &N, &K,
            &alpha, A, &lda, B, &ldb,
            &beta, C, &ldc
        )

    # Now we need to perform the product of the y-modes
    # with all the map and x-mode products
    M = Nm
    N = Nm
    K = Ny
    lda = Ny
    ldb = Ny
    ldc = Nm
    alpha = 1 # reset as already applied dA
    for i in range(Nm):
        for k in range(Nm):
            A = Umm_ + i*Nm*Ny # &Umm_[i,0,0]
            B = tmp + k*Nm*Ny # &tmp[k,0,0]
            C = result + i*Nm*Nm*Nm + k*Nm*Nm # &result[i,k,0,0]
            zgemm("T", "N",
                &M, &N, &K,
                &alpha, A, &lda, B, &ldb,
                &beta, C, &ldc
            )


def composite_newton_cotes_weights(N, order):
    """
    Constructs the weights for a composite Newton-Cotes rule for integration
    along 1-dimensional line with equally spaced steps. Newton-Cotes are a
    generalisation of a various discrete integration methods that are
    approximating an integrated by some polynomial. Common methods are:

        N = 0 : Riemann sum
        N = 1 : Trapezoid rule
        N = 2 : Simpsons rule
        N = 4 : Simpsons 3/8 rule

    Approximating a large bound with a high order polynomial can be numerically
    problematic. Thus a composite rule is generated by subdividing a larger area
    into multiple chunks and applying each rule along it.

    If the order Newton-Cotes order specified does not produce a rule that fits
    into N, the order is decremented and that is used to fill gaps that do
    no fit.

    See https://mathworld.wolfram.com/Newton-CotesFormulas.html

    Parameters
    ----------
    N : integer >= 0
        1D size of array being ingrated over

    order : integer >= 0
        Order of Newton-Cotes rule to use

    Returns
    -------
    weights : array
        Array of weights to multiply data with before summing
    """
    # ensure we have a 1xN array
    if order == 0:
        return np.ones((N,))
    W = newton_cotes(order, 1)[0]
    wx = np.zeros(N, dtype=np.float64)
    i = 0
    while i < N - 1:
        try:
            wx[i:(i+len(W))] += W
            i += len(W)-1
        except ValueError as ex:
            # if we can't fit a newton-cotes rule in to the space
            # needed then pick a slightly smaller one
            if len(wx[i:(i+len(W))]) < len(W):
                order -= 1
                W = newton_cotes(order, 1)[0]
    return wx


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
def map_coupling_matrix_riemann(complex_t[:,::1] Y, double dx, double dy, complex_t[:,::1] Un, complex_t[:,::1] Um, long[:,::1] index_map):
    cdef:
        Py_ssize_t i, j, k, l, n, m, nn, mm, Nm
        complex_t a, b
        complex_t[:, ::1] K
        double D = dx * dy
        complex_t sum = 0
        complex_t [:, ::1] Un_
        complex_t [:, ::1] Um_

    Nm = index_map.shape[0]
    Nx = Un.shape[1]
    Ny = Um.shape[1]
    K = np.zeros((Nm, Nm), dtype=np.complex128)
    Un_ = np.conj(Un)
    Um_ = np.conj(Um)

    for i in range(Nm):
        n = index_map[i, 0]
        m = index_map[i, 1]
        for j in range(Nm):
            nn = index_map[j, 0]
            mm = index_map[j, 1]
            sum = 0
            for k in range(Nx):
                for l in range(Ny):
                    a = Un[n, k] * Un_[nn, k]
                    b = Um[m, l] * Um_[mm, l]
                    sum += a * b * Y[k, l]

            K[i, j] = K[i, j]  + sum * D

    return np.asarray(K)

# WIP integration function
# needs to separate the real H(x) functions for integrand and the complex
# scaling factors still.

# @cython.boundscheck(False)
# @cython.wraparound(False)
# @cython.initializedcheck(False)
# cpdef void compute_map_knm_scatterins_riemann_optimised_mode_matched(
#     double dA,
#     double[:,::1] Z_real,
#     double[:,::1] Z_imag,
#     double[:,:,::1] Unn_,
#     double[:,:,::1] Umm_,
#     double[:,:,::1] tmp_real,
#     double[:,:,::1] tmp_imag,
#     double[:,:,:,::1] result_real,
#     double[:,:,:,::1] result_imag,
#     complex_t[:,:,:,::1] result,
# ) except *:
#     cdef:
#         Py_ssize_t i, j, k, l,
#         int Nx, Ny, Nm, inc=1, lda, ldb, ldc, M, N, K
#         double alpha = dA
#         double beta = 0
#         double *A
#         double *B
#         double *C
#         double *X
#         double *Y

#     Nx = Z_real.shape[1]
#     Ny = Z_real.shape[0]
#     Nm = result_real.shape[0] # computing (Nm, Nm, Nm, Nm) output
#     assert(result_real.shape[0] == result_real.shape[1] == result_real.shape[2] == result_real.shape[3])
#     assert(result_imag.shape[0] == result_imag.shape[1] == result_imag.shape[2] == result_imag.shape[3])
#     assert(Unn_.shape[0] == Unn_.shape[1] == result_imag.shape[0] == result_real.shape[0])
#     assert(Unn_.shape[0] == Unn_.shape[1] == result_imag.shape[0] == result_real.shape[0])
#     assert(Unn_.shape[2] == Nx)
#     assert(Umm_.shape[2] == Ny)

#     # setup blas zgemm variables for map product with x-modes
#     # store this in a temporary memory and then apply the
#     M = Ny
#     N = Nm
#     K = Nx
#     lda = K
#     ldb = K
#     ldc = M
#     for i in range(Nm):
#         B = &Unn_[i,0,0]

#         A = &Z_real[0, 0]
#         C = &tmp_real[i,0,0]
#         dgemm("T", "N",
#             &M, &N, &K,
#             &alpha, A, &lda, B, &ldb,
#             &beta, C, &ldc
#         )
#         A = &Z_imag[0, 0]
#         C = &tmp_imag[i,0,0]
#         dgemm("T", "N",
#             &M, &N, &K,
#             &alpha, A, &lda, B, &ldb,
#             &beta, C, &ldc
#         )

#     # Now we need to perform the product of the y-modes
#     # with all the map and x-mode products
#     M = Nm
#     N = Nm
#     K = Ny
#     lda = Ny
#     ldb = Ny
#     ldc = Nm
#     alpha = 1 # reset as already applied dA
#     for i in range(Nm):
#         for k in range(Nm):
#             A = &Umm_[i,0,0]
#             B = &tmp_real[k,0,0]
#             C = &result_real[i,k,0,0]
#             dgemm("T", "N",
#                 &M, &N, &K,
#                 &alpha, A, &lda, B, &ldb,
#                 &beta, C, &ldc
#             )
#             B = &tmp_imag[k,0,0]
#             C = &result_imag[i,k,0,0]
#             dgemm("T", "N",
#                 &M, &N, &K,
#                 &alpha, A, &lda, B, &ldb,
#                 &beta, C, &ldc
#             )

#     for i in range(Nm):
#         for j in range(Nm):
#             for k in range(Nm):
#                 for l in range(Nm):
#                     result[i,j,k,l].real = result_real[i,j,k,l]

#     for i in range(Nm):
#         for j in range(Nm):
#             for k in range(Nm):
#                 for l in range(Nm):
#                     result[i,j,k,l].imag = result_imag[i,j,k,l]
