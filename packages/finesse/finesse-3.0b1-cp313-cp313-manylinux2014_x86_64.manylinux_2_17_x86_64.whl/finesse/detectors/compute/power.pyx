#cython: boundscheck=False, wraparound=False, initializedcheck=False

cimport numpy as np
import numpy as np
from finesse.symbols import simplification

from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj, cexp
from finesse.cymath.complex cimport cnorm
from finesse.cymath.math cimport float_eq

from finesse.cymath.sparsemath cimport zcsrgecmv, zcsrgevmv, csr_matrix
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver
from finesse.frequency cimport frequency_info_t
from finesse.detectors.workspace cimport (
    DetectorWorkspace,
    MaskedDetectorWorkspace,
    OutputFuncWrapper,
)
from finesse.element_workspace cimport BaseCValues
from finesse.detectors import pdtypes
from finesse.parameter import Parameter, ParameterState

cimport finesse.constants

from libc.stdlib cimport calloc, realloc, free

ctypedef (double*,) ptr_tuple_1
ctypedef (double*, double*) ptr_tuple_2
ctypedef (double*, double*, double*) ptr_tuple_3
ctypedef (double*, double*, double*, double*) ptr_tuple_4
ctypedef (double*, double*, double*, double*, double*) ptr_tuple_5
ctypedef (double*, double*, double*, double*, double*, double*) ptr_tuple_6
ctypedef (double*, double*, double*, double*, double*, double*, double*) ptr_tuple_7
ctypedef (double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_8
ctypedef (double*, double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_9
ctypedef (double*, double*, double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_10
ctypedef (double*, double*, double*, double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_11

IF UNAME_SYSNAME == "Windows":
    cdef extern from "<math.h>":
        double nan(const char* input)

    cdef double NAN = nan("")
ELSE:
    cdef double NAN = 0.0/0.0


def check_is_fsig(model, f: Parameter):
    """Checks if a frequency parameter `f` is dependant or the same value as
    the current model signal frequency.
    """
    if model.fsig.f.value is None:
        return False  # signal simulations disabled

    with simplification():
        if f.state == ParameterState.Symbolic:
            f_value = f.value.collect()
        else:
            f_value = float(f.value)

        if model.fsig.f.state == ParameterState.Symbolic:
            fsig_value = model.fsig.f.value.collect()
        else:
            fsig_value = float(model.fsig.f)

    return (
        fsig_value == f_value
        or model.fsig.f.ref == f_value
        or f.ref == fsig_value
    )


cdef inline void do_zcsrgecmv(
        csr_matrix *M, HOMSolver mtx,
        int node_id, int f1_index, int f2_index,
        int N, complex *result
    ) noexcept:
    """Wrapper for computing:

    .. math::
        v2^H M v1

    where M is a CSR matrix and the v1 and v2 are HOM vectors
    extraced from mtx solution at a given node between two different
    frequencies. The result pointer value is incremented by the product.

    Note
    ----
    v2 is conjugated for the product.

    Parameters
    ----------
    M : csr_matrix pointer
        Photodiode segementation matrix, should be Hermitian
    N : int
        Size of HOM matrix to extract from solvers
    mtx : HOMSolver
        Matrix system solution to extract HOM vectors for
    node_id : int
        Node ID to extract vector information for
    f1_index, f2_index : int
        Frequency index to extract vector information for
    increment_ptr : complex*
        Pointer to incredment result of operation to
    """
    cdef complex z
    cdef Py_ssize_t _N = 0
    # Get optical field vector pointers
    cdef complex *E1 = mtx.node_field_vector_fast(node_id, f1_index, &_N)
    cdef complex *E2 = mtx.node_field_vector_fast(node_id, f2_index, &_N)
    assert(N == _N)
    # Compute vector matrix vector to compute
    # segmentation effects
    zcsrgecmv(M, E1, _N, E2, _N, &z)
    result[0] += z


cdef inline void do_zcsrgecmv2(
        csr_matrix *M,
        int N,
        HOMSolver mtx1,
        int node1_id,
        int f1_index,
        HOMSolver mtx2,
        int node2_id,
        int f2_index,
        bint conjugate_result,
        complex *increment_ptr
    ) noexcept:
    """Wrapper for computing:

    .. math::
        v2^H M v1

    where M is a CSR matrix and the v1 and v2 are HOM vectors
    extraced from different mtx solutions at a given node between two different
    frequencies. The result pointer value is incremented by the product.

    Note
    ----
    v2 is conjugated for the product.

    Parameters
    ----------
    M : csr_matrix pointer
        Photodiode segementation matrix, should be Hermitian
    N : int
        Size of HOM matrix to extract from solvers
    mtx1, mtx2 : HOMSolver
        Matrix system solution to extract HOM vectors for
    node1_id, node2_id : int
        Node ID to extract vector information for
    f1_index, f2_index : int
        Frequency index to extract vector information for
    conjugate_result : bool
        Whether to conjugate result before summing to result pointer
    increment_ptr : complex*
        Pointer to incredment result of operation to
    """
    cdef complex z
    cdef Py_ssize_t _N = 0
    # Get optical field vector pointers
    cdef complex *E1 = mtx1.node_field_vector_fast(node1_id, f1_index, &_N)
    cdef complex *E2 = mtx2.node_field_vector_fast(node2_id, f2_index, &_N)
    # Compute vector matrix vector to compute
    # segmentation effects
    zcsrgecmv(M, E1, N, E2, N, &z)
    if conjugate_result:
        increment_ptr[0] += conj(z)
    else:
        increment_ptr[0] += z


cdef inline void do_zcsrgevmv2(
        csr_matrix *M,
        int N,
        HOMSolver mtx1,
        int node1_id,
        int f1_index,
        HOMSolver mtx2,
        int node2_id,
        int f2_index,
        bint conjugate_result,
        complex *increment_ptr
    ) noexcept:
    """Wrapper for computing:

    .. math::
        v2^T M v1

    where M is a CSR matrix and the v1 and v2 are HOM vectors
    extraced from different mtx solutions at a given node between two different
    frequencies. The result pointer value is incremented by the product.

    Note
    ----
    v2 is *NOT* conjugated for the product.

    Parameters
    ----------
    M : csr_matrix pointer
        Photodiode segementation matrix, should be Hermitian
    N : int
        Size of HOM matrix to extract from solvers
    mtx1, mtx2 : HOMSolver
        Matrix system solution to extract HOM vectors for
    node1_id, node2_id : int
        Node ID to extract vector information for
    f1_index, f2_index : int
        Frequency index to extract vector information for
    conjugate_result : bool
        Whether to conjugate result before summing to result pointer
    increment_ptr : complex*
        Pointer to incredment result of operation to
    """
    cdef complex z
    cdef Py_ssize_t _N = 0
    # Get optical field vector pointers
    cdef complex *E1 = mtx1.node_field_vector_fast(node1_id, f1_index, &_N)
    cdef complex *E2 = mtx2.node_field_vector_fast(node2_id, f2_index, &_N)
    # Compute vector matrix vector to compute
    # segmentation effects, no conjugation
    zcsrgevmv(M, E1, N, E2, N, &z)
    if conjugate_result:
        increment_ptr[0] += conj(z)
    else:
        increment_ptr[0] += z



### PD0 workspace & output funcs ###


cdef class PD0Workspace(MaskedDetectorWorkspace):
    def __init__(
            self,
            owner,
            BaseSimulation sim,
            values=None,
            *,
            oinfo=None,
            pdtype : dict = None
        ):
        super().__init__(owner, sim, values, oinfo=oinfo, needs_carrier=True)
        oinfo = self.oinfo
        ni = sim.carrier.get_node_info(oinfo.nodes[0])
        self.rhs_index = ni["rhs_index"]
        self.dc_node_id = sim.carrier.node_id(oinfo.nodes[0])

        if self.has_mask:
            if pdtype is not None:  # not supported yet
                raise NotImplementedError()
            else:
                self.set_output_fn(pd0_DC_output_masked)
        else:
            if pdtype is not None:
                #self.tmp = np.zeros(self.size, dtype=complex)
                self.K = pdtypes.construct_segment_beat_matrix(
                    sim.model.mode_index_map, pdtype, sparse_output=True
                )
                self.set_output_fn(pd0_DC_output_segmented)
            else:
                self.set_output_fn(pd0_DC_output)


pd0_DC_output = OutputFuncWrapper.make_from_ptr(c_pd0_DC_output)
cdef c_pd0_DC_output(DetectorWorkspace dws) :
    """This expects a `PD0Workspace` input. Fast computation of DC power at a node."""
    cdef:
        PD0Workspace ws = <PD0Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i, j
        double tmp = 0
        Py_ssize_t N = 0
        complex *E = NULL
        frequency_info_t *f1 = NULL
        Py_ssize_t Nf = carrier.optical_frequencies.size

    for i in range(Nf):
        f1 = &carrier.optical_frequencies.frequency_info[i]
        E = carrier.node_field_vector_fast(ws.dc_node_id, f1.index, &N)
        if E != NULL:
            for j in range(N):
                tmp += cnorm(E[j])

    return tmp * ws.sim.model_settings.EPSILON0_C * 0.5


pd0_DC_output_segmented = OutputFuncWrapper.make_from_ptr(c_pd0_DC_output_segmented)
cdef c_pd0_DC_output_segmented(DetectorWorkspace dws) :
    """This expects a `PD0Workspace` input. Fast computation of DC power at a node
    with segmentation assumed in the photodiode. Where :math:`E` is the vector of
    complex fields, and :math:`K` is a modal scattering Knm matrix describing the
    segmentation of a detector, the output is:
    .. math::
        E^{\ast} \cdot (K \cdot E)
    """
    cdef:
        PD0Workspace ws = <PD0Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i
        complex_t res = 0
        complex_t z = 0
        frequency_info_t *f1
        Py_ssize_t Nf = carrier.optical_frequencies.size
        Py_ssize_t N = 0
        const complex_t* E

    for i in range(Nf):
        f1 = &carrier.optical_frequencies.frequency_info[i]
        E = carrier.node_field_vector_fast(ws.dc_node_id, f1.index, &N)
        # Compute vector matrix vector
        zcsrgecmv(&ws.K.M, E, N, E, N, &z)
        res += z
    # Only select the real part of this
    return res.real * ws.sim.model_settings.EPSILON0_C * 0.5


pd0_DC_output_masked = OutputFuncWrapper.make_from_ptr(c_pd0_DC_output_masked)
cdef c_pd0_DC_output_masked(DetectorWorkspace dws) :
    """This expects a `PD0Workspace` input. Fast computation of DC power at a node where
    a HOM mask has been applied to the PD."""
    cdef:
        PD0Workspace ws = <PD0Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i, j, k
        Py_ssize_t freq_idx
        double tmp = 0
        frequency_info_t *f1
        Py_ssize_t Nf = carrier.optical_frequencies.size
        Py_ssize_t N = 0
        const complex_t* E

    for i in range(Nf):
        f1 = &carrier.optical_frequencies.frequency_info[i]
        E = carrier.node_field_vector_fast(ws.dc_node_id, f1.index, &N)
        for j in range(ws.num_unmasked_HOMs):
            tmp += cnorm(E[ws.unmasked_mode_indices[j]])

    return tmp * ws.sim.model_settings.EPSILON0_C * 0.5


### PD1 workspace & output funcs ###

cdef class PD1Values(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_2 ptr = (&self.f, &self.phase)
        cdef tuple params = ("f", "phase")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class PD1Workspace(MaskedDetectorWorkspace):
    def __cinit__(self, *args, **kwargs):
        self.num_pre_set_beats = 0
        self.pre_set_beats[0] = NULL
        self.pre_set_beats[1] = NULL

    def __init__(self, owner, sim, frequency : Parameter, phase : Parameter, *, phase_offset=0, oinfo=None, pdtype=None):
        assert(frequency is not None)
        if sim.signal:
            self.is_audio_mixing = check_is_fsig(sim.model, frequency)
        else:
            if check_is_fsig(sim.model, frequency):
                raise Exception(
                    f"Powerdetector {self} is demodulating at the signal frequency, but fsig is set to None"
                )
        if self.is_audio_mixing:
            super().__init__(owner, sim, PD1Values(), oinfo=oinfo, needs_signal=True, needs_carrier=True)
        else:
            super().__init__(owner, sim, PD1Values(), oinfo=oinfo, needs_carrier=True)
        self.cvalues = <PD1Values>self.values
        self.is_f_changing = frequency.is_changing
        self.is_phase_changing = phase.is_changing if phase is not None else False
        self.phase_offset = phase_offset
        self.homs = sim.model_settings.homs_view
        # store the node information for faster accesses
        self.dc_node_id = sim.carrier.node_id(self.oinfo.nodes[0])
        if sim.signal:
            self.ac_node_id = sim.signal.node_id(self.oinfo.nodes[0])
        # depeding on what the phase value is determines whether we
        # are doing a real or complex demodulation
        if self.is_phase_changing or (phase is not None and phase.value is not None):
            # We might change from None to some actual value
            self.output_real = True
            self.oinfo._set_dtype(np.float64)
        else:
            # If no phase defined output complex power
            self.output_real = False
            self.oinfo._set_dtype(np.complex128)
        # Determine if we are setting this workspace to be computing
        # some segmented photodiode
        self.is_segmented = pdtype is not None
        if self.is_segmented:
            if self.has_mask:
                raise NotImplementedError()
            else:
                self.K = pdtypes.construct_segment_beat_matrix(
                    sim.model.mode_index_map, pdtype, sparse_output=True
                )
        # Determine which fill function we need to use
        if self.is_audio_mixing:
            self.set_output_fn(pd1_AC_output)
        else:
            self.set_output_fn(pd1_DC_output)
        # precompute these things if nothing is changing
        if not self.is_f_changing:
            self.update_parameter_values()
            self.update_beats()

    cpdef update_beats(self) :
        """
        Requires full initialisation and `self.update_parameter_values` calling
        before using
        """
        cdef:
            list beats = []
            frequency_info_t *f1
            frequency_info_t *f2
            HOMSolver carrier = self.sim.carrier
            Py_ssize_t N1, N2
            Py_ssize_t i, j, n, prev_num_beats
            Py_ssize_t Nf = carrier.optical_frequencies.size

        self.update_parameter_values() # update values we might need
        prev_num_beats = self.num_pre_set_beats

        for i in range(Nf):
            f1 = &carrier.optical_frequencies.frequency_info[i]
            for j in range(Nf):
                f2 = &carrier.optical_frequencies.frequency_info[j]
                if abs((f1.f - f2.f) - self.cvalues.f) < 1e-14:
                    beats.append((
                        (self.dc_node_id, f1.index),
                        (self.dc_node_id, f2.index),
                    ))

        self.num_pre_set_beats = len(beats)

        if self.num_pre_set_beats > 0:
            if prev_num_beats > 0:
                self.pre_set_beats[0] = <complex**>realloc(
                    self.pre_set_beats[0],
                    self.num_pre_set_beats
                )
                if not self.pre_set_beats[0]:
                    raise MemoryError()
                self.pre_set_beats[1] = <complex**>realloc(
                    self.pre_set_beats[1],
                    self.num_pre_set_beats
                )
                if not self.pre_set_beats[1]:
                    raise MemoryError()
            else:
                self.pre_set_beats[0] = <complex**>calloc(
                    self.num_pre_set_beats,
                    sizeof(Py_ssize_t)
                )
                if not self.pre_set_beats[0]:
                    raise MemoryError()
                self.pre_set_beats[1] = <complex**>calloc(
                    self.num_pre_set_beats,
                    sizeof(Py_ssize_t)
                )
                if not self.pre_set_beats[1]:
                    raise MemoryError()

            for n in range(self.num_pre_set_beats):
                self.pre_set_beats[0][n] = carrier.node_field_vector_fast(beats[n][0][0], beats[n][0][1], &N1)
                self.pre_set_beats[1][n] = carrier.node_field_vector_fast(beats[n][1][0], beats[n][1][1], &N2)

                if N1 != N2 != self.sim.model_settings.num_HOMs:
                    raise RuntimeError("Mismatched HOM vector sizes")

        elif prev_num_beats > 0:
            self.__dealloc__()

    def __dealloc__(self):
        if self.pre_set_beats[0] != NULL:
            free(self.pre_set_beats[0])
        if self.pre_set_beats[1] != NULL:
            free(self.pre_set_beats[1])


pd1_AC_output = OutputFuncWrapper.make_from_ptr(c_pd1_AC_output)
cdef object c_pd1_AC_output(DetectorWorkspace dws) :
    """Computes a single signal frequency demodulation of some power output.
    This single function will handle:
        - masks
        - segmentation
        - neither

    Masks and segmentation are not supported at the same time.

    Parameters
    ----------
    dws : DetectorWorkspace
        Expects a `PD1Workspace` type

    Returns
    -------
    value : float or complex
        Demodulated power of signal frequency
    """
    cdef:
        PD1Workspace ws = <PD1Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        HOMSolver signal = ws.sim.signal
        frequency_info_t *f1,
        Py_ssize_t F, i, j, k
        Py_ssize_t m # mode index
        complex_t tmp, z
        complex_t *Ec
        complex_t *Es
        Py_ssize_t Nf = carrier.optical_frequencies.size
        Py_ssize_t Nc = 0
        Py_ssize_t Ns = 0
        double demod_phase = (ws.phase_offset + ws.cvalues.phase) * finesse.constants._DEG2RAD
    ws.Aij = 0
    if ws.is_segmented:
        for F in range(Nf):
            f1 = &carrier.optical_frequencies.frequency_info[F]
            # Get optical carrier field vector pointers
            Ec = carrier.node_field_vector_fast(ws.dc_node_id, f1.index, &Nc)
            # Next compute vector matrix vector to compute segmentation effects.
            # use hermitian conjugate option to conjugate carrier to multiple with
            # upper signal sideband
            Es = signal.node_field_vector_fast(ws.ac_node_id, f1.audio_upper_index, &Ns)
            zcsrgecmv(&ws.K.M, Ec, Nc, Es, Ns, &z)
            ws.Aij += z
            # lower sideband needs unconjugated carrier, as we compute
            # the conjugated lower sideband propagation
            Es = signal.node_field_vector_fast(ws.ac_node_id, f1.audio_lower_index, &Ns)
            zcsrgevmv(&ws.K.M, Ec, Nc, Es, Ns, &z)
            ws.Aij += z
    else:
        for F in range(Nf):
            f1 = &carrier.optical_frequencies.frequency_info[F]
            for k in range(ws.num_unmasked_HOMs):
                m = ws.unmasked_mode_indices[k]
                tmp = carrier.get_out_fast(ws.dc_node_id, f1.index, m)
                ws.Aij += conj(tmp) * signal.get_out_fast(ws.ac_node_id, f1.audio_upper_index, m)
                # lower sideband conjugate is modelled
                ws.Aij += tmp * signal.get_out_fast(ws.ac_node_id, f1.audio_lower_index, m)

    # Factor of two to undo 0.5 demodulation gain
    if ws.output_real:
        tmp = ws.Aij * cexp(-1j * demod_phase)
        return 2 * tmp.real * ws.sim.model_settings.EPSILON0_C * 0.5
    else:
        return 2 * ws.Aij * ws.sim.model_settings.EPSILON0_C * 0.5


pd1_DC_output = OutputFuncWrapper.make_from_ptr(c_pd1_DC_output)
cdef object c_pd1_DC_output(DetectorWorkspace dws) :
    """Computes a single RF demodulation of a power output.
    This single function will handle:
        - masks
        - segmentation
        - neither

    Masks and segmentation are not supported at the same time.

    Parameters
    ----------
    dws : DetectorWorkspace
        Expects a `PD1Workspace` type

    Returns
    -------
    value : float or complex
        Demodulated power
    """
    cdef:
        PD1Workspace ws = <PD1Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        frequency_info_t *f1
        frequency_info_t *f2
        Py_ssize_t i, j, k, n
        Py_ssize_t N = ws.sim.model_settings.num_HOMs
        Py_ssize_t N1, N2
        Py_ssize_t m # mode index
        complex_t tmp, z
        complex_t* E1
        complex_t* E2
        double demod_phase = (ws.phase_offset + ws.cvalues.phase) * finesse.constants._DEG2RAD

    ws.Aij = 0

    if ws.num_pre_set_beats > 0:
        if ws.is_segmented:
            for n in range(ws.num_pre_set_beats):
                # Get the RHS view indices
                E1 = ws.pre_set_beats[0][n]
                E2 = ws.pre_set_beats[1][n]
                # Compute vector matrix vector to compute
                # segmentation effects
                zcsrgecmv(&ws.K.M, E1, N, E2, N, &z)
                ws.Aij += z
        else:
            for n in range(ws.num_pre_set_beats):
                # Get the RHS view indices
                E1 = ws.pre_set_beats[0][n]
                E2 = ws.pre_set_beats[1][n]
                for k in range(ws.num_unmasked_HOMs):
                    m = ws.unmasked_mode_indices[k]
                    ws.Aij += E1[m] * conj(E2[m])
    else:
        # Do dumb thing and check everything if we have/can not optimise
        for i in range(carrier.optical_frequencies.size):
            f1 = &carrier.optical_frequencies.frequency_info[i]
            for j in range(carrier.optical_frequencies.size):
                f2 = &carrier.optical_frequencies.frequency_info[j]
                if float_eq(f1.f - f2.f, ws.cvalues.f):
                    if ws.is_segmented:
                        # get indicies pointing to start of particular frequency
                        i = carrier.field_fast(ws.dc_node_id, f1.index, 0)
                        j = carrier.field_fast(ws.dc_node_id, f2.index, 0)
                        # Get optical field vector pointers
                        E1 = carrier.node_field_vector_fast(ws.dc_node_id, f1.index, &N1)
                        E2 = carrier.node_field_vector_fast(ws.dc_node_id, f2.index, &N2)
                        # Compute vector matrix vector to compute
                        # segmentation effects
                        zcsrgecmv(&ws.K.M, E1, N1, E2, N2, &z)
                        ws.Aij += z
                    else:
                        for k in range(ws.num_unmasked_HOMs):
                            m = ws.unmasked_mode_indices[k]
                            ws.Aij += (carrier.get_out_fast(ws.dc_node_id, f1.index, m) *
                                conj(carrier.get_out_fast(ws.dc_node_id, f2.index, m)))

    if demod_phase:
        tmp = ws.Aij*cexp(-1j * demod_phase)
    else:
        tmp = ws.Aij

    if ws.output_real:
        return tmp.real * ws.sim.model_settings.EPSILON0_C * 0.5
    else:
        return tmp * ws.sim.model_settings.EPSILON0_C * 0.5



### PD2 workspace & output funcs ###


cdef class PD2Values(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_4 ptr = (&self.f1, &self.phase1, &self.f2, &self.phase2)
        cdef tuple params = ("f1", "phase1", "f2", "phase2")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class PD2Workspace(MaskedDetectorWorkspace):
    def __init__(self, owner, sim, f1, phase1, f2, phase2, *, phase1_offset=0, oinfo=None, pdtype=None):
        assert(phase1 is not None)
        assert(f1 is not None)
        assert(f2 is not None)
        if sim.signal:
            if check_is_fsig(sim.model, f1):
                raise Exception(
                    f"pd2 {self.name} f1 cannot be an audio frequency, use f2 for audio demodulation"
                )
            self.is_audio_mixing = check_is_fsig(sim.model, f2)

        if self.is_audio_mixing:
            super().__init__(owner, sim, PD2Values(), oinfo=oinfo, needs_carrier=True, needs_signal=True)
        else:
            super().__init__(owner, sim, PD2Values(), oinfo=oinfo, needs_carrier=True)

        self.cvalues = <PD2Values>self.values
        self.homs = sim.model_settings.homs_view
        self.dc_node_id = sim.carrier.node_id(self.oinfo.nodes[0])
        if sim.signal:
            self.ac_node_id = sim.signal.node_id(self.oinfo.nodes[0])

        if self.is_phase2_changing or (phase2 is not None and phase2.value is not None):
            # We might change from None to some actual value
            self.output_real = True
            self.oinfo._set_dtype(np.float64)
        else:
            # If no phase defined output complex power
            self.output_real = False
            self.oinfo._set_dtype(np.complex128)
        # Determine if we are setting this workspace to be computing
        # some segmented photodiode
        self.is_segmented = pdtype is not None
        if self.is_segmented:
            if self.has_mask:
                raise NotImplementedError()
            else:
                self.K = pdtypes.construct_segment_beat_matrix(
                    sim.model.mode_index_map, pdtype, sparse_output=True
                )
        # Choose the appropriate output function
        if self.is_audio_mixing:
            self.set_output_fn(pd2_AC_output)
        else:
            self.set_output_fn(pd2_DC_output)

        # if not ws.is_f1_changing and not (ws.is_f2_changing and ws.is_audio_mixing):
        #     # Sidebands beating together are known apriori if frequency bins are not
        #     # changing, or if this is just an audio mixer.
        #     ws.update_parameter_values()
        #     # If frequency is fixed then we just precompute the beats
        #     ws.update_beats()


pd2_DC_output = OutputFuncWrapper.make_from_ptr(c_pd2_DC_output)
cdef object c_pd2_DC_output(DetectorWorkspace dws) :
    """This expects a `PD2Workspace` input"""
    cdef:
        PD2Workspace ws = <PD2Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        frequency_info_t *f1
        frequency_info_t *f2
        Py_ssize_t i, j, k
        Py_ssize_t m # mode index
        complex_t tmp, phs
        double f_plus = ws.cvalues.f1 + ws.cvalues.f2
        double f_minus = ws.cvalues.f2 - ws.cvalues.f1
        Py_ssize_t Nf = carrier.optical_frequencies.size
        int N = ws.sim.model_settings.num_HOMs

    ws.z1 = 0
    ws.z2 = 0

    for i in range(Nf):
        f1 = &carrier.optical_frequencies.frequency_info[i]
        for j in range(Nf):
            f2 = &carrier.optical_frequencies.frequency_info[j]
            if f1.f - f2.f == f_plus:
                if ws.is_segmented:
                    do_zcsrgecmv(&ws.K.M, carrier, ws.dc_node_id, f2.index, f1.index, N, &ws.z1)
                else:
                    for k in range(ws.num_unmasked_HOMs):
                        m = ws.unmasked_mode_indices[k]
                        ws.z1 += (carrier.get_out_fast(ws.dc_node_id, f1.index, m) *
                            conj(carrier.get_out_fast(ws.dc_node_id, f2.index, m)))

            if f1.f - f2.f == f_minus:
                if ws.is_segmented:
                    do_zcsrgecmv(&ws.K.M, carrier, ws.dc_node_id, f2.index, f1.index, N, &ws.z1)
                else:
                    for k in range(ws.num_unmasked_HOMs):
                        m = ws.unmasked_mode_indices[k]
                        ws.z2 += (carrier.get_out_fast(ws.dc_node_id, f1.index, m) *
                            conj(carrier.get_out_fast(ws.dc_node_id, f2.index, m)))

    if ws.cvalues.phase1:
        phs = cexp(-1j * ws.cvalues.phase1 * finesse.constants._DEG2RAD)
        tmp = ws.z1 * phs + ws.z2 * conj(phs)
    else:
        tmp = ws.z1 + ws.z2

    if ws.cvalues.phase2:
        tmp *= cexp(-1j * ws.cvalues.phase2 * finesse.constants._DEG2RAD)

    # Factor 1/2 from demod gain
    # And a mystery factor of two to match up with v2
    if ws.output_real:
        return tmp.real * ws.sim.model_settings.EPSILON0_C * 0.5 * 0.5
    else:
        return tmp * ws.sim.model_settings.EPSILON0_C * 0.5 * 0.5


pd2_AC_output = OutputFuncWrapper.make_from_ptr(c_pd2_AC_output)
cdef object c_pd2_AC_output(DetectorWorkspace dws) :
    """This expects a `PD2Workspace` input"""
    cdef:
        PD2Workspace ws = <PD2Workspace> dws
        HOMSolver carrier = ws.sim.carrier
        HOMSolver signal = ws.sim.signal
        frequency_info_t *f1
        frequency_info_t *f2
        Py_ssize_t i, j, k
        Py_ssize_t m # mode index
        complex_t tmp, phs, car1, car2
        double df
        Py_ssize_t Nf = carrier.optical_frequencies.size
        int N = ws.sim.model_settings.num_HOMs

    ws.z1 = 0
    ws.z2 = 0
    phs = cexp(-1j * ws.cvalues.phase1 * finesse.constants._DEG2RAD)

    # Here we loop over each of the carrier beats and apply the relevant signal sideband
    # beats. This should be the equivalent code in readout elements but they fill the maxtrix
    # instead.
    for i in range(Nf):
        f1 = &carrier.optical_frequencies.frequency_info[i]
        for j in range(Nf):
            f2 = &carrier.optical_frequencies.frequency_info[j]
            df = f1.f - f2.f
            if float_eq(df, -ws.cvalues.f1):
                # negative beats get negative demod phase
                if ws.is_segmented:
                    # Compute E(carrier)^T @ K @ E(lower)^*
                    do_zcsrgevmv2(
                        &ws.K.M, N,
                        signal, ws.ac_node_id, f2.audio_lower_index,
                        carrier, ws.dc_node_id, f1.index,
                        False, &ws.z2
                    )
                    # Compute E(carrier)^H @ K @ E(upper)
                    do_zcsrgecmv2(
                        &ws.K.M, N,
                        signal, ws.ac_node_id, f1.audio_upper_index,
                        carrier, ws.dc_node_id, f2.index,
                        False, &ws.z2
                    )
                else:
                    for k in range(ws.num_unmasked_HOMs):
                        m = ws.unmasked_mode_indices[k]
                        car1 = carrier.get_out_fast(ws.dc_node_id, f1.index, m)
                        ws.z2 += car1 * signal.get_out_fast(ws.ac_node_id, f2.audio_lower_index, m)

                        car2 = carrier.get_out_fast(ws.dc_node_id, f2.index, m)
                        ws.z2 += signal.get_out_fast(ws.ac_node_id, f1.audio_upper_index, m) * conj(car2)

            if float_eq(df, ws.cvalues.f1):
                # positive beats get positive demod phase
                if ws.is_segmented:
                    # Compute E(carrier)^T @ K @ E(lower)^*
                    do_zcsrgevmv2(
                        &ws.K.M, N,
                        signal, ws.ac_node_id, f2.audio_lower_index,
                        carrier, ws.dc_node_id, f1.index,
                        False, &ws.z1
                    )
                    # Compute E(carrier)^H @ K @ E(upper)
                    do_zcsrgecmv2(
                        &ws.K.M, N,
                        signal, ws.ac_node_id, f1.audio_upper_index,
                        carrier, ws.dc_node_id, f2.index,
                        False, &ws.z1
                    )
                else:
                    for k in range(ws.num_unmasked_HOMs):
                        m = ws.unmasked_mode_indices[k]
                        car1 = carrier.get_out_fast(ws.dc_node_id, f1.index, m)
                        ws.z1 += car1 * signal.get_out_fast(ws.ac_node_id, f2.audio_lower_index, m)

                        car2 = carrier.get_out_fast(ws.dc_node_id, f2.index, m)
                        ws.z1 += signal.get_out_fast(ws.ac_node_id, f1.audio_upper_index, m) * conj(car2)

    # 1/2 from cos(X)*cos(Y) = 1/2(cos(X+Y)+cos(X-Y)) expansion
    tmp = (ws.z1 * phs + ws.z2 * conj(phs)) * 0.5

    if ws.cvalues.phase2:
       tmp *= cexp(-1j * ws.cvalues.phase2 * finesse.constants._DEG2RAD)

    # Factor of two because of signal scaling
    if ws.output_real:
        return 2 * tmp.real * ws.sim.model_settings.EPSILON0_C * 0.5
    else:
        return 2 * tmp * ws.sim.model_settings.EPSILON0_C * 0.5


# ### Generic (slower) PD workspace & output funcs ###
# TODO ddb this all needs changing over to use the SparseMatrixSimulation
# class, which as none of this is used anywhere really I can't be bothered doing
# right now, as I'm not sure if any of this have any valid test cases
# cdef class PDWorkspace(DetectorWorkspace):
#     cdef:
#         public BaseSimulation DC
#         public BaseSimulation AC
#         public Py_ssize_t dc_node_id
#         public Py_ssize_t ac_node_id
#         public int[:, ::1] homs
#         const int[:, ::1] mask
#         bint mode_is_network
#         double[:, :, :, ::1] beat_factors
#         Py_ssize_t num_demod
#         Py_ssize_t num_mixes
#         double[:, ::1] fmix_view
#         double EPSILON0_C
#         complex_t[::1] zview

#     def __init__(self,
#                 owner,
#                 sims,
#                 int N_demods,
#                 double EPSILON0_C,
#                 const int[:, ::1] mask,
#                 bint mode_is_network,
#                 beat_factors=None):

#         super().__init__(owner, sims)
#         self.EPSILON0_C = EPSILON0_C
#         self.mask = mask
#         self.mode_is_network = mode_is_network
#         self.beat_factors = beat_factors
#         # Computing values and allocating arrays that will be used throughout
#         # the simulation output calculations
#         self.num_demod = N_demods
#         self.num_mixes = 1 + self.num_demod * (self.num_demod - 1) / 2
#         self.fmix_view = np.ones((self.num_mixes, self.num_demod))
#         self.zview = np.zeros(self.num_mixes, dtype=np.complex128)
#         # TODO ddb - I think the mix table only needs to be made once
#         # Might need to update if the demod frequencies change
#         _create_mix_table(self.num_demod, self.fmix_view)

# def mixer_pd_output(PDWorkspace ws,
#                     double[::1] freqs,
#                     double[::1] phases,
#                     long long[::1] max_phase_indices
# ):
#     cdef:
#         Py_ssize_t mix_index
#         double f_ref
#         complex_t dm_amp
#         complex_t power
#         # Flag for whether this pd is computing purely a transfer function
#         # TODO: Is this really needed, or just an artifact from the past?
#         int transfer = 0

#     for mix_index in range(ws.num_mixes):
#         f_ref = _get_reference_freq(ws.num_demod, mix_index, ws.fmix_view, freqs)
#         if ws.beat_factors is not None:
#             ws.zview[mix_index] = compute_amplitude_beats(ws, &transfer, f_ref)
#         else:
#             ws.zview[mix_index] = compute_amplitude(ws, &transfer, f_ref)

#     dm_amp = _set_demodulation_phase(
#         ws.num_demod, ws.zview, ws.fmix_view, ws.num_mixes, phases, max_phase_indices
#     )
#     power = _get_demodulation_signal(
#         ws.num_demod, dm_amp, phases, max_phase_indices, ws.EPSILON0_C, ws.mode_is_network, transfer
#     )

#     return power


# cdef _create_mix_table(Py_ssize_t num_demod, double[:, ::1] fmix_view) noexcept:
#     cdef:
#         int num_mixes = 1

#         Py_ssize_t demod_index_outer, demod_index_inner, mix_permutation_index

#         np.ndarray[double, ndim=1] fmix_tmp = np.ones(num_demod)
#         double[::1] fmix_tmp_view = fmix_tmp

#     for demod_index_outer in range(1, num_demod):
#         for mix_permutation_index in range(demod_index_outer, 0, -1):
#             num_mixes += 1
#             fmix_tmp_view[mix_permutation_index - 1] *= -1

#             for demod_index_inner in range(num_demod):
#                 fmix_view[num_mixes - 1][demod_index_inner] = fmix_tmp_view[demod_index_inner]


# def dc_pd_output(PDWorkspace ws):
#     cdef:
#         complex_t power = COMPLEX_0
#         int transfer = 0

#     if ws.beat_factors is not None:
#         power = compute_amplitude_beats(ws, &transfer)
#     else:
#         power = compute_amplitude(ws, &transfer)

#     return power.real * ws.EPSILON0_C * 0.5


# cdef double _get_reference_freq(
#     Py_ssize_t num_demod,
#     Py_ssize_t mix_index,
#     double[:, ::1] fmix_view,
#     double[::1] freqs
# ) noexcept nogil:
#     cdef:
#         double f_ref = 0.0
#         Py_ssize_t demod_index

#     for demod_index in range(num_demod):
#         f_ref += fmix_view[mix_index][demod_index] * freqs[demod_index]

#     return f_ref



# cdef complex_t _set_demodulation_phase(
#     Py_ssize_t num_demod,
#     complex_t[::1] zview,
#     double[:, ::1] fmix_view,
#     Py_ssize_t num_mixes,
#     double[::1] phases,
#     long long[::1] max_phase_indices
# ) noexcept nogil:
#     cdef:
#         Py_ssize_t demod_index, mix_index
#         complex_t demod_amp = COMPLEX_0

#         complex_t z1, z2
#         double phi_max

#         double* phi = <double*> calloc(num_mixes, sizeof(double))

#     for demod_index in range(num_demod - 1):
#         z1 = COMPLEX_0
#         z2 = COMPLEX_0
#         # max phase
#         if in_index_array(max_phase_indices, demod_index):
#             for mix_index in range(num_mixes):
#                 if fmix_view[mix_index][demod_index] < 0.0:
#                     z1 += zview[mix_index]
#                 else:
#                     z2 += zview[mix_index]

#             phi_max = 0.5 * (carg(z2) - carg(z1))
#             phases[demod_index] = phi_max

#             for mix_index in range(num_mixes):
#                 phi[mix_index] -= phi_max * fmix_view[mix_index][demod_index]
#         # user defined phase
#         else:
#             for mix_index in range(num_mixes):
#                 phi[mix_index] -= (
#                     phases[demod_index] * fmix_view[mix_index][demod_index]
#                 )

#     for mix_index in range(num_mixes):
#         demod_amp += crotate(zview[mix_index], phi[mix_index])

#     free(phi)

#     return demod_amp


# cdef complex_t _get_demodulation_signal(
#     Py_ssize_t num_demod,
#     complex_t demod_amp,
#     double[::1] phases,
#     long long[::1] max_phase_indices,
#     double epsilon0_c,
#     bint mode_is_network,
#     int transfer
# ) noexcept nogil:
#     cdef:
#         complex_t z = demod_amp

#     if not mode_is_network:
#         if in_index_array(max_phase_indices, num_demod - 1):
#             z = cabs(demod_amp)
#         else:
#             z = (
#                 creal(demod_amp) * cos(phases[num_demod - 1])
#                 + cimag(demod_amp) * sin(phases[num_demod - 1])
#             )

#     z *= 0.5**(num_demod - 1)

#     if transfer == 2:
#         z *= 2

#     return z * epsilon0_c * 0.5

# cdef complex_t compute_amplitude(
#     PDWorkspace ws,
#     int *transfer,
#     double f_ref=NAN
# ) noexcept:
#     cdef:
#         complex_t amplitude = COMPLEX_0

#         Py_ssize_t field_idx
#         Py_ssize_t N = ws.homs.shape[0]
#         int n, m
#         bint mixed = False

#     if not isnan(f_ref):
#         mixed = True

#     for field_idx in range(N):
#         n = ws.homs[field_idx][0]
#         m = ws.homs[field_idx][1]

#         if in_mask(n, m, ws.mask):
#             continue

#         amplitude += compute_mode_amplitude(
#                 carrier,
#                 signal,
#                 ws.dc_node_id,
#                 ws.ac_node_id,
#                 field_idx,
#                 field_idx,
#                 transfer,
#                 f_ref,
#                 mixed
#         )

#     return amplitude


# cdef complex_t compute_amplitude_beats(
#     PDWorkspace ws,
#     int *transfer,
#     double f_ref=NAN
# ) noexcept:
#     cdef:
#         complex_t amplitude = COMPLEX_0

#         Py_ssize_t N = ws.homs.shape[0]
#         Py_ssize_t field_idx_outer, field_idx_inner
#         int n1, m1, n2, m2
#         double pd_factor
#         bint mixed = False

#     if ~isnan(f_ref):
#         mixed = True

#     for field_idx_outer in range(N):
#         n1 = ws.homs[field_idx_outer][0]
#         m1 = ws.homs[field_idx_outer][1]

#         # TODO ddb : probably worth changing ws.mask to a list of included
#         # mode indicies rather than checking all the time
#         if in_mask(n1, m1, ws.mask):
#             continue

#         for field_idx_inner in range(N):
#             n2 = ws.homs[field_idx_inner][0]
#             m2 = ws.homs[field_idx_inner][1]

#             pd_factor = ws.beat_factors [n1][m1][n2][m2]
#             if pd_factor == 0.0:
#                 continue

#             amplitude += compute_mode_amplitude(
#                     carrier,
#                     signal,
#                     ws.dc_node_id,
#                     ws.ac_node_id,
#                     field_idx_outer,
#                     field_idx_inner,
#                     transfer,
#                     f_ref,
#                     mixed
#             ) * pd_factor

#     return amplitude


# cdef complex_t compute_mode_amplitude(
#     BaseSimulation DC,
#     BaseSimulation AC,
#     Py_ssize_t dc_node_id,
#     Py_ssize_t ac_node_id,
#     Py_ssize_t field_idx_outer,
#     Py_ssize_t field_idx_inner,
#     int *transfer,
#     double f_ref,
#     bint mixed
# ) noexcept nogil:
#     cdef:
#         Py_ssize_t i, j

#         complex_t inner, outer
#         complex_t amplitude = COMPLEX_0

#         frequency_info_t f1, f2

#     for i in range(DC.num_frequencies):
#         f1 = DC.frequency_info[i]
#         outer = DC.get_out_fast(dc_node_id, f1.index, field_idx_outer)
#         for j in range(DC.num_frequencies):
#             f2 = DC.frequency_info[j]
#             if mixed:
#                 if not float_eq(f1.f - f2.f, f_ref):
#                     continue
#             else:
#                 if not float_eq(f1.f, f2.f):
#                     continue

#             transfer[0] |= 1
#             inner = DC.get_out_fast(dc_node_id, f2.index, field_idx_inner)
#             amplitude += outer * conj(inner)

#         if not mixed or AC is None:
#             continue

#         for j in range(AC.num_frequencies):
#             f2 = AC.frequency_info[j]

#             if not float_eq(f1.f - f2.f, f_ref):
#                 continue

#             transfer[0] |= 2

#             inner = AC.get_out_fast(ac_node_id, f2.index, field_idx_inner)

#             if f2.audio_order < 0:
#                 amplitude += outer * inner
#             else:
#                 amplitude += outer * conj(inner)

#     if AC is not None and mixed:
#         for i in range(AC.num_frequencies):
#             f1 = AC.frequency_info[i]
#             outer = AC.get_out_fast(ac_node_id, f1.index, field_idx_outer)
#             if f1.audio_order < 0:
#                 outer = conj(outer)
#             for j in range(DC.num_frequencies):
#                 f2 = DC.frequency_info[j]

#                 if not float_eq(f1.f - f2.f, f_ref):
#                     continue

#                 transfer[0] |= 2

#                 inner = DC.get_out_fast(dc_node_id, f2.index, field_idx_inner)

#                 amplitude += outer * conj(inner)

#     return amplitude


# cdef bint in_index_array(long long[::] indices, Py_ssize_t idx) noexcept nogil:
#     cdef:
#         Py_ssize_t i
#         Py_ssize_t N = indices.shape[0]

#     for i in range(N):
#         if indices[i] == idx:
#             return True

#     return False
