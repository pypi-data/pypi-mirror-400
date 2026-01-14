#cython: boundscheck=False, wraparound=False, initializedcheck=False

from finesse.cymath cimport complex_t
from finesse.simulations.simulation cimport BaseSimulation
from finesse.cymath.cmatrix cimport SubCCSView1DArray
from finesse.symbols import Symbol
from finesse.frequency cimport frequency_info_t
from finesse.cymath.cmatrix cimport SubCCSView
from finesse.components.workspace cimport FillFuncWrapper
from cpython.ref cimport PyObject

import logging

ctypedef (double*, ) ptr_tuple_1
ctypedef (double*, double*) ptr_tuple_2


LOGGER = logging.getLogger(__name__)


cdef class LensValues(BaseCValues):
    def __init__(LensValues self):
        cdef ptr_tuple_1 ptr = (&self.f, )
        cdef tuple params = ("f", )
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class AstigmaticLensValues(BaseCValues):
    def __init__(AstigmaticLensValues self):
        cdef ptr_tuple_2 ptr = (&self.fx, &self.fy)
        cdef tuple params = ("fx", "fy")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class LensConnections:
    def __cinit__(self, BaseSimulation sim):
        self.P1i_P2o = SubCCSView1DArray(sim.carrier.optical_frequencies.size)
        self.P2i_P1o = SubCCSView1DArray(sim.carrier.optical_frequencies.size)

        self.conn_ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.conn_ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views


cdef class BaseLensWorkspace(KnmConnectorWorkspace):
    def __init__(self, owner, BaseSimulation sim, BaseCValues values):
        super().__init__(
            owner,
            sim,
            LensConnections(sim),
            None,
            values,
        )
        self.lc = self.carrier.connections

        self.P1i_id = sim.trace_node_index[owner.p1.i]
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.P2i_id = sim.trace_node_index[owner.p2.i]
        self.P2o_id = sim.trace_node_index[owner.p2.o]

        self.sym_abcd_Cx = NULL
        self.sym_abcd_Cy = NULL

    def __dealloc__(self):
        cy_expr_free(self.sym_abcd_Cx)
        cy_expr_free(self.sym_abcd_Cy)

    def compile_abcd_cy_exprs(self):
        cdef:
            dict abcd_handles = self.owner._abcd_matrices
            tuple keyx = (self.owner.p1.i, self.owner.p2.o, "x")
            tuple keyy = (self.owner.p1.i, self.owner.p2.o, "y")
            cdef object[:, ::1] Mx_sym = abcd_handles[keyx][0]
            cdef object[:, ::1] My_sym = abcd_handles[keyy][0]

        # NOTE (sjr) Only element C of a Lens ABCD matrix can possibly change

        if isinstance(Mx_sym[1][0], Symbol):
            ch_sym = Mx_sym[1][0].expand_symbols().eval(keep_changing_symbols=True)
            if isinstance(ch_sym, Symbol):
                self.sym_abcd_Cx = cy_expr_new()
                cy_expr_init(self.sym_abcd_Cx, ch_sym)

        if isinstance(My_sym[1][0], Symbol):
            ch_sym = My_sym[1][0].expand_symbols().eval(keep_changing_symbols=True)
            if isinstance(ch_sym, Symbol):
                self.sym_abcd_Cy = cy_expr_new()
                cy_expr_init(self.sym_abcd_Cy, ch_sym)

    cpdef update_parameter_values(self) :
        ConnectorWorkspace.update_parameter_values(self)

        if self.sym_abcd_Cx != NULL:
            self.abcd_x[1][0] = cy_expr_eval(self.sym_abcd_Cx)

        if self.sym_abcd_Cy != NULL:
            self.abcd_y[1][0] = cy_expr_eval(self.sym_abcd_Cy)


cdef class LensWorkspace(BaseLensWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        self.lv = LensValues()
        super().__init__(owner, sim, self.lv)


cdef class AstigmaticLensWorkspace(BaseLensWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        self.lv = AstigmaticLensValues()
        super().__init__(owner, sim, self.lv)



# TODO (sjr) make c_lens_fill function?

lens_fill_qnoise = FillFuncWrapper.make_from_ptr(c_lens_fill_qnoise)
cdef object c_lens_fill_qnoise(ConnectorWorkspace cws) :
    r"""
    Fills the quantum noise input matrix elements corresponding to this `lens`.
    """
    cdef:
        BaseLensWorkspace ws = <BaseLensWorkspace> cws
        PyObject ***noises = ws.output_noise.ptrs
        frequency_info_t *freq

        Py_ssize_t i, j
        complex_t factor

    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        factor = 0.5 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)

        if ws.sim.is_modal:
            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += ws.oconn_info[0].loss[j]
            (<SubCCSView>noises[0][freq.index]).fill_za_dv(factor, ws.total_losses)

            ws.total_losses[:] = 0
            for j in range(ws.sim.signal.nhoms):
                ws.total_losses[j] += ws.oconn_info[1].loss[j]
            (<SubCCSView>noises[1][freq.index]).fill_za_dv(factor, ws.total_losses)
