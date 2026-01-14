from finesse.components.workspace import Connections
from finesse.cymath.complex cimport cexp, complex_t
from finesse.simulations.homsolver cimport HOMSolver

ctypedef (double*, double*) ptr_tuple_2

cdef extern from "constants.h":
    long double PI
    double C_LIGHT
    double DEG2RAD


cdef class SignalGeneratorValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_2 ptr = (&self.amplitude, &self.phase)
        cdef tuple params = ("amplitude","phase")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class SignalGeneratorWorkspace(ConnectorWorkspace):
    def __init__(self, owner, sim):
        super().__init__(
            owner,
            sim,
            Connections(),
            Connections(),
            SignalGeneratorValues()
        )
        self.v = <SignalGeneratorValues>self.values


siggen_fill_rhs = FillFuncWrapper.make_from_ptr(c_siggen_fill_rhs)
cdef object c_siggen_fill_rhs(ConnectorWorkspace cws) :
    cdef:
        SignalGeneratorWorkspace ws = <SignalGeneratorWorkspace>cws
        HOMSolver signal = ws.sim.signal
        complex_t A

    A = (ws.v.amplitude * ws.scaling) * cexp(1j * ws.v.phase * DEG2RAD)
    signal.set_source_fast_2(ws.rhs_idx, A)
