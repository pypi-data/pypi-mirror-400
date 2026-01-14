from ..simulation cimport BaseSimulation

cdef class SparseMatrixSimulation(BaseSimulation):

    cpdef initialise_workspaces(self)
    cpdef initialise_noise_matrices(self)
    cpdef initialise_noise_sources(self)
    cpdef initialise_noise_selection_vectors(self)

    cpdef compute_knm_matrices(self)
