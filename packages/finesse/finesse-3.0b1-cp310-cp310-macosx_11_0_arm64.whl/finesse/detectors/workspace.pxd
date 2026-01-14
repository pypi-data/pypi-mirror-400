from finesse.simulations.simulation cimport BaseSimulation
from finesse.element_workspace cimport ElementWorkspace

import numpy as np
cimport numpy as np

ctypedef object (*fptr_c_output)(DetectorWorkspace)


cdef class OutputInformation:
    cdef:
        readonly unicode name
        object __detector_type
        object __nodes
        object __dtype
        object __dtype_shape
        object __unit
        object __label
        object __needs_fields
        object __needs_trace
        Py_ssize_t __dtype_size


cdef class OutputFuncWrapper:
    cdef fptr_c_output func
    @staticmethod
    cdef OutputFuncWrapper make_from_ptr(fptr_c_output f)


cdef class DetectorWorkspace(ElementWorkspace):
    cdef:
        OutputFuncWrapper fn_c  # C output function
        object fn_py  # Python output function
        readonly OutputInformation oinfo

        readonly bint needs_carrier # Requires sim.run_carrier
        readonly bint needs_signal # Requires sim.run_signal
        readonly bint needs_noise # Requires sim.run_noise
        readonly bint needs_modal_update # Requires sim.modal_update

        bint ignore_sim_mask # Whether to ignore masking and continue call to get_output

    cpdef get_output(self)


cdef class MaskedDetectorWorkspace(DetectorWorkspace):
    cdef:
        Py_ssize_t* unmasked_mode_indices

    cdef readonly:
        np.ndarray unmasked_indices_arr
        Py_ssize_t num_unmasked_HOMs
        bint has_mask

    cdef int setup_mask(self) except -1
    cdef bint hom_in_modes(self, Py_ssize_t hom_idx) noexcept
