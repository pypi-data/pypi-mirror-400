from finesse.cymath.cmatrix cimport SubCCSView1DArray
from finesse.knm cimport KnmMatrix
from finesse.components.workspace cimport ConnectorWorkspace
from finesse.element_workspace cimport BaseCValues
from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.sparse.solver cimport SparseSolver
from finesse.components.modal.workspace cimport KnmConnectorWorkspace

from cpython.ref cimport PyObject


cdef class IsolatorValues(BaseCValues):
    cdef public:
        double S


cdef struct isolator_connections:
    PyObject** P1i_P2o
    PyObject** P2i_P1o


cdef class IsolatorConnections:
    cdef public:
        int P1i_P2o_idx
        int P2i_P1o_idx
    cdef readonly:
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
    cdef:
        isolator_connections conn_ptrs


cdef class IsolatorWorkspace(KnmConnectorWorkspace):
    cdef public:
        # Complete scattering matrices for each propagation direction
        KnmMatrix K12
        KnmMatrix K21

        # Arrays of scattering losses for each mode coupling
        double[::1] K12_loss
        double[::1] K21_loss

        # Refractive indices of adjacent spaces
        double nr1
        double nr2

    cdef:
        IsolatorValues iv
        IsolatorConnections icc
        IsolatorConnections ics

        # Indices (in sim._c_node_info and sim.trace) of nodes
        Py_ssize_t P1i_id
        Py_ssize_t P1o_id
        Py_ssize_t P2i_id
        Py_ssize_t P2o_id
