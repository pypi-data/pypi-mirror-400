#cython: boundscheck=False, wraparound=False, initializedcheck=False

from finesse.cymath cimport complex_t
from finesse.cymath.math cimport radians
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.sparse.solver cimport SparseSolver
from finesse.frequency cimport frequency_info_t
from finesse.utilities import refractive_index
from finesse.cymath.cmatrix cimport SubCCSView
from libc.stdlib cimport calloc, free
from libc.string cimport memset
from numpy cimport ndarray

import numpy as np
cimport numpy as np
from scipy.special import jn

import logging

ctypedef (double*, double*, double*) ptr_tuple_3

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD

LOGGER = logging.getLogger(__name__)

cdef double[:,::1] abcd_unity = np.eye(2, dtype=float)

cdef class ModulatorValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_3 ptr = (&self.f, &self.midx, &self.phase)
        cdef tuple params = ("f", "midx", "phase")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class ModulatorOpticalConnections:
    """Contains C accessible references to submatrices for
    optical connections for this element.
    """
    def __cinit__(self, SparseSolver mtx):
        cdef int Nf = mtx.optical_frequencies.size

        self.P1i_P2o = SubCCSView2DArray(Nf, Nf)
        self.P2i_P1o = SubCCSView2DArray(Nf, Nf)
        self.opt_conn_ptrs.P1i_P2o = <PyObject***>self.P1i_P2o.views
        self.opt_conn_ptrs.P2i_P1o = <PyObject***>self.P2i_P1o.views


cdef class ModulatorSignalConnections:
    """Contains C accessible references to submatrices for
    optical connections for this element.
    """
    def __cinit__(self, SparseSolver mtx):
        cdef int Nf = mtx.optical_frequencies.size

        self.amp_P2o = SubCCSView2DArray(1, Nf)
        self.amp_P1o = SubCCSView2DArray(1, Nf)
        self.phs_P2o = SubCCSView2DArray(1, Nf)
        self.phs_P1o = SubCCSView2DArray(1, Nf)

        self.sig_conn_ptrs.amp_P2o = <PyObject***>self.amp_P2o.views
        self.sig_conn_ptrs.amp_P1o = <PyObject***>self.amp_P1o.views
        self.sig_conn_ptrs.phs_P2o = <PyObject***>self.phs_P2o.views
        self.sig_conn_ptrs.phs_P1o = <PyObject***>self.phs_P1o.views


cdef void set_coupling_orders(ndarray orders, int set_order, double f, mtx, modulator_coupling_order** rtn, Py_ssize_t* N, dict coupling_orders) noexcept:
    """Returns a [frequency input index, frequency output index, order] array
    free must be called on rtn* once finished with object.
    """
    for f1 in mtx.optical_frequencies.frequencies:
        coupling_orders[f1, f1] = 0
        for f2 in mtx.optical_frequencies.frequencies:
            df = f2.f - f1.f
            order = df / float(f)
            if hasattr(order, "eval"):
                order = order.eval()

            if not order.is_integer():
                continue

            order = int(round(order))

            if abs(order) <= set_order:
                coupling_orders[f1, f2] = order
                coupling_orders[f2, f1] = -order

    items = tuple(coupling_orders.items())
    N[0] = len(items)
    rtn[0] = <modulator_coupling_order*>calloc(N[0], sizeof(modulator_coupling_order))
    if not rtn[0]:
        raise MemoryError()

    for i, ((f1, f2), _order) in enumerate(items):
        rtn[0][i].f1_index = f1.index
        rtn[0][i].f2_index = f2.index
        rtn[0][i].order = _order
        order_index = np.argwhere(orders == _order)
        assert order_index.shape == (1, 1)
        rtn[0][i].order_index = int(order_index[0][0])


cdef class ModulatorWorkspace(KnmConnectorWorkspace):
    def __init__(self, object owner, BaseSimulation sim):
        cdef Py_ssize_t i
        super().__init__(owner,
            sim,
            ModulatorOpticalConnections(sim.carrier),
            ModulatorSignalConnections(sim.signal) if sim.signal else None,
            ModulatorValues()
        )

        self.nr1 = refractive_index(owner.p1)
        self.nr2 = refractive_index(owner.p2)

        self.cvalues = self.values
        self.mcc = self.carrier.connections

        if sim.signal:
            self.mcs = self.signal.connections
            self.amp_signal_enabled = owner.amp.i.full_name in sim.signal.nodes
            self.phs_signal_enabled = owner.phs.i.full_name in sim.signal.nodes
        else:
            self.mcs = None

        if sim.is_modal:
            self.set_knm_info(
                "P1i_P2o", abcd_x=abcd_unity, abcd_y=abcd_unity, nr_from=self.nr1, nr_to=self.nr2, is_transmission=True
            )
            self.set_knm_info(
                "P2i_P1o", abcd_x=abcd_unity, abcd_y=abcd_unity, nr_from=self.nr2, nr_to=self.nr1, is_transmission=True
            )

        order = int(owner.order.eval())
        self.N_orders = 2 * order + 1
        self.orders = np.zeros(self.N_orders, dtype=np.int32)
        self.phases = np.zeros(self.N_orders, dtype=np.complex128)
        self.amps = np.zeros(self.N_orders, dtype=np.float64)

        for i in range(-order, order + 1):
            if i < 0:
                self.orders[self.N_orders + i] = i
            else:
                self.orders[i] = i

        # there are no fill functions defined for amplitude modulators
        if owner.mod_type == ModulatorType.am:
            if self.amp_signal_enabled:
                raise NotImplementedError("amplitude signal injection not supported yet for amplitude modulators")
            if self.phs_signal_enabled:
                raise NotImplementedError("phase signal injection not supported yet for amplitude modulators")
        # https://gitlab.com/ifosim/finesse/finesse3/-/issues/711
        elif owner.mod_type == ModulatorType.pm and self.phs_signal_enabled:
            raise NotImplementedError("phase signal injection not supported yet for phase modulators")

        self.factors_12 = np.zeros((self.N_orders, sim.model_settings.num_HOMs, sim.model_settings.num_HOMs), dtype=np.complex128)
        self.factors_21 = np.zeros((self.N_orders, sim.model_settings.num_HOMs, sim.model_settings.num_HOMs), dtype=np.complex128)

        self.carrier_frequency_couplings = {}
        self.signal_frequency_couplings = {}

        # need to free this memory later
        set_coupling_orders(
            self.orders,
            order, owner.f,
            sim.carrier, &self.car_coupling_orders,
            &self.N_car_coupling_orders,
            self.carrier_frequency_couplings
        )
        if sim.signal:
            set_coupling_orders(
                self.orders,
                order, owner.f, sim.signal, &self.sig_coupling_orders,
                &self.N_sig_coupling_orders,
                self.signal_frequency_couplings
            )
            self.increment_sig = <bint*>calloc(self.sim.signal.optical_frequencies.size, sizeof(bint))
            if not self.increment_sig:
                raise MemoryError()
            self.eye = np.eye(sim.model_settings.num_HOMs, dtype=np.complex128)

    def __dealloc__(self):
        if self.sig_coupling_orders:
            free(self.sig_coupling_orders)
        if self.car_coupling_orders:
            free(self.car_coupling_orders)
        if self.increment_sig:
            free(self.increment_sig)

    cpdef fill_quantum_matrix(self) :
        cdef:
            modulator_coupling_order* mco = NULL
            modulator_optical_connections *conn = &self.mcs.opt_conn_ptrs
            Py_ssize_t i

        for i in range(self.N_sig_coupling_orders):
            mco = (self.sig_coupling_orders + i)
            if mco.f1_index != mco.f2_index:
                if conn.P1i_P2o[mco.f1_index][mco.f2_index]:
                    (<SubCCSView>conn.P1i_P2o[mco.f1_index][mco.f2_index]).fill_negative_za(0)
                if conn.P2i_P1o[mco.f1_index][mco.f2_index]:
                    (<SubCCSView>conn.P2i_P1o[mco.f1_index][mco.f2_index]).fill_negative_za(0)
            else:
                if conn.P1i_P2o[mco.f1_index][mco.f2_index]:
                    (<SubCCSView>conn.P1i_P2o[mco.f1_index][mco.f2_index]).fill_negative_zm(self.eye)
                if conn.P2i_P1o[mco.f1_index][mco.f2_index]:
                    (<SubCCSView>conn.P2i_P1o[mco.f1_index][mco.f2_index]).fill_negative_zm(self.eye)


cdef object compute_factors(ModulatorWorkspace ws) :
    """
    ToDo
    ----
    This function still needs optimising, plenty of Python calls still
    """
    cdef:
        double phi = radians(ws.cvalues.phase)
        double midx = ws.cvalues.midx
        Py_ssize_t i

    if ws.cvalues.mod_type == ModulatorType.am:
        ws.amps[:] = 0.25 * midx
        ws.amps[0] = 1.0 - 0.5 * midx
    elif ws.cvalues.mod_type == ModulatorType.pm:
        ws.amps[:] = jn(ws.orders, midx)
        phi += 0.5 * PI

    np.exp(1j * phi * ws.orders, out=ws.phases)

    if ws.cvalues.positive_only:
        ws.amps[0] = 1.0 - 0.5 * (1.0 - ws.amps[0])

        for i in range(-ws.cvalues.order, 0):
            ws.amps[ws.N_orders + i] = 0.0

    # TODO ddb can use a faster outer product here probably
    np.multiply.outer(ws.amps * ws.phases, ws.K12.data, out=ws.factors_12)
    np.multiply.outer(ws.amps * ws.phases, ws.K21.data, out=ws.factors_21)


cdef void fill_optical_2_optical(
    ModulatorWorkspace ws,
    modulator_optical_connections *conn,
    modulator_coupling_order* cpl_orders,
    Py_ssize_t N_cpl_orders
) noexcept:
    cdef modulator_coupling_order* mco = NULL
    cdef Py_ssize_t i = 0

    assert(cpl_orders)
    assert(conn)
    compute_factors(ws)

    for i in range(N_cpl_orders):
        mco = (cpl_orders + i)
        if conn.P1i_P2o[mco.f1_index][mco.f2_index]:
            (<SubCCSView>conn.P1i_P2o[mco.f1_index][mco.f2_index]).fill_za_zm(
                -1, ws.factors_12[mco.order_index][:]
            )
        if conn.P2i_P1o[mco.f1_index][mco.f2_index]:
            (<SubCCSView>conn.P2i_P1o[mco.f1_index][mco.f2_index]).fill_za_zm(
                -1, ws.factors_21[mco.order_index][:]
            )


modulator_carrier_fill = FillFuncWrapper.make_from_ptr(c_modulator_carrier_fill)
cdef object c_modulator_carrier_fill(ConnectorWorkspace cws) :
    cdef ModulatorWorkspace ws = <ModulatorWorkspace>cws
    fill_optical_2_optical(ws, &ws.mcc.opt_conn_ptrs, ws.car_coupling_orders, ws.N_car_coupling_orders)


modulator_signal_optical_fill = FillFuncWrapper.make_from_ptr(c_modulator_signal_optical_fill)
cdef object c_modulator_signal_optical_fill(ConnectorWorkspace cws) :
    cdef ModulatorWorkspace ws = <ModulatorWorkspace>cws
    fill_optical_2_optical(ws, &ws.mcs.opt_conn_ptrs, ws.sig_coupling_orders, ws.N_sig_coupling_orders)


modulator_signal_phase_fill = FillFuncWrapper.make_from_ptr(c_modulator_signal_phase_fill)
cdef object c_modulator_signal_phase_fill(ConnectorWorkspace cws) :
    cdef ModulatorWorkspace ws = <ModulatorWorkspace>cws
    if ws.values.mod_type == ModulatorType.pm:
        fill_phase_mod_phs_2_optical_signals(ws)


modulator_signal_amp_fill = FillFuncWrapper.make_from_ptr(c_modulator_signal_amp_fill)
cdef object c_modulator_signal_amp_fill(ConnectorWorkspace cws) :
    cdef ModulatorWorkspace ws = <ModulatorWorkspace>cws
    if ws.values.mod_type == ModulatorType.pm:
        fill_phase_mod_amp_2_optical_signals(ws)


cdef object fill_phase_mod_phs_2_optical_signals(
        ModulatorWorkspace ws
    ) :
    """Fills the phase noise to output optical field coupling for a phase modulator
    """
    cdef:
        double midx = ws.cvalues.midx
        modulator_coupling_order* mco = NULL
        Py_ssize_t i = 0
        frequency_info_t *f
        frequency_info_t* fs[2]
        complex_t factor
        double k
        modulator_signal_connections *signal_conn = &ws.mcs.sig_conn_ptrs
        modulator_optical_connections *carrier_conn = &ws.mcc.opt_conn_ptrs
    # we use this flag array to keep track of whether we will
    # increment or reset a coupling.
    memset(ws.increment_sig, 0, ws.sim.signal.optical_frequencies.size * sizeof(bint))
    # Steps here:
    # 1 - Get each carrier coupling order
    # 2 - compute the factor i*k*midx/2
    # 4 - apply this phase modulation only around incoming carrier that gets coupled
    # 3 - get the upper and lower sidebands around the outgoing carrier frequency
    for i in range(ws.N_car_coupling_orders):
        mco = (ws.car_coupling_orders + i)
        # get audio sidebands
        f = &ws.sim.carrier.optical_frequencies.frequency_info[mco.f2_index]
        # this is the line that segfaults (https://gitlab.com/ifosim/finesse/finesse3/-/issues/711)
        k = ws.sim.model_settings.k0 * (1 + f.f_car[0]/ws.sim.model_settings.f0)
        fs[0] = &ws.sim.signal.optical_frequencies.frequency_info[f.audio_upper_index]
        fs[1] = &ws.sim.signal.optical_frequencies.frequency_info[f.audio_lower_index]
        factor = 1j * k * midx * 0.5 # two half factor from two cosine gains

        for f in fs:
            if signal_conn.phs_P2o[0][f.index]:
                (<SubCCSView>signal_conn.phs_P2o[0][f.index]).fill_prop_za (
                    (<SubCCSView>carrier_conn.P1i_P2o[mco.f1_index][mco.f2_index]), 0, factor, ws.increment_sig[f.index]
                )
            if signal_conn.phs_P1o[0][f.index]:
                (<SubCCSView>signal_conn.phs_P1o[0][f.index]).fill_prop_za (
                    (<SubCCSView>carrier_conn.P2i_P1o[mco.f1_index][mco.f2_index]), 0, factor, ws.increment_sig[f.index]
                )
            # flag that any other coupling into this output frequency needs to increment now
            # otherwise we'll overwrite previouslly set couplings
            ws.increment_sig[f.index] |= 1


cdef object fill_phase_mod_amp_2_optical_signals(
        ModulatorWorkspace ws
    ) :
    """Fills amplitude noise input to optical output coupling elements.
    Based on a small relative modulation index excitation
    .. math::
        J_{k}\\left(m \\left(\\delta \\cos{\\left(\\Omega t \\right)} + 1\\right)\\right)
    .. math::
        \\delta \\left(\\left(\\frac{m J_{k - 1}\\left(m\\right)}{4} - \\frac{m J_{k + 1}\\left(m\\right)}{4}\\right) e^{i \\Omega t} + \\left(\\frac{m J_{k - 1}\\left(m\\right)}{4} - \\frac{m J_{k + 1}\\left(m\\right)}{4}\\right) e^{- i \\Omega t}\\right) + J_{k}\\left(m\\right)
    """
    cdef:
        double midx = ws.cvalues.midx
        modulator_coupling_order* mco = NULL
        Py_ssize_t i = 0
        double J_m1, J, J_p1
        frequency_info_t *f
        frequency_info_t* fs[2]
        complex_t factor
        modulator_signal_connections *signal_conn = &ws.mcs.sig_conn_ptrs
        modulator_optical_connections *carrier_conn = &ws.mcc.opt_conn_ptrs
    # we use this flag array to keep track of whether we will
    # increment or reset a coupling.
    memset(ws.increment_sig, 0, ws.sim.signal.optical_frequencies.size * sizeof(bint))

    # Steps here:
    # 1 - Get each carrier coupling order
    # 2 - compute the bessel function delta*(J(order-1)-J(order+1)) factor
    # 3 - get the upper and lower sidebands around the outgoing carrier frequency
    # 4 - apply this amplitude modulation only around incoming carrier that gets coupled
    for i in range(ws.N_car_coupling_orders):
        mco = (ws.car_coupling_orders + i)
        # need to divide by J(order, midx) because this is included in the carrier coupling
        # and not in the signal sideband terms
        J = jn(mco.order, midx)
        J_m1 = jn(mco.order-1, midx)
        J_p1 = jn(mco.order+1, midx)
        # get audio sidebands
        f = &ws.sim.carrier.optical_frequencies.frequency_info[mco.f2_index]
        fs[0] = &ws.sim.signal.optical_frequencies.frequency_info[f.audio_upper_index]
        fs[1] = &ws.sim.signal.optical_frequencies.frequency_info[f.audio_lower_index]
        factor = midx * 0.5 * 0.5 * (J_m1 - J_p1)/J # two half factor from two cosine gains

        for f in fs:
            if signal_conn.amp_P2o[0][f.index]:
                (<SubCCSView>signal_conn.amp_P2o[0][f.index]).fill_prop_za (
                    (<SubCCSView>carrier_conn.P1i_P2o[mco.f1_index][mco.f2_index]), 0, factor, ws.increment_sig[f.index]
                )
            if signal_conn.amp_P1o[0][f.index]:
                (<SubCCSView>signal_conn.amp_P1o[0][f.index]).fill_prop_za (
                    (<SubCCSView>carrier_conn.P2i_P1o[mco.f1_index][mco.f2_index]), 0, factor, ws.increment_sig[f.index]
                )
            # flag that any other coupling into this output frequency needs to increment now
            # otherwise we'll overwrite previouslly set couplings
            ws.increment_sig[f.index] |= 1


# def modulator_fill(object modulator, ModulatorWorkspace ws, SparseSolver mtx, connections, dict values, dict cporders, unicode
#         mod_type, bint quantum_fill=False):


#     for (f1, f2), _order in cporders.items():
#         if quantum_fill:
#             if f1.index == f2.index:
#                 with mtx.component_edge_fill3(ws.owner_id, connections.P1i_P2o_idx, f1.index, f2.index) as mat:
#                     mat[:] = 1
#                 with mtx.component_edge_fill3(ws.owner_id, connections.P2i_P1o_idx, f1.index, f2.index) as mat:
#                     mat[:] = 1
#             else:
#                 with mtx.component_edge_fill3(ws.owner_id, connections.P1i_P2o_idx, f1.index, f2.index) as mat:
#                     mat[:] = 0
#                 with mtx.component_edge_fill3(ws.owner_id, connections.P2i_P1o_idx, f1.index, f2.index) as mat:
#                     mat[:] = 0
#         else:
#             with mtx.component_edge_fill3(ws.owner_id, connections.P1i_P2o_idx, f1.index, f2.index) as mat:
#                 mat[:] = factors_12[_order][:]
#             with mtx.component_edge_fill3(ws.owner_id, connections.P2i_P1o_idx, f1.index, f2.index) as mat:
#                 mat[:] = factors_21[_order][:]
