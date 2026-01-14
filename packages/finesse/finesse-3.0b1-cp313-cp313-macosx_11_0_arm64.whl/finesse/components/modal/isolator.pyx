#cython: boundscheck=False, wraparound=False, initializedcheck=False

from finesse.cymath.cmatrix cimport SubCCSView1DArray

from cpython.ref cimport PyObject

import logging

ctypedef (double*, ) ptr_tuple_1


LOGGER = logging.getLogger(__name__)

# TODO (sjr) make c_isolator_fill function?

cdef class IsolatorValues(BaseCValues):
    def __init__(IsolatorValues self):
        cdef ptr_tuple_1 ptr = (&self.S, )
        cdef tuple params = ("S", )
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class IsolatorConnections:
    def __cinit__(self, SparseSolver mtx):
        size = mtx.optical_frequencies.size
        self.P1i_P2o = SubCCSView1DArray(size)
        self.P2i_P1o = SubCCSView1DArray(size)

        self.conn_ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.conn_ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views


cdef class IsolatorWorkspace(KnmConnectorWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        if sim.signal:
            signal_connections = IsolatorConnections(sim.signal)
        else:
            signal_connections = None
        super().__init__(
            owner,
            sim,
            IsolatorConnections(sim.carrier),
            signal_connections,
            IsolatorValues()
        )
        self.P1i_id = sim.trace_node_index[owner.p1.i]
        self.P1o_id = sim.trace_node_index[owner.p1.o]
        self.P2i_id = sim.trace_node_index[owner.p2.i]
        self.P2o_id = sim.trace_node_index[owner.p2.o]
