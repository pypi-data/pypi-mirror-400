#cython: boundscheck=False, wraparound=False, initializedcheck=False

from finesse.cymath.complex cimport csqrt, cimag, COMPLEX_0
from finesse.cymath.math cimport acos, sqrt, PI
from finesse.cymath.math cimport sgn

from finesse.symbols import Symbol
from finesse.exceptions import BeamTraceException


cdef class CavityWorkspace(ElementWorkspace):
    def __init__(self, owner, BaseSimulation sim):
        cdef:
            TraceTree tree
            Py_ssize_t tree_idx

        super().__init__(sim, owner)

        self.tree = None
        for tree_idx in range(sim.trace_forest.size()):
            tree = sim.trace_forest.forest[tree_idx]

            if tree.dependency == owner and tree.is_source:
                if self.tree is not None:
                    raise BeamTraceException(
                        "Found multiple trees in the simulation "
                        f"trace forest corresponding to the same cavity {owner.name}"
                    )

                self.tree = tree

        self.is_changing = self.tree is not None

        self.abcd_x = owner.ABCDx
        self.abcd_y = owner.ABCDy

        ch_sym_length = owner._optical_length.expand_symbols().eval(keep_changing_symbols=True)
        self.length = float(ch_sym_length)
        if isinstance(ch_sym_length, Symbol):
            self.sym_length = cy_expr_new()
            cy_expr_init(self.sym_length, ch_sym_length)
        else:
            self.sym_length = NULL

        ch_sym_loss = owner._loss.expand_symbols().eval(keep_changing_symbols=True)
        self.loss = float(ch_sym_loss)
        if isinstance(ch_sym_loss, Symbol):
            self.sym_loss = cy_expr_new()
            cy_expr_init(self.sym_loss, ch_sym_loss)
        else:
            self.sym_loss = NULL

        ch_sym_finesse = owner._finesse.expand_symbols().eval(keep_changing_symbols=True)
        self.finesse = float(ch_sym_finesse)
        if isinstance(ch_sym_finesse, Symbol):
            self.sym_finesse = cy_expr_new()
            cy_expr_init(self.sym_finesse, ch_sym_finesse)
        else:
            self.sym_finesse = NULL

        ch_sym_fsr = owner._FSR.expand_symbols().eval(keep_changing_symbols=True)
        self.fsr = float(ch_sym_fsr)
        if isinstance(ch_sym_fsr, Symbol):
            self.sym_fsr = cy_expr_new()
            cy_expr_init(self.sym_fsr, ch_sym_fsr)
        else:
            self.sym_fsr = NULL

        ch_sym_fwhm = owner._FWHM.expand_symbols().eval(keep_changing_symbols=True)
        self.fwhm = float(ch_sym_fwhm)
        if isinstance(ch_sym_fwhm, Symbol):
            self.sym_fwhm = cy_expr_new()
            cy_expr_init(self.sym_fwhm, ch_sym_fwhm)
        else:
            self.sym_fwhm = NULL

        ch_sym_tau = owner._tau.expand_symbols().eval(keep_changing_symbols=True)
        self.tau = float(ch_sym_tau)
        if isinstance(ch_sym_tau, Symbol):
            self.sym_tau = cy_expr_new()
            cy_expr_init(self.sym_tau, ch_sym_tau)
        else:
            self.sym_tau = NULL

        ch_sym_pole = owner._pole.expand_symbols().eval(keep_changing_symbols=True)
        self.pole = float(ch_sym_tau)
        if isinstance(ch_sym_pole, Symbol):
            self.sym_pole = cy_expr_new()
            cy_expr_init(self.sym_pole, ch_sym_pole)
        else:
            self.sym_pole = NULL

        self.__update_geometric()

    def __dealloc__(self):
        cy_expr_free(self.sym_length)
        cy_expr_free(self.sym_loss)
        cy_expr_free(self.sym_finesse)
        cy_expr_free(self.sym_fsr)
        cy_expr_free(self.sym_fwhm)
        cy_expr_free(self.sym_tau)
        cy_expr_free(self.sym_pole)

    cdef void __update_geometric(self) noexcept:
        cdef:
            bint qx_ok, qy_ok

        qx_ok = self.update_eigenmode(cavity_plane.X)
        qy_ok = self.update_eigenmode(cavity_plane.Y)

        self.update_stability(cavity_plane.X)
        self.update_stability(cavity_plane.Y)
        self.is_stable_x = self.gx > 0.0 and self.gx < 1.0
        self.is_stable_y = self.gy > 0.0 and self.gy < 1.0
        self.is_stable = self.is_stable_x and self.is_stable_y

        if qx_ok or self.gx == 0 or self.gx == 1:
            self.update_rt_gouy(cavity_plane.X)
            self.update_Df(cavity_plane.X)
            self.update_S(cavity_plane.X)
        else:
            self.qx = COMPLEX_0
            self.rt_gouy_x = 0.0
            self.Df_x = 0.0
            self.Sx = 0.0

        if qy_ok or self.gy == 0 or self.gy == 1:
            self.update_rt_gouy(cavity_plane.Y)
            self.update_Df(cavity_plane.Y)
            self.update_S(cavity_plane.Y)
        else:
            self.qy = COMPLEX_0
            self.rt_gouy_y = 0.0
            self.Df_y = 0.0
            self.Sy = 0.0

    cdef void update(self) noexcept:
        # Update all the changing symbolic parameters
        if self.sym_length != NULL:
            self.length = cy_expr_eval(self.sym_length)
        if self.sym_loss != NULL:
            self.loss = cy_expr_eval(self.sym_loss)
        if self.sym_finesse != NULL:
            self.finesse = cy_expr_eval(self.sym_finesse)
        if self.sym_fsr != NULL:
            self.fsr = cy_expr_eval(self.sym_fsr)
        if self.sym_fwhm != NULL:
            self.fwhm = cy_expr_eval(self.sym_fwhm)
        if self.sym_tau != NULL:
            self.tau = cy_expr_eval(self.sym_tau)
        if self.sym_pole != NULL:
            self.pole = cy_expr_eval(self.sym_pole)

        # Update round-trip ABCD and dependent params if necessary
        if self.is_changing:
            self.tree.compute_rt_abcd(self.abcd_x, self.abcd_y)
            self.__update_geometric()

    cdef bint update_eigenmode(self, cavity_plane plane) noexcept:
        cdef:
            double[:, ::1] abcd = self.abcd_x if plane == cavity_plane.X else self.abcd_y
            double D_minus_A = abcd[1][1] - abcd[0][0]
            double minus_B = -abcd[0][1]
            double C = abcd[1][0]

            double half_inv_C
            complex_t sqrt_term
            complex_t lower, upper

            complex_t q

        if C == 0.0:
            return False

        half_inv_C = 0.5 / C

        sqrt_term = csqrt(D_minus_A * D_minus_A - 4 * C * minus_B)
        lower = (-D_minus_A - sqrt_term) * half_inv_C
        upper = (-D_minus_A + sqrt_term) * half_inv_C

        if cimag(lower) > 0:
            q = lower
        elif cimag(upper) > 0:
            q = upper
        else:
            return False

        if plane == cavity_plane.X:
            self.qx = q
        else:
            self.qy = q

        return True

    cdef void update_stability(self, cavity_plane plane) noexcept:
        cdef:
            double[:, ::1] abcd = self.abcd_x if plane == cavity_plane.X else self.abcd_y
            double A = abcd[0][0]
            double D = abcd[1][1]

            double g = 0.5 * (1 + 0.5 * (A + D))

        if plane == cavity_plane.X:
            self.gx = g
        else:
            self.gy = g

    cdef void update_rt_gouy(self, cavity_plane plane) noexcept:
        cdef:
            double[:, ::1] abcd = self.abcd_x if plane == cavity_plane.X else self.abcd_y
            double g = self.gx if plane == cavity_plane.X else self.gy
            double B = abcd[0][1]

            double gouy = 2.0 * acos(sgn(B) * sqrt(g))

        if plane == cavity_plane.X:
            self.rt_gouy_x = gouy
        else:
            self.rt_gouy_y = gouy

    cdef void update_Df(self, cavity_plane plane) noexcept:
        cdef:
            double gouy = self.rt_gouy_x if plane == cavity_plane.X else self.rt_gouy_y

            double df = 0.5 * self.fsr * gouy / PI

        if gouy > PI:
            df = self.fsr - df

        if plane == cavity_plane.X:
            self.Df_x = df
        else:
            self.Df_y = df

    cdef void update_S(self, cavity_plane plane) noexcept:
        cdef:
            double gouy = self.rt_gouy_x if plane == cavity_plane.X else self.rt_gouy_y

            double s = 0.5 * self.finesse * gouy / PI

        if gouy > PI:
            s = self.finesse - s

        if plane == cavity_plane.X:
            self.Sx = s
        else:
            self.Sy = s
