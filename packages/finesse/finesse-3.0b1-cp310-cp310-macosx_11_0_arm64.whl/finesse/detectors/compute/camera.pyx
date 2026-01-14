#cython: boundscheck=False, wraparound=False, initializedcheck=False

r"""
Functions for computing images of a beam at arbitrary points
in the interferometer configuration.

.. _camera_equations:

Camera Equations
----------------

Each function in this sub-module has two modes - single frequency (mimicking
amplitude detectors at each coordinate) and multi frequency (mimicking CCD
cameras).

.. rubric:: Single-frequency mode

If the argument `f` (i.e. the field frequency to probe) is specified then this
function computes the amplitude and phase of the light field at this given
frequency, for the specified `x` and `y` coordinate. The light field at frequency
:math:`\omega_{\mathrm{i}}` is given by a complex number (:math:`z`) and is calculated
as follows:

.. math::
    z(x, y) = \displaystyle\sum_{\mathrm{j}} \sum_{nm} u_{nm}(x, y) a_{\mathrm{j}nm}
    \quad\text{with}\quad
    \left\{\,\mathrm{j}\,|\,\mathrm{j} \in [0, \dots, N] \wedge \omega_{\mathrm{j}} = \omega_{\mathrm{i}}\right\}.

.. rubric:: Multi-frequency mode

Otherwise, if `f` is not specified, then this function acts like a CCD camera for the
given pixel. It plots the *beam intensity* as a function of the `x` and `y` coordinates
given. The output is a real number computed as:

.. math::
    s(x, y) = \displaystyle\sum_{\mathrm{ij}} \sum_{nm} u_{nm}(x, y) u_{nm}^*(x,y) a_{\mathrm{i}nm} a_{\mathrm{j}nm}^*
    \quad\text{with}\quad
    \left\{\,\mathrm{i,j}\,|\,\mathrm{i,j} \in [0, \dots, N] \wedge \omega_{\mathrm{i}} = \omega_{\mathrm{j}}\right\}.
"""

import logging

from cython.parallel import prange
cimport numpy as np
import numpy as np

from finesse.cymath cimport complex_t
from finesse.cymath.complex cimport conj, creal
from finesse.cymath.complex cimport crotate2, COMPLEX_0
from finesse.cymath.gaussbeam cimport bp_waistsize
from finesse.cymath.math cimport cos, sin
from finesse.cymath.math cimport float_eq, nmax
from finesse.cymath.homs cimport (
    unm_ws_recache_from_bp,
    unm_factor_store_init,
    unm_factor_store_recache,
    unm_factor_store_free,
    u_nm__fast
)

from finesse.utilities.cyomp cimport determine_nthreads_even
from finesse.simulations.sparse.solver cimport SparseSolver

ctypedef (double*,) ptr_tuple_1

cdef extern from "constants.h":
    double INV_ROOT2


LOGGER = logging.getLogger(__name__)


cdef class CameraWorkspace(MaskedDetectorWorkspace):
    """Workspace class for cameras."""

    def __init__(self, owner, sim, values=None):
        super().__init__(owner, sim, values, needs_carrier=True)

        self.node_id = self.sim.trace_node_index[owner.node]
        self.q = &self.sim.trace[self.node_id]
        self.sparse_carrier_solver = <SparseSolver>(self.sim.carrier)

        x = owner.xdata
        y = owner.ydata
        if owner.w0_scaled:
            x *= bp_waistsize(&self.q.qx)
            y *= bp_waistsize(&self.q.qy)

        if isinstance(x, np.ndarray):
            self.x_view = x
            self.scan_ax = XAXIS
        else:
            self.x_view = np.array([x], dtype=np.float64)

        if isinstance(y, np.ndarray):
            self.y_view = y
            self.scan_ax = YAXIS
        else:
            self.y_view = np.array([y], dtype=np.float64)

        self.xpts = self.x_view.shape[0]
        self.ypts = self.y_view.shape[0]

        cdef int outer_pts = nmax(self.xpts, self.ypts)
        # Nominal number of threads will be outer pixel loop size // 50
        self.nthreads = determine_nthreads_even(outer_pts, 50)

        LOGGER.info(
            "Using %d threads for %s outer pixel loop.",
            self.nthreads,
            self.owner.name,
        )

        self.phase_cache = np.zeros((self.num_unmasked_HOMs, 2))

        self.cache(initial=True)

    def __dealloc__(self):
        unm_factor_store_free(&self.ufs)

    cpdef cache(self, bint initial=False) :
        """Cache, or re-cache, the u_nm variables and Gouy phase data."""
        cdef:
            Py_ssize_t i
            Py_ssize_t p # mode index
            int n, m

            double n0 = 0.0
            double m0 = 0.0
            double phase

            int max_n, max_m

        unm_ws_recache_from_bp(&self.uws, &self.q.qx, &self.q.qy)
        if initial:
            max_n = self.sim.model_settings.max_n
            max_m = self.sim.model_settings.max_m
            unm_factor_store_init(&self.ufs, &self.uws, max_n, max_m, False, False)
        else:
            unm_factor_store_recache(&self.ufs, &self.uws, False, False)

        if not self.sim.model_settings.phase_config.zero_tem00_gouy:
            n0 = 0.5
            m0 = 0.5

        for i in range(self.num_unmasked_HOMs):
            p = self.unmasked_mode_indices[i]
            n = self.sim.model_settings.homs_view[p][0]
            m = self.sim.model_settings.homs_view[p][1]

            phase = (n + n0) * self.uws.gouyx + (m + m0) * self.uws.gouyy

            self.phase_cache[i][0] = cos(phase)
            self.phase_cache[i][1] = -sin(phase)

### CCD type camera workspaces ###

cdef class CCDWorkspace(CameraWorkspace):
    def __init__(self, owner, sim, out):
        super().__init__(owner, sim)

        self.out = out


cdef class CCDLineWorkspace(CameraWorkspace):
    def __init__(self, owner, sim, out):
        super().__init__(owner, sim)

        self.out = out

### Field / complex camera type workspaces ###

cdef class ComplexCameraValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_1 ptr = (&self.f, )
        cdef tuple params = ("f", )
        self.setup(params, sizeof(ptr), <double**>&ptr)

cdef class ComplexCameraWorkspace(CameraWorkspace):
    def __init__(self, owner, sim):
        super().__init__(owner, sim, ComplexCameraValues())
        self.v = <ComplexCameraValues>self.values

cdef class FieldCameraWorkspace(ComplexCameraWorkspace):
    def __init__(self, owner, sim, out):
        super().__init__(owner, sim)

        self.out = out

cdef class FieldLineWorkspace(ComplexCameraWorkspace):
    def __init__(self, owner, sim, out):
        super().__init__(owner, sim)

        self.out = out


cdef complex_t field_beam_pixel(ComplexCameraWorkspace cws, double x, double y) noexcept nogil:
    cdef:
        Py_ssize_t freq_idx, k, field_idx
        int n, m
        complex_t z_ij = COMPLEX_0
        complex_t unm, at
        double cph, sph
        frequency_info_t *freq

        Py_ssize_t node_id = cws.node_id
        Py_ssize_t Nfreqs = cws.sim.carrier.optical_frequencies.size
        Py_ssize_t Nfields = cws.num_unmasked_HOMs

    for freq_idx in range(Nfreqs):
        freq = &cws.sim.carrier.optical_frequencies.frequency_info[freq_idx]
        if float_eq(freq.f, cws.v.f):
            at = COMPLEX_0
            for k in range(Nfields):
                field_idx = cws.unmasked_mode_indices[k]
                n = cws.sim.model_settings.homs_view[field_idx][0]
                m = cws.sim.model_settings.homs_view[field_idx][1]

                cph = cws.phase_cache[k][0]
                sph = cws.phase_cache[k][1]
                unm = u_nm__fast(&cws.uws, &cws.ufs, n, m, x, y)
                at += (
                    unm
                    * crotate2(
                        cws.sparse_carrier_solver.get_out_fast(node_id, freq_idx, field_idx),
                        cph,
                        sph
                    )
                    * INV_ROOT2
                )

            z_ij += at

    return z_ij


cdef double ccd_beam_pixel(CameraWorkspace cws, double x, double y) noexcept nogil:
    cdef:
        Py_ssize_t freq_idx_outer, freq_idx_inner, k, field_idx
        int n, m
        complex_t z_ij = COMPLEX_0
        complex_t unm, at1, at2
        double cph, sph

        Py_ssize_t node_id = cws.node_id

        Py_ssize_t Nfreqs = cws.sim.carrier.optical_frequencies.size
        Py_ssize_t Nfields = cws.num_unmasked_HOMs

    for freq_idx_outer in range(Nfreqs):
        for freq_idx_inner in range(Nfreqs):
            if not float_eq(
                cws.sim.carrier.optical_frequencies.frequency_info[freq_idx_outer].f,
                cws.sim.carrier.optical_frequencies.frequency_info[freq_idx_inner].f
            ):
                continue

            at1 = at2 = COMPLEX_0

            for k in range(Nfields):
                field_idx = cws.unmasked_mode_indices[k]
                n = cws.sim.model_settings.homs_view[field_idx][0]
                m = cws.sim.model_settings.homs_view[field_idx][1]

                cph = cws.phase_cache[k][0]
                sph = cws.phase_cache[k][1]
                unm = u_nm__fast(&cws.uws, &cws.ufs, n, m, x, y)
                at1 += (
                    unm
                    * crotate2(
                        cws.sparse_carrier_solver.get_out_fast(node_id, freq_idx_outer, field_idx),
                        cph,
                        sph
                    )
                    * INV_ROOT2
                )
                at2 += (
                    unm
                    * crotate2(
                        cws.sparse_carrier_solver.get_out_fast(node_id, freq_idx_inner, field_idx),
                        cph,
                        sph
                    )
                    * INV_ROOT2
                )

            z_ij += at1 * conj(at2)

    return creal(z_ij)


field_pixel_output = OutputFuncWrapper.make_from_ptr(c_field_pixel_output)
cdef c_field_pixel_output(DetectorWorkspace dws) :
    cdef:
        FieldPixelWorkspace ws = <CameraWorkspace> dws

    if not ws.q.is_fixed:
        ws.cache()

    return field_beam_pixel(ws, ws.x_view[0], ws.y_view[0])


ccd_pixel_output = OutputFuncWrapper.make_from_ptr(c_ccd_pixel_output)
cdef c_ccd_pixel_output(DetectorWorkspace dws) :
    cdef:
        CameraWorkspace ws = <CameraWorkspace> dws

    if not ws.q.is_fixed:
        ws.cache()

    return ccd_beam_pixel(ws, ws.x_view[0], ws.y_view[0])


field_line_output = OutputFuncWrapper.make_from_ptr(c_field_line_output)
cdef c_field_line_output(DetectorWorkspace dws) :
    cdef:
        FieldLineWorkspace ws = <CameraWorkspace> dws
        Py_ssize_t i, Npts
        double x, y

        int nthreads = ws.nthreads


    if not ws.q.is_fixed:
        ws.cache()

    if ws.scan_ax == XAXIS:
        Npts = ws.xpts
    else:
        Npts = ws.ypts

    if ws.scan_ax == XAXIS:
        y = ws.y_view[0]
        for i in prange(Npts, nogil=True, num_threads=nthreads, schedule="static"):
            ws.out[i] = field_beam_pixel(ws, ws.x_view[i], y)
    else:
        x = ws.x_view[0]
        for i in prange(Npts, nogil=True, num_threads=nthreads, schedule="static"):
            ws.out[i] = field_beam_pixel(ws, x, ws.y_view[i])

    return ws.out.base.copy()

ccd_line_output = OutputFuncWrapper.make_from_ptr(c_ccd_line_output)
cdef c_ccd_line_output(DetectorWorkspace dws) :
    cdef:
        CCDLineWorkspace ws = <CameraWorkspace> dws
        Py_ssize_t i, Npts
        double x, y

        int nthreads = ws.nthreads

    if not ws.q.is_fixed:
        ws.cache()

    if ws.scan_ax == XAXIS:
        Npts = ws.xpts
    else:
        Npts = ws.ypts

    if ws.scan_ax == XAXIS:
        y = ws.y_view[0]
        for i in prange(Npts, nogil=True, num_threads=nthreads, schedule="static"):
            ws.out[i] = ccd_beam_pixel(ws, ws.x_view[i], y)
    else:
        x = ws.x_view[0]
        for i in prange(Npts, nogil=True, num_threads=nthreads, schedule="static"):
            ws.out[i] = ccd_beam_pixel(ws, x, ws.y_view[i])

    return ws.out.base.copy()

field_camera_output = OutputFuncWrapper.make_from_ptr(c_field_camera_output)
cdef c_field_camera_output(DetectorWorkspace dws) :
    cdef:
        FieldCameraWorkspace ws = <CameraWorkspace> dws
        Py_ssize_t i, j

        int nthreads = ws.nthreads

    if not ws.q.is_fixed:
        ws.cache()

    for i in prange(ws.xpts, nogil=True, num_threads=nthreads, schedule="static"):
        for j in range(ws.ypts):
            ws.out[j][i] = field_beam_pixel(ws, ws.x_view[i], ws.y_view[j])

    return ws.out.base.copy()

ccd_output = OutputFuncWrapper.make_from_ptr(c_ccd_output)
cdef c_ccd_output(DetectorWorkspace dws) :
    cdef:
        CCDWorkspace ws = <CameraWorkspace> dws
        Py_ssize_t i, j

        int nthreads = ws.nthreads

    if not ws.q.is_fixed:
        ws.cache()

    for i in prange(ws.xpts, nogil=True, num_threads=nthreads, schedule="static"):
        for j in range(ws.ypts):
            ws.out[j][i] = ccd_beam_pixel(ws, ws.x_view[i], ws.y_view[j])

    return ws.out.base.copy()
