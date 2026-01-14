#cython: boundscheck=False, wraparound=False, initializedcheck=False, profile=False

cimport numpy as np
import numpy as np
from finesse.knm.matrix cimport make_unscaled_X_scatter_knm_matrix, make_unscaled_Y_scatter_knm_matrix
from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj, cexp
from finesse.cymath.gaussbeam cimport bp_beamsize
from finesse.cymath.math cimport sqrt
from finesse.frequency cimport FrequencyContainer
from finesse.cymath.cmatrix cimport SubCCSView, SubCCSView1DArray, SubCCSView2DArray
from finesse.symbols import Symbol
from finesse.cymath.complex cimport DenseZVector
from finesse.utilities import refractive_index

from cpython.ref cimport PyObject
from libc.stdlib cimport free, calloc

import logging

ctypedef (double*, double*, double*, double*, double*, double*, double*, double*, double*, double*, double*) ptr_tuple_11

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD


LOGGER = logging.getLogger(__name__)


cdef class BeamsplitterOpticalConnections:
    def __cinit__(self, object bs, HOMSolver mtx):
        # Only 1D arrays of views as spaces don't
        # couple frequencies together.
        Nf = mtx.optical_frequencies.size
        self.P1i_P2o = SubCCSView1DArray(Nf)
        self.P2i_P1o = SubCCSView1DArray(Nf)
        self.P3i_P4o = SubCCSView1DArray(Nf)
        self.P4i_P3o = SubCCSView1DArray(Nf)
        self.P1i_P3o = SubCCSView1DArray(Nf)
        self.P3i_P1o = SubCCSView1DArray(Nf)
        self.P2i_P4o = SubCCSView1DArray(Nf)
        self.P4i_P2o = SubCCSView1DArray(Nf)

        self.opt_conn_ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.opt_conn_ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views
        self.opt_conn_ptrs.P3i_P4o = <PyObject**>self.P3i_P4o.views
        self.opt_conn_ptrs.P4i_P3o = <PyObject**>self.P4i_P3o.views
        self.opt_conn_ptrs.P1i_P3o = <PyObject**>self.P1i_P3o.views
        self.opt_conn_ptrs.P3i_P1o = <PyObject**>self.P3i_P1o.views
        self.opt_conn_ptrs.P2i_P4o = <PyObject**>self.P2i_P4o.views
        self.opt_conn_ptrs.P4i_P2o = <PyObject**>self.P4i_P2o.views


cdef class BeamsplitterSignalConnections(BeamsplitterOpticalConnections):
    def __cinit__(self, object bs, HOMSolver mtx):
        cdef:
            int Nfo =  mtx.optical_frequencies.size

        Nmz = bs.mech.z.num_frequencies # num of mechanic frequencies

        self.P1i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P1o_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P2i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P2o_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P3i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P3o_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P4i_Fz = SubCCSView2DArray(Nfo, Nmz)
        self.P4o_Fz = SubCCSView2DArray(Nfo, Nmz)

        self.Z_P1o = SubCCSView2DArray(Nmz, Nfo)
        self.Z_P2o = SubCCSView2DArray(Nmz, Nfo)
        self.Z_P3o = SubCCSView2DArray(Nmz, Nfo)
        self.Z_P4o = SubCCSView2DArray(Nmz, Nfo)

        self.sig_conn_ptrs.P1i_Fz = <PyObject***>self.P1i_Fz.views
        self.sig_conn_ptrs.P1o_Fz = <PyObject***>self.P1o_Fz.views
        self.sig_conn_ptrs.P2i_Fz = <PyObject***>self.P2i_Fz.views
        self.sig_conn_ptrs.P2o_Fz = <PyObject***>self.P2o_Fz.views
        self.sig_conn_ptrs.P3i_Fz = <PyObject***>self.P3i_Fz.views
        self.sig_conn_ptrs.P3o_Fz = <PyObject***>self.P3o_Fz.views
        self.sig_conn_ptrs.P4i_Fz = <PyObject***>self.P4i_Fz.views
        self.sig_conn_ptrs.P4o_Fz = <PyObject***>self.P4o_Fz.views
        self.sig_conn_ptrs.Z_P1o = <PyObject***>self.Z_P1o.views
        self.sig_conn_ptrs.Z_P2o = <PyObject***>self.Z_P2o.views
        self.sig_conn_ptrs.Z_P3o = <PyObject***>self.Z_P3o.views
        self.sig_conn_ptrs.Z_P4o = <PyObject***>self.Z_P4o.views

        self.P1i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P1o_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P2i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P2o_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P3i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P3o_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P4i_Fyaw = SubCCSView2DArray(Nfo, 1)
        self.P4o_Fyaw = SubCCSView2DArray(Nfo, 1)

        self.yaw_P1o = SubCCSView2DArray(1, Nfo)
        self.yaw_P2o = SubCCSView2DArray(1, Nfo)
        self.yaw_P3o = SubCCSView2DArray(1, Nfo)
        self.yaw_P4o = SubCCSView2DArray(1, Nfo)

        self.sig_conn_ptrs.P1i_Fyaw = <PyObject***>self.P1i_Fyaw.views
        self.sig_conn_ptrs.P1o_Fyaw = <PyObject***>self.P1o_Fyaw.views
        self.sig_conn_ptrs.P2i_Fyaw = <PyObject***>self.P2i_Fyaw.views
        self.sig_conn_ptrs.P2o_Fyaw = <PyObject***>self.P2o_Fyaw.views
        self.sig_conn_ptrs.P3i_Fyaw = <PyObject***>self.P3i_Fyaw.views
        self.sig_conn_ptrs.P3o_Fyaw = <PyObject***>self.P3o_Fyaw.views
        self.sig_conn_ptrs.P4i_Fyaw = <PyObject***>self.P4i_Fyaw.views
        self.sig_conn_ptrs.P4o_Fyaw = <PyObject***>self.P4o_Fyaw.views
        self.sig_conn_ptrs.yaw_P1o = <PyObject***>self.yaw_P1o.views
        self.sig_conn_ptrs.yaw_P2o = <PyObject***>self.yaw_P2o.views
        self.sig_conn_ptrs.yaw_P3o = <PyObject***>self.yaw_P3o.views
        self.sig_conn_ptrs.yaw_P4o = <PyObject***>self.yaw_P4o.views

        self.P1i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P1o_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P2i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P2o_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P3i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P3o_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P4i_Fpitch = SubCCSView2DArray(Nfo, 1)
        self.P4o_Fpitch = SubCCSView2DArray(Nfo, 1)

        self.pitch_P1o = SubCCSView2DArray(1, Nfo)
        self.pitch_P2o = SubCCSView2DArray(1, Nfo)
        self.pitch_P3o = SubCCSView2DArray(1, Nfo)
        self.pitch_P4o = SubCCSView2DArray(1, Nfo)

        self.sig_conn_ptrs.P1i_Fpitch = <PyObject***>self.P1i_Fpitch.views
        self.sig_conn_ptrs.P1o_Fpitch = <PyObject***>self.P1o_Fpitch.views
        self.sig_conn_ptrs.P2i_Fpitch = <PyObject***>self.P2i_Fpitch.views
        self.sig_conn_ptrs.P2o_Fpitch = <PyObject***>self.P2o_Fpitch.views
        self.sig_conn_ptrs.P3i_Fpitch = <PyObject***>self.P3i_Fpitch.views
        self.sig_conn_ptrs.P3o_Fpitch = <PyObject***>self.P3o_Fpitch.views
        self.sig_conn_ptrs.P4i_Fpitch = <PyObject***>self.P4i_Fpitch.views
        self.sig_conn_ptrs.P4o_Fpitch = <PyObject***>self.P4o_Fpitch.views
        self.sig_conn_ptrs.pitch_P1o = <PyObject***>self.pitch_P1o.views
        self.sig_conn_ptrs.pitch_P2o = <PyObject***>self.pitch_P2o.views
        self.sig_conn_ptrs.pitch_P3o = <PyObject***>self.pitch_P3o.views
        self.sig_conn_ptrs.pitch_P4o = <PyObject***>self.pitch_P4o.views


cdef class BeamsplitterValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_11 ptr = (&self.R, &self.T, &self.L, &self.phi, &self.Rcx, &self.Rcy, &self.xbeta, &self.ybeta, &self.alpha, &self.plane, &self.misaligned)
        cdef tuple params = ("R","T","L","phi","Rcx","Rcy","xbeta","ybeta","alpha","plane","misaligned")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class BeamsplitterWorkspace(KnmConnectorWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        cdef FrequencyContainer fcnt

        super().__init__(
            owner,
            sim,
            BeamsplitterOpticalConnections(owner, sim.carrier),
            BeamsplitterSignalConnections(owner, sim.signal) if sim.signal else None,
            BeamsplitterValues()
        )
        # Store direct type cast for C access
        self.boc = self.carrier.connections
        if sim.signal:
            self.bsc = self.signal.connections
        else:
            self.bsc = None
        self.cvalues = self.values

        self.nr1 = refractive_index(owner.p1)
        self.nr2 = refractive_index(owner.p3)

        if owner.alpha.value == 0.0:
            self.cos_alpha = 1
            self.cos_alpha_2 = 1
        else:
            self.cos_alpha = np.cos(float(owner.alpha.value*DEG2RAD))
            self.cos_alpha_2 = np.cos(np.arcsin(self.nr1 / self.nr2 * np.sin(float(owner.alpha.value*DEG2RAD))))

        # tracing node information
        self.P1i_id = sim.trace_node_index[owner.p1.i]
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.P2i_id = sim.trace_node_index[owner.p2.i]
        self.P2o_id = sim.trace_node_index[owner.p2.o]
        self.P3i_id = sim.trace_node_index[owner.p3.i]
        self.P3o_id = sim.trace_node_index[owner.p3.o]
        self.P4i_id = sim.trace_node_index[owner.p4.i]
        self.P4o_id = sim.trace_node_index[owner.p4.o]

        self.car_p1o_idx = sim.carrier.node_id(owner.p1.o)
        self.car_p1i_idx = sim.carrier.node_id(owner.p1.i)
        self.car_p2o_idx = sim.carrier.node_id(owner.p2.o)
        self.car_p2i_idx = sim.carrier.node_id(owner.p2.i)
        self.car_p3o_idx = sim.carrier.node_id(owner.p3.o)
        self.car_p3i_idx = sim.carrier.node_id(owner.p3.i)
        self.car_p4o_idx = sim.carrier.node_id(owner.p4.o)
        self.car_p4i_idx = sim.carrier.node_id(owner.p4.i)

        if sim.signal:
            self.car_p1o_rhs_idx = sim.carrier.get_node_info(owner.p1.o)["rhs_index"]
            self.car_p1i_rhs_idx = sim.carrier.get_node_info(owner.p1.i)["rhs_index"]
            self.car_p2o_rhs_idx = sim.carrier.get_node_info(owner.p2.o)["rhs_index"]
            self.car_p2i_rhs_idx = sim.carrier.get_node_info(owner.p2.i)["rhs_index"]
            self.car_p3o_rhs_idx = sim.carrier.get_node_info(owner.p3.o)["rhs_index"]
            self.car_p3i_rhs_idx = sim.carrier.get_node_info(owner.p3.i)["rhs_index"]
            self.car_p4o_rhs_idx = sim.carrier.get_node_info(owner.p4.o)["rhs_index"]
            self.car_p4i_rhs_idx = sim.carrier.get_node_info(owner.p4.i)["rhs_index"]
            self.car_p_num_hom = sim.carrier.get_node_info(owner.p1.o)["nhoms"]

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

        self.sym_abcd_elements[:] = [
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
            <cy_expr**> calloc(4, sizeof(cy_expr*)), <cy_expr**> calloc(4, sizeof(cy_expr*)),
        ]
        for ptr in self.sym_abcd_elements:
            if not ptr:
                raise MemoryError()
        self.abcd_elements[:] = [
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        ]

    def __dealloc__(self):
        cdef Py_ssize_t k, i
        for k in range(16):
            if self.sym_abcd_elements[k] == NULL:
                continue

            for i in range(4):
                cy_expr_free(self.sym_abcd_elements[k][i])

            free(self.sym_abcd_elements[k])
            self.sym_abcd_elements[k] = NULL

    def compile_abcd_cy_exprs(self):
        cdef:
            object beamsplitter = self.owner
            list abcd_handles = list(beamsplitter._abcd_matrices.values())

        if self.sim.is_modal:
            # Check for total reflections first
            if self.abcd_p1p2_x is None:
                self.abcd_elements[0] = NULL
                self.abcd_elements[1] = NULL
            else:
                self.abcd_elements[0] = <double*>&self.abcd_p1p2_x[0][0]
                self.abcd_elements[1] = <double*>&self.abcd_p1p2_y[0][0]
            if self.abcd_p2p1_x is None:
                self.abcd_elements[2] = NULL
                self.abcd_elements[3] = NULL
            else:
                self.abcd_elements[2] = <double*>&self.abcd_p2p1_x[0][0]
                self.abcd_elements[3] = <double*>&self.abcd_p2p1_y[0][0]
            if self.abcd_p3p4_x is None:
                self.abcd_elements[4] = NULL
                self.abcd_elements[5] = NULL
            else:
                self.abcd_elements[4] = <double*>&self.abcd_p3p4_x[0][0]
                self.abcd_elements[5] = <double*>&self.abcd_p3p4_y[0][0]
            if self.abcd_p4p3_x is None:
                self.abcd_elements[6] = NULL
                self.abcd_elements[7] = NULL
            else:
                self.abcd_elements[6] = <double*>&self.abcd_p4p3_x[0][0]
                self.abcd_elements[7] = <double*>&self.abcd_p4p3_y[0][0]

            self.abcd_elements[8:16] = [
                <double*>&self.abcd_p1p3_x[0][0], <double*>&self.abcd_p1p3_y[0][0],
                <double*>&self.abcd_p3p1_x[0][0], <double*>&self.abcd_p3p1_y[0][0],
                <double*>&self.abcd_p2p4_x[0][0], <double*>&self.abcd_p2p4_y[0][0],
                <double*>&self.abcd_p4p2_x[0][0], <double*>&self.abcd_p4p2_y[0][0],
            ]

        cdef Py_ssize_t k, i, j
        cdef object[:, ::1] M_sym
        for k in range(16):
            if abcd_handles[k][0] is None:
                continue

            M_sym = abcd_handles[k][0]
            for i in range(2):
                for j in range(2):
                    if isinstance(M_sym[i][j], Symbol):
                        ch_sym = M_sym[i][j].expand_symbols().eval(keep_changing_symbols=True)
                        if isinstance(ch_sym, Symbol):
                            self.sym_abcd_elements[k][2 * i + j] = cy_expr_new()
                            cy_expr_init(
                                self.sym_abcd_elements[k][2 * i + j],
                                ch_sym,
                            )

    cpdef update_parameter_values(self) :
        ConnectorWorkspace.update_parameter_values(self)

        cdef Py_ssize_t k, i
        for k in range(16):
            if self.abcd_elements[k] == NULL:
                continue

            for i in range(4):
                if self.sym_abcd_elements[k][i] != NULL:
                    self.abcd_elements[k][i] = cy_expr_eval(
                        self.sym_abcd_elements[k][i]
                    )


cdef inline void beamsplitter_fill_optical_2_optical(
        bs_optical_connections *conn,
        BeamsplitterWorkspace ws,
        frequency_info_t *freq,
        double r,
        double t,
        double phi_0,
        double alpha
    ) noexcept:
    if ws.cvalues.misaligned >= 1:
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
        # are opposite phase on each side
        phi_r1 = 2 * phi_0 * ws.cos_alpha * phase_shift_scaling
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
        phi_r2 = -2 * phi_0 * ws.nr2 * ws.cos_alpha_2 * phase_shift_scaling
        if ws.imaginary_transmission:
            # Uses N=-1 of Eq.2.25
            phi_r1 = 2 * phi_0 * ws.nr1 * ws.cos_alpha * phase_shift_scaling
            phi_t = PI/2 + 0.5 * (phi_r1 + phi_r2)
        else:
            # Uses N=0 of Eq.2.25
            phi_r1 = PI + 2 * phi_0 * ws.nr1 * ws.cos_alpha * phase_shift_scaling
            phi_t = -PI/2 + 0.5 * (phi_r1 + phi_r2)

        _r1 = r * cexp(1j * phi_r1)
        _r2 = r * cexp(1j * phi_r2)
        _t0 = t * cexp(1j * phi_t)

    # reflections
    if conn.P1i_P2o[freq.index]:
        (<SubCCSView>conn.P1i_P2o[freq.index]).fill_negative_za_zm_2(_r1, &ws.K12.mtx)
    if conn.P2i_P1o[freq.index]:
        (<SubCCSView>conn.P2i_P1o[freq.index]).fill_negative_za_zm_2(_r1, &ws.K21.mtx)
    if conn.P3i_P4o[freq.index]:
        (<SubCCSView>conn.P3i_P4o[freq.index]).fill_negative_za_zm_2(_r2, &ws.K34.mtx)
    if conn.P4i_P3o[freq.index]:
        (<SubCCSView>conn.P4i_P3o[freq.index]).fill_negative_za_zm_2(_r2, &ws.K43.mtx)
    # transmissions
    if conn.P1i_P3o[freq.index]:
        (<SubCCSView>conn.P1i_P3o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K13.mtx)
    if conn.P3i_P1o[freq.index]:
        (<SubCCSView>conn.P3i_P1o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K31.mtx)
    if conn.P2i_P4o[freq.index]:
        (<SubCCSView>conn.P2i_P4o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K24.mtx)
    if conn.P4i_P2o[freq.index]:
        (<SubCCSView>conn.P4i_P2o[freq.index]).fill_negative_za_zm_2(_t0, &ws.K42.mtx)


beamsplitter_carrier_fill = FillFuncWrapper.make_from_ptr(c_beamsplitter_carrier_fill)
cdef object c_beamsplitter_carrier_fill(ConnectorWorkspace cws) :
    r"""
    Fills the sub-matrix of the interferometer matrix held by `sim`, corresponding
    to the `beamsplitter` component.

    A beam splitter is similar to a mirror except for the extra parameter :math:`\alpha`,
    which indicates the angle of incidence of the incoming beams, and that it has four
    ports with two couplings each. This is shown in :numref:`fig_bs_couplings`. See
    :func:`mirror_fill` for details on the common surface arguments.

    .. _fig_bs_couplings:
    .. figure:: /images/beamsplitter.*
        :align: center

        Field couplings at a beam splitter with a representation of the reference plane and
        the angle of incidence.

    Displacement of the beam splitter is assumed to be perpendicular to its optical surface,
    therefore the angle of incidence affects the phase change of the reflected light. This phase
    shift is given by,

    .. math::
        \varphi = 2\phi\frac{\omega}{\omega_0} \cos{\left(\alpha\right)},

    where :math:`omega` is the angular frequency of the reflected light.

    From this (and the details given in :func:`mirror_fill`), for each frequency light field :math:`f`
    in the interferometer, the following quantities are computed in general (including higher-order
    spatial modes) for the field couplings,

    .. math::
        \begin{array}{l}
            \mathrm{bs}_{12} = r K_{12} \exp{\left(i 2\phi \left(1 + \frac{f}{f_0}\right) \cos{\alpha} \right)},\\
            \mathrm{bs}_{21} = r K_{21} \exp{\left(i 2\phi \left(1 + \frac{f}{f_0}\right) \cos{\alpha} \right)},\\
            \mathrm{bs}_{13} = it K_{13},\\
            \mathrm{bs}_{31} = it K_{31},\\
            \mathrm{bs}_{34} = r K_{34} \exp{\left(-i 2\phi \left(1 + \frac{f}{f_0}\right) \cos{\alpha} \right)},\\
            \mathrm{bs}_{43} = r K_{43} \exp{\left(-i 2\phi \left(1 + \frac{f}{f_0}\right) \cos{\alpha} \right)},\\
            \mathrm{bs}_{24} = it K_{24},\\
            \mathrm{bs}_{42} = it K_{42},
        \end{array}

    where :math:`K_{\mathrm{ij}}` are the scattering matrices for each direction (see
    :ref:`scatter_matrices`). Here, each :math:`\mathrm{bs}_{\mathrm{ij}}` term now represents a
    vector of the couplings of all higher-order spatial mode fields present.

    Parameters
    ----------
    beamsplitter : :class:`.Beamsplitter`
        The beamsplitter object to fill.

    sim : :class:`.BaseSimulation`
        A handle to the simulation.

    values : dict
        Dictionary of evaluated model parameters.

    cos_alpha : float
        Cosine of the angle of incidence at the front surface.

    cos_alpha_2 : float
        Cosine of the angle of incidence at the back surface.

    lambda0 : float
        Wavelength of the laser beam light for the model.
    """
    cdef:
        BeamsplitterWorkspace ws = <BeamsplitterWorkspace>cws
        HOMSolver carrier = ws.sim.carrier
        double r = sqrt(ws.cvalues.R)
        double t = sqrt(ws.cvalues.T)
        double phi = DEG2RAD * ws.cvalues.phi
        double alpha = DEG2RAD * ws.cvalues.alpha

        Py_ssize_t _i, size
        frequency_info_t *frequencies
        bs_optical_connections *conn = &ws.boc.opt_conn_ptrs

    size = carrier.optical_frequencies.size
    frequencies = carrier.optical_frequencies.frequency_info

    for i in range(size):
        beamsplitter_fill_optical_2_optical(
            conn, ws, &frequencies[i], r, t, phi, alpha
        )


beamsplitter_signal_fill = FillFuncWrapper.make_from_ptr(c_beamsplitter_signal_fill)
cdef object c_beamsplitter_signal_fill(ConnectorWorkspace cws) :
    cdef:
        BeamsplitterWorkspace ws = <BeamsplitterWorkspace>cws
        HOMSolver carrier = ws.sim.carrier
        double r = sqrt(ws.cvalues.R)
        double t = sqrt(ws.cvalues.T)
        double phi = DEG2RAD * ws.cvalues.phi
        double alpha = DEG2RAD * ws.cvalues.alpha
        Py_ssize_t _i, size

        frequency_info_t *frequencies
        bs_optical_connections *car_conn = &ws.boc.opt_conn_ptrs
        bs_optical_connections *conn = &ws.bsc.opt_conn_ptrs
        bs_signal_connections *sconn = &ws.bsc.sig_conn_ptrs

    ws.z_to_field1 = 1j * ws.cos_alpha * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale
    ws.z_to_field2 = 1j * ws.cos_alpha_2 * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale
    ws.field1_to_F = ws.cos_alpha / (C_LIGHT * ws.sim.model_settings.x_scale)
    ws.field2_to_F = ws.cos_alpha_2 / (C_LIGHT * ws.sim.model_settings.x_scale)
    size = ws.sim.signal.optical_frequencies.size
    frequencies = ws.sim.signal.optical_frequencies.frequency_info

    for i in range(size):
        beamsplitter_fill_optical_2_optical(
            conn, ws, &frequencies[i], r, t, phi, alpha
        )

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
                single_yaw_mechanical_frequency_signal_calc(ws, carrier, sconn, car_conn, freq, phi, 0, freq.audio_carrier_index)
            else:
                raise NotImplementedError()

    if ws.pitch_signal_enabled:
        for i in range(size):
            freq = &(frequencies[i])
            if ws.pitch_mech_freqs_size == 1:
                single_pitch_mechanical_frequency_signal_calc(ws, carrier, sconn, car_conn, freq, phi, 0, freq.audio_carrier_index)
            else:
                raise NotImplementedError()


cdef void get_carrier_vectors(BeamsplitterWorkspace ws, HOMSolver carrier, int carrier_index,
        DenseZVector *c_p1_i, DenseZVector *c_p2_i,
        DenseZVector *c_p3_i, DenseZVector *c_p4_i,
        DenseZVector *c_p1_o, DenseZVector *c_p2_o,
        DenseZVector *c_p3_o, DenseZVector *c_p4_o
    ) noexcept nogil:
    assert(c_p1_i)
    assert(c_p2_i)
    assert(c_p3_i)
    assert(c_p4_i)
    assert(c_p1_o)
    assert(c_p2_o)
    assert(c_p3_o)
    assert(c_p4_o)
    cdef Py_ssize_t N = 0

    c_p1_i.size = c_p1_o.size = c_p2_i.size = c_p2_o.size = ws.car_p_num_hom
    c_p1_i.stride = c_p1_o.stride = c_p2_i.stride = c_p2_o.stride = 1
    c_p3_i.size = c_p3_o.size = c_p4_i.size = c_p4_o.size = ws.car_p_num_hom
    c_p3_i.stride = c_p3_o.stride = c_p4_i.stride = c_p4_o.stride = 1
    # Get incoming/outgoing carrier field amplitudes
    c_p1_i.ptr = carrier.node_field_vector_fast(ws.car_p1i_idx, carrier_index, &N)
    assert(c_p1_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_i.ptr = carrier.node_field_vector_fast(ws.car_p2i_idx, carrier_index, &N)
    assert(c_p2_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p3_i.ptr = carrier.node_field_vector_fast(ws.car_p3i_idx, carrier_index, &N)
    assert(c_p3_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p4_i.ptr = carrier.node_field_vector_fast(ws.car_p4i_idx, carrier_index, &N)
    assert(c_p4_i.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p1_o.ptr = carrier.node_field_vector_fast(ws.car_p1o_idx, carrier_index, &N)
    assert(c_p1_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p2_o.ptr = carrier.node_field_vector_fast(ws.car_p2o_idx, carrier_index, &N)
    assert(c_p2_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p3_o.ptr = carrier.node_field_vector_fast(ws.car_p3o_idx, carrier_index, &N)
    assert(c_p3_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)

    c_p4_o.ptr = carrier.node_field_vector_fast(ws.car_p4o_idx, carrier_index, &N)
    assert(c_p4_o.ptr != NULL)
    assert(ws.car_p_num_hom == N)


cdef void multiple_z_mechanical_freq_signal_calc (
        BeamsplitterWorkspace ws,
        HOMSolver carrier,
        bs_signal_connections *conn,
        bs_optical_connections *car_conn,
        frequency_info_t *freq,
        double phi
    ) noexcept:
    """Computes the opto-mechanics for a mirror with multiple optical and mechanical frequencies.
    """

    cdef:
        Py_ssize_t i, j
        frequency_info_t *ofrequencies = carrier.optical_frequencies.frequency_info
        Py_ssize_t osize = carrier.optical_frequencies.size
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
        BeamsplitterWorkspace ws,
        HOMSolver carrier,
        bs_signal_connections *conn,
        bs_optical_connections *car_conn,
        frequency_info_t *freq,
        double phi,
        Py_ssize_t z_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        complex_t _tuning, _ctuning
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o
        DenseZVector c_p3_i, c_p4_i, c_p3_o, c_p4_o

    get_carrier_vectors(ws, carrier, carrier_index,
        &c_p1_i, &c_p2_i, &c_p3_i, &c_p4_i,
        &c_p1_o, &c_p2_o, &c_p3_o, &c_p4_o,
    )

    # -------------------------------------------------
    # Optical to mechanical connections
    # -------------------------------------------------
    # - Longitudinal
    # -------------------------------------------------
    # These fill a nHOMx1 matrix to compute RP force
    if conn.P1i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P1i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field1_to_F, c_p1_i.ptr, 1, 1
        )
    if conn.P1o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P1o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field1_to_F, c_p1_o.ptr, 1, 1
        )
    if conn.P2i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P2i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field1_to_F, c_p2_i.ptr, 1, 1
        )
    if conn.P2o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P2o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            -ws.field1_to_F, c_p2_o.ptr, 1, 1
        )

    # Minus sign as we force the mirror in the opposite
    # direction from the other side
    if conn.P3i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P3i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field2_to_F, c_p3_i.ptr, 1, 1
        )
    if conn.P3o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P3o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field2_to_F, c_p3_o.ptr, 1, 1
        )
    if conn.P4i_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P4i_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field2_to_F, c_p4_i.ptr, 1, 1
        )
    if conn.P4o_Fz[freq.index][z_freq_idx]:
        (<SubCCSView>conn.P4o_Fz[freq.index][z_freq_idx]).fill_negative_za_zmc (
            ws.field2_to_F, c_p4_o.ptr, 1, 1
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
    _tuning = cexp(1.0j * phase_shift)
    if conn.Z_P1o[z_freq_idx][freq.index]:
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P1o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P2i_P1o[carrier_index]), 0, ws.z_to_field1 * _tuning, False
        )
    if conn.Z_P2o[z_freq_idx][freq.index]:
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P2o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0, ws.z_to_field1 * _tuning, False
        )
    # -----------------------------------------------------------------
    # Signal generation z->p2.o
    # extra 180 phase here as we're doing the opposite
    # modulation when looked at from the other side of the mirror
    if conn.Z_P3o[z_freq_idx][freq.index]:
        _ctuning = conj(_tuning)
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P3o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P4i_P3o[carrier_index]), 0, -ws.z_to_field2 * _ctuning, False
        )
    if conn.Z_P4o[z_freq_idx][freq.index]:
        _ctuning = conj(_tuning)
        # fill_prop_za as off-diagonal -1 is already included in the carrier connection
        (<SubCCSView>conn.Z_P4o[z_freq_idx][freq.index]).fill_prop_za (
            (<SubCCSView>car_conn.P3i_P4o[carrier_index]), 0, -ws.z_to_field2 * _ctuning, False
        )


cdef void single_yaw_mechanical_frequency_signal_calc (
        BeamsplitterWorkspace ws,
        HOMSolver carrier,
        bs_signal_connections *conn,
        bs_optical_connections *car_conn,
        frequency_info_t *freq, # audio sideband
        double phi,
        Py_ssize_t yaw_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        double wx1i, wx2i, wx3i, wx4i
        double wx1o = 0.0
        double wx2o = 0.0
        double wx3o = 0.0
        double wx4o = 0.0
        NodeBeamParam *q_P1o
        NodeBeamParam *q_P1i
        NodeBeamParam *q_P2o
        NodeBeamParam *q_P2i
        NodeBeamParam *q_P3o
        NodeBeamParam *q_P3i
        NodeBeamParam *q_P4o
        NodeBeamParam *q_P4i
        complex_t a1_2_o_factor, a2_2_o_factor
        complex_t phase_shift = cexp(1j*phi * freq.f / ws.sim.model_settings.f0)
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o
        DenseZVector c_p3_i, c_p4_i, c_p3_o, c_p4_o

    get_carrier_vectors(ws, carrier, carrier_index,
        &c_p1_i, &c_p2_i, &c_p3_i, &c_p4_i,
        &c_p1_o, &c_p2_o, &c_p3_o, &c_p4_o,
    )

    # We use an unscaled Knm matrix, so we need to apply the waist size and gouy phase
    # as we always reverse the gouy phase anyway, we just don't bother adding it here
    # k0 scaling with nr is done in code jsut below, along with spot size
    # TODO ddb - these matrix multiplications would be more efficient with a sparse matrix
    # format, CSR maybe? As dense product scales badly with maxtem
    if ws.sim.is_modal: # ignore filling this if doing plane-wave
        a1_2_o_factor = 1j * ws.cos_alpha * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
        a2_2_o_factor = 1j * ws.cos_alpha_2 * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
        q_P1o = &ws.sim.trace[ws.P1o_id]
        q_P2o = &ws.sim.trace[ws.P2o_id]
        q_P3o = &ws.sim.trace[ws.P3o_id]
        q_P4o = &ws.sim.trace[ws.P4o_id]
        q_P1i = &ws.sim.trace[ws.P1i_id]
        q_P2i = &ws.sim.trace[ws.P2i_id]
        q_P3i = &ws.sim.trace[ws.P3i_id]
        q_P4i = &ws.sim.trace[ws.P4i_id]

        if conn.yaw_P1o[yaw_freq_idx][freq.index]:
            wx1o = bp_beamsize(&q_P1o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P1o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P2i_P1o[carrier_index]), 0,
                2/2*ws.nr1 * wx1o * a1_2_o_factor * phase_shift,
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.yaw_P1o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P3i_P1o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wx1o * a1_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        if conn.yaw_P2o[yaw_freq_idx][freq.index]:
            wx2o = bp_beamsize(&q_P2o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P2o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                2/2*ws.nr1 * wx2o * a1_2_o_factor * phase_shift,
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.yaw_P2o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wx2o * a1_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        if conn.yaw_P3o[yaw_freq_idx][freq.index]:
            wx3o = bp_beamsize(&q_P3o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P3o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P4i_P3o[carrier_index]), 0,
                2/2*ws.nr2 * wx3o * a2_2_o_factor * conj(phase_shift),
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission coupling
            (<SubCCSView>conn.yaw_P3o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P3o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wx3o * a2_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        if conn.yaw_P4o[yaw_freq_idx][freq.index]:
            wx4o = bp_beamsize(&q_P4o.qx)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.yaw_P4o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P3i_P4o[carrier_index]), 0,
                -2/2*ws.nr2 * wx4o * a2_2_o_factor * conj(phase_shift),
                &ws.K_yaw_sig.mtx, False
            )
            # Transmission coupling
            (<SubCCSView>conn.yaw_P4o[yaw_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P2i_P4o[carrier_index]), 0,
                -0.5 * (ws.nr1 - ws.nr2) * wx4o * a2_2_o_factor,
                &ws.K_yaw_sig.mtx, True
            )

        # -------------------------------------------------
        # Optical to mechanical connections
        # -------------------------------------------------
        # These fill a nHOMx1 matrix to compute RP force
        # There is a minus sign difference between side 1 and 2 here, because
        # of the coordinate system change
        if conn.P1i_Fyaw[freq.index][yaw_freq_idx]:
            wx1i = bp_beamsize(&q_P1i.qx)
            (<SubCCSView>conn.P1i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr1 * wx1i * ws.field1_to_F, &ws.K_yaw_sig.mtx, &c_p1_i
            )
        # differing minus signs here because of the x coordinate flip compared to mechanical node x
        if conn.P1o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P1o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wx1o * ws.field1_to_F, &ws.K_yaw_sig.mtx, &c_p1_o
            )

        if conn.P2i_Fyaw[freq.index][yaw_freq_idx]:
            wx2i = bp_beamsize(&q_P2i.qx)
            (<SubCCSView>conn.P2i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr1 * wx2i * ws.field1_to_F, &ws.K_yaw_sig.mtx, &c_p2_i
            )
        if conn.P2o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P2o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wx2o * ws.field1_to_F, &ws.K_yaw_sig.mtx, &c_p2_o
            )

        if conn.P3i_Fyaw[freq.index][yaw_freq_idx]:
            wx3i = bp_beamsize(&q_P3i.qx)
            (<SubCCSView>conn.P3i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wx3i * ws.field2_to_F, &ws.K_yaw_sig.mtx,  &c_p3_i
            )
        if conn.P3o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P3o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr2 * wx3o * ws.field2_to_F, &ws.K_yaw_sig.mtx, &c_p3_o
            )

        if conn.P4i_Fyaw[freq.index][yaw_freq_idx]:
            wx4i = bp_beamsize(&q_P4i.qx)
            (<SubCCSView>conn.P4i_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wx4i * ws.field2_to_F, &ws.K_yaw_sig.mtx,  &c_p4_i
            )
        if conn.P4o_Fyaw[freq.index][yaw_freq_idx]:
            (<SubCCSView>conn.P4o_Fyaw[freq.index][yaw_freq_idx]).fill_negative_za_zmvc (
                -ws.nr2 * wx4o * ws.field2_to_F, &ws.K_yaw_sig.mtx, &c_p4_o
            )


cdef void single_pitch_mechanical_frequency_signal_calc (
        BeamsplitterWorkspace ws,
        HOMSolver carrier,
        bs_signal_connections *conn,
        bs_optical_connections *car_conn,
        frequency_info_t *freq, # audio sideband
        double phi,
        Py_ssize_t pitch_freq_idx,
        Py_ssize_t carrier_index
    ) noexcept:
    cdef:
        double wy1i, wy2i, wy3i, wy4i
        double wy1o = 0.0
        double wy2o = 0.0
        double wy3o = 0.0
        double wy4o = 0.0
        NodeBeamParam *q_P1o
        NodeBeamParam *q_P1i
        NodeBeamParam *q_P2o
        NodeBeamParam *q_P2i
        NodeBeamParam *q_P3o
        NodeBeamParam *q_P3i
        NodeBeamParam *q_P4o
        NodeBeamParam *q_P4i
        complex_t a1_2_o_factor, a2_2_o_factor
        complex_t phase_shift = cexp(1j*phi * freq.f / ws.sim.model_settings.f0)
        DenseZVector c_p1_i, c_p2_i, c_p1_o, c_p2_o
        DenseZVector c_p3_i, c_p4_i, c_p3_o, c_p4_o

    get_carrier_vectors(ws, carrier, carrier_index,
        &c_p1_i, &c_p2_i, &c_p3_i, &c_p4_i,
        &c_p1_o, &c_p2_o, &c_p3_o, &c_p4_o,
    )

    if ws.sim.is_modal: # ignore filling this if doing plane-wave
        a1_2_o_factor = 1j * ws.cos_alpha * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
        a2_2_o_factor = 1j * ws.cos_alpha_2 * ws.sim.model_settings.k0 * ws.sim.model_settings.x_scale * (1 + freq.f_car[0]/ws.sim.model_settings.f0)
        q_P1o = &ws.sim.trace[ws.P1o_id]
        q_P2o = &ws.sim.trace[ws.P2o_id]
        q_P3o = &ws.sim.trace[ws.P3o_id]
        q_P4o = &ws.sim.trace[ws.P4o_id]
        q_P1i = &ws.sim.trace[ws.P1i_id]
        q_P2i = &ws.sim.trace[ws.P2i_id]
        q_P3i = &ws.sim.trace[ws.P3i_id]
        q_P4i = &ws.sim.trace[ws.P4i_id]

        if conn.pitch_P1o[pitch_freq_idx][freq.index]:
            wy1o = bp_beamsize(&q_P1o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.pitch_P1o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P2i_P1o[carrier_index]), 0,
                -2/2*ws.nr1 * wy1o * a1_2_o_factor * phase_shift,
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.pitch_P1o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P3i_P1o[carrier_index]), 0,
                -0.5 * (ws.nr1 - ws.nr2) * wy1o * a1_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )

        if conn.pitch_P2o[pitch_freq_idx][freq.index]:
            wy2o = bp_beamsize(&q_P2o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.pitch_P2o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                -2/2*ws.nr1 * wy2o * a1_2_o_factor * phase_shift,
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission
            (<SubCCSView>conn.pitch_P2o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P2o[carrier_index]), 0,
                -0.5 * (ws.nr1 - ws.nr2) * wy2o * a1_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )

        if conn.pitch_P3o[pitch_freq_idx][freq.index]:
            wy3o = bp_beamsize(&q_P3o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.pitch_P3o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P4i_P3o[carrier_index]), 0,
                2/2*ws.nr2 * wy3o * a2_2_o_factor * conj(phase_shift),
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission coupling
            (<SubCCSView>conn.pitch_P3o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P1i_P3o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wy3o * a2_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )

        if conn.pitch_P4o[pitch_freq_idx][freq.index]:
            wy4o = bp_beamsize(&q_P4o.qy)
            # fill_prop_za as off-diagonal -1 is already included in the carrier connection
            (<SubCCSView>conn.pitch_P4o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                # factor of 2 because misalignment is 2 * x/ybeta, but 0.5 factor from upper/lower SB gain
                (<SubCCSView>car_conn.P3i_P4o[carrier_index]), 0,
                2/2*ws.nr2 * wy4o * a2_2_o_factor * conj(phase_shift),
                &ws.K_pitch_sig.mtx, False
            )
            # Transmission coupling
            (<SubCCSView>conn.pitch_P4o[pitch_freq_idx][freq.index]).fill_prop_za_zm (
                (<SubCCSView>car_conn.P2i_P4o[carrier_index]), 0,
                0.5 * (ws.nr1 - ws.nr2) * wy4o * a2_2_o_factor,
                &ws.K_pitch_sig.mtx, True
            )

        # -------------------------------------------------
        # Optical to mechanical connections
        # -------------------------------------------------
        # These fill a nHOMx1 matrix to compute RP force
        # There is a minus sign difference between side 1 and 2 here, because
        # of the coordinate system change
        if conn.P1i_Fpitch[freq.index][pitch_freq_idx]:
            wy1i = bp_beamsize(&q_P1i.qy)
            (<SubCCSView>conn.P1i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wy1i * ws.field1_to_F, &ws.K_pitch_sig.mtx, &c_p1_i
            )
        # differing minus signs here because of the x coordinate flip compared to mechanical node x
        if conn.P1o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P1o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wy1o * ws.field1_to_F, &ws.K_pitch_sig.mtx, &c_p1_o
            )

        if conn.P2i_Fpitch[freq.index][pitch_freq_idx]:
            wy2i = bp_beamsize(&q_P2i.qy)
            (<SubCCSView>conn.P2i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wy2i * ws.field1_to_F, &ws.K_pitch_sig.mtx, &c_p2_i
            )
        if conn.P2o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P2o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                -ws.nr1 * wy2o * ws.field1_to_F, &ws.K_pitch_sig.mtx, &c_p2_o
            )

        if conn.P3i_Fpitch[freq.index][pitch_freq_idx]:
            wy3i = bp_beamsize(&q_P3i.qy)
            (<SubCCSView>conn.P3i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy3i * ws.field2_to_F, &ws.K_pitch_sig.mtx,  &c_p3_i
            )
        if conn.P3o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P3o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy3o * ws.field2_to_F, &ws.K_pitch_sig.mtx, &c_p3_o
            )

        if conn.P4i_Fpitch[freq.index][pitch_freq_idx]:
            wy4i = bp_beamsize(&q_P4i.qy)
            (<SubCCSView>conn.P4i_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy4i * ws.field2_to_F, &ws.K_pitch_sig.mtx,  &c_p4_i
            )
        if conn.P4o_Fpitch[freq.index][pitch_freq_idx]:
            (<SubCCSView>conn.P4o_Fpitch[freq.index][pitch_freq_idx]).fill_negative_za_zmvc (
                ws.nr2 * wy4o * ws.field2_to_F, &ws.K_pitch_sig.mtx, &c_p4_o
            )


beamsplitter_fill_qnoise = FillFuncWrapper.make_from_ptr(c_beamsplitter_fill_qnoise)
cdef object c_beamsplitter_fill_qnoise(ConnectorWorkspace cws) :
    r"""
    Fills the quantum noise input matrix elements corresponding to this `beamsplitter`.
    """
    cdef:
        BeamsplitterWorkspace ws = <BeamsplitterWorkspace> cws
        PyObject ***noises = ws.output_noise.ptrs
        frequency_info_t *freq

        Py_ssize_t i, j

        double qn_internal_loss
        complex_t factor

    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        factor = 0.5 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)
        qn_internal_loss = ws.cvalues.L
        if not ws.sim.is_modal:
            (<SubCCSView>noises[0][freq.index]).fill_za(factor * qn_internal_loss)
            (<SubCCSView>noises[1][freq.index]).fill_za(factor * qn_internal_loss)
            (<SubCCSView>noises[2][freq.index]).fill_za(factor * qn_internal_loss)
            (<SubCCSView>noises[3][freq.index]).fill_za(factor * qn_internal_loss)
        else:
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.cvalues.R * ws.oconn_info[1].loss[j]
                ws.total_losses[j] += ws.cvalues.T * ws.oconn_info[6].loss[j]
            (<SubCCSView>noises[0][freq.index]).fill_za_dv(factor, ws.total_losses)
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.cvalues.R * ws.oconn_info[0].loss[j]
                ws.total_losses[j] += ws.cvalues.T * ws.oconn_info[7].loss[j]
            (<SubCCSView>noises[1][freq.index]).fill_za_dv(factor, ws.total_losses)
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.cvalues.R * ws.oconn_info[3].loss[j]
                ws.total_losses[j] += ws.cvalues.T * ws.oconn_info[4].loss[j]
            (<SubCCSView>noises[2][freq.index]).fill_za_dv(factor, ws.total_losses)
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += qn_internal_loss
                ws.total_losses[j] += ws.cvalues.R * ws.oconn_info[2].loss[j]
                ws.total_losses[j] += ws.cvalues.T * ws.oconn_info[5].loss[j]
            (<SubCCSView>noises[3][freq.index]).fill_za_dv(factor, ws.total_losses)
