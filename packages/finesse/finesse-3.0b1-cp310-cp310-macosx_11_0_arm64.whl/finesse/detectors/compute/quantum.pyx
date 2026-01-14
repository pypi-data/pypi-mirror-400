#cython: boundscheck=False, wraparound=False, initializedcheck=False

cimport numpy as np
import numpy as np

from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport cabs, cexp, conj, creal, crotate
from finesse.cymath.math cimport isfinite, float_eq, nmax, radians, sqrt, NAN
from finesse.components.node import NodeType
from finesse.detectors.workspace cimport (
    DetectorWorkspace,
    OutputFuncWrapper,
)
from finesse.detectors.compute.power cimport (
    PD1Workspace,
    PD2Workspace,
    c_pd1_AC_output,
    c_pd2_AC_output,
)
from finesse.frequency cimport frequency_info_t, FrequencyContainer
from finesse.element_workspace cimport BaseCValues
from finesse.simulations.homsolver cimport HOMSolver
from finesse.simulations.sparse.solver cimport SparseSolver

cdef extern from "constants.h":
    long double H_PLANCK
    double ROOT2

ctypedef (double*, double*) ptr_tuple_2
ctypedef (double*, double*, double*, double*) ptr_tuple_4
ctypedef (double*, double*, double*, double*, double*, double*) ptr_tuple_6

# The names of these f, f1,f2,f3 etc. have to match the model parameters
# defined by the owner. Which is a bit annoying.

cdef class QND1Values(BaseCValues):
    cdef public:
        double f, phase

    def __init__(self):
        cdef ptr_tuple_2 ptr = (&self.f, &self.phase)
        cdef tuple params = ("f", "phase")
        self.setup(params, sizeof(ptr), <double**>&ptr)

cdef class QNDNValues(BaseCValues):
    cdef public:
        double f1, phase1
        double f2, phase2
        double f3, phase3

    def __init__(self):
        cdef ptr_tuple_6 ptr = (
                &self.f1, &self.phase1, &self.f2, &self.phase2, &self.f3, &self.phase3
                )
        cdef tuple params = ("f1", "phase1", "f2", "phase2", "f3", "phase3")
        self.setup(params, sizeof(ptr), <double**>&ptr)

cdef class QND0Workspace(DetectorWorkspace):
    cdef:
        complex_t[::1] s
        complex_t[::1] source_s
        complex_t[::1] cov
        PD1Workspace pd_ws
        int dc_node_id
        int ac_node_id
        int rhs_index
        int neq
        bint nsr

    def __init__(self, owner, sim, nsr, sources, exclude_sources):
        super().__init__(owner, sim, needs_noise=True)

        self.dc_node_id = sim.carrier.node_id(owner.node)
        self.ac_node_id = sim.signal.node_id(owner.node)
        self.neq = sim.signal.M().num_equations
        self.s = np.zeros(self.neq, dtype=np.complex128)
        self.source_s = np.empty(self.neq, dtype=np.complex128)
        self.set_output_fn(qnd0_output)

        self.rhs_index = self.owner._requested_selection_vectors[self.owner.name]

        self.nsr = nsr
        if self.nsr:
            self.pd_ws = PD1Workspace(owner, sim, sim.model.fsig.f, None)

        if sources:
            self.source_s[:] = 0
        elif exclude_sources:
            self.source_s[:] = 1
        if sources:
            self.fill_source_selection_vector(sources, 1)
        if exclude_sources:
            self.fill_source_selection_vector(exclude_sources, 0)

    cpdef fill_selection_vector(self) :
        cdef:
            HOMSolver carrier = self.sim.carrier
            HOMSolver signal = self.sim.signal
            Py_ssize_t i, j
            Py_ssize_t s_idx
            frequency_info_t fc, fs
            complex_t tmp

        self.update_parameter_values()
        for i in range(signal.optical_frequencies.size):
            fs = signal.optical_frequencies.frequency_info[i]
            fc = carrier.optical_frequencies.frequency_info[fs.audio_carrier_index]
            for j in range(nmax(signal.nhoms, 1)):
                s_idx = signal.field_fast(self.ac_node_id, fs.index, j)
                tmp = carrier.get_out_fast(self.dc_node_id, fc.index, j) * ROOT2
                if fs.audio_order > 0:
                    self.s[s_idx] = tmp
                else:
                    self.s[s_idx] = conj(tmp)

        for i in range(self.neq):
            signal.set_source_fast_3(i, self.s[i], self.rhs_index)

    cdef fill_source_selection_vector(self, sources, complex_t fill_value) :
        cdef:
            Py_ssize_t i, j
            Py_ssize_t node_id
            Py_ssize_t idx
            FrequencyContainer frequencies
            HOMSolver signal = self.sim.signal

        for comp in sources:
            for node_name in comp.nodes:
                if node_name not in signal.nodes:
                    continue
                node = signal.nodes[node_name]
                node_id = signal.node_id(node)
                if node.type == NodeType.OPTICAL:
                    for i in range(signal.optical_frequencies.size):
                        fs = signal.optical_frequencies.frequency_info[i]
                        for j in range(nmax(signal.nhoms, 1)):
                            idx = signal.field_fast(node_id, fs.index, j)
                            self.source_s[idx] = fill_value
                else:
                    if node.type == NodeType.MECHANICAL:
                        frequencies = signal.signal_frequencies[node]
                    elif node.type == NodeType.ELECTRICAL:
                        frequencies = signal.signal_frequencies[node]
                    else:
                        continue
                    for i in range(frequencies.size):
                        fs = frequencies.frequency_info[i]
                        idx = signal.field_fast(node_id, fs.index)
                        self.source_s[idx] = fill_value

    cpdef get_source_selection_vector(self) :
        return self.source_s

    cpdef set_covariance_matrix(self, complex_t[::1] v, unicode name) :
        # TODO: Should this be a copy?
        self.cov = v

qnd0_output = OutputFuncWrapper.make_from_ptr(c_qnd0_output)
cdef object c_qnd0_output(DetectorWorkspace self) :
    cdef:
        QND0Workspace ws = <QND0Workspace> self
        double rtn = 0
        double f0 = ws.sim.model_settings.f0
        double unit_vacuum = ws.sim.model_settings.UNIT_VACUUM
        double nf_factor = 0.25**1  # factor 0.25 per demodulation
        complex_t pdo
    for i in range(ws.neq):
        rtn += creal(ws.cov[i] * conj(ws.s[i]))
    # Compensate for demod 0.5 factor when demodulating a signal
    # frequency as this is what a network analyser would do.
    rtn *= 2

    if ws.nsr:
        pdo = c_pd1_AC_output(ws.pd_ws)
        rtn /= pdo.real * pdo.real + pdo.imag * pdo.imag

    return sqrt(
        unit_vacuum
        * rtn
        * H_PLANCK
        * f0
        * nf_factor
    )

cdef class QNDNWorkspace(DetectorWorkspace):
    cdef:
        complex_t[::1] s
        complex_t[::1] source_s
        complex_t[::1] cov
        DetectorWorkspace pd_ws
        int num_demod
        int Ndm
        int Nf
        int dc_node_id
        int ac_node_id
        int rhs_index
        long[:, ::1] demod_vac_contri
        long[:, ::1] demod_vac_contri_phi
        long[::1] demod_f_sig
        double[::1] demod_f
        double[::1] demod_phi
        QNDNValues cvalues
        bint nsr

        double[::1] freqs
        double[::1] phases
        int neq
        list carrier_demods

    def __init__(self, owner, sim, carrier_demods, nsr, sources, exclude_sources):
        assert(sim.signal is not None)
        assert(isinstance(sim.signal, SparseSolver))

        self.carrier_demods = carrier_demods
        num_carrier_demod = len(carrier_demods)
        if num_carrier_demod == 1:
            _values = QND1Values()
        else:
            _values = QNDNValues()
        super().__init__(owner, sim, _values, needs_noise=True)
        self.cvalues = <QNDNValues>self.values

        self.dc_node_id = self.sim.carrier.node_id(owner.node)
        self.ac_node_id = self.sim.signal.node_id(owner.node)
        self.set_output_fn(qndN_output)

        self.neq = self.sim.signal.M().num_equations
        # N demodulations, so we have a maximum of 2**N signal frequencies for each carrier
        # frequency, and each signal frequency can only have a maximum of 2**N contributing carrier
        # frequencies
        self.num_demod = num_carrier_demod + 1
        self.Ndm = int(2**self.num_demod)
        self.Nf = self.Ndm * self.sim.carrier.optical_frequencies.size
        self.demod_vac_contri = np.empty((self.Nf, self.Ndm), dtype=np.dtype("long"))
        self.demod_vac_contri_phi = np.empty((self.Nf, self.Ndm), dtype=np.dtype("long"))
        self.demod_f = np.full(self.Nf, np.nan, dtype=np.float64)
        self.demod_f_sig = np.zeros(self.Nf, dtype=np.dtype("long"))
        self.demod_phi = np.full(self.Ndm, np.nan, dtype=np.float64)
        self.s = np.zeros(self.neq, dtype=np.complex128)
        self.source_s = np.empty(self.neq, dtype=np.complex128)

        self.rhs_index = self.owner._requested_selection_vectors[self.owner.name]

        self.freqs = np.empty(self.num_demod, dtype=np.float64)
        self.phases = np.empty(self.num_demod, dtype=np.float64)

        self.nsr = nsr
        if self.nsr:
            # ddb todo: add more options here
            if num_carrier_demod == 1:
                # 1RF + 1fsig demodulation
                self.pd_ws = PD2Workspace(
                    owner,
                    sim,
                    carrier_demods[0][0],
                    carrier_demods[0][1],
                    sim.model.fsig.f,
                    None
                )
            else:
                raise NotImplementedError(f"Not yet implemented to calculate NSR for {num_carrier_demod} RF carrier demodulations")

        if sources:
            self.source_s[:] = 0
        elif exclude_sources:
            self.source_s[:] = 1
        if sources:
            self.fill_source_selection_vector(sources, 1)
        if exclude_sources:
            self.fill_source_selection_vector(exclude_sources, 0)

    cdef fill_carrier_qnoise_contributions(self) :
        cdef:
            Py_ssize_t i, j, k, nf
            Py_ssize_t base_idx
            frequency_info_t f
            double freq
            HOMSolver signal = self.sim.signal

        self.freqs[0] = self.cvalues.f1
        self.phases[0] = self.cvalues.phase1
        if self.num_demod > 2:
            self.freqs[1] = self.cvalues.f2
            self.phases[1] = self.cvalues.phase2
        if self.num_demod > 3:
            self.freqs[2] = self.cvalues.f3
            self.phases[2] = self.cvalues.phase3
        self.freqs[self.num_demod - 1] = self.sim.model_settings.fsig
        self.phases[self.num_demod - 1] = 0  # fsig demod doesn't affect result, so assume 0

        self.demod_phi[:] = 0
        for i in range(self.Ndm):
            for j in range(self.num_demod):
                if (i >> j) & 0x01:
                    self.demod_phi[i] += self.phases[j]
                else:
                    self.demod_phi[i] -= self.phases[j]
            self.demod_phi[i] = radians(self.demod_phi[i])

        self.demod_f[:] = 0
        for i in range(self.sim.carrier.optical_frequencies.size):
            f = self.sim.carrier.optical_frequencies.frequency_info[i]
            base_idx = i * self.Ndm
            for j in range(self.Ndm):
                self.demod_f[base_idx + j] = f.f
                for k in range(self.num_demod):
                    if (j >> k) & 0x01:
                        self.demod_f[base_idx + j] += self.freqs[k]
                    else:
                        self.demod_f[base_idx + j] -= self.freqs[k]

        # Use -1 to signal empty entries
        self.demod_f_sig[:] = -1
        self.demod_vac_contri[:] = -1

        # Check all frequencies to see if they match up to any signal sidebands
        for i in range(self.sim.carrier.optical_frequencies.size):
            f = self.sim.carrier.optical_frequencies.frequency_info[i]
            base_idx = i * self.Ndm
            for nf in range(self.Ndm):
                freq = self.demod_f[base_idx + nf]
                for j in range(self.Nf):
                    # Check frequencies against any existing signals
                    for k in range(signal.optical_frequencies.size):
                        if float_eq(self.demod_f[j], signal.optical_frequencies.frequency_info[k].f):
                            self.demod_f_sig[j] = k
                            break
                    if self.demod_f_sig[j] != -1:
                        continue
                    # If no signal frequency could be found then this is a pure
                    # vacuum noise field so need to add it to the contribution list
                    if float_eq(freq, self.demod_f[j]):
                        # If we have already found another item with this
                        # carrier frequency then these noises are correlated
                        for k in range(self.Ndm):
                            if self.demod_vac_contri[j][k] == -1:
                                self.demod_vac_contri[j][k] = f.index
                                self.demod_vac_contri_phi[j][k] = nf
                                break
                        break

    cpdef fill_selection_vector(self) :
        cdef:

            Py_ssize_t i, j, k
            Py_ssize_t f_idx, s_idx
            frequency_info_t fc, fs
            complex_t tmp
            HOMSolver signal = self.sim.signal
            HOMSolver carrier = self.sim.carrier

        self.update_parameter_values()
        self.fill_carrier_qnoise_contributions()

        self.s[:] = 0
        # For each carrier field check if the corresponding demodulated
        # frequency is a signal sideband. If so, we need to include it in the
        # selection vector.
        for i in range(self.sim.carrier.optical_frequencies.size):
            fc = self.sim.carrier.optical_frequencies.frequency_info[i]
            for j in range(self.Ndm):
                # If this is a signal sideband frequency this is the
                # product between the i'th carrier and this.
                f_idx = self.demod_f_sig[i * self.Ndm + j]
                if f_idx >= 0:
                    fs = signal.optical_frequencies.frequency_info[f_idx]
                    for k in range(nmax(signal.nhoms, 1)):
                        s_idx = signal.field_fast(self.ac_node_id, fs.index, k)
                        tmp = carrier.get_out_fast(self.dc_node_id, fc.index, k) * ROOT2
                        tmp = crotate(tmp, self.demod_phi[j])
                        if fs.audio_order > 0:
                            self.s[s_idx] = self.s[s_idx] + tmp
                        else:
                            self.s[s_idx] = self.s[s_idx] + conj(tmp)

        for i in range(self.neq):
            signal.set_source_fast_3(i, self.s[i], self.rhs_index)

    cdef fill_source_selection_vector(self, sources, complex_t fill_value) :
        cdef:
            Py_ssize_t i, j
            Py_ssize_t node_id
            Py_ssize_t idx
            FrequencyContainer frequencies
            HOMSolver signal = self.sim.signal

        for comp in sources:
            for node_name in comp.nodes:
                if node_name not in signal.nodes:
                    continue
                node = signal.nodes[node_name]
                node_id = signal.node_id(node)
                if node.type == NodeType.OPTICAL:
                    for i in range(signal.optical_frequencies.size):
                        fs = signal.optical_frequencies.frequency_info[i]
                        for j in range(nmax(signal.nhoms, 1)):
                            idx = signal.field_fast(node_id, fs.index, j)
                            self.source_s[idx] = fill_value
                else:
                    if node.type == NodeType.MECHANICAL:
                        frequencies = signal.signal_frequencies[node]
                    elif node.type == NodeType.ELECTRICAL:
                        frequencies = signal.signal_frequencies[node]
                    else:
                        continue
                    for i in range(frequencies.size):
                        fs = frequencies.frequency_info[i]
                        idx = signal.field_fast(node_id, fs.index, 0)
                        self.source_s[idx] = fill_value

    cpdef get_source_selection_vector(self) :
        return self.source_s

    cpdef set_covariance_matrix(self, complex_t[::1] v, unicode name) :
        # TODO: Should this be a copy?
        self.cov = v


qndN_output = OutputFuncWrapper.make_from_ptr(c_qndN_output)
cdef object c_qndN_output(DetectorWorkspace self) :
    cdef:
        QNDNWorkspace ws = <QNDNWorkspace> self
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i, j, k
        Py_ssize_t Nhom = max(ws.sim.signal.nhoms, 1)
        double rtn = 0
        double f
        double f0 = ws.sim.model_settings.f0
        double unit_vacuum = ws.sim.model_settings.UNIT_VACUUM
        double nf_factor = 0.25**ws.num_demod  # factor 0.25 per demodulation
        complex_t pdo
        complex_t car_sum

    for i in range(ws.neq):
        rtn += creal(ws.cov[i] * conj(ws.s[i]))

    # Pick up pure vacuum noise and demodulate that into our signal.
    for i in range(ws.Nf):
        f = ws.demod_f[i]
        car_sum = 0
        for j in range(Nhom):
            for k in range(ws.Ndm):
                if ws.demod_vac_contri[i][k] == -1:
                    break
                car_sum += crotate(
                        carrier.get_out_fast(ws.dc_node_id, ws.demod_vac_contri[i][k], j),
                        # FIXME: There should be a minus sign here, why isn't there?
                        ws.demod_phi[ws.demod_vac_contri_phi[i][k]]
                        )
            rtn += cabs(car_sum)**2 * (1 + f / f0)

    if ws.nsr:
        if ws.num_demod == 2:
            (<PD2Workspace>ws.pd_ws).cvalues.f1 = ws.cvalues.f1
            (<PD2Workspace>ws.pd_ws).cvalues.phase1 = ws.cvalues.phase1
            (<PD2Workspace>ws.pd_ws).cvalues.f2 = 0
            (<PD2Workspace>ws.pd_ws).cvalues.phase2 = 0
        else:
            raise ValueError(f"Can't calculate NSR for {ws.num_demod-1} RF demodulations")
        pdo = c_pd2_AC_output(ws.pd_ws)
        rtn /= pdo.real * pdo.real + pdo.imag * pdo.imag

    # Compensate for demod 0.5 factor when demodulating a signal
    # frequency as this is what a network analyser would do.
    rtn *= 2

    return sqrt(
        unit_vacuum
        * rtn
        * H_PLANCK
        * f0
        * nf_factor
    )

cdef class QShot0Workspace(DetectorWorkspace):
    cdef:
        PD1Workspace pd_ws
        int Nf
        int dc_node_id
        int ac_node_id
        long[:, ::1] demod_vac_contri
        double[::1] demod_f
        bint nsr

    def __init__(self, owner, sim, nsr, *, output_info=None):
        assert(sim.signal is not None)
        super().__init__(owner, sim, oinfo=output_info, needs_noise=True)

        self.dc_node_id = self.sim.carrier.node_id(self.oinfo.nodes[0])
        self.ac_node_id = self.sim.signal.node_id(self.oinfo.nodes[0])
        self.set_output_fn(qshot0_output)

        # As we're only doing 1 demodulation, we have a maximum of 2 signal frequencies for each
        # carrier frequency, and each signal frequency can only have a maximum of 2 contributing
        # carrier frequencies
        self.Nf = 2 * self.sim.carrier.optical_frequencies.size
        self.demod_vac_contri = np.empty((self.Nf, 2), dtype=np.dtype("long"))
        self.demod_f = np.full(self.Nf, np.nan, dtype=np.float64)

        self.nsr = nsr
        if self.nsr:
            self.pd_ws = PD1Workspace(owner, sim, sim.model.fsig.f, None)

    cdef fill_carrier_qnoise_contributions(self) :
        cdef:
            Py_ssize_t i
            frequency_info_t f
            double freq
            double fsig = self.sim.model_settings.fsig

        # Use NAN / -1 to signal empty entries
        self.demod_f[:] = NAN
        self.demod_vac_contri[:] = -1

        for i in range(self.sim.carrier.optical_frequencies.size):
            f = self.sim.carrier.optical_frequencies.frequency_info[i]

            freq = f.f - fsig
            for j in range(self.Nf):
                if not isfinite(self.demod_f[j]):
                    self.demod_f[j] = freq
                    self.demod_vac_contri[j][0] = f.index
                    break
                elif float_eq(freq, self.demod_f[j]):
                    self.demod_vac_contri[j][1] = f.index
                    break

            freq = f.f + fsig
            for j in range(self.Nf):
                if not isfinite(self.demod_f[j]):
                    self.demod_f[j] = freq
                    self.demod_vac_contri[j][0] = f.index
                    break
                elif float_eq(freq, self.demod_f[j]):
                    self.demod_vac_contri[j][1] = f.index
                    break


qshot0_output = OutputFuncWrapper.make_from_ptr(c_qshot0_output)
cdef object c_qshot0_output(DetectorWorkspace self) :
    cdef:
        QShot0Workspace ws = <QShot0Workspace> self
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i, j
        Py_ssize_t Nhom = max(ws.sim.signal.nhoms, 1)
        double rtn = 0
        double f
        double f0 = ws.sim.model_settings.f0
        double unit_vacuum = ws.sim.model_settings.UNIT_VACUUM
        double nf_factor = 0.25**1  # factor 0.25 per demodulation
        complex_t c1, c2
        complex_t pdo

    ws.fill_carrier_qnoise_contributions()

    # Pick up pure vacuum noise and demodulate that into our signal.
    for i in range(ws.Nf):
        f = ws.demod_f[i]
        if ws.demod_vac_contri[i][0] == -1:
            break
        if ws.demod_vac_contri[i][1] == -1:
            for j in range(Nhom):
                c1 = carrier.get_out_fast(ws.dc_node_id, ws.demod_vac_contri[i][0], j)
                rtn += cabs(c1)**2 * (1 + f / f0)
        else:
            for j in range(Nhom):
                c1 = carrier.get_out_fast(ws.dc_node_id, ws.demod_vac_contri[i][0], j)
                c2 = carrier.get_out_fast(ws.dc_node_id, ws.demod_vac_contri[i][1], j)
                rtn += cabs(c1 + c2)**2 * (1 + f / f0)

    # Compensate for demod 0.5 factor when demodulating a signal
    # frequency as this is what a network analyser would do.
    rtn *= 2

    if ws.nsr:
        pdo = c_pd1_AC_output(ws.pd_ws)
        rtn /= pdo.real * pdo.real + pdo.imag * pdo.imag

    return sqrt(
        unit_vacuum
        * rtn
        * H_PLANCK
        * f0
        * nf_factor
    )


cdef class QShotNWorkspace(DetectorWorkspace):
    """An N RF demodulation quantum shot noise detector workspace.

    Parameters
    ----------
    owner : object
        The model element that owns this workspace
    sim : object
        The current Simulation object that this workspace will use
        to generate its outputs
    carrier_demods : list
        A list of (frequency, phase) pairs. The frequency and phase
        object should be
    nsr : bool
        If True, the signal transfer function is computed and then
        used to compute the noise in equivalent units of the
        singal being injected at runtime.
    """
    cdef:
        DetectorWorkspace pd_ws
        list carrier_demods
        int num_demod
        int Ndm
        int Nf
        int dc_node_id
        int ac_node_id
        long[:, ::1] demod_vac_contri
        long[:, ::1] demod_vac_contri_phi
        double[::1] demod_f
        double[::1] demod_phi
        QNDNValues cvalues
        bint nsr

        double[::1] freqs
        double[::1] phases
        double[::1] tmp_fs


    def __init__(self, owner, sim, carrier_demods : list, nsr, *, output_info=None):
        assert(sim.signal is not None)
        self.carrier_demods = carrier_demods
        num_carrier_demod = len(carrier_demods)
        if num_carrier_demod == 1:
            _values = QND1Values()
        else:
            _values = QNDNValues()
        super().__init__(owner, sim, _values, oinfo=output_info, needs_noise=True)
        self.cvalues = <QNDNValues>self.values

        self.dc_node_id = self.sim.carrier.node_id(self.oinfo.nodes[0])
        self.ac_node_id = self.sim.signal.node_id(self.oinfo.nodes[0])
        self.set_output_fn(qshotN_output)

        # N demodulations, so we have a maximum of 2**N signal frequencies for each carrier
        # frequency, and each signal frequency can only have a maximum of 2**N contributing carrier
        # frequencies
        self.num_demod = num_carrier_demod + 1
        self.Ndm = int(2**self.num_demod)
        self.Nf = self.Ndm * self.sim.carrier.optical_frequencies.size
        self.demod_vac_contri = np.empty((self.Nf, self.Ndm), dtype=np.dtype("long"))
        self.demod_vac_contri_phi = np.empty((self.Nf, self.Ndm), dtype=np.dtype("long"))
        self.demod_f = np.full(self.Nf, np.nan, dtype=np.float64)
        self.demod_phi = np.full(self.Ndm, np.nan, dtype=np.float64)

        self.freqs = np.empty(self.num_demod, dtype=np.float64)
        self.phases = np.empty(self.num_demod, dtype=np.float64)
        self.tmp_fs = np.empty(self.Ndm, dtype=np.float64)

        self.nsr = nsr
        if self.nsr:
            # ddb todo: add more options here
            if num_carrier_demod == 1:
                # 1RF + 1fsig demodulation
                self.pd_ws = PD2Workspace(
                    owner,
                    sim,
                    carrier_demods[0][0],
                    carrier_demods[0][1],
                    sim.model.fsig.f,
                    None
                )
            else:
                raise NotImplementedError(f"Not yet implemented to calculate NSR for {num_carrier_demod} RF carrier demodulations")

    cdef fill_carrier_qnoise_contributions(self) :
        cdef:
            Py_ssize_t i, j, k
            frequency_info_t f
            double freq

        self.freqs[0] = self.cvalues.f1
        self.phases[0] = self.cvalues.phase1
        if self.num_demod > 2:
            self.freqs[1] = self.cvalues.f2
            self.phases[1] = self.cvalues.phase2
        if self.num_demod > 3:
            self.freqs[2] = self.cvalues.f3
            self.phases[2] = self.cvalues.phase3
        self.freqs[self.num_demod - 1] = self.sim.model_settings.fsig
        self.phases[self.num_demod - 1] = 0  # fsig demod doesn't affect result, so assume 0

        self.demod_phi[:] = 0
        for i in range(self.Ndm):
            for j in range(self.num_demod):
                if (i >> j) & 0x01:
                    self.demod_phi[i] += self.phases[j]
                else:
                    self.demod_phi[i] -= self.phases[j]
            self.demod_phi[i] = radians(self.demod_phi[i])

        # Use NAN / -1 to signal empty entries
        self.demod_f[:] = NAN
        self.demod_vac_contri[:] = -1

        for i in range(self.sim.carrier.optical_frequencies.size):
            f = self.sim.carrier.optical_frequencies.frequency_info[i]
            for j in range(self.Ndm):
                self.tmp_fs[j] = f.f
                for k in range(self.num_demod):
                    if (j >> k) & 0x01:
                        self.tmp_fs[j] += self.freqs[k]
                    else:
                        self.tmp_fs[j] -= self.freqs[k]

            for nf in range(self.Ndm):
                freq = self.tmp_fs[nf]
                for j in range(self.Nf):
                    if not isfinite(self.demod_f[j]):
                        self.demod_f[j] = freq
                        self.demod_vac_contri[j][0] = f.index
                        self.demod_vac_contri_phi[j][0] = nf
                        break
                    elif float_eq(freq, self.demod_f[j]):
                        for k in range(self.Ndm):
                            if self.demod_vac_contri[j][k] == -1:
                                self.demod_vac_contri[j][k] = f.index
                                self.demod_vac_contri_phi[j][k] = nf
                                break
                        break


qshotN_output = OutputFuncWrapper.make_from_ptr(c_qshotN_output)
cdef object c_qshotN_output(DetectorWorkspace self) :
    cdef:
        QShotNWorkspace ws = <QShotNWorkspace> self
        HOMSolver carrier = ws.sim.carrier
        Py_ssize_t i, j, k
        Py_ssize_t Nhom = max(ws.sim.signal.nhoms, 1)
        double rtn = 0
        double f
        double f0 = ws.sim.model_settings.f0
        double unit_vacuum = ws.sim.model_settings.UNIT_VACUUM
        double nf_factor = 0.25**ws.num_demod  # factor 0.25 per demodulation
        complex_t car_sum
        complex_t pdo

    ws.fill_carrier_qnoise_contributions()

    # Pick up pure vacuum noise and demodulate that into our signal.
    for i in range(ws.Nf):
        f = ws.demod_f[i]
        if ws.demod_vac_contri[i][0] == -1:
            break
        car_sum = 0
        for j in range(Nhom):
            for k in range(ws.Ndm):
                if ws.demod_vac_contri[i][k] == -1:
                    break
                car_sum += crotate(
                        carrier.get_out_fast(ws.dc_node_id, ws.demod_vac_contri[i][k], j),
                        # FIXME: There should be a minus sign here, why isn't there?
                        ws.demod_phi[ws.demod_vac_contri_phi[i][k]]
                        )
            rtn += cabs(car_sum)**2 * (1 + f / f0)

    # Compensate for demod 0.5 factor when demodulating a signal
    # frequency as this is what a network analyser would do.
    rtn *= 2

    if ws.nsr:
        if ws.num_demod == 2:
            (<PD2Workspace>ws.pd_ws).cvalues.f1 = ws.cvalues.f1
            (<PD2Workspace>ws.pd_ws).cvalues.phase1 = ws.cvalues.phase1
            (<PD2Workspace>ws.pd_ws).cvalues.f2 = 0
            (<PD2Workspace>ws.pd_ws).cvalues.phase2 = 0
        else:
            raise ValueError(f"Can't calculate NSR for {ws.num_demod-1} RF demodulations")
        pdo = c_pd2_AC_output(ws.pd_ws)
        rtn /= pdo.real * pdo.real + pdo.imag * pdo.imag

    return sqrt(
        unit_vacuum
        * rtn
        * H_PLANCK
        * f0
        * nf_factor
    )

cdef class QuantumNoiseDetectorWorkspace(DetectorWorkspace):
    cdef:
        long[:, ::1] demod_f_sig
        double[:, ::1] demod_f
        double[::1] demod_phi
        complex_t[::1] s
        complex_t[::1] v
        dict demod_vac_contri
        int dc_node_id
        int ac_node_id
        int Nf
        int Ndm
        int neq

    def __init__(self, owner, sim):
        assert(sim.signal is not None)
        super().__init__(owner, sim)
        for sim in sim:
            if sim.is_audio:
                self.sim.carrier = sim.sim.carrier
                self.sim.signal = sim

        self.dc_node_id = self.sim.carrier.node_id(owner.node)
        self.ac_node_id = self.sim.signal.node_id(owner.node)

        self.Nf = len(owner.freqs)
        self.Ndm = int(2 ** self.Nf)
        self.neq = self.sim.signal.M().num_equations

        self.demod_f = np.zeros((self.sim.carrier.optical_frequencies.size, self.Ndm))
        self.demod_f_sig = np.zeros((self.sim.carrier.optical_frequencies.size, self.Ndm), dtype=np.dtype("long"))
        self.demod_phi = np.zeros(self.Ndm)
        self.s = np.zeros(self.neq, dtype=np.complex128)

        self.set_output_fn(self.c_qnoised_output)

    cpdef fill_selection_vector(self) :
        cdef HOMSolver signal = self.sim.signal

        self.demod_f[:] = 0
        self.demod_f_sig[:] = 0
        self.demod_phi[:] = 0
        self.s[:] = 0

        self.fill_demod_f_table()
        self.fill_carrier_qnoise_contributions()
        self.fill_qnoised_selection_vector()

        for i in range(self.neq):
            signal.set_source_fast_3(i, self.s[i], self.owner.name)

    cpdef set_covariance_matrix(self, complex_t[::1] v, unicode name) :
        # TODO: Should this be a copy?
        self.v = v

    cdef void fill_demod_f_table(QuantumNoiseDetectorWorkspace self) noexcept:
        cdef:
            frequency_info_t f
            Py_ssize_t i, j, k

        for i in range(self.sim.carrier.optical_frequencies.size):
            f = self.sim.carrier.optical_frequencies.frequency_info[i]
            self.demod_f[f.index][:] = f.f

        for i in range(self.Ndm):
            for j in range(self.Nf):
                # Use bit shifting here to determine whether we add a plus
                # or minus to the total frequency and phases
                if (i >> j) & 0x01:
                    self.demod_phi[i] += self.owner.phases[j]
                    for k in range(self.sim.carrier.optical_frequencies.size):
                        f = self.sim.carrier.optical_frequencies.frequency_info[k]
                        self.demod_f[f.index][i] += float(self.owner.freqs[j])
                else:
                    self.demod_phi[i] -= self.owner.phases[j]
                    for k in range(self.sim.carrier.optical_frequencies.size):
                        f = self.sim.carrier.optical_frequencies.frequency_info[k]
                        self.demod_f[f.index][i] -= float(self.owner.freqs[j])

    cdef fill_carrier_qnoise_contributions(QuantumNoiseDetectorWorkspace self) :
        cdef:
            Py_ssize_t i, j, k
            Py_ssize_t car_idx
            frequency_info_t f
            HOMSolver signal = self.sim.signal

        self.demod_vac_contri = {}

        # Check all frequencies to see if they match up to any signal
        # sidebands
        for i in range(self.sim.carrier.optical_frequencies.size):
            car_idx = self.sim.carrier.optical_frequencies.frequency_info[i].index
            for j in range(self.Ndm):
                self.demod_f_sig[car_idx][j] = -1
                # Check frequencies against any existing signals, if we're not
                # only considering pure vacuum states
                if not self.owner.shot_only:
                    for k in range(signal.optical_frequencies.size):
                        f = signal.optical_frequencies.frequency_info[k]
                        if float_eq(self.demod_f[car_idx][j], f.f):
                            self.demod_f_sig[car_idx][j] = k
                            break

                # If no signal frequency could be found then this is a pure
                # vacuum noise field so need to add it to the contribution list
                if self.demod_f_sig[car_idx][j] == -1:
                    # Check if there are any other contributions listed already
                    # for this carrier
                    # TODO: remove direct comparison of floats
                    if self.demod_f[car_idx][j] in self.demod_vac_contri:
                        # If we have already found another item with this
                        # carrier frequency then these noises are correlated
                        elt = self.demod_vac_contri[self.demod_f[car_idx][j]]
                        elt["c_idx"].append(car_idx)
                        elt["phi_idx"].append(j)
                    else:
                        elt = {
                            "c_idx": [car_idx],
                            "phi_idx": [j],
                            "f": self.demod_f[car_idx][j],
                        }
                        self.demod_vac_contri[self.demod_f[car_idx][j]] = elt

    cdef fill_qnoised_selection_vector(QuantumNoiseDetectorWorkspace self) :
        cdef:
            Py_ssize_t i, j, k
            Py_ssize_t s_idx
            frequency_info_t fc, fs
            HOMSolver signal = self.sim.signal

        # For each carrier field check if the corresponding demodulated
        # frequency is a signal sideband. If so, we need to include it in the
        # selection vector.
        for j in range(self.sim.carrier.optical_frequencies.size):
            fc = self.sim.carrier.optical_frequencies.frequency_info[j]
            for k in range(self.Ndm):
                if self.demod_f_sig[j][k] >= 0:
                    # If this is a signal sideband frequency this is the
                    # product between the j'th carrier and this.
                    fs = signal.optical_frequencies.frequency_info[self.demod_f_sig[j][k]]
                    if fs.audio_order > 0:
                        for i in range(nmax(signal.nhoms, 1)):
                            s_idx = signal.field_fast(self.ac_node_id, fs.index, i)
                            self.s[s_idx] = self.s[s_idx] + (
                                self.sim.carrier.get_out_fast(self.dc_node_id, fc.index, i)
                                * ROOT2
                                * cexp(-1j * radians(self.demod_phi[k]))
                            )
                    else:
                        for i in range(nmax(signal.nhoms, 1)):
                            s_idx = signal.field_fast(self.ac_node_id, fs.index, i)
                            self.s[s_idx] = self.s[s_idx] + conj(
                                self.sim.carrier.get_out_fast(self.dc_node_id, fc.index, i)
                                * ROOT2
                                * cexp(-1j * radians(self.demod_phi[k]))
                            )

    cdef c_qnoised_output(self) :
        """Computes the output of the quantum noise detector.

        Returns
        -------
        np.complex128
            The output of this `QuantumNoiseDetector`.
        """
        cdef:
            double rtn = 0
            double f0 = self.sim.model_settings.f0
            double unit_vacuum = self.sim.model_settings.UNIT_VACUUM
            double nf_factor = 0.25**self.Nf
            HOMSolver signal = self.sim.signal
            HOMSolver carrier = self.sim.carrier

        if not self.owner.shot_only:
            for i in range(self.neq):
                rtn += creal(self.v[i] * conj(self.s[i]))

        # Now we must loop over the contributions from the demodulation for
        # frequencies that are not signal sidebands, i.e. we pick up pure
        # vacuum noise and demodulate that into our signal.
        for el in self.demod_vac_contri.values():
            if len(el["c_idx"]) > 1:
                for j in range(max(signal.nhoms, 1)):
                    val = 0
                    for k in el["c_idx"]:
                        val += (
                            carrier.get_out_fast(self.dc_node_id, k, j)
                        ).conjugate() * np.exp(
                            1j * np.deg2rad(self.demod_phi[<int>el["phi_idx"][j]])
                        )
                    if not self.owner.shot_only:
                        # TODO: why is this factor needed?
                        val *= np.sqrt(2)
                    rtn += abs(val)**2 * (1 + el["f"] / f0)
            else:
                val = 0
                for j in range(max(signal.nhoms, 1)):
                    val += abs(carrier.get_out_fast(self.dc_node_id, el["c_idx"][0], j)) ** 2
                rtn += val * (1 + el["f"] / f0)

        for f in self.owner.freqs:
            # Compensate for demod 0.5 factor if demodulating a signal
            # frequency as this is what a network analyser would do.
            if np.isclose(float(f), float(signal.model.fsig.f)):
                rtn *= 2

        return (
            unit_vacuum
            * rtn
            * H_PLANCK
            * f0
            * nf_factor
        ) ** 0.5
