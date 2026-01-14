from finesse.simulations.workspace cimport ABCDWorkspace
from finesse.cymath.cmatrix cimport SubCCSView
from finesse.frequency cimport frequency_info_t

from libc.stdlib cimport calloc, free
from cpython.ref cimport PyObject, Py_XINCREF, Py_XDECREF

cdef class FillFuncWrapper:
    """
    Helper class for wrapping a C fill function that
    can be referenced from Python by objects. This
    allows a direct C call to the function from other
    cdef functions.

    Examples
    --------
    Create a C function then wrap it using this class:

    >>> cdef void c_fill(ConnectorWorkspace ptr_ws) noexcept:
    >>>    cdef MirrorWorkspace ws = <MirrorWorkspace>ptr_ws
    >>>    ...
    >>>
    >>> fill = FillFuncWrapper.make_from_ptr(c_fill)
    """
    def __cinit__(self):
       self.func = NULL

    @staticmethod
    cdef FillFuncWrapper make_from_ptr(fptr_c_fill f) :
        cdef FillFuncWrapper out = FillFuncWrapper()
        out.func = f
        return out


class Connections:
    """This is a container object for storing the connection submatrices defined by
    a component. This is used in the default case where no optimised C class is provided."""
    pass


class NoiseSources:
    """This is a container object for storing the noise submatrices defined by
    a component. This is used in the default case where no optimised C class is provided."""
    pass


cdef class ConnectorMatrixSimulationInfo:
    def __init__(self, object connections=None, object noise_sources=None):
        self.fn_rhs_c = None
        self.fn_rhs_py = None
        self.fn_quantum_noise_c = None
        self.fn_quantum_noise_py = None
        self.fn_quantum_noise_input_c = None
        self.fn_quantum_noise_input_py = None
        self.connections = connections or Connections()
        self.connection_settings = {}
        self.noise_sources = noise_sources or NoiseSources()

    def __dealloc__(self):
        for i in range(self.matrix_fills.size):
            if self.matrix_fills.infos[i].fn_py != NULL:
                Py_XDECREF(self.matrix_fills.infos[i].fn_py)
                self.matrix_fills.infos[i].fn_py = NULL

    def add_fill_function(self, callback, bint refill):
        """ This adds a callback function that will be used by the model to
        fill the matrix elements. This can either be a Python function or cdef
        wrapped with `FillFuncWrapper`.

        Parameters
        ----------
        callback : Callable or FillFuncWrapper
            Callback for fill function
        refill : boolean
            Flags that this fill function will need to be called multiple times
            during simulation to refill the simulation matrix
        """
        cdef Py_ssize_t MAX = sizeof(self.matrix_fills.infos)//sizeof(fill_info_t)

        if self.matrix_fills.size >= MAX:
            raise IndexError(f"Reached maximum number ({MAX}) of fill functions")

        if type(callback) is FillFuncWrapper:
            self.matrix_fills.infos[self.matrix_fills.size].fn_c = (<FillFuncWrapper>callback).func
            self.matrix_fills.infos[self.matrix_fills.size].fn_py = NULL
        elif callable(callback):
            self.matrix_fills.infos[self.matrix_fills.size].fn_py = <PyObject*> callback
            Py_XINCREF(self.matrix_fills.infos[self.matrix_fills.size].fn_py)
        else:
            raise ValueError(f"Callback {callback} should be callable or a FillFuncWrapper")

        self.matrix_fills.infos[self.matrix_fills.size].refill = refill
        self.matrix_fills.size += 1
        self.matrix_fills.num_refills += int(refill)
        self.callback_flag = <ConnectorCallbacks> (self.callback_flag | ConnectorCallbacks.FILL_MATRIX)

    def set_fill_rhs_fn(self, callback):
        """ This sets the callback function that will be used by the model to
        fill the RHS vector elements. This can either be a Python function or cdef
        wrapped with `FillFuncWrapper`.
        """
        if type(callback) is FillFuncWrapper:
            self.fn_rhs_c = callback
        elif callable(callback):
            self.fn_rhs_py = callback
        else:
            raise ValueError(f"Callback {callback} should be callable or a FillFuncWrapper")

        self.callback_flag = <ConnectorCallbacks> (self.callback_flag | ConnectorCallbacks.FILL_RHS)

    def set_fill_noise_function(self, noise_type, callback):
        """ This sets the callback function that will be used by the model to
        fill the noise matrix elements. This can either be a Python
        function, which accepts a
        """
        from finesse.components.general import NoiseType

        if noise_type == NoiseType.QUANTUM:
            if type(callback) is FillFuncWrapper:
                self.fn_quantum_noise_c = callback
            elif callable(callback):
                self.fn_quantum_noise_py = callback
            else:
                raise ValueError(f"Callback {callback} should be callable or a FillFuncWrapper")
        else:
            raise ValueError(f"Unsupported noise type {noise_type}")

        self.callback_flag = <ConnectorCallbacks> (self.callback_flag | ConnectorCallbacks.FILL_NOISE)

    def set_fill_quantum_noise_input_function(self, callback):
        """ This sets the callback function that will be used by the model to
        fill the quantum noise matrix elements due to input nodes.
        """
        if type(callback) is FillFuncWrapper:
            self.fn_quantum_noise_input_c = callback
        elif callable(callback):
            self.fn_quantum_noise_input_py = callback
        else:
            raise ValueError(f"Callback {callback} should be callable or a FillFuncWrapper")

        self.callback_flag = <ConnectorCallbacks> (self.callback_flag | ConnectorCallbacks.FILL_INPUT_NOISE)


cdef class ConnectorWorkspace(ABCDWorkspace):
    """
    This workspace represents the basic container for storing details
    for modelling Connector elements - those which form edges and nodes
    in a model.
    """
    def __init__(
        self,
        object owner,
        object sim,
        object carrier_connections=None,
        object signal_connections=None,
        object values=None,
        object noise_sources=None
    ):
        super().__init__(sim, owner, values=values)
        self.carrier = ConnectorMatrixSimulationInfo(carrier_connections)
        self.signal = ConnectorMatrixSimulationInfo(signal_connections, noise_sources)

        if sim.signal:
            self.setup_quantum_noise()

    cdef setup_quantum_noise(self) :
        cdef:
            int i
            int num_input_nodes
            int num_output_nodes
        from finesse.components.space import Space

        input_nodes = []
        output_nodes = []
        # Spaces don't own any nodes, can't be unconnected, and can't have mismatches across them
        if not isinstance(self.owner, Space):
            for node in self.owner.optical_nodes:
                if node.is_input:
                    # Only add input nodes if they are unconnected
                    # or known as an open port where vacuum noise
                    # gets injected in
                    if not node.port.is_connected:
                        input_nodes.append(node)
                else:
                    output_nodes.append(node)
        num_input_nodes = len(input_nodes)
        num_output_nodes = len(output_nodes)

        self.input_noise = NoiseInfo(num_input_nodes, self.sim.signal.optical_frequencies.size)
        self.output_noise = NoiseInfo(num_output_nodes, self.sim.signal.optical_frequencies.size)

        for i in range(num_input_nodes):
            node = input_nodes[i]
            self.input_noise.node_info[i].idx = self.sim.signal.node_id(node)

        for i in range(num_output_nodes):
            node = output_nodes[i]
            self.output_noise.node_info[i].idx = self.sim.signal.node_id(node)

        self.signal.set_fill_quantum_noise_input_function(optical_quantum_noise_plane_wave)


cdef class NoiseInfo:
    def __init__(self, int num_nodes, int num_frequencies):
        self.num_nodes = num_nodes
        self.nodes = SubCCSView2DArray(num_nodes, num_frequencies)
        self.node_info = <node_noise_info *>calloc(num_nodes, sizeof(node_noise_info))
        if not self.node_info:
            raise MemoryError()
        self.ptrs = self.nodes.views

    def __del__(self):
        if self.node_info:
            free(self.node_info)


optical_quantum_noise_plane_wave = FillFuncWrapper.make_from_ptr(c_optical_quantum_noise_plane_wave)
cdef c_optical_quantum_noise_plane_wave(ConnectorWorkspace ws) :
    cdef:
        int i, j
        double qn
        frequency_info_t *freq

    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        qn  = ws.sim.model_settings.UNIT_VACUUM / 2 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)
        for j in range(ws.input_noise.num_nodes):
            (<SubCCSView>ws.input_noise.ptrs[j][i]).fill_za(qn)
