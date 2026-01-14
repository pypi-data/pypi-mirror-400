from libc.stdlib cimport calloc, free

cimport cython

cimport numpy as np
import numpy as np

from finesse.cymath cimport complex_t
from finesse.cymath.math cimport degrees
from finesse.cymath.gaussbeam cimport (
    bp_beamsize,
    bp_waistsize,
    bp_waistpos,
    bp_rayleigh,
    bp_gouy,
    bp_divergence,
    bp_radius_curvature,
    bp_defocus,
    bp_overlap,
    transform_q,
    overlap,
)
from finesse.detectors.workspace cimport (
    DetectorWorkspace,
    OutputFuncWrapper,
)
from finesse.simulations.workspace cimport ABCDWorkspace
from finesse.components.modal.space cimport SpaceWorkspace

from finesse.gaussian import BeamParam


### Beam Property Detector ###


cdef class BPDetectorWorkspace(DetectorWorkspace):
    """Workspace for beam property calculations used by :class:`.BeamPropertyDetector`."""
    def __init__(self, owner, sim):
        # https://gitlab.com/ifosim/finesse/finesse3/-/issues/688 for `needs_carrier`
        super().__init__(owner, sim, needs_modal_update=True, needs_carrier=True)
        cdef Py_ssize_t n_id = self.sim.trace_node_index[owner.node]
        if owner.direction == "x":
            self.q = &self.sim.trace[n_id].qx
        else:
            self.q = &self.sim.trace[n_id].qy

        self.is_changing = not self.sim.trace[n_id].is_fixed

        self.detecting = owner.detecting
        if self.detecting == BeamProperty.Q:
            self.compute_func = NULL
            self.initial = -1.0
            self.set_output_fn(bp_q_detector_output)
        else:
            if self.detecting == BeamProperty.SIZE:
                self.compute_func = bp_beamsize
            elif self.detecting == BeamProperty.WAISTSIZE:
                self.compute_func = bp_waistsize
            elif self.detecting == BeamProperty.DISTANCE:
                self.compute_func = bp_waistpos
            elif self.detecting == BeamProperty.RAYLEIGH:
                self.compute_func = bp_rayleigh
            elif self.detecting == BeamProperty.GOUY:
                self.compute_func = bp_gouy
            elif self.detecting == BeamProperty.DIVERGENCE:
                self.compute_func = bp_divergence
            elif self.detecting == BeamProperty.ROC:
                self.compute_func = bp_radius_curvature
            elif self.detecting == BeamProperty.DEFOCUS:
                self.compute_func = bp_defocus
            else:
                raise RuntimeError(f"Unrecognised value for BeamProperty: {self.detecting}")

            self.initial = self.compute_func(self.q)
            self.set_output_fn(bp_detector_output)

bp_detector_output = OutputFuncWrapper.make_from_ptr(c_bp_detector_output)
cdef c_bp_detector_output(DetectorWorkspace dws) :
    cdef BPDetectorWorkspace ws = <BPDetectorWorkspace> dws

    if not ws.is_changing:
        return ws.initial

    return ws.compute_func(ws.q)

bp_q_detector_output = OutputFuncWrapper.make_from_ptr(c_bp_q_detector_output)
cdef c_bp_q_detector_output(DetectorWorkspace dws) :
    cdef BPDetectorWorkspace ws = <BPDetectorWorkspace> dws

    if ws.q_as_bp:
        return BeamParam(ws.q.wavelength, ws.q.nr, ws.q.q)

    return ws.q.q


### Cavity Detector ###


cdef class CPDetectorWorkspace(DetectorWorkspace):
    """Workspace for cavity property calculations, used by :class:`.CavityPropertyDetector`,
    for scalar properties which do not rely on the cavity eigenmode."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        cdef CavityWorkspace cav_ws = self.sim.cavity_workspaces[owner.cavity]
        self.detecting = owner.detecting

        # Set the target ptr
        if self.detecting == CavityProperty.LENGTH:
            self.target = &cav_ws.length
        elif self.detecting == CavityProperty.LOSS:
            self.target = &cav_ws.loss
        elif self.detecting == CavityProperty.FINESSE:
            self.target = &cav_ws.finesse
        elif self.detecting == CavityProperty.FSR:
            self.target = &cav_ws.fsr
        elif self.detecting == CavityProperty.FWHM:
            self.target = &cav_ws.fwhm
        elif self.detecting == CavityProperty.POLE:
            self.target = &cav_ws.pole
        elif self.detecting == CavityProperty.TAU:
            self.target = &cav_ws.tau
        elif self.detecting == CavityProperty.RTGOUY:
            if owner.direction == "x":
                self.target = &cav_ws.rt_gouy_x
            else:
                self.target = &cav_ws.rt_gouy_y
        elif self.detecting == CavityProperty.MODESEP:
            if owner.direction == "x":
                self.target = &cav_ws.Df_x
            else:
                self.target = &cav_ws.Df_y
        elif self.detecting == CavityProperty.STABILITY:
            if owner.direction == "x":
                self.target = &cav_ws.gx
            else:
                self.target = &cav_ws.gy
        elif self.detecting == CavityProperty.RESOLUTION:
            if owner.direction == "x":
                self.target = &cav_ws.Sx
            else:
                self.target = &cav_ws.Sy
        else:
            raise RuntimeError(f"Invalid value for CavityProperty: {self.detecting}")

        # None of the properties detectable by this workspace require
        # valid beam traces so mark it as ok to compute outputs for
        # invalid trace data points
        self.ignore_sim_mask = True

        self.set_output_fn(cp_detector_output)

cp_detector_output = OutputFuncWrapper.make_from_ptr(c_cp_detector_output)
cdef c_cp_detector_output(DetectorWorkspace dws) :
    cdef CPDetectorWorkspace ws = <CPDetectorWorkspace> dws

    # Convert to degrees first if detecting round-trip Gouy phase
    if ws.detecting == CavityProperty.RTGOUY:
        return degrees(ws.target[0])

    return ws.target[0]


cdef class CPDetectorABCDWorkspace(DetectorWorkspace):
    """Workspace for obtaining cavity round-trip ABCD matrix, used
    by :class:`.CavityPropertyDetector`."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        cdef CavityWorkspace cav_ws = self.sim.cavity_workspaces[owner.cavity]
        if owner.direction == "x":
            self.abcd = cav_ws.abcd_x
        else:
            self.abcd = cav_ws.abcd_y

        self.ignore_sim_mask = True

        self.set_output_fn(cp_detector_abcd_output)

cp_detector_abcd_output = OutputFuncWrapper.make_from_ptr(c_cp_detector_abcd_output)
cdef c_cp_detector_abcd_output(DetectorWorkspace dws) :
    cdef CPDetectorABCDWorkspace ws = <CPDetectorABCDWorkspace> dws

    return ws.abcd.base.copy()


cdef class CPDetectorModeWorkspace(DetectorWorkspace):
    """Workspace for cavity property calculations, used by :class:`.CavityPropertyDetector`,
    for properties which rely on the cavity eigenmode."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        self.detecting = owner.detecting

        cdef CavityWorkspace cav_ws = self.sim.cavity_workspaces[owner.cavity]
        cdef Py_ssize_t n_id = self.sim.trace_node_index[owner.cavity.source]
        # Set the q ptr to cav_ws eigenmode of relevant plane
        if owner.direction == "x":
            self.q = &self.sim.trace[n_id].qx
            self.is_stable = &cav_ws.is_stable_x
        else:
            self.q = &self.sim.trace[n_id].qy
            self.is_stable = &cav_ws.is_stable_y

        self.is_changing = not self.sim.trace[n_id].is_fixed

        if self.detecting == CavityProperty.EIGENMODE:
            self.compute_func = NULL
            self.initial = -1.0
            self.set_output_fn(cp_detector_mode_output)
        else:
            if self.detecting == CavityProperty.SOURCE_SIZE:
                self.compute_func = bp_beamsize
            elif self.detecting == CavityProperty.SOURCE_WAISTSIZE:
                self.compute_func = bp_waistsize
            elif self.detecting == CavityProperty.SOURCE_DISTANCE:
                self.compute_func = bp_waistpos
            elif self.detecting == CavityProperty.SOURCE_RAYLEIGH:
                self.compute_func = bp_rayleigh
            elif self.detecting == CavityProperty.SOURCE_DIVERGENCE:
                self.compute_func = bp_divergence
            elif self.detecting == CavityProperty.SOURCE_ROC:
                self.compute_func = bp_radius_curvature
            elif self.detecting == CavityProperty.SOURCE_DEFOCUS:
                self.compute_func = bp_defocus
            else:
                raise RuntimeError(f"Invalid value for CavityProperty: {self.detecting}")

            if self.is_stable[0]:
                self.initial = self.compute_func(self.q)
            else:
                self.initial = np.nan

            self.set_output_fn(cp_detector_from_mode_output)

cp_detector_from_mode_output = OutputFuncWrapper.make_from_ptr(c_cp_detector_from_mode_output)
cdef c_cp_detector_from_mode_output(DetectorWorkspace dws) :
    cdef CPDetectorModeWorkspace ws = <CPDetectorModeWorkspace> dws

    if not ws.is_stable[0]:
        return np.nan

    if not ws.is_changing:
        return ws.initial

    return ws.compute_func(ws.q)

cp_detector_mode_output = OutputFuncWrapper.make_from_ptr(c_cp_detector_mode_output)
cdef c_cp_detector_mode_output(DetectorWorkspace dws) :
    cdef CPDetectorModeWorkspace ws = <CPDetectorModeWorkspace> dws

    if not ws.is_stable[0]:
        return np.nan

    if ws.q_as_bp:
        return BeamParam(ws.q.wavelength, ws.q.nr, ws.q.q)

    return ws.q.q


### Astigmatism Detector ###


cdef class AstigmatismDetectorWorkspace(DetectorWorkspace):
    """Workspace for node astigmatism calculations used by :class:`.AstigmatismDetector`."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        cdef Py_ssize_t n_id = self.sim.trace_node_index[owner.node]
        self.q = &self.sim.trace[n_id]

        self.initial = 1.0 - bp_overlap(&self.q.qx, &self.q.qy)

        self.set_output_fn(astig_detector_output)

astig_detector_output = OutputFuncWrapper.make_from_ptr(c_astig_detector_output)
cdef c_astig_detector_output(DetectorWorkspace dws) :
    cdef AstigmatismDetectorWorkspace ws = <AstigmatismDetectorWorkspace> dws

    if ws.q.is_fixed:
        return ws.initial

    return 1.0 - bp_overlap(&ws.q.qx, &ws.q.qy)


### Mode Mismatch Detector ###


cdef class ModeMismatchDetectorWorkspace(DetectorWorkspace):
    """Workspace for mode mismatch (at a node coupling) calculations
    used by :class:`.ModeMismatchDetector`."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        node1, node2 = owner.in_node, owner.out_node
        comp = node1.component
        direction = owner.direction

        cdef ABCDWorkspace ws = None
        for cws in self.sim.workspaces:
            if cws.owner is comp:
                ws = cws
                break

        if ws is None:
            raise RuntimeError(
                "Could not find a workspace associated "
                f"with the component of name {comp.name}"
            )

        cdef Py_ssize_t n1_id = self.sim.trace_node_index[node1]
        cdef Py_ssize_t n2_id = self.sim.trace_node_index[node2]
        if owner.direction == "x":
            self.q1 = &self.sim.trace[n1_id].qx
            self.q2 = &self.sim.trace[n2_id].qx
        else:
            self.q1 = &self.sim.trace[n1_id].qy
            self.q2 = &self.sim.trace[n2_id].qy

        self.pscale = 100 if owner.in_percent else 1

        p1name, p2name = node1.port.name, node2.port.name
        # First case is if connector ws has single abcd
        # matrix view for all couplings
        if hasattr(ws, "abcd"):
            self.abcd = ws.abcd
        # Next is a connector ws with abcd views same for
        # each node coupling but different for x,y planes
        # e.g. a lens
        elif hasattr(ws, f"abcd_{direction}"):
            self.abcd = getattr(ws, f"abcd_{direction}")
        # If not then check for connector ws with abcd views
        # which are different for each node coupling and x,y
        # plane --- e.g. a mirror or beam splitter
        elif hasattr(ws, f"abcd_{p1name}{p2name}_{direction}"):
            self.abcd = getattr(ws, f"abcd_{p1name}{p2name}_{direction}")
        # Finally, if the connector does not define any abcd
        # matrix views then simply use identity matrix
        else:
            self.abcd = np.eye(2)

        # Determine whether the node coupling is one with changing mismatch
        self.is_changing = (node1, node2) in self.sim.changing_mismatch_couplings
        cdef complex_t q1_matched = transform_q(self.abcd, self.q1.q, self.q1.nr, self.q2.nr)
        self.initial = self.pscale * (1.0 - overlap(q1_matched, self.q2.q))

        self.set_output_fn(mode_mismatch_detector_output)

mode_mismatch_detector_output = OutputFuncWrapper.make_from_ptr(c_mode_mismatch_detector_output)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef c_mode_mismatch_detector_output(DetectorWorkspace dws) :
    cdef ModeMismatchDetectorWorkspace ws = <ModeMismatchDetectorWorkspace> dws

    if not ws.is_changing:
        return ws.initial

    cdef complex_t q1_matched = transform_q(ws.abcd, ws.q1.q, ws.q1.nr, ws.q2.nr)
    return ws.pscale * (1.0 - overlap(q1_matched, ws.q2.q))


### Accumulated Gouy Phase Detector ###


cdef class GouyDetectorWorkspace(DetectorWorkspace):
    """Workspace for accumulated Gouy phase calculations used by :class:`.Gouy`."""
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_modal_update=True)

        cdef list spaces = owner.spaces
        self.Nspaces = len(spaces)

        if self.gouy_targets != NULL:
            raise MemoryError()
        self.gouy_targets = <double**> calloc(self.Nspaces, sizeof(double*))
        if not self.gouy_targets:
            raise MemoryError()

        cdef SpaceWorkspace sws
        cdef Py_ssize_t i
        for i in range(self.Nspaces):
            space = spaces[i]
            for ws in sim.workspaces:
                if ws.owner is space:
                    sws = <SpaceWorkspace> ws
                    if owner.direction == "x":
                        self.gouy_targets[i] = &(sws.sv.computed_gouy_x)
                    else:
                        self.gouy_targets[i] = &(sws.sv.computed_gouy_y)

                    break

            if self.gouy_targets[i] == NULL:
                raise RuntimeError(
                    "Could not find a workspace associated "
                    f"with the Space of name {space.name}"
                )

        self.set_output_fn(acc_gouy_detector_output)

    def __dealloc__(self):
        if self.gouy_targets != NULL:
            free(self.gouy_targets)
            self.gouy_targets = NULL

acc_gouy_detector_output = OutputFuncWrapper.make_from_ptr(c_acc_gouy_detector_output)
cdef c_acc_gouy_detector_output(DetectorWorkspace dws) :
    cdef:
        GouyDetectorWorkspace ws = <GouyDetectorWorkspace> dws

        Py_ssize_t i
        double acc = 0.0

    for i in range(ws.Nspaces):
        acc += ws.gouy_targets[i][0]

    return acc
