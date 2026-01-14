from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView2DArray
from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport crotate, conj
from finesse.cymath.math cimport radians, cosh, sinh
from finesse.frequency cimport frequency_info_t
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.sparse.solver cimport SparseSolver
import numpy as np
cimport numpy as np

ctypedef (double*, double*, double*) ptr_tuple_3

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD
    double DB2R


cdef class SqueezerConnections:
    def __cinit__(self, SparseSolver mtx):
        cdef:
            int Nfo =  mtx.optical_frequencies.size

        self.UPPER_P1o = SubCCSView2DArray(1, Nfo)
        self.LOWER_P1o = SubCCSView2DArray(1, Nfo)
        self.ptrs.UPPER_P1o = <PyObject***>self.UPPER_P1o.views
        self.ptrs.LOWER_P1o = <PyObject***>self.LOWER_P1o.views


cdef class SqueezerNoiseSources:
    def __cinit__(self, SparseSolver mtx):
        cdef:
            int Nfo =  mtx.optical_frequencies.size

        self.P1o = SubCCSView2DArray(Nfo, Nfo)
        self.ptrs.P1o = <PyObject***>self.P1o.views


cdef class SqueezerValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_3 ptr = (&self.db, &self.angle, &self.f)
        cdef tuple params = ("db","angle","f")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class SqueezerWorkspace(ConnectorWorkspace):
    def __init__(self, object owner, BaseSimulation sim):
        super().__init__(
            owner,
            sim,
            None,
            SqueezerConnections(sim.signal) if sim.signal else None,
            values=SqueezerValues(),
            noise_sources=SqueezerNoiseSources(sim.signal) if sim.signal else None
        )
        self.v = self.values
        self.conns = self.signal.connections if sim.signal else None
        self.ns = self.signal.noise_sources if sim.signal else None
        self.qn_coeffs = np.zeros((sim.model_settings.num_HOMs, sim.model_settings.num_HOMs), dtype=np.complex128)
        self.qn_coeffs_diag = np.zeros(sim.model_settings.num_HOMs, dtype=np.complex128)
        self.hom_vector = np.zeros(sim.model_settings.num_HOMs, dtype=complex)
        self.hom_vector[0] = 1 # TODO ddb - always HG00 for the squeezer for now
        # fixed definitions for vector
        self.c_p1_o.size = sim.model_settings.num_HOMs
        self.c_p1_o.stride = 1
        self.c_p1_o.ptr = &self.hom_vector[0]


squeezer_fill_qnoise = FillFuncWrapper.make_from_ptr(c_squeezer_fill_qnoise)
cdef object c_squeezer_fill_qnoise(ConnectorWorkspace cws) :
    r"""
    Fills the quantum noise right hand side (RHS) vector corresponding
    to the squeezed-light source `squeezer`.
    """
    cdef:
        SqueezerWorkspace ws = cws

        # Laser quantum noise injection
        complex_t n = ws.sim.model_settings.UNIT_VACUUM / 2
        complex_t phs = crotate(1, 2 * radians(ws.v.angle))
        double r = ws.v.db * DB2R
        complex_t qn
        squeezer_noise_sources noises = ws.ns.ptrs
        frequency_info_t *ifreq
        frequency_info_t *ofreq

        Py_ssize_t i

    # TODO: Shouldn't this quantum noise be frequency-dependent, as for other noise sources?
    ws.qn_coeffs_diag[:] = n

    for i in range(ws.sim.signal.optical_frequencies.size):
        ifreq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        if ifreq.audio_carrier_index != ws.fsrc_car_idx:
            (<SubCCSView>noises.P1o[ifreq.index][ifreq.index]).fill_za(n)
            continue
        for j in range(ws.sim.signal.optical_frequencies.size):
            ofreq = &(ws.sim.signal.optical_frequencies.frequency_info[j])
            if ofreq.audio_carrier_index != ws.fsrc_car_idx:
                continue
            # Reflections

            if ws.sim.signal.optical_frequencies.frequency_info[i].audio_order > 0:
                if i == j:
                    qn = n * cosh(2 * r)
                else:
                    qn = n * sinh(2 * r) * phs
            else:
                if i == j:
                    qn = conj(n * cosh(2 * r))
                else:
                    qn = conj(n * sinh(2 * r) * phs)

            # We only want to squeeze the main mode of the interferometer, so just set the first
            # element of the relevant matrix/diagonal
            if i == j:
                ws.qn_coeffs_diag[0] = qn
                (<SubCCSView>noises.P1o[ifreq.index][ofreq.index]).fill_zd(ws.qn_coeffs_diag)
            else:
                ws.qn_coeffs[0][0] = qn
                (<SubCCSView>noises.P1o[ifreq.index][ofreq.index]).fill_zm(ws.qn_coeffs)


squeezer_fill_rhs = FillFuncWrapper.make_from_ptr(c_squeezer_fill_rhs)
cdef object c_squeezer_fill_rhs(ConnectorWorkspace cws) :
    cdef:
        SqueezerWorkspace ws = <SqueezerWorkspace>cws

    if not ws.sim.is_modal:
        ws.sim.set_source_fast(
            ws.node_id, ws.fsrc_car_idx, 0, 0, 0
        )
    else:
        for i in range(ws.signal.nhoms):
            ws.sim.set_source_fast(
                ws.node_id, ws.fsrc_car_idx, i, 0, 0
            )


squeezer_fill_signal = FillFuncWrapper.make_from_ptr(c_squeezer_fill_signal)
cdef object c_squeezer_fill_signal(ConnectorWorkspace cws) :
    cdef:
        SqueezerWorkspace ws = <SqueezerWorkspace>cws
        squeezer_connections conns = <squeezer_connections>ws.conns.ptrs
        complex_t factor = crotate(np.sqrt(2), radians(ws.v.angle))
        frequency_info_t *f = NULL

    # TODO ddb - these are all assuming a single electronic frequency here, hence first 0 index

    f = &ws.sim.signal.optical_frequencies.frequency_info[ws.fcar_sig_sb_idx[0]]
    if conns.UPPER_P1o[0][f.index]:
        (<SubCCSView>conns.UPPER_P1o[0][f.index]).fill_negative_za_zv(factor, &ws.c_p1_o)

    f = &ws.sim.signal.optical_frequencies.frequency_info[ws.fcar_sig_sb_idx[1]]
    if conns.LOWER_P1o[0][f.index]:
        (<SubCCSView>conns.LOWER_P1o[0][f.index]).fill_negative_za_zv(factor, &ws.c_p1_o)
