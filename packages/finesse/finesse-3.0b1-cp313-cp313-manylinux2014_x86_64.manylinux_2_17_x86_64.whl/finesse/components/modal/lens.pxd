from libc.stdlib cimport free, calloc

from finesse.cymath.cmatrix cimport SubCCSView1DArray
from finesse.knm cimport KnmMatrix
from finesse.components.workspace cimport ConnectorWorkspace
from finesse.element_workspace cimport BaseCValues
from finesse.simulations.simulation cimport BaseSimulation
from finesse.components.modal.workspace cimport KnmConnectorWorkspace

from finesse.cyexpr cimport (
    cy_expr,
    cy_expr_new,
    cy_expr_init,
    cy_expr_free,
    cy_expr_eval,
)

from cpython.ref cimport PyObject


cdef class LensValues(BaseCValues):
    cdef public:
        double f


cdef class AstigmaticLensValues(BaseCValues):
    cdef public:
        double fx
        double fy


cdef struct lens_connections:
    PyObject** P1i_P2o
    PyObject** P2i_P1o


cdef class LensConnections:
    cdef public:
        int P1i_P2o_idx
        int P2i_P1o_idx
    cdef readonly:
        SubCCSView1DArray P1i_P2o
        SubCCSView1DArray P2i_P1o
    cdef:
        lens_connections conn_ptrs


cdef class BaseLensWorkspace(KnmConnectorWorkspace):
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

        # ABCD matrix views (note same for forward & backward propagations)
        double[:, ::1] abcd_x
        double[:, ::1] abcd_y
    cdef:
        LensConnections lc

        # Indices (in sim._c_node_info and sim.trace) of nodes
        Py_ssize_t P1i_id
        Py_ssize_t P1o_id
        Py_ssize_t P2i_id
        Py_ssize_t P2o_id

        # Only elements C of ABCD matrices can change, store pointers
        # to compiled changing expression for these elements here
        cy_expr* sym_abcd_Cx
        cy_expr* sym_abcd_Cy



cdef class LensWorkspace(BaseLensWorkspace):
    cdef:
        LensValues lv


cdef class AstigmaticLensWorkspace(BaseLensWorkspace):
    cdef:
        AstigmaticLensValues lv
