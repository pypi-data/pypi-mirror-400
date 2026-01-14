# cython: boundscheck=False, wraparound=False, initializedcheck=False, profile=False
from finesse.knm.matrix cimport make_unscaled_X_scatter_knm_matrix, make_unscaled_Y_scatter_knm_matrix
from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj, cexp
from finesse.cymath.gaussbeam cimport bp_beamsize
from finesse.cymath.math cimport sqrt
from finesse.cymath.math cimport radians
from finesse.frequency cimport FrequencyContainer
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray
from finesse.symbols import Symbol
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver

from cpython.ref cimport PyObject
from finesse.cymath.complex cimport DenseZVector
import logging

ctypedef (double*, double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_9

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD


LOGGER = logging.getLogger(__name__)


cdef class MirrorValues(BaseCValues):
    def __init__(MirrorValues self):
        cdef ptr_tuple_9 ptr = (&self.R, &self.T, &self.L, &self.phi, &self.Rcx, &self.Rcy, &self.xbeta, &self.ybeta, &self.misaligned)
        cdef tuple params = ("R","T","L","phi","Rcx","Rcy","xbeta","ybeta","misaligned")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class MirrorOpticalConnections:
    """Contains C accessible references to submatrices for
    optical connections for this element.
    """
    def __cinit__(self, object mirror, HOMSolver mtx):
        # Only 1D arrays of submatrices as no frequency coupling happening
        cdef int Nf = mtx.optical_frequencies.size

        self.P1i_P1o = SubCCSView1DArray(Nf)
        self.P2i_P2o = SubCCSView1DArray(Nf)
        self.P1i_P2o = SubCCSView1DArray(Nf)
        self.P2i_P1o = SubCCSView1DArray(Nf)
        self.opt_conn_ptrs.P1i_P1o = <PyObject**>self.P1i_P1o.views
        self.opt_conn_ptrs.P2i_P2o = <PyObject**>self.P2i_P2o.views
        self.opt_conn_ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.opt_conn_ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views


cdef class MirrorSignalConnections(MirrorOpticalConnections):
    """Contains C accessible references to submatrices for
    optical, electrical, and mechanical connections for this
    element.
    """
    def __cinit__(self, object mirror, HOMSolver mtx):
        cdef:
            int Nfo =  mtx.optical_frequencies.size

        Nmz = mirror.mech.z.num_frequencies # num of mechanic frequencies
        self.P1i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P1o_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P2i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P2o_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P1i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P1o_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P2i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P2o_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P1i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P1o_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P2i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P2o_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.Z_P1o = SubCCSView2DArray(Nmz, Nfo)
        self.Z_P2o = SubCCSView2DArray(Nmz, Nfo)
        self.yaw_P1o = SubCCSView2DArray(1, Nfo)
        self.yaw_P2o = SubCCSView2DArray(1, Nfo)
        self.pitch_P1o = SubCCSView2DArray(1, Nfo)
        self.pitch_P2o = SubCCSView2DArray(1, Nfo)

        self.sig_conn_ptrs.P1i_Fz = <PyObject***>self.P1i_Fz.views
        self.sig_conn_ptrs.P2i_Fz = <PyObject***>self.P2i_Fz.views
        self.sig_conn_ptrs.P1o_Fz = <PyObject***>self.P1o_Fz.views
        self.sig_conn_ptrs.P2o_Fz = <PyObject***>self.P2o_Fz.views
        self.sig_conn_ptrs.P1i_Fyaw = <PyObject***>self.P1i_Fyaw.views
        self.sig_conn_ptrs.P2i_Fyaw = <PyObject***>self.P2i_Fyaw.views
        self.sig_conn_ptrs.P1o_Fyaw = <PyObject***>self.P1o_Fyaw.views
        self.sig_conn_ptrs.P2o_Fyaw = <PyObject***>self.P2o_Fyaw.views
        self.sig_conn_ptrs.P1i_Fpitch = <PyObject***>self.P1i_Fpitch.views
        self.sig_conn_ptrs.P2i_Fpitch = <PyObject***>self.P2i_Fpitch.views
        self.sig_conn_ptrs.P1o_Fpitch = <PyObject***>self.P1o_Fpitch.views
        self.sig_conn_ptrs.P2o_Fpitch = <PyObject***>self.P2o_Fpitch.views
        self.sig_conn_ptrs.Z_P1o = <PyObject***>self.Z_P1o.views
        self.sig_conn_ptrs.Z_P2o = <PyObject***>self.Z_P2o.views
        self.sig_conn_ptrs.yaw_P1o = <PyObject***>self.yaw_P1o.views
        self.sig_conn_ptrs.yaw_P2o = <PyObject***>self.yaw_P2o.views
        self.sig_conn_ptrs.pitch_P1o = <PyObject***>self.pitch_P1o.views
        self.sig_conn_ptrs.pitch_P2o = <PyObject***>self.pitch_P2o.views


cdef class MirrorWorkspace(KnmConnectorWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        cdef FrequencyContainer fcnt
        super().__init__(
            owner,
            sim,
            MirrorOpticalConnections(owner, sim.carrier),
            MirrorSignalConnections(owner, sim.signal) if sim.signal else None,
            MirrorValues()
        )
        # Casting python objects to known types for faster access
        self.mv = self.values
        self.mcc = self.carrier.connections
        self.cvalues = self.values
        if sim.signal:
            self.mcs = self.signal.connections
        else:
            self.mcs = None

        # These are only use for beam tracing as far as I can tell
        # for the beam tracing, which only has optical nodes.
        self.P1i_id = sim.trace_node_index[owner.p1.i]
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.P2i_id = sim.trace_node_index[owner.p2.i]
        self.P2o_id = sim.trace_node_index[owner.p2.o]

        self.car_p1o_idx = sim.carrier.node_id(owner.p1.o)
        self.car_p1i_idx = sim.carrier.node_id(owner.p1.i)
        self.car_p2o_idx = sim.carrier.node_id(owner.p2.o)
        self.car_p2i_idx = sim.carrier.node_id(owner.p2.i)

        if sim.signal:
            # If we have a signal simulation then we need to cache some indicies
            # for grabbing data when filling
            self.car_p1o_rhs_idx = sim.carrier.get_node_info(owner.p1.o)["rhs_index"]
            self.car_p2o_rhs_idx = sim.carrier.get_node_info(owner.p2.o)["rhs_index"]
            self.car_p1i_rhs_idx = sim.carrier.get_node_info(owner.p1.i)["rhs_index"]
            self.car_p2i_rhs_idx = sim.carrier.get_node_info(owner.p2.i)["rhs_index"]
            self.car_p_num_hom =   sim.carrier.get_node_info(owner.p1.o)["nhoms"]

            self.z_signal_enabled = owner.mech.z.full_name in sim.signal.nodes
            if self.z_signal_enabled:
                # Get a reference to the mechanical node frequencies
                fcnt = sim.signal.signal_frequencies[owner.mech.z]
                self.z_mech_freqs = fcnt.frequency_info
                self.z_mech_freqs_size = sim.signal.signal_frequencies[owner.mech.z].size

            self.yaw_signal_enabled = owner.mech.yaw.full_name in sim.signal.nodes
            if self.yaw_signal_enabled:
                fcnt = sim.signal.signal_frequencies[owner.mech.yaw]
                self.yaw_mech_freqs = fcnt.frequency_info
                self.yaw_mech_freqs_size = sim.signal.signal_frequencies[owner.mech.yaw].size
                self.K_yaw_sig = make_unscaled_X_scatter_knm_matrix(self.sim.model_settings.homs_view)

            self.pitch_signal_enabled = owner.mech.pitch.full_name in sim.signal.nodes
            if self.pitch_signal_enabled:
                fcnt = sim.signal.signal_frequencies[owner.mech.pitch]
                self.pitch_mech_freqs = fcnt.frequency_info
                self.pitch_mech_freqs_size = sim.signal.signal_frequencies[owner.mech.pitch].size
                self.K_pitch_sig = make_unscaled_Y_scatter_knm_matrix(self.sim.model_settings.homs_view)

        self.sym_abcd_Cs[:] = [
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        ]
        self.abcd_Cs[:] = [
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        ]

    def __dealloc__(self):
        cdef Py_ssize_t i
        for i in range(8):
            cy_expr_free(self.sym_abcd_Cs[i])

    def compile_abcd_cy_exprs(self):
        cdef:
            object mirror = self.owner
            list abcd_handles = list(mirror._abcd_matrices.values())

        if self.sim.is_modal:
            self.abcd_Cs[:] = [
                <double*>&self.abcd_p1p1_x[1][0], <double*>&self.abcd_p1p1_y[1][0],
                <double*>&self.abcd_p2p2_x[1][0], <double*>&self.abcd_p2p2_y[1][0],
                <double*>&self.abcd_p1p2_x[1][0], <double*>&self.abcd_p1p2_y[1][0],
                <double*>&self.abcd_p2p1_x[1][0], <double*>&self.abcd_p2p1_y[1][0],
            ]

        cdef Py_ssize_t i
        cdef object[:, ::1] M_sym
        for i in range(8):
            M_sym = abcd_handles[i][0]

            # NOTE (sjr) Only element C of a Mirror ABCD matrix can possibly change
            if isinstance(M_sym[1][0], Symbol):
                ch_sym = M_sym[1][0].expand_symbols().eval(keep_changing_symbols=True)
                if isinstance(ch_sym, Symbol):
                    self.sym_abcd_Cs[i] = cy_expr_new()
                    cy_expr_init(self.sym_abcd_Cs[i], ch_sym)

    cpdef update_parameter_values(self):
        ConnectorWorkspace.update_parameter_values(self)

        cdef Py_ssize_t i
        for i in range(8):
            if self.sym_abcd_Cs[i] != NULL and self.abcd_Cs[i] != NULL:
                self.abcd_Cs[i][0] = cy_expr_eval(self.sym_abcd_Cs[i])


cdef inline int mirror_fill_optical_2_optical(
        mirror_optical_connections *conn,
        MirrorWorkspace ws,
        frequency_info_t *freq,
        double r,
        double t,
        double phi_0
    ) except -1:
    if ws.mv.misaligned >= 1:
        r = 0

    # Until we have a better way to handle cython validators
    # Ensure that it's always positive and between 0 and 1
    if r < 0:
        r = 0
    if t < 0:
        t = 0
    if r > 1:
        r = 1
    if t > 1:
        t = 1

    cdef double phase_shift_scaling = (1 + freq.f / ws.sim.model_settings.f0)
    # Phase on reflection is not equal if nr1 != nr2 and AoI != 0
    # so the usual i on transmission phase no longer works.
    cdef double phi_r1, phi_r2, phi_t
    cdef complex_t _r1, _r2, _t0
    if ws.sim.model_settings.phase_config.v2_transmission_phase or ws.nr1 == ws.nr2:
        # old v2 phase on transmission
        # The usual i on transmission and reflections
        # are opposite phase on each side, ignores refractive index
        phi_r1 = 2 * phi_0 * phase_shift_scaling
        if ws.imaginary_transmission:
            _r1 = r * cexp(1j * phi_r1)
            _r2 = conj(_r1)
            _t0 = 1j * t
        else:
            _r1 = -r * cexp(1j * phi_r1)
            _r2 = -conj(_r1)
            _t0 = t

    else:
        # Transmission conventions are described by Eq.2.25 of
        # Living Rev Relativ (2016) 19:3 DOI 10.1007/s41114-016-0002-8
        # bs transmission phase depends on the reflectivity, refractive indices,
        # and angle of incidence
        phi_r2 = -2 * phi_0 * ws.nr2 * phase_shift_scaling
        if ws.imaginary_transmission:
            # Uses N=-1 of Eq.2.25
            phi_r1 = 2 * phi_0 * ws.nr1 * phase_shift_scaling
            phi_t = PI/2 + 0.5 * (phi_r1 + phi_r2)
        else:
            # Uses N=0 of Eq.2.25
            phi_r1 = PI + 2 * phi_0 * ws.nr1 * phase_shift_scaling
            phi_t = -PI/2 + 0.5 * (phi_r1 + phi_r2)

        _r1 = r * cexp(1j * phi_r1)
        _r2 = r * cexp(1j * phi_r2)
        _t0 = t * cexp(1j * phi_t)
    # Reflections
    if conn.P1i_P1o[freq.index]:
        (<SubCCSView>conn.P1i_P1o[freq.index]).fill_negative_za_zm_2(_r1, &ws.K11.mtx)
    if conn.P2i_P2o[freq.index]:
        (<SubCCSView>conn.P2i_P2o[freq.index]).fill_negative_za_zm_2(_r2, &ws.K22.mtx)
    # Transmission
    if conn.P1i_P2o[freq.index]:
        (<SubCCSView>conn.P1i_P2o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K12.mtx)
    if conn.P2i_P1o[freq.index]:
        (<SubCCSView>conn.P2i_P1o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K21.mtx)


mirror_carrier_fill = FillFuncWrapper.make_from_ptr(c_mirror_carrier_fill)
cdef object c_mirror_carrier_fill(ConnectorWorkspace cws) :
    r"""
    Fills the sub-matrix of the interferometer matrix held by `sim`, corresponding
    to the `mirror` component.

    A light field :math:`E_{\mathrm{in}}` reflected by a mirror is in general changed in phase
    and amplitude (in the plane-wave picture):

    .. math::
        E_{\mathrm{refl}} = r\exp{\left(i\varphi\right)} E_{\mathrm{in}},

    where :math:`r` is the amplitude reflectance of the mirror and :math:`\varphi = 2kx` the
    phase shift acquired by the propagation towards and back from the mirror (:math:`x` is the
    displacement from the reference plane - see :numref:`fig_mirror_couplings`).

    .. _fig_mirror_couplings:
    .. figure:: ../images/mirror.*
        :align: center

        Field couplings at mirror with a representation of the reference plane.

    The tuning :math:`\phi` gives the displacement of the mirror expressed in radians, with respect
    to the reference plane. A tuning of :math:`\phi = 2\pi` represents a displacement of the mirror,
    :math:`x_m - x_0` on :numref:`fig_mirror_couplings`, by one carrier wavelength :math:`x = \lambda_0`.

    A certain displacement results in different phase shifts for light fields with different frequencies. The
    phase shift a general field acquires at the reflection on the front surface of the mirror can be written
    as:

    .. math::
        \varphi = 2\phi\frac{\omega}{\omega_0},

    where :math:`omega` is the angular frequency of the reflected light. If a second light beam hits the mirror
    from the other direction, the phase change :math:`\varphi_2` with respect to the same tuning would be:

    .. math::
        \varphi_2 = -\varphi.

    The tuning of a mirror (or beam splitter) does not represent a change in the path length but a change in the
    position of the component. The transmitted light is thus not affected by the tuning of the mirror. Only the
    phase shift of :math:`\pi/2` for every transmission has to be taken into account:

    .. math::
        E_{\mathrm{trans}} = i t E_{\mathrm{in}},

    with :math:`t` as the amplitude transmittance of the mirror.

    Putting all this together, for each frequency light field :math:`f` in the interferometer, the following
    quantities are computed in general (including higher-order spatial modes) for the field couplings,

    .. math::
        \begin{array}{l}
            m_{11} = r K_{11} \exp{\left(i 2\phi \left(1 + \frac{f}{f_0}\right) \right)},\\
            m_{22} = r K_{22} \exp{\left(-i 2\phi \left(1 + \frac{f}{f_0}\right) \right)},\\
            m_{12} = it K_{12},\\
            m_{21} = it K_{21},
        \end{array}

    where :math:`K_{\mathrm{ij}}` are the scattering matrices for each direction (see
    :ref:`scatter_matrices`). Here, each :math:`m_{\mathrm{ij}}` term now represents a
    vector of the couplings of all higher-order spatial mode fields present.
    """
    cdef:
        MirrorWorkspace ws = <MirrorWorkspace>cws
        double t = sqrt(ws.mv.T)
        double r = sqrt(ws.mv.R)
        double phi = radians(ws.mv.phi)
        Py_ssize_t i, size
        mirror_optical_connections *conn = &ws.mcc.opt_conn_ptrs
        frequency_info_t *frequencies

    size = ws.sim.carrier.optical_frequencies.size
    frequencies = ws.sim.carrier.optical_frequencies.frequency_info

    for i in range(size):
        mirror_fill_optical_2_optical(conn, ws, &(frequencies[i]), r, t, phi)


mirror_signal_opt_fill = FillFuncWrapper.make_from_ptr(c_mirror_signal_opt_fill)
cdef object c_mirror_signal_opt_fill(ConnectorWorkspace cws) :
    cdef:
        MirrorWorkspace ws = <MirrorWorkspace>cws
        double t = sqrt(ws.mv.T)
        double r = sqrt(ws.mv.R)
        double phi = radians(ws.mv.phi)
        Py_ssize_t i, size
        mirror_optical_connections *conn = &ws.mcs.opt_conn_ptrs
        frequency_info_t *frequencies

    size = ws.sim.signal.optical_frequencies.size
    frequencies = ws.sim.signal.optical_frequencies.frequency_info
    ws.z_to_field = 1j * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale
    ws.field_to_F = 1 / (C_LIGHT * ws.sim.model_settings.x_scale)

    for i in range(size):
        mirror_fill_optical_2_optical(conn, ws, &(frequencies[i]), r, t, phi)


mirror_signal_mech_fill = FillFuncWrapper.make_from_ptr(c_mirror_signal_mech_fill)
cdef object c_mirror_signal_mech_fill(ConnectorWorkspace cws) :
    cdef:
        MirrorWorkspace ws = <MirrorWorkspace>cws
        HOMSolver carrier = ws.sim.carrier
        HOMSolver signal = ws.sim.signal
        double phi = radians(ws.mv.phi)
        Py_ssize_t i, size
        mirror_optical_connections *car_conn = &ws.mcc.opt_conn_ptrs
        mirror_signal_connections *sconn = &ws.mcs.sig_conn_ptrs
        frequency_info_t *freq
        frequency_info_t *frequencies

    size = ws.sim.signal.optical_frequencies.size
    frequencies = ws.sim.signal.optical_frequencies.frequency_info
    ws.z_to_field = 1j * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale
    ws.field_to_F = 1 / (C_LIGHT * ws.sim.model_settings.x_scale)

    if ws.z_signal_enabled:
        for i in range(size):
            freq = &(frequencies[i])
            if ws.z_mech_freqs_size == 1:
                single_z_mechanical_frequency_signal_calc(ws, carrier, sconn, car_conn, freq, phi, 0, freq.audio_carrier_index)
            else:
                multiple_z_mechanical_freq_signal_calc(ws, carrier, sconn, car_conn, freq, phi)

    if ws.yaw_signal_enabled:
        for i in range(size):
            freq = &(frequencies[i])
            if ws.yaw_mech_freqs_size == 1:
                single_yaw_mechanical_frequency_signal_calc(ws, carrier, signal, sconn, car_conn, freq, phi, 0, freq.audio_carrier_index)
            else:
                raise NotImplementedError()

    if ws.pitch_signal_enabled:
        for i in range(size):
            freq = &(frequencies[i])
            if ws.pitch_mech_freqs_size == 1:
                single_pitch_mechanical_frequency_signal_calc(ws, carrier, signal, sconn, car_conn, freq, phi, 0, freq.audio_carrier_index)
            else:
                raise NotImplementedError()

cdef void get_carrier_vectors(HOMSolver carrier, MirrorWorkspace ws, int carrier_index, DenseZVector *c_p1_i, DenseZVector *c_p2_i, DenseZVector *c_p1_o, DenseZVector *c_p2_o) noexcept:
    cdef Py_ssize_t N = 0
    assert(c_p1_i)
    assert(c_p2_i)
    assert(c_p1_o)
    assert(c_p2_o)
    c_p1_i.size = c_p1_o.size = c_p2_i.size = c_p2_o.size = ws.car_p_num_hom
    c_p1_i.stride = c_p1_o.stride = c_p2_i.stride = c_p2_o.stride = 1
    # Get incoming/outgoing carrier field amplitudes
    c_p1_i.ptr = carrier.node_field_vector_fast(ws.car_p1i_idx, carrier_index, &N)
    assert(c_p1_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_i.ptr = carrier.node_field_vector_fast(ws.car_p2i_idx, carrier_index, &N)
    assert(c_p2_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p1_o.ptr = carrier.node_field_vector_fast(ws.car_p1o_idx, carrier_index, &N)
    assert(c_p1_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_o.ptr = carrier.node_field_vector_fast(ws.car_p2o_idx, carrier_index, &N)
    assert(c_p2_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)

cdef void single_yaw_mechanical_frequency_signal_calc (
        MirrorWorkspace ws,
        HOMSolver carrier,
        HOMSolver signal,
        mirror_signal_connections *conn,
        mirror_optical_connections *car_conn,
        frequency_info_t *freq, # audio sideband
        double phi,
        Py_ssize_t yaw_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        double wx = 0.0
        NodeBeamParam *q_P1o
        NodeBeamParam *q_P2o
        complex_t a_2_o_factor
        complex_t phase_shift = cexp(1j*phi * freq.f / ws.sim.model_settings.f0)
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o

    get_carrier_vectors(carrier, ws, carrier_index, &c_p1_i, &c_p2_i, &c_p1_o, &c_p2_o)

    # We use an unscaled Knm matrix, so we need to apply the waist size and gouy phase
    # as we always reverse the gouy phase anyway, we just don't bother adding it here
    # k0 scaling with nr is done in code jsut below, along with spot size
    # TODO ddb - these matrix multiplications would be more efficient with a sparse matrix
    # format, CSR maybe? As dense product scales badly with maxtem
    if ws.sim.is_modal: # ignore filling this if doing plane-wave
        a_2_o_factor = 1j * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
        q_P1o = &ws.sim.trace[ws.P1o_id]
        q_P2o = &ws.sim.trace[ws.P2o_id]
        if conn.yaw_P1o[yaw_freq_idx][freq.index]:
            wx = bp_beamsize(&q_P1o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P1o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P1i_P1o[carrier_index]), 0,
                2/2*ws.nr1 * wx * a_2_o_factor * phase_shift,
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.yaw_P1o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P2i_P1o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wx * a_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        if conn.yaw_P2o[yaw_freq_idx][freq.index]:
            wx = bp_beamsize(&q_P2o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P2o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P2i_P2o[carrier_index]), 0,
                2/2*ws.nr2 * wx * a_2_o_factor * conj(phase_shift),
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission coupling
            (<SubCCSView>conn.yaw_P2o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wx * a_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        # -------------------------------------------------
        # Optical to mechanical connections
        # -------------------------------------------------
        # These fill a nHOMx1 matrix to compute RP force
        # There is a minus sign difference between side 1 and 2 here, because
        # of the coordinate system change
        if conn.P1i_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P1i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr1 * wx * ws.field_to_F, &ws.K_yaw_sig.mtx, &c_p1_i
            )
        # differing minus signs here because of the x coordinate flip compared to mechanical node x
        if conn.P1o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P1o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wx * ws.field_to_F, &ws.K_yaw_sig.mtx, &c_p1_o
            )
        if conn.P2i_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P2i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wx * ws.field_to_F, &ws.K_yaw_sig.mtx,  &c_p2_i
            )
        if conn.P2o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P2o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr2 * wx * ws.field_to_F, &ws.K_yaw_sig.mtx, &c_p2_o
            )

cdef void single_pitch_mechanical_frequency_signal_calc (
        MirrorWorkspace ws,
        HOMSolver carrier,
        HOMSolver signal,
        mirror_signal_connections *conn,
        mirror_optical_connections *car_conn,
        frequency_info_t *freq, # audio sideband
        double phi,
        Py_ssize_t pitch_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        complex_t _tuning  = 0.0
        complex_t _ctuning = 0.0
        double wy          = 0.0
        NodeBeamParam *q_P1o
        NodeBeamParam *q_P2o
        complex_t phase_shift = cexp(1j*phi * freq.f / ws.sim.model_settings.f0)
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o

    get_carrier_vectors(carrier, ws, carrier_index, &c_p1_i, &c_p2_i, &c_p1_o, &c_p2_o)

    # We use an unscaled Knm matrix, so we need to apply the waist size and gouy phase
    # as we always reverse the gouy phase anyway, we just don't bother adding it here
    # k0 scaling with nr is done in code jsut below, along with spot size
    # TODO ddb - these matrix multiplications would be more efficient with a sparse matrix
    # format, CSR maybe? As dense product scales badly with maxtem
    cdef complex_t a_2_o_factor = 1j * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
    if ws.sim.is_modal:
        q_P1o = &ws.sim.trace[ws.P1o_id]
        q_P2o = &ws.sim.trace[ws.P2o_id]

        if conn.pitch_P1o[pitch_freq_idx][freq.index]:
            wy = bp_beamsize(&q_P1o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.pitch_P1o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P1i_P1o[carrier_index]), 0,
                2/2 * ws.nr1 * wy * a_2_o_factor * phase_shift,
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.pitch_P1o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P2i_P1o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wy * a_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )

        if conn.pitch_P2o[pitch_freq_idx][freq.index]:
            wy = bp_beamsize(&q_P2o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            # Extra minus sign here because of coordinate system from back side of of tilted mirror
            (<SubCCSView>conn.pitch_P2o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                # minus because side 2 pitch sends beam upwards
                (<SubCCSView>car_conn.P2i_P2o[carrier_index]), 0,
                -2/2 * ws.nr2 * wy * a_2_o_factor * conj(phase_shift),
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.pitch_P2o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                -0.5 * (ws.nr1 - ws.nr2) * wy * a_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )
        # -------------------------------------------------
        # Optical to mechanical connections
        # -------------------------------------------------
        # These fill a nHOMx1 matrix to compute RP force
        # negative sign because a positive displacemtn from side 1 generates a negative pitch torque
        if conn.P1i_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P1i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                - ws.nr1 * wy * ws.field_to_F, &ws.K_pitch_sig.mtx, &c_p1_i
            )
        if conn.P1o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P1o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                - ws.nr1 * wy * ws.field_to_F, &ws.K_pitch_sig.mtx, &c_p1_o
            )
        if conn.P2i_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P2i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy * ws.field_to_F, &ws.K_pitch_sig.mtx, &c_p2_i
            )
        if conn.P2o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P2o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy * ws.field_to_F, &ws.K_pitch_sig.mtx, &c_p2_o
            )


cdef void multiple_z_mechanical_freq_signal_calc (
        MirrorWorkspace ws,
        HOMSolver carrier,
        mirror_signal_connections *conn,
        mirror_optical_connections *car_conn,
        frequency_info_t *freq,
        double phi
    ) noexcept:
    """Computes the opto-mechanics for a mirror with multiple optical and mechanical frequencies.
    """

    cdef:
        Py_ssize_t i, j
        frequency_info_t *ofrequencies = ws.sim.carrier.optical_frequencies.frequency_info
        Py_ssize_t osize = ws.sim.carrier.optical_frequencies.size
        double fs, fc, fm

    for i in range(osize): # Loop over optical DC
        for j in range(ws.z_mech_freqs_size): # Loop over mechanical frequencies
            fs = freq.f
            fc = ofrequencies[i].f
            fm = ws.z_mech_freqs[j].f

            if (fc-fs == fm) or (fs-fc == fm):
                single_z_mechanical_frequency_signal_calc(
                    ws, carrier, conn, car_conn, freq, phi, j, i
                )


cdef void single_z_mechanical_frequency_signal_calc (
        MirrorWorkspace ws,
        HOMSolver carrier,
        mirror_signal_connections *conn,
        mirror_optical_connections *car_conn,
        frequency_info_t *freq,
        double phi,
        Py_ssize_t z_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        complex_t _tuning   = 0.0
        complex_t _ctuning  = 0.0
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o

    get_carrier_vectors(carrier, ws, carrier_index, &c_p1_i, &c_p2_i, &c_p1_o, &c_p2_o)

    # -------------------------------------------------
    # Optical to mechanical connections
    # -------------------------------------------------
    # - Longitudinal
    # -------------------------------------------------
    # These fill a nHOMx1 matrix to compute RP force
    if conn.P1i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P1i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field_to_F,
            c_p1_i.ptr, 1, 1
        )
    if conn.P1o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P1o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field_to_F,
            c_p1_o.ptr, 1, 1
        )

    # Minus sign as we force the mirror in the opposite
    # direction from the other side
    if conn.P2i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P2i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field_to_F,
            c_p2_i.ptr, 1, 1
        )
    if conn.P2o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P2o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field_to_F,
            c_p2_o.ptr, 1, 1
        )

    # -----------------------------------------------------------------
    # Mechanical to optical connections
    # -----------------------------------------------------------------
    # - Longitudinal
    # -----------------------------------------------------------------
    # As the output has a mixture of both refl and transmitted we only
    # modulate the incoming and refl'd field so we have to propagate
    # the input

    # As we are using the propagaged carrier, it already has the various phase
    # static phase+amplitude factors, HOM scattering, etc. included, which is
    # useful as that means we don't duplicate the calculations here. However,
    # the phase accumulated is slightly different, as frequency shift happens
    # at the mirror so it picks up a slightly different detuning phase coming
    # back from the mirror, here we correct that
    phase_shift = phi * freq.f / ws.sim.model_settings.f0

    # -----------------------------------------------------------------
    # Signal generation z->p1.o
    if conn.Z_P1o[z_freq_idx][freq.index]:
        _tuning = cexp(1.0j * phase_shift)
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P1o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P1i_P1o[carrier_index]), 0, ws.z_to_field * _tuning, False
        )
    # -----------------------------------------------------------------
    # Signal generation z->p2.o
    # extra 180 phase here as we're doing the opposite
    # modulation when looked at from the other side of the mirror
    if conn.Z_P2o[z_freq_idx][freq.index]:
        _ctuning = conj(_tuning)
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P2o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P2i_P2o[carrier_index]), 0, -ws.z_to_field * _ctuning, False
        )


mirror_fill_qnoise = FillFuncWrapper.make_from_ptr(c_mirror_fill_qnoise)
cdef object c_mirror_fill_qnoise(ConnectorWorkspace cws) :
    r"""
    Fills the quantum noise input matrix elements corresponding to this `mirror`.
    """
    cdef:
        MirrorWorkspace ws = <MirrorWorkspace> cws
        PyObject ***noises = ws.output_noise.ptrs
        frequency_info_t *freq

        Py_ssize_t i, j

        double qn_internal_loss
        complex_t factor

    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        factor = 0.5 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)
        qn_internal_loss = ws.mv.L
        if not ws.sim.is_modal:
            (<SubCCSView>noises[0][freq.index]).fill_za(factor * qn_internal_loss)
            (<SubCCSView>noises[1][freq.index]).fill_za(factor * qn_internal_loss)
        else:
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.mv.R * ws.oconn_info[0].loss[j]
                ws.total_losses[j] += ws.mv.T * ws.oconn_info[3].loss[j]

            (<SubCCSView>noises[0][freq.index]).fill_za_dv(factor, ws.total_losses)
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.mv.R * ws.oconn_info[1].loss[j]
                ws.total_losses[j] += ws.mv.T * ws.oconn_info[2].loss[j]

            (<SubCCSView>noises[1][freq.index]).fill_za_dv(factor, ws.total_losses)
