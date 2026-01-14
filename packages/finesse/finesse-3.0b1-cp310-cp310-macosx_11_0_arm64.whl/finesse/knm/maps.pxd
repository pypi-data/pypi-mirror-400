import numpy as np
cimport numpy as np
from ..cymath.homs cimport unm_workspace, unm_factor_store
from finesse.cymath.complex cimport complex_t
from finesse.cymath.complex cimport DenseZVector, DenseZMatrix
from finesse.simulations.base cimport NodeBeamParam
from cpython.ref cimport PyObject


cdef class Map:
    cdef readonly:
        np.ndarray x
        np.ndarray y
        np.ndarray X
        np.ndarray Y
        np.ndarray R
        np.ndarray opd # meters
        np.ndarray amplitude # 0 - 1

    cdef:
        object put_focal_length
        object _opd_function
        object _amplitude_function
        bint is_focusing_element
        bint has_opd_function
        bint opd_function_is_method
        bint has_amplitude_function
        bint amplitude_function_is_method
        bint do_remove_tilts
        bint do_remove_curvatures
        bint do_remove_astigmatism


cdef struct knm_map_workspace:
    bint new_map_data # Is this the first calculation of the current map data
    bint map_is_changing # Should map be recalculated
    bint is_focusing_element # whether mode mismatch should be calculated in map integration
    PyObject *map_obj # object for reference counting
    PyObject *z_obj # object for reference counting
    PyObject *model
    NodeBeamParam *q_from
    NodeBeamParam *q_to
    double k # wavenumber to use for phase conversion
    double phase_factor # Phase factor to apply to opds
    const double* x # x coordinates
    double dx
    int Nx
    const double* y # y coordinates
    double dy
    int Ny
    complex_t *z # map values [:, ::1] (Ny, Nx)
    int Nm # number of modes
    complex_t* Un   # complex_t[:, ::1]  (Nm, Nx)
    complex_t* Um   # complex_t[:, ::1]  (Nm, Ny)
    complex_t* Un_  # complex_t[:, ::1]  (Nm, Nx)
    complex_t* Um_  # complex_t[:, ::1]  (Nm, Ny)
    complex_t* Unn_ # complex_t[:, :, ::1]  (Nm, Nm, Nx)
    complex_t* Umm_ # complex_t[:, :, ::1]  (Nm, Nm, Ny)
    complex_t* tmp  # complex_t[:, :, ::1]  (Nm, Nm, Ny)
    complex_t* K    # complex_t[:, :, :, ::1] (Nm, Nm, Nm, Nm)
    unm_workspace *uiws # input workspace for Unm calculations
    unm_factor_store *unm_i_factor_ws
    unm_workspace *uows # output workspace for Unm calculations
    unm_factor_store *unm_o_factor_ws


cdef set_knm_map_workspace(object model, knm_map_workspace *ws, Map _map, double k, double phase_factor)
cdef init_knm_map_workspace(
    knm_map_workspace *ws,
    int Nm,
    NodeBeamParam *q_from,
    NodeBeamParam *q_to,
    bint flip_odd_x_output_modes
)
cdef free_knm_map_workspace(knm_map_workspace *ws)

cdef void c_scattering_coefficients_to_KnmMatrix(
        int[:,::1] modes, Py_ssize_t Nm, complex_t *K, DenseZMatrix *out
    ) noexcept nogil

cdef update_map_data_in_workspace(knm_map_workspace *ws)
