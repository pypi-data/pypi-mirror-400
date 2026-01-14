from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport cexp
from finesse.cymath.math cimport sqrt, radians
from finesse.cymath.gaussbeam cimport bp_gouy, bp_beamsize
from finesse.cymath.cmatrix cimport SubCCSView
from finesse.simulations.base cimport NodeBeamParam
from finesse.frequency cimport frequency_info_t
from finesse.cymath.math cimport sgn
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver
from finesse.cymath.complex cimport DenseZVector
from finesse.knm.matrix cimport make_unscaled_X_scatter_knm_matrix, make_unscaled_Y_scatter_knm_matrix
from finesse.simulations.workspace cimport ABCDWorkspace

import numpy as np
cimport numpy as np
cimport cython

from cpython.ref cimport PyObject

ctypedef (double*, double*, double*) ptr_tuple_3

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD

cdef class LaserConnections:
    def __cinit__(self, HOMSolver mtx):
        cdef:
            int Nfo =  mtx.optical_frequencies.size

        # There are no carrier connections at a laser, just signals
        self.SIGPWR_P1o = SubCCSView2DArray(1, Nfo)
        self.SIGAMP_P1o = SubCCSView2DArray(1, Nfo)
        self.SIGFRQ_P1o = SubCCSView2DArray(1, Nfo)
        self.SIGPHS_P1o = SubCCSView2DArray(1, Nfo)
        self.dz_P1o = SubCCSView2DArray(1, Nfo)
        self.dx_P1o = SubCCSView2DArray(1, Nfo)
        self.dy_P1o = SubCCSView2DArray(1, Nfo)
        self.xbeta_P1o = SubCCSView2DArray(1, Nfo)
        self.ybeta_P1o = SubCCSView2DArray(1, Nfo)

        self.ptrs.SIGPWR_P1o = <PyObject***>self.SIGPWR_P1o.views
        self.ptrs.SIGAMP_P1o = <PyObject***>self.SIGAMP_P1o.views
        self.ptrs.SIGFRQ_P1o = <PyObject***>self.SIGFRQ_P1o.views
        self.ptrs.SIGPHS_P1o = <PyObject***>self.SIGPHS_P1o.views
        self.ptrs.dz_P1o = <PyObject***>self.dz_P1o.views
        self.ptrs.dx_P1o = <PyObject***>self.dx_P1o.views
        self.ptrs.dy_P1o = <PyObject***>self.dy_P1o.views
        self.ptrs.xbeta_P1o = <PyObject***>self.xbeta_P1o.views
        self.ptrs.ybeta_P1o = <PyObject***>self.ybeta_P1o.views


cdef class LaserValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_3 ptr = (&self.P, &self.phase, &self.f)
        cdef tuple params = ("P", "phase", "f")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class LaserWorkspace(ConnectorWorkspace):
    def __init__(self, object owner, BaseSimulation sim):
        super().__init__(
                owner,
                sim,
                None,
                LaserConnections(sim.signal) if sim.signal else None,
                LaserValues()
                )
        self.cvalues = self.values
        self.lc = self.signal.connections if sim.signal else None
        self.PIj_2 = PI*0.5j
        # indexes for beam tracing
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.K_yaw_sig = make_unscaled_X_scatter_knm_matrix(sim.model_settings.homs_view)
        self.K_pitch_sig = make_unscaled_Y_scatter_knm_matrix(sim.model_settings.homs_view)
        self.hom_vector = np.zeros(sim.model_settings.num_HOMs, dtype=complex)
        self.phase_vector = np.zeros(sim.model_settings.num_HOMs, dtype=complex)


cdef complex_t laser_scalar(LaserWorkspace ws) noexcept:
    """Scalar value for laser output"""
    return sqrt(2 * ws.cvalues.P / ws.sim.model_settings.EPSILON0_C) * cexp(1.0j * radians(ws.cvalues.phase))


cdef void fill_hom_vector(complex_t E, LaserWorkspace ws) noexcept:
    """Fills the workspace HOM vector for this laser"""
    cdef Py_ssize_t i

    if ws.sim.is_modal:
        for i in range(ws.sim.model_settings.num_HOMs):
            ws.hom_vector[i] = E * ws.power_coeffs[i] * ws.phase_vector[i]
    else:
        ws.hom_vector[0] = E # planewave


laser_carrier_fill_rhs = FillFuncWrapper.make_from_ptr(c_laser_carrier_fill_rhs)
cdef object c_laser_carrier_fill_rhs(ConnectorWorkspace cws) :
    r"""
    Fills the right hand side (RHS) vector corresponding to the light source `laser`.

    The field amplitude is set as

    .. math::
        a_{\mathrm{in}} = \sqrt{\frac{2P}{\epsilon_c}}~\exp{\left(i \varphi\right)},

    where :math:`P` is the laser power and :math:`\varphi` is the specified phase of
    the laser.

    Parameters
    ----------

    laser : :class:`.Laser`
        The laser object to fill.

    sim : :class:`.BaseSimulation`
        A handle to the simulation.

    values : dict
        Dictionary of evaluated model parameters.

    fsrc_index : int
        Index of source frequency bin.
    """
    cdef:
        LaserWorkspace ws = <LaserWorkspace>cws
        HOMSolver carrier = ws.sim.carrier
        complex_t Ein = laser_scalar(ws)
        Py_ssize_t i

    if ws.cvalues.signals_only:
        return

    if not ws.sim.is_modal:
        carrier.set_source_fast(
            ws.node_car_id, ws.fsrc_car_idx, 0, Ein, 0
        )
    else:
        fill_hom_vector(Ein, ws)
        for i in range(ws.sim.model_settings.num_HOMs):
            carrier.set_source_fast(
                ws.node_car_id, ws.fsrc_car_idx, i, ws.hom_vector[i], 0
            )


laser_fill_qnoise = FillFuncWrapper.make_from_ptr(c_laser_fill_qnoise)
cdef object c_laser_fill_qnoise(ConnectorWorkspace cws) :
    r"""
    Fills the quantum noise input matrix corresponding to the light source `laser`.
    """
    cdef:
        LaserWorkspace ws = <LaserWorkspace>cws
        PyObject ***noises = ws.output_noise.ptrs
        frequency_info_t *freq

        # Laser quantum noise injection
        complex_t qn

    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        qn = ws.sim.model_settings.UNIT_VACUUM / 2 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)
        (<SubCCSView>noises[0][freq.index]).fill_za(qn)


laser_fill_signal = FillFuncWrapper.make_from_ptr(c_laser_fill_signal)
cdef object c_laser_fill_signal(ConnectorWorkspace cws) :
    cdef:
        LaserWorkspace ws = <LaserWorkspace>cws
        laser_connections conns = <laser_connections>ws.lc.ptrs
        Py_ssize_t i
        double factor = ws.sim.model_settings.EPSILON0_C

        complex_t phs_sig
        complex_t frq_sig

        frequency_info_t *f
        DenseZVector c_p1_o
        NodeBeamParam *q_P1o
        double w
        double k = ws.sim.model_settings.k0

        complex_t Ein

    # Recompute any input field changes
    Ein = laser_scalar(ws)
    fill_hom_vector(Ein, ws)
    # fixed definitions for vector
    c_p1_o.size = ws.sim.model_settings.num_HOMs
    c_p1_o.stride = 1
    c_p1_o.ptr = &ws.hom_vector[0]

    for i in range(2): # Loop over each signal sideband
        f = &ws.sim.signal.optical_frequencies.frequency_info[ws.fcar_sig_sb_idx[i]]
        # TODO ddb - these are all assuming a single electronic frequency here, hence first 0 index
        if conns.SIGAMP_P1o[0][f.index]:
            # m/2 to get 2 * m * cosine power fluctuations
            (<SubCCSView>conns.SIGAMP_P1o[0][f.index]).fill_negative_za_zv(factor * 0.5, &c_p1_o)

        if conns.SIGPWR_P1o[0][f.index]:
            # m/4 to get m * cosine power fluctuations
            (<SubCCSView>conns.SIGPWR_P1o[0][f.index]).fill_negative_za_zv(factor * 0.5 * 0.5, &c_p1_o)

        if conns.SIGFRQ_P1o[0][f.index]:
            frq_sig =  0.5 / ws.sim.model_settings.fsig * sgn(f.audio_order)
            (<SubCCSView>conns.SIGFRQ_P1o[0][f.index]).fill_negative_za_zv(factor * frq_sig, &c_p1_o)

        if conns.SIGPHS_P1o[0][f.index]:
            phs_sig = 1j * 0.5
            (<SubCCSView>conns.SIGPHS_P1o[0][f.index]).fill_negative_za_zv(factor * phs_sig, &c_p1_o)

        if conns.dz_P1o[0][f.index]:
            (<SubCCSView>conns.dz_P1o[0][f.index]).fill_negative_za_zv(0.5j * k * factor, &c_p1_o)

        if conns.dx_P1o[0][f.index] or conns.xbeta_P1o[0][f.index]:
            q_P1o = &ws.sim.trace[ws.P1o_id]
            w = bp_beamsize(&q_P1o.qx)
            if conns.dx_P1o[0][f.index]:
                (<SubCCSView>conns.dx_P1o[0][f.index]).fill_negative_za_zmv(0.5 * k *  factor * w, &ws.K_yaw_sig.mtx, &c_p1_o)
            if conns.xbeta_P1o[0][f.index]:
                (<SubCCSView>conns.xbeta_P1o[0][f.index]).fill_negative_za_zmv(0.5j * k * factor * w, &ws.K_yaw_sig.mtx, &c_p1_o)

        if conns.dy_P1o[0][f.index] or conns.ybeta_P1o[0][f.index]:
            q_P1o = &ws.sim.trace[ws.P1o_id]
            w = bp_beamsize(&q_P1o.qy)
            if conns.dy_P1o[0][f.index]:
                (<SubCCSView>conns.dy_P1o[0][f.index]).fill_negative_za_zmv(0.5 * k * factor * w, &ws.K_pitch_sig.mtx, &c_p1_o)
            if conns.ybeta_P1o[0][f.index]:
                (<SubCCSView>conns.ybeta_P1o[0][f.index]).fill_negative_za_zmv(0.5j * k * factor * w, &ws.K_pitch_sig.mtx, &c_p1_o)


laser_set_gouy = GouyFuncWrapper.make_from_ptr(set_tem_gouy_phases)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef int set_tem_gouy_phases(ABCDWorkspace ws) except -1:
    cdef:
        const NodeBeamParam* q_p1o = &ws.sim.trace[ws.P1o_id]
        double gouy_x
        double gouy_y
        double phase00 = 0.0
        Py_ssize_t i
        int n, m

    gouy_x = bp_gouy(&q_p1o.qx)
    gouy_y = bp_gouy(&q_p1o.qy)

    if ws.sim.model_settings.phase_config.zero_tem00_gouy:
        phase00 = 0.5 * gouy_x + 0.5 * gouy_y

    for i in range(ws.sim.model_settings.num_HOMs):
        if ws.add_gouy_phase:
            n = ws.sim.model_settings.homs_view[i][0]
            m = ws.sim.model_settings.homs_view[i][1]
            ws.phase_vector[i] = cexp(1j*(((n + 0.5) * gouy_x + (m + 0.5) * gouy_y - phase00)))
        else:
            ws.phase_vector[i] = 1

    return 0
