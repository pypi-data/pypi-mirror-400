from finesse.element_workspace cimport ElementWorkspace
from finesse.simulations.simulation cimport BaseSimulation
from finesse.utilities.collections cimport OrderedSet

ctypedef int (*fptr_c_gouy)(ABCDWorkspace) except -1


cdef class GouyFuncWrapper:
    cdef fptr_c_gouy func
    @staticmethod
    cdef GouyFuncWrapper make_from_ptr(fptr_c_gouy f)


cdef class ABCDWorkspace(ElementWorkspace):
    cdef readonly:
        GouyFuncWrapper fn_gouy_c  # C set Gouy phase function
        object fn_gouy_py  # Python set gouy function

    cpdef flag_changing_beam_parameters(self, OrderedSet changing_edges)
    cpdef update_map_data(self)
