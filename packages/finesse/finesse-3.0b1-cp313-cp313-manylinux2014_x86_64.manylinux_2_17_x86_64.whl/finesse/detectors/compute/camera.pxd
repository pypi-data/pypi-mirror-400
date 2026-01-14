from finesse.cymath cimport complex_t
from finesse.cymath.gaussbeam cimport beam_param
from finesse.cymath.homs cimport unm_workspace, unm_factor_store

from finesse.detectors.workspace cimport (
    DetectorWorkspace,
    MaskedDetectorWorkspace,
    OutputFuncWrapper,
)
from finesse.element_workspace cimport BaseCValues
from finesse.simulations.sparse.solver cimport SparseSolver
from finesse.frequency cimport frequency_info_t

from finesse.simulations.base cimport NodeBeamParam

cdef enum ScanningAxis:
    XAXIS,
    YAXIS

cdef class CameraWorkspace(MaskedDetectorWorkspace):
    cdef:
        Py_ssize_t node_id
        SparseSolver sparse_carrier_solver

        unm_workspace uws
        unm_factor_store ufs

        double[:, ::1] phase_cache

        const double[::1] x_view
        const double[::1] y_view
        Py_ssize_t xpts
        Py_ssize_t ypts
        ScanningAxis scan_ax

        int nthreads

        const NodeBeamParam* q

    cpdef cache(self, bint initial=?)

### CCD type camera workspaces ###

cdef class CCDWorkspace(CameraWorkspace):
    cdef:
        double[:, ::1] out


cdef class CCDLineWorkspace(CameraWorkspace):
    cdef:
        double[::1] out

# NOTE (sjr) Just here for completion / type checking, doesn't need to store anything
#            extra beyond CameraWorkspace as it just computes a single pixel intensity
cdef class CCDPixelWorkspace(CameraWorkspace):
    pass

### Field / complex camera type workspaces ###

cdef class ComplexCameraValues(BaseCValues):
    cdef public:
        double f

cdef class ComplexCameraWorkspace(CameraWorkspace):
    cdef:
        ComplexCameraValues v

cdef class FieldCameraWorkspace(ComplexCameraWorkspace):
    cdef:
        complex_t[:, ::1] out


cdef class FieldLineWorkspace(ComplexCameraWorkspace):
    cdef:
        complex_t[::1] out

# NOTE (sjr) Again just here for completion / type checking, doesn't need to store anything
#            extra beyond CameraWorkspace as it just computes a single pixel field
cdef class FieldPixelWorkspace(ComplexCameraWorkspace):
    pass
