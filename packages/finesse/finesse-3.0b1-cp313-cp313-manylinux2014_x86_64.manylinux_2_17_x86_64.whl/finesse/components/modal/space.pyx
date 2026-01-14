# cython: profile=False

from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport cexp, ceq, creal, cimag, cabs
from finesse.cymath.math cimport fabs, radians, degrees
from finesse.cymath.gaussbeam cimport bp_gouy, transform_q
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.simulations.base cimport NodeBeamParam
from finesse.frequency cimport frequency_info_t
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver
from finesse.simulations.workspace cimport ABCDWorkspace
from finesse.symbols import Symbol

cimport cython

from cpython.ref cimport PyObject
from libc.stdlib cimport free, calloc


cdef extern from "math.h":
    double sin(double)
    double cos(double)


ctypedef (double*, double*, double*, double*) ptr_tuple_4


cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD


cdef class SpaceOpticalConnections:
    def __cinit__(self, HOMSolver mtx):
        # Only 1D arrays of views as spaces don't
        # couple frequencies together.
        Nf = mtx.optical_frequencies.size
        self.P1i_P2o = SubCCSView1DArray(Nf)
        self.P2i_P1o = SubCCSView1DArray(Nf)
        self.opt_ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.opt_ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views


cdef class SpaceSignalConnections(SpaceOpticalConnections):
    def __cinit__(self, HOMSolver mtx):
        # Only 1D arrays of views as spaces don't
        # couple frequencies together.
        if not mtx.is_signal_matrix:
            raise Exception("Signal simulation not enabled")
        Nf = mtx.optical_frequencies.size
        self.SIGAMP_P1o = SubCCSView2DArray(1, Nf)
        self.SIGAMP_P2o = SubCCSView2DArray(1, Nf)
        self.SIGPHS_P1o = SubCCSView2DArray(1, Nf)
        self.SIGPHS_P2o = SubCCSView2DArray(1, Nf)
        self.H_P1o = SubCCSView2DArray(1, Nf)
        self.H_P2o = SubCCSView2DArray(1, Nf)

        self.sig_ptrs.SIGAMP_P1o = <PyObject***>self.SIGAMP_P1o.views
        self.sig_ptrs.SIGAMP_P2o = <PyObject***>self.SIGAMP_P2o.views
        self.sig_ptrs.SIGPHS_P1o = <PyObject***>self.SIGPHS_P1o.views
        self.sig_ptrs.SIGPHS_P2o = <PyObject***>self.SIGPHS_P2o.views
        self.sig_ptrs.H_P1o = <PyObject***>self.H_P1o.views
        self.sig_ptrs.H_P2o = <PyObject***>self.H_P2o.views


cdef class SpaceValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_4 ptr = (&self.L, &self.nr, &self.user_gouy_x, &self.user_gouy_y)
        cdef tuple params = ("L","nr","user_gouy_x","user_gouy_y") #
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class SpaceWorkspace(ConnectorWorkspace):
    def __init__(self, object owner, BaseSimulation sim):
        cdef HOMSolver carrier = sim.carrier
        cdef HOMSolver signal = sim.signal

        super().__init__(
            owner, sim,
            SpaceOpticalConnections(carrier),
            SpaceSignalConnections(signal) if signal is not None else None,
            SpaceValues()
        )

        # Here we cast connections and values to a non-specific object
        # so the fill functions don't have to and cython can optimise better
        self.sco = self.carrier.connections
        self.scs = self.signal.connections if signal is not None else None
        self.sv = self.values

        self.P1i_id = sim.trace_node_index[owner.p1.i]
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.P2i_id = sim.trace_node_index[owner.p2.i]
        self.P2o_id = sim.trace_node_index[owner.p2.o]

        self.car_p1o_idx = sim.carrier.node_id(owner.p1.o)
        self.car_p2o_idx = sim.carrier.node_id(owner.p2.o)

        if signal is not None:
            # If we have a signal simulation then we need to cache some indicies
            # for grabbing data when filling
            self.car_p1o_rhs_idx = carrier.get_node_info(owner.p1.o)["rhs_index"]
            self.car_p2o_rhs_idx = carrier.get_node_info(owner.p2.o)["rhs_index"]
            self.car_p_num_hom =   carrier.get_node_info(owner.p1.o)["nhoms"]
            self.strain_signal_enabled = owner.h.i.full_name in signal.nodes
            self.phase_signal_enabled = owner.phs.i.full_name in signal.nodes
            self.amp_signal_enabled = owner.amp.i.full_name in signal.nodes

        self.couplings = <complex_t*> calloc(sim.model_settings.num_HOMs, sizeof(complex_t))
        if not self.couplings:
            raise MemoryError()
        self.sym_abcd_B = NULL

    def __dealloc__(self):
        if self.couplings:
            free(self.couplings)

        cy_expr_free(self.sym_abcd_B)

    def compile_abcd_cy_exprs(self):
        cdef:
            object space = self.owner
            cdef object[:, ::1] M_sym = list(space._abcd_matrices.values())[0][0]

        # NOTE (sjr) Only element B of a Space ABCD matrix can possibly change
        if isinstance(M_sym[0][1], Symbol):
            ch_sym = M_sym[0][1].expand_symbols().eval(keep_changing_symbols=True)
            if isinstance(ch_sym, Symbol):
                self.sym_abcd_B = cy_expr_new()
                cy_expr_init(self.sym_abcd_B, ch_sym)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cpdef update_parameter_values(self) :
        ConnectorWorkspace.update_parameter_values(self)

        if self.sym_abcd_B != NULL:
            self.abcd[0][1] = cy_expr_eval(self.sym_abcd_B)


space_carrier_fill = FillFuncWrapper.make_from_ptr(c_space_carrier_fill)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef object c_space_carrier_fill(ConnectorWorkspace cws) :
    r"""
    Fills the sub-matrix of the interferometer matrix held by `sim`, corresponding
    to the `space` component.

    The space component propagates a light field over a length :math:`L` with index of refraction
    :math:`n_r`. The product :math:`n_rL` is, by definition in Finesse, always a multiple of the default
    laser wavelength :math:`\lambda_0`. This defines a *macroscopic length*.

    .. _fig_space_couplings:
    .. figure:: ../images/space.*
        :align: center

        Field couplings for a space.

    The propagation only affects the phase of the field (in the plane-wave picture):

    .. math::
        s_1 = s_2 = \exp{\left(-i(\omega_0 + \Delta\omega) n_rL / c\right)}
        = \exp{\left(-i\Delta\omega n_rL / c\right)},

    where :math:`\exp{\left(-i\omega_0 n_rL / c\right)} = 1` following from the definition of macroscopic lengths
    above. The quantity :math:`\Delta\omega` is the offset to the default (angular) frequency :math:`\omega`.

    In the modal picture, Gouy phases are accumulated over space components. This results in the coupling equation
    including these phase terms such that each field of a different mode order has a different phase accumulation:

    .. math::
        s_{1, \mathrm{nm}} = s_{2, \mathrm{nm}} = \exp{\left(-i(\Delta\omega n_rL / c + n\psi_x + m\psi_y)\right)},

    where :math:`n, m` are the mode indices and :math:`\psi_x, \psi_y` are the Gouy phases of the space in tangential
    and sagittal planes, respectively. Note that if the flag `zero_tem00_gouy` is false, then :math:`n \rightarrow n + 1/2`
    and :math:`m \rightarrow m + 1/2`.

    Parameters
    ----------
    """
    cdef:
        SpaceWorkspace ws = <SpaceWorkspace>cws
        HOMSolver carrier = ws.sim.carrier
        space_optical_connections *conns = <space_optical_connections*>&ws.sco.opt_ptrs

        double pre_factor = 2 * PI * ws.sv.nr * ws.sv.L / C_LIGHT

        double gouy_x
        double gouy_y

        Py_ssize_t size
        int i
        frequency_info_t *frequencies
        frequency_info_t *freq

    # use user gouy phase if set
    gouy_x = radians(ws.sv.user_gouy_x if ws.use_user_gouy_x else ws.sv.computed_gouy_x)
    gouy_y = radians(ws.sv.user_gouy_y if ws.use_user_gouy_y else ws.sv.computed_gouy_y)

    frequencies = carrier.optical_frequencies.frequency_info
    size = carrier.optical_frequencies.size

    for i in range(size):
        freq = &frequencies[i]
        space_fill_optical_2_optical(
            conns, ws, freq, pre_factor,
            gouy_x, gouy_y,
            ws.sim.model_settings.phase_config.zero_tem00_gouy,
            ws.sim.model_settings.homs_view
        )

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline void space_fill_optical_2_optical(
        space_optical_connections *conn,
        SpaceWorkspace ws,
        frequency_info_t *freq,
        double pre_factor,
        double gouy_x,
        double gouy_y,
        bint zero_tem00_gouy,
        int[:, ::1] homs_view
    ) noexcept:
    cdef:
        int n, m
        double ni

    phi = pre_factor * freq.f

    for field_idx in range(homs_view.shape[0]):
        n = homs_view[field_idx][0]
        m = homs_view[field_idx][1]

        if zero_tem00_gouy:
            ni = n
            mi = m
        else:
            ni = n + 0.5
            mi = m + 0.5

        gouy = ni * gouy_x + mi * gouy_y
        ws.couplings[field_idx] = cexp(1j * (-phi + gouy))

    # Fill diagonals with the vector
    if conn.P1i_P2o[freq.index]:
        (<SubCCSView>conn.P1i_P2o[freq.index]).fill_negative_zd_2(ws.couplings, 1)
    if conn.P2i_P1o[freq.index]:
        (<SubCCSView>conn.P2i_P1o[freq.index]).fill_negative_zd_2(ws.couplings, 1)


space_signal_fill = FillFuncWrapper.make_from_ptr(c_space_signal_fill)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef object c_space_signal_fill(ConnectorWorkspace cws) :
    cdef:
        SpaceWorkspace ws = <SpaceWorkspace>cws
        HOMSolver signal = ws.sim.signal
        space_optical_connections *oconns = <space_optical_connections*>&ws.scs.opt_ptrs
        space_signal_connections *sconns = <space_signal_connections*>&ws.scs.sig_ptrs

        double pre_factor = 2 * PI * ws.sv.nr * ws.sv.L / C_LIGHT

        double gouy_x
        double gouy_y

        Py_ssize_t size
        int i
        frequency_info_t *frequencies

    # use user gouy phase if set
    gouy_x = radians(ws.sv.user_gouy_x if ws.use_user_gouy_x else ws.sv.computed_gouy_x)
    gouy_y = radians(ws.sv.user_gouy_y if ws.use_user_gouy_y else ws.sv.computed_gouy_y)

    frequencies = signal.optical_frequencies.frequency_info
    size = signal.optical_frequencies.size

    for i in range(size): # for each optical signal sideband
        space_fill_optical_2_optical(
            oconns, ws, &frequencies[i], pre_factor,
            gouy_x, gouy_y,
            ws.sim.model_settings.phase_config.zero_tem00_gouy,
            ws.sim.model_settings.homs_view
        )

    if ws.strain_signal_enabled:
        for i in range(size): # for each optical signal sideband
            strain_signal_fill(sconns, ws, &frequencies[i])

    if ws.phase_signal_enabled:
        for i in range(size): # for each optical signal sideband
            phase_signal_fill(sconns, ws, &frequencies[i])

    if ws.amp_signal_enabled:
        for i in range(size): # for each optical signal sideband
            amplitude_signal_fill(sconns, ws, &frequencies[i])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline void phase_signal_fill(
    space_signal_connections *sconns,
    SpaceWorkspace ws,
    frequency_info_t *freq
) noexcept:
    cdef:
        Py_ssize_t N = 0
        HOMSolver carrier = ws.sim.carrier
        const complex_t* c_p1_o = NULL
        const complex_t* c_p2_o = NULL
        complex_t z = -1j * 0.5 # Just some pure phase modulation on the space outputs
        # Minus sign here because we model phase propagation as exp(-1j*(phi+A sin(Omega*t)))

    # Here we use the outgoing carrier field at each port.
    # This ensures that we include any gouy phase terms, etc.
    # that would otherwise need to be applied here as well,
    # compared to using the incoming fields.
    c_p1_o = carrier.node_field_vector_fast(ws.car_p1o_idx, freq.audio_carrier_index, &N)
    assert(c_p1_o != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_o = carrier.node_field_vector_fast(ws.car_p2o_idx, freq.audio_carrier_index, &N)
    assert(c_p2_o != NULL)
    assert(ws.car_p_num_hom == N)

    if sconns.SIGPHS_P1o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.SIGPHS_P1o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p1_o, 1 # 1D contiguous array from outview
        )

    if sconns.SIGPHS_P2o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.SIGPHS_P2o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p2_o, 1 # 1D contiguous array from outview
        )


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline void amplitude_signal_fill(
    space_signal_connections *sconns,
    SpaceWorkspace ws,
    frequency_info_t *freq
) noexcept:
    cdef:
        Py_ssize_t N = 0
        HOMSolver carrier = ws.sim.carrier
        const complex_t* c_p1_o = NULL
        const complex_t* c_p2_o = NULL
        # Just some pure amplitude modulate whatever
        # is coming out of the space ports
        complex_t z = 0.5

    # Here we use the outgoing carrier field at each port.
    # This ensures that we include any gouy phase terms, etc.
    # that would otherwise need to be applied here as well,
    # compared to using the incoming fields.
    c_p1_o = carrier.node_field_vector_fast(ws.car_p1o_idx, freq.audio_carrier_index, &N)
    assert(c_p1_o != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_o = carrier.node_field_vector_fast(ws.car_p2o_idx, freq.audio_carrier_index, &N)
    assert(c_p2_o != NULL)
    assert(ws.car_p_num_hom == N)

    if sconns.SIGAMP_P1o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.SIGAMP_P1o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p1_o, 1 # 1D contiguous array from outview
        )

    if sconns.SIGAMP_P2o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.SIGAMP_P2o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p2_o, 1 # 1D contiguous array from outview
        )


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void strain_signal_fill(
    space_signal_connections *sconns,
    SpaceWorkspace ws,
    frequency_info_t *freq
) noexcept:
    cdef:
        Py_ssize_t N = 0
        double w_g, m_g, w_0
        const complex_t* c_p1_o = NULL
        const complex_t* c_p2_o = NULL
        complex_t z
        HOMSolver carrier = ws.sim.carrier

    # Reference for strain signal over a space...
    # Interferometer responses to gravitational waves:
    # Comparing Finesse simulations and analytical solutions
    # Charlotte Bond, Daniel Brown and Andreas Freise
    # LIGO DCC: T1300190
    # https://arxiv.org/pdf/1306.6752.pdf
    w_g = 2 * PI * ws.sim.model_settings.fsig  # GW frequency [rad/s]
    # What isn't really noted in the document is signals around multiple carrier
    # fields, but this is really just a scaling of w0
    w_0 = 2 * PI * (ws.sim.model_settings.f0 + freq.f_car[0])
    # 1/2 factor from Eq.7
    m_g = - 0.5 * w_0/w_g * sin(w_g * ws.sv.L * ws.sv.nr / 2 / C_LIGHT) # GW signal per strain [1/h] Eq.14
    phi_sb = - w_g * ws.sv.L * ws.sv.nr / 2 / C_LIGHT # Eq.15
    # audio order here takes care of minus sign options in Eq.17
    z = 1j*m_g * cexp(1j * phi_sb * freq.audio_order) # i factor from pi/2 in Eq.17
    # Carrier phase term in Eq.17 is included already using the out
    # going field at the ports below

    # Here we use the outgoing carrier field at each port.
    # This ensures that we include any gouy phase terms, etc.
    # that would otherwise need to be applied here as well,
    # compared to using the incoming fields.
    c_p1_o = carrier.node_field_vector_fast(ws.car_p1o_idx, freq.audio_carrier_index, &N)
    assert(c_p1_o != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_o = carrier.node_field_vector_fast(ws.car_p2o_idx, freq.audio_carrier_index, &N)
    assert(c_p2_o != NULL)
    assert(ws.car_p_num_hom == N)

    if sconns.H_P1o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.H_P1o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p1_o, 1 # 1D contiguous array from outview
        )

    if sconns.H_P2o[0][freq.index]:
        # Assume H only has a single frequency as input...
        (<SubCCSView>sconns.H_P2o[0][freq.index]).fill_negative_za_zd_2 (
            z, c_p2_o, 1 # 1D contiguous array from outview
        )


space_set_gouy = GouyFuncWrapper.make_from_ptr(c_set_gouy_phase)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef int c_set_gouy_phase(ABCDWorkspace cws) except -1:
    cdef:
        SpaceWorkspace ws = <SpaceWorkspace>cws
        const NodeBeamParam* q_p1o = &ws.sim.trace[ws.P1i_id]
        const NodeBeamParam* q_p2i = &ws.sim.trace[ws.P2o_id]

        double nr = ws.sv.nr

        complex_t qx_p1o_propagated
        complex_t qy_p1o_propagated

    qx_p1o_propagated = transform_q(
        ws.abcd, q_p1o.qx.q, nr, nr
    )
    qy_p1o_propagated = transform_q(
        ws.abcd, q_p1o.qy.q, nr, nr
    )

    # Can't have mismatches across spaces, these must occur at
    # components, so if a mismatch is present then report a bug
    # with an informative error message.
    if not ceq(q_p2i.qx.q, qx_p1o_propagated):
        raise RuntimeError(
            _space_mismatch_bug_report(
                ws,
                ws.P1i_id,
                ws.P2o_id,
                q_p1o.qx.q,
                q_p2i.qx.q,
                qx_p1o_propagated,
                "x"
            )
        )

    if not ceq(q_p2i.qy.q, qy_p1o_propagated):
        raise RuntimeError(
            _space_mismatch_bug_report(
                ws,
                ws.P1i_id,
                ws.P2o_id,
                q_p1o.qy.q,
                q_p2i.qy.q,
                qy_p1o_propagated,
                "y"
            )
        )

    # set workspace values
    ws.sv.computed_gouy_x = degrees(
        fabs(bp_gouy(&q_p2i.qx) - bp_gouy(&q_p1o.qx))
    )
    ws.sv.computed_gouy_y = degrees(
        fabs(bp_gouy(&q_p2i.qy) - bp_gouy(&q_p1o.qy))
    )

    return 0


cdef _space_mismatch_bug_report(
    SpaceWorkspace ws,
    Py_ssize_t node1_id,
    Py_ssize_t node2_id,
    complex_t q1,
    complex_t q2,
    complex_t q2e, # expected q
    direction, # "x" or "y"
) :
    node1_name = list(ws.sim.carrier.nodes.keys())[node1_id]
    node2_name = list(ws.sim.carrier.nodes.keys())[node2_id]

    z_diff = fabs(creal(q2e) - creal(q2))
    zr_diff = fabs(cimag(q2e) - cimag(q2))
    mag_diff = cabs(q2e - q2)

    return (
        f"Mismatch in space {ws.owner.name} "
        f"from {node1_name} -> {node2_name}:"
        f"\n    STORED q{direction} @ {node2_name} = {q2}"
        f"\n    EXPECTED q{direction} = {q2e}"
        f"\n        given q{direction} @ {node1_name} = {q1},"
        f"\n        with ABCD = {ws.abcd.base.tolist()}"
        f"\n    DIFFERENCES: |z2 - z1| = {z_diff}, |zr2 - zr1| = {zr_diff};"
        f"\n                 |q1 - q2| = {mag_diff}"
    )
