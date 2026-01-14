from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from finesse.element_workspace cimport BaseCValues

cdef class SignalGeneratorValues(BaseCValues):
    cdef public:
        double amplitude
        double phase

cdef class SignalGeneratorWorkspace(ConnectorWorkspace):
    cdef public:
        SignalGeneratorValues v
        Py_ssize_t rhs_idx
        double scaling

cdef object c_siggen_fill_rhs(ConnectorWorkspace cws)
