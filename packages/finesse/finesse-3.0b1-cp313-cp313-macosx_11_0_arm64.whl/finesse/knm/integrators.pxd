from finesse.cymath cimport complex_t
from ..cymath.homs cimport unm_workspace, unm_factor_store

cpdef compute_map_scattering_coeffs_riemann_optimised(
            double dA,
            complex_t[:,::1] Z,
            complex_t[:,:,::1] Unn_,
            complex_t[:,:,::1] Umm_,
            complex_t[:,:,::1] tmp,
            complex_t[:,:,:,::1] result,
        )

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
        ) noexcept nogil

cpdef void outer_conj_product(complex_t[:,::1] U, complex_t[:,:,::1] result) except *
cdef void c_outer_conj_product(
        Py_ssize_t Nm,
        Py_ssize_t Ns,
        complex_t *U, # complex[Nm, Ns] C-ordered
        complex_t *result  # complex[Nm, Nm, Ns] C-ordered
    ) noexcept nogil

cpdef void outer_conj_product_2(complex_t[:,::1] U1, complex_t[:,::1] U2, complex_t[:,:,::1] result) except *
cdef void c_outer_conj_product_2(
        Py_ssize_t Nm,
        Py_ssize_t Ns,
        complex_t* U1,
        complex_t* U2,
        complex_t* result
    ) noexcept nogil

cdef void update_U_xy_array(
        double *x, Py_ssize_t Nx, double *y, Py_ssize_t Ny,
        complex_t *Un, complex_t *Um, Py_ssize_t Nm,
        unm_workspace *ws, unm_factor_store *store) noexcept nogil
