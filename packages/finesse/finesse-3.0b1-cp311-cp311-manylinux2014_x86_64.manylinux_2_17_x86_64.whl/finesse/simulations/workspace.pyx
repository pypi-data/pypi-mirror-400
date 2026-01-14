from finesse.utilities.collections cimport OrderedSet
from finesse.utilities.collections import OrderedSet

cdef class GouyFuncWrapper:
    """
    Helper class for wrapping a C fill function that
    can be referenced from Python by objects. This
    allows a direct C call to the function from other
    cdef functions.

    Wraps a cdef for setting the gouy phase during a
    modal simulation.

    Examples
    --------
    Create a C function then wrap it using this class:

    >>> cdef int c_set_gouy(ABCDWorkspace ptr_ws) noexcept:
    >>>    cdef MirrorWorkspace ws = <MirrorWorkspace>ptr_ws
    >>>    ...
    >>>
    >>> fill = GouyFuncWrapper.make_from_ptr(c_set_gouy)
    """
    def __cinit__(self):
       self.func = NULL

    @staticmethod
    cdef GouyFuncWrapper make_from_ptr(fptr_c_gouy f) :
        cdef GouyFuncWrapper out = GouyFuncWrapper()
        out.func = f
        return out


cdef class ABCDWorkspace(ElementWorkspace):
    """
    This class represents a workspace for ABCD matrix calculations in Finesse simulations.
    It inherits from the ElementWorkspace class.

    Attributes
    ----------
    sim : BaseSimulation
        The BaseSimulation object associated with the workspace.
    owner : object
        The owner object of the workspace.
    values : object, optional
        Additional values associated with the workspace.

    Methods
    -------
    set_gouy_function(callback)
        Sets the callback function for computing the gouy phase terms.
    compile_abcd_cy_exprs()
        Compiles the ABCD matrix expressions for the workspace.
    flag_changing_beam_parameters(changing_edges)
        Called when the workspace should check if changing beam parameters
        will affect this workspace's calculations.
    update_map_data()
        Called when the workspace should update any map data
    """

    def __init__(
        self,
        BaseSimulation sim,
        object owner,
        object values=None,
    ):
        super().__init__(sim, owner, values)

    def set_gouy_function(self, callback):
        """
        Sets the callback function that will be used by the model to compute the gouy phase terms for an element.
        This can either be a Python function or cdef wrapped with `GouyFuncWrapper`.

        Parameters
        ----------
        callback : function or GouyFuncWrapper
            The callback function that computes the gouy phase terms for an element.
            It can be either a Python function or a cdef wrapped function.
        """
        if type(callback) is GouyFuncWrapper:
            self.fn_gouy_c = callback
        else:
            self.fn_gouy_py = callback

    def compile_abcd_cy_exprs(self):
        """
        Compiles the ABCD matrix expressions for the workspace.
        It is called during the simulation setup phase.
        """
        pass

    cpdef flag_changing_beam_parameters(self, OrderedSet changing_edges):
        """
        Flags changing beam parameters for the workspace.
        Workspaces that inherit from this must then check the edges it is dealing with
        and determine whether it needs to do extra calculations or not.

        Parameters
        ----------
        changing_edges : set
            A set of edges (tuple of (in, out) node indices) that have a changing
            beam parameter. The index can be related back to a node object by
            checking the BaseSimulation.trace_node_index dictionary.
        """
        raise NotImplementedError()

    cpdef update_map_data(self):
        """
        Signals that a workspace should update any data held in maps it is using.
        This is called when the simulation is first run and when the `UpdateMaps` action is called.
        """
        raise NotImplementedError()
