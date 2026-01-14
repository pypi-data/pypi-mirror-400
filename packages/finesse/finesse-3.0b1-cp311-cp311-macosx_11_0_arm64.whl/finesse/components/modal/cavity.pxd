from finesse.cymath cimport complex_t
from finesse.cyexpr cimport (
    cy_expr,
    cy_expr_new,
    cy_expr_init,
    cy_expr_free,
    cy_expr_eval,
)
from finesse.element_workspace cimport ElementWorkspace
from finesse.tracing.tree cimport TraceTree
from finesse.simulations.simulation cimport BaseSimulation

cdef enum cavity_plane:
    X,
    Y


cdef class CavityWorkspace(ElementWorkspace):
    cdef:
        # Round-trip ABCDs in both planes
        double[:, ::1] abcd_x
        double[:, ::1] abcd_y

        # The internal cavity tree (grabbed from the
        # simulations' changing forest)
        TraceTree tree

        # Flag for whether the internal cavity tree is
        # in the changing forest of the simulation
        bint is_changing
        bint is_stable # is 0 < {gx, gy} < 1
        bint is_stable_x # is 0 < gx < 1
        bint is_stable_y # is 0 < gy < 1

        # Store both symbolic and numeric expressions for
        # the relevant cavity parameters - the symbolic
        # fields consist of only the changing symbols if any
        cy_expr* sym_length
        double length

        cy_expr* sym_loss
        double loss

        cy_expr* sym_finesse
        double finesse

        cy_expr* sym_fsr
        double fsr

        cy_expr* sym_fwhm
        double fwhm

        cy_expr* sym_tau
        double tau

        cy_expr* sym_pole
        double pole

        # These parameters are dependent upon the round-trip ABCD
        # so are computed differently (via the cavity trace tree)
        # for efficiency

        # round-trip Gouy phase
        double rt_gouy_x
        double rt_gouy_y

        # mode separation frequency
        double Df_x
        double Df_y

        # eigenmode
        complex_t qx
        complex_t qy

        # resolution
        double Sx
        double Sy

        # stability (g-factor)
        double gx
        double gy


    cdef void __update_geometric(self) noexcept

    cdef void update(self) noexcept
    cdef bint update_eigenmode(self, cavity_plane plane) noexcept
    cdef void update_stability(self, cavity_plane plane) noexcept
    cdef void update_rt_gouy(self, cavity_plane plane) noexcept
    cdef void update_Df(self, cavity_plane plane) noexcept
    cdef void update_S(self, cavity_plane plane) noexcept
