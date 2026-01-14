from finesse.cymath cimport complex_t
from finesse.cymath.gaussbeam cimport beam_param
from finesse.components.modal.cavity cimport CavityWorkspace
from finesse.detectors.workspace cimport DetectorWorkspace
from finesse.simulations.base cimport NodeBeamParam

### Beam Property Detector ###


cpdef enum BeamProperty:
    SIZE = 0
    WAISTSIZE = 1
    DISTANCE = 2
    RAYLEIGH = 3
    GOUY = 4
    DIVERGENCE = 5
    ROC = 6
    Q = 7
    DEFOCUS = 8

cdef class BPDetectorWorkspace(DetectorWorkspace):
    cdef readonly:
        BeamProperty detecting

        bint is_changing
        double initial
    cdef public:
        bint q_as_bp # Whether to return q as a BeamParam or just complex_t

    cdef:
        const beam_param* q
        double (*compute_func)(const beam_param*)


### Cavity Property Detector ###


cpdef enum CavityProperty:
    LENGTH = 0
    LOSS = 1
    FINESSE = 2
    FSR = 3
    FWHM = 4
    POLE = 5
    TAU = 6
    ABCD = 7
    STABILITY = 8
    RTGOUY = 9
    MODESEP = 10
    RESOLUTION = 11
    EIGENMODE = 12
    SOURCE_SIZE = 13
    SOURCE_WAISTSIZE = 14
    SOURCE_DISTANCE = 15
    SOURCE_RAYLEIGH = 16
    SOURCE_DIVERGENCE = 17
    SOURCE_ROC = 18
    SOURCE_DEFOCUS = 19

cdef class CPDetectorWorkspace(DetectorWorkspace):
    cdef readonly:
        CavityProperty detecting

    cdef:
        # Pointer to the attribute of CavityWorkspace being detected
        double* target

cdef class CPDetectorABCDWorkspace(DetectorWorkspace):
    cdef double[:, ::1] abcd

cdef class CPDetectorModeWorkspace(DetectorWorkspace):
    cdef readonly:
        CavityProperty detecting

        bint is_changing
        double initial
    cdef:
        # Pointer to eigenmode
        const beam_param* q
        # Pointer to flag for whether cavity is stable in relevant plane
        bint* is_stable

        double (*compute_func)(const beam_param*)

    cdef public:
        bint q_as_bp # Whether to return q as a BeamParam or just complex_t


### Astigmatism Detector ###


cdef class AstigmatismDetectorWorkspace(DetectorWorkspace):
    # Pointer to beam parameter entry in sim.trace
    cdef const NodeBeamParam* q

    cdef readonly double initial


### Mode Mismatch Detector ###


cdef class ModeMismatchDetectorWorkspace(DetectorWorkspace):
    cdef readonly:
        int pscale

        bint is_changing
        double initial
    cdef:
        # Pointers to beam parameter entries in sim.trace
        const beam_param* q1
        const beam_param* q2
        const double[:, ::1] abcd


### Accumulated Gouy Phase Detector ###


cdef class GouyDetectorWorkspace(DetectorWorkspace):
    # Array of pointers to gouy_[x|y] attribute of each space workspace
    cdef double** gouy_targets
    cdef Py_ssize_t Nspaces
