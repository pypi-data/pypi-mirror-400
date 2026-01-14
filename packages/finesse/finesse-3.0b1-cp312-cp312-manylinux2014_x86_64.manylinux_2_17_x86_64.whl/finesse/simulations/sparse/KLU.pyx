

import logging
import numpy as np

from finesse.config import config_instance
from finesse.cymath.cmatrix import KLUMatrix
from finesse.cymath.cmatrix cimport KLUMatrix
from finesse.cymath cimport complex_t
from .solver cimport SparseSolver

LOGGER = logging.getLogger(__name__)

from finesse.components.modulator import Modulator
from finesse.components.general import NoiseType
from finesse.detectors.general import Detector
from finesse.detectors.workspace import DetectorWorkspace
from finesse.components.workspace cimport ConnectorWorkspace, fill_list_t

class KLUStatWorkspace(DetectorWorkspace):
    pass

class KLUStatsDetector(Detector):
    """
    A detector that can be used to output some of the KLU solver statistics.
    """

    def __init__(self, name, matrix, stat):
        Detector.__init__(self, name, None, dtype=np.float64, label="a.u")
        self.stat = stat.lower()
        self.matrix = matrix.lower()
        if matrix.lower() not in ("carrier", "signal"):
            raise Exception("Matrix setting must be either `carrier` or `signal`")
        if stat.lower() not in ("rcond", "growth", "condest"):
            raise Exception("Matrix setting must be either 'rcond', 'growth', or 'condest'")

    def _get_workspace(self, sim):
        ws = KLUStatWorkspace(self, sim)
        ws.fn = getattr(sim, self.stat)
        ws.set_output_fn(self.fill)
        return ws

    def fill(self, ws):
        return ws.fn()


cdef class KLUSolver(SparseSolver):
    def __init__(self, *args, **kwargs):
        super().__init__(KLUMatrix, *args, **kwargs)
        self.rcond_diff_lim = float(config_instance()["klu"]["rcond_diff_lim"])

    cpdef refactor(self) :
        #cdef double rcond = (<KLUMatrix>self._M).rcond()
        #cdef double diff = abs((self.prev_rcond - rcond)/self.prev_rcond)

        #if diff > self.rcond_diff_lim:
        #    self._M.factor()
        #    self.prev_rcond = rcond
        #else:
        #    self._M.refactor()
        self._M.refactor()

    cpdef solve(self) :
        self._M.solve()
        self.num_solves += 1

    cpdef solve_noises(self) :
        cdef:
            Py_ssize_t idx, i
            bint factor = False
            KLUMatrix noise_M
            complex_t[::1] rhs
            fill_list_t *fill_list
            ConnectorWorkspace cws

        # Modulators couple things differently for the purposes of quantum noise, so we need to
        # refill them here
        # TODO: Really this shouldn't be needed, and the modulator should just behave as normal.
        # However, we don't currently model the extra sidebands required, and so would lose some
        # quantum noise if we were to do so. Instead, we just treat it as if the modulator were not
        # there - this is correct as long as squeezing is not involved.
        if NoiseType.QUANTUM in self._noise_matrices:
            for ws in self.workspaces.to_initial_fill:
                if isinstance(ws.owner, Modulator):
                    ws.fill_quantum_matrix()
                    factor = True
            if factor:
                self.refactor()

        # First ask all of the noise detectors to fill their selection vectors
        for ws in self.workspaces.noise_detectors:
            ws.fill_selection_vector()

        # Then solve all of these at once
        self._M.solve_extra_rhs(transpose=True, conjugate=True)

        # Next, perform the necessary multiplication for each solved rhs
        # TODO: This should be parallelizable per-noise-source, if we can guarantee that the rhs
        # vectors of the same noise type are contiguous
        for ws in self.workspaces.noise_detectors:
            noise_M = self._noise_matrices[ws.owner.noise_type]
            rhs_view = noise_M.get_rhs_view(0)
            rhs_array = np.asarray(rhs_view)
            for idx in ws.owner._requested_selection_vectors.values():
                rhs = self._M.get_rhs_view(idx)
                if ws.owner._has_sources():
                    source_s = ws.get_source_selection_vector()
                    np.multiply(rhs, source_s, out=rhs_array)
                else:
                    rhs_view[:] = rhs[:]
                noise_M.zgemv(rhs)

        # Solve all of the rhs vectors at once again
        self._M.solve_extra_rhs(transpose=False, conjugate=False)

        # Finally give the results back to the noise detectors
        for ws in self.workspaces.noise_detectors:
            for name, idx in ws.owner._requested_selection_vectors.items():
                rhs = self._M.get_rhs_view(idx)
                ws.set_covariance_matrix(rhs, name)

        # Restore the original signal matrix if it's not going to be refilled on the next step
        # TODO: is this needed? Probably
        if NoiseType.QUANTUM in self._noise_matrices:
            for cws in self.workspaces.to_initial_fill:
                if isinstance(cws.owner, Modulator) and cws not in self.workspaces.to_refill:
                    fill_list  = &cws.signal.matrix_fills
                    for i in range(fill_list.size):
                        if fill_list.infos[i].fn_c:
                            fill_list.infos[i].fn_c(cws)
                        elif fill_list.infos[i].fn_py:
                            (<object>fill_list.infos[i].fn_py).__call__(cws)
            if factor:
                self.refactor()

    cpdef double rcond(self) noexcept:
        return (<KLUMatrix>self._M).rcond()

    cpdef double condest(self) noexcept:
        return (<KLUMatrix>self._M).condest()

    cpdef double rgrowth(self) noexcept:
        return (<KLUMatrix>self._M).rgrowth()

    cpdef initial_run(self) :
        self.initial_fill()
        self._M.factor()
        self.prev_rcond = self._M.rcond()
        self.fill_rhs()
        self.solve()

    cpdef add_noise_matrix(self, object key):
        if key in self._noise_matrices:
            raise ValueError(f"Noise matrix '{key}' already added to system.")
        self._noise_matrices[key] = KLUMatrix(str(key))

    cpdef add_rhs(self, unicode key) :
        self._M.get_rhs_index(key)
