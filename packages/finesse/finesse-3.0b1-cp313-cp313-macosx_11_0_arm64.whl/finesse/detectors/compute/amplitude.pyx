#cython: boundscheck=False, wraparound=False, initializedcheck=False

cimport numpy as np
import numpy as np

import logging

from ...cymath cimport complex_t
from ...cymath.complex cimport conj, cexp, carg
from ...cymath.complex cimport cnorm, COMPLEX_0
from ...cymath.math cimport sqrt
from ...knm cimport KnmMatrix
from ...components.node import NodeType
from ...simulations.homsolver cimport HOMSolver
from ...env import warn
from ..workspace cimport (
    DetectorWorkspace,
    MaskedDetectorWorkspace,
    OutputFuncWrapper,
)


LOGGER = logging.getLogger(__name__)

### Amplitude detector workspace & output funcs ###

cdef class ADWorkspace(MaskedDetectorWorkspace):
    cdef public:
        object ntype
        double scaling
        bint is_f_changing
        Py_ssize_t node_id
        Py_ssize_t freq_idx
        Py_ssize_t hom_idx
        HOMSolver solver

    def __init__(self, owner, sim):
        self.is_f_changing = owner.f.is_changing
        if owner.f.eval() is None:
            raise ValueError(f"{owner.f}: frequency value is `None`, check values have been set correctly.")
        fval = float(owner.f)
        fs = []

        for mtx in (sim.carrier, sim.signal):
            if mtx:
                f = mtx.get_frequency_object(fval, owner.node)
                if f is not None:
                    fs.append((f, mtx))
        if len(fs) == 0:
            raise Exception(
                f"Error in amplitude detector {owner.name}:\n"
                f"    Could not find a frequency bin at {owner.f}"
            )
        elif len(fs) > 1:
            raise Exception(
                f"Error in amplitude detector {owner.name}:\n"
                f"    Found multiple frequency bins at {owner.f}"
            )

        freq, self.solver = fs[0]

        if self.solver is sim.carrier:
            super().__init__(owner, sim, needs_carrier=True)
        else:
            super().__init__(owner, sim, needs_signal=True)

        cdef bint multi_field_mode = False
        cdef Py_ssize_t hom_idx = 0
        if owner.node.type == NodeType.OPTICAL:
            if self.sim.is_modal:
                multi_field_mode = owner.n is None and owner.m is None
                if not multi_field_mode:
                    try:
                        hom_idx = self.sim.model.mode_index_map[(owner.n, owner.m)]
                    except KeyError:
                        raise Exception(
                            f"Error in amplitude detector {owner.name}:\n"
                            f"    HOM (n={owner.n}, m={owner.m}) not found in the model"
                        )
        self.freq_idx = freq.index
        self.node_id = self.solver.node_id(owner.node)
        self.hom_idx = hom_idx

        if not multi_field_mode:
            if self.has_mask and not self.hom_in_modes(hom_idx):
                self.set_output_fn(ad_single_field_output_masked)
                warn(
                    f"Masking {repr(owner.name)} which is in single-frequency mode. "
                    f"This will always return values of complex zero in a simulation."
                )
            else:
                if self.has_mask:
                    warn(f"Mask applied to {repr(owner.name)} has no effect!")

                if freq.audio_order == -1:
                    self.set_output_fn(ad_conj_single_field_output)
                else:
                    self.set_output_fn(ad_single_field_output)
        else:
            if freq.audio_order == -1:
                if self.has_mask:
                    self.set_output_fn(ad_conj_multi_field_output_masked)
                else:
                    self.set_output_fn(ad_conj_multi_field_output)
            else:
                if self.has_mask:
                    self.set_output_fn(ad_multi_field_output_masked)
                else:
                    self.set_output_fn(ad_multi_field_output)

        if owner.node.type == NodeType.OPTICAL:
            self.scaling = sqrt(0.5 * self.sim.model_settings.EPSILON0_C)
        elif owner.node.type == NodeType.MECHANICAL:
            self.scaling = self.sim.model_settings.x_scale
        else:
            self.scaling = 1


ad_single_field_output = OutputFuncWrapper.make_from_ptr(c_ad_single_field_output)
cdef c_ad_single_field_output(DetectorWorkspace dws) :
    cdef ADWorkspace ws = <ADWorkspace> dws
    cdef Py_ssize_t N = 0
    cdef complex_t *ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)
    assert(N > 0)
    assert(ptr != NULL)
    return ws.scaling * ptr[ws.hom_idx]

ad_conj_single_field_output = OutputFuncWrapper.make_from_ptr(c_ad_conj_single_field_output)
cdef c_ad_conj_single_field_output(DetectorWorkspace dws) :
    cdef ADWorkspace ws = <ADWorkspace> dws
    cdef Py_ssize_t N = 0
    cdef complex_t *ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)
    assert(N > 0)
    assert(ptr != NULL)
    return ws.scaling * conj(ptr[ws.hom_idx])

ad_single_field_output_masked = OutputFuncWrapper.make_from_ptr(c_ad_single_field_output_masked)
cdef c_ad_single_field_output_masked(DetectorWorkspace dws) :
    return COMPLEX_0


ad_multi_field_output = OutputFuncWrapper.make_from_ptr(c_ad_multi_field_output)
cdef c_ad_multi_field_output(DetectorWorkspace dws) :
    cdef:
        ADWorkspace ws = <ADWorkspace> dws
        complex_t fields_sum = COMPLEX_0
        double amp = 0.0
        double phase = 0.0
        Py_ssize_t i # field index
        Py_ssize_t N = 0
        complex_t *ptr = NULL

    ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)
    assert(N > 0)
    assert(ptr != NULL)

    for i in range(N):
        fields_sum += ptr[i]
        amp += cnorm(ptr[i])

    phase = carg(fields_sum)
    amp = sqrt(amp)
    return ws.scaling * amp * cexp(1j * phase)

ad_multi_field_output_masked = OutputFuncWrapper.make_from_ptr(c_ad_multi_field_output_masked)
cdef c_ad_multi_field_output_masked(DetectorWorkspace dws) :
    cdef:
        ADWorkspace ws = <ADWorkspace> dws
        complex_t field_amp = COMPLEX_0
        complex_t fields_sum = COMPLEX_0
        double amp = 0.0
        double phase = 0.0
        Py_ssize_t i # field index
        Py_ssize_t N = 0
        complex_t *ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)

    assert(N > 0)
    assert(ptr != NULL)

    for i in range(ws.num_unmasked_HOMs):
        field_amp = ptr[ws.unmasked_mode_indices[i]]
        fields_sum += field_amp
        amp += cnorm(field_amp)

    phase = carg(fields_sum)
    amp = sqrt(amp)

    return ws.scaling * amp * cexp(1j * phase)

ad_conj_multi_field_output = OutputFuncWrapper.make_from_ptr(c_ad_conj_multi_field_output)
cdef c_ad_conj_multi_field_output(DetectorWorkspace dws) :
    cdef:
        ADWorkspace ws = <ADWorkspace> dws
        complex_t field_amp = COMPLEX_0
        complex_t fields_sum = COMPLEX_0
        double amp = 0.0
        double phase = 0.0
        Py_ssize_t i # field index
        Py_ssize_t N = 0
        complex_t *ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)

    assert(N > 0)
    assert(ptr != NULL)

    for i in range(ws.sim.model_settings.num_HOMs):
        field_amp = conj(ptr[i])
        fields_sum += field_amp
        amp += cnorm(field_amp)

    phase = carg(fields_sum)
    amp = sqrt(amp)

    return ws.scaling * amp * cexp(1j * phase)

ad_conj_multi_field_output_masked = OutputFuncWrapper.make_from_ptr(c_ad_conj_multi_field_output_masked)
cdef c_ad_conj_multi_field_output_masked(DetectorWorkspace dws) :
    cdef:
        ADWorkspace ws = <ADWorkspace> dws
        complex_t field_amp = COMPLEX_0
        complex_t fields_sum = COMPLEX_0
        double amp = 0.0
        double phase = 0.0
        Py_ssize_t i # field index
        Py_ssize_t N = 0
        complex_t *ptr = ws.solver.node_field_vector_fast(ws.node_id, ws.freq_idx, &N)

    assert(N > 0)
    assert(ptr != NULL)

    for i in range(ws.num_unmasked_HOMs):
        field_amp = conj(ptr[ws.unmasked_mode_indices[i]])
        fields_sum += field_amp
        amp += cnorm(field_amp)

    phase = carg(fields_sum)
    amp = sqrt(amp)

    return ws.scaling * amp * cexp(1j * phase)

### Knm detector workspace & output funcs ###

cdef class KnmDetectorWorkspace(DetectorWorkspace):
    cdef public:
        Py_ssize_t from_idx, to_idx

        KnmMatrix knm_matrix

    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

knm_detector_scalar_output = OutputFuncWrapper.make_from_ptr(c_knm_detector_scalar_output)
cdef c_knm_detector_scalar_output(DetectorWorkspace dws) :
    """Outputs single coefficient of (n1, m1) -> (n2, m2)."""
    cdef KnmDetectorWorkspace kdws = <KnmDetectorWorkspace> dws
    return kdws.knm_matrix.data_view[kdws.to_idx][kdws.from_idx]

knm_detector_mode1_output = OutputFuncWrapper.make_from_ptr(c_knm_detector_mode1_output)
cdef c_knm_detector_mode1_output(DetectorWorkspace dws) :
    """Outputs coefficient vector of (n1, m1) -> (n, m) for each n, m."""
    cdef KnmDetectorWorkspace kdws = <KnmDetectorWorkspace> dws
    return np.asarray(kdws.knm_matrix.data_view[:,kdws.from_idx].copy())

knm_detector_mode2_output = OutputFuncWrapper.make_from_ptr(c_knm_detector_mode2_output)
cdef c_knm_detector_mode2_output(DetectorWorkspace dws) :
    """Outputs coefficient vector of (n, m) -> (n2, m2) for each n, m."""
    cdef KnmDetectorWorkspace kdws = <KnmDetectorWorkspace> dws
    return np.asarray(kdws.knm_matrix.data_view[kdws.to_idx].copy())

knm_detector_matrix_output = OutputFuncWrapper.make_from_ptr(c_knm_detector_matrix_output)
cdef c_knm_detector_matrix_output(DetectorWorkspace dws) :
    """Outputs full matrix of coupling coefficients."""
    cdef KnmDetectorWorkspace kdws = <KnmDetectorWorkspace> dws
    return kdws.knm_matrix.data.copy()
