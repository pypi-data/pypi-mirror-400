cimport numpy as np
import numpy as np
cimport cython

from finesse.cymath.homs cimport in_mask
from finesse.detectors.general import Detector
from copy import copy

cdef class OutputInformation:
    def __init__(self, name, detector_type, nodes, dtype, unit, shape, label, needs_fields, needs_trace):
        if shape is None:
            shape = ()
        self.name = name
        self.__detector_type = detector_type
        self.__nodes = nodes
        self.__dtype = dtype
        self.__unit = unit
        self.__label = label
        self.__needs_fields = needs_fields
        self.__needs_trace = needs_trace
        self._update_dtype_shape(shape)

    def _set_dtype(self, dtype):
        self.__dtype = dtype

    @property
    def detector_type(self):
        """The type of the detector that has generated this output information."""
        return self.__detector_type

    @property
    def needs_fields(self):
        """Flag indicating whether the detector requires light fields (i.e. solving of
        the interferometer matrix)."""
        return self.__needs_fields

    @property
    def needs_trace(self):
        """Flag indicating whether the detector requires beam traces."""
        return self.__needs_trace

    @property
    def nodes(self):
        """The nodes this detector observes.

        :`getter`: Returns copy of detected nodes.
        """
        return copy(self.__nodes)

    @property
    def dtype(self):
        return self.__dtype

    @property
    def dtype_shape(self):
        return self.__dtype_shape

    def _update_dtype_shape(self, shape):
        """Only to be used internally by detectors like Cameras for updating the shape
        if resolution is changed. Shouldn't be changed by users directly or during a simulation."""
        self.__dtype_shape = shape
        self.__dtype_size = int(np.prod(shape))

    @property
    def dtype_size(self):
        """Size of the output in terms of number of elements.

        This is typically unity as most detectors return a single
        value via their output functions.

        Equivalent to the product of :attr:`.Detector.dtype_shape`.
        """
        return self.__dtype_size

    @property
    def unit(self):
        return self.__unit

    def _update_unit(self, unit):
        self.__unit = unit

    @property
    def label(self):
        return self.__label

    def _update_label(self, label):
        self.__label = label


cdef class OutputFuncWrapper:
    """Helper class for wrapping a C fill function that can be referenced from Python by
    objects. This allows a direct C call to the function from other cdef functions.

    Examples
    --------
    Create a C function then wrap it using this class:

    >>> cdef void c_output(DetectorWorkspace ptr_ws) noexcept:
    >>>    cdef PDWorkspace ws = <PDWorkspace>ptr_ws
    >>>    ...
    >>>
    >>> fill = OutputFuncWrapper.make_from_ptr(c_fill)
    """
    def __cinit__(self):
       self.func = NULL

    def __call__(self, ws):
        return self.func(ws)

    @staticmethod
    cdef OutputFuncWrapper make_from_ptr(fptr_c_output f) :
        cdef OutputFuncWrapper out = OutputFuncWrapper()
        out.func = f
        return out


cdef class DetectorWorkspace(ElementWorkspace):
    """A base class that all detector workspaces should inherit from. Provides a generic
    set of data needed to compute values and output them with metadata needed for
    storing the outputs.

    Parameters
    ----------
    owner : :class:`finesse.element.ModelElement`
        Detector `Element` that owns this workspace and will be setting it up
    sim : Simulation object
        Simulation object this workspace should be associated with
    values :  [object, :class:`finesse.element_workspace.BaseCValues`], optional
        The object containing the values that will be used by this workspace to
        calculate some output. These should match the parameters offered by the
        owner. A pure Python object can be used but will be slower to access.
        A :class:`finesse.element_workspace.BaseCValues` object can also be used that offers cythonised
        access to parameter values
    oinfo : OutputInformation, optional
        When provided this will set the output information of this detector, such
        as units, datatype, shape/dimension of outputs.
    needs_carrier : bool, optional
        If the carrier simulation data is needed, this must be True
    needs_signal : bool, optional
        If the signal simulation data (transfer functions) is needed, this must be True
    needs_noise : bool, optional
        If this detector requires noise covariances to be calculated this must be True
    needs_modal_update: bool, optional
        If this detector outputs some modal or geometric property, this must be True.

    Notes
    -----
    The `needs_*` flags specify which simulations should be run to evaluate this
    workspace. At least one should be True, unless `needs_simulation` is
    flagged as False. This is to catch certain cases which mean the workspace
    will just not produce any output.

    When adding new `needs_*` flag, ensure you update the `MathDetector` object
    to correctly fill these flags. The `MathDetector` essentially borrows workspaces
    from other detectors to compute its output and
    """

    def __init__(
            self,
            object owner,
            object sim,
            object values=None,
            *,
            OutputInformation oinfo=None,
            bint needs_carrier=False,
            bint needs_signal=False,
            bint needs_noise=False,
            bint needs_modal_update=False,
            bint needs_simulation=True):

        flags = (needs_noise or needs_signal or needs_carrier or needs_modal_update)
        if not flags and needs_simulation:
            raise Exception(f"Detector workspace {self} has the flags set so that `needs_noise or needs_signal or needs_carrier or needs_modal_update == False`, so no calculations will be done.")
        elif not needs_simulation and flags:
            raise Exception(f"Detector workspace {self} is marked as not needing a simulation result but is flagging that it does.")

        super().__init__(sim, owner, values)
        self.needs_noise = needs_noise
        self.needs_signal = needs_signal
        self.needs_carrier = needs_carrier
        self.needs_modal_update = needs_modal_update
        if oinfo is None and isinstance(owner, Detector):
            oinfo = owner.output_information
        elif oinfo is None:
            raise ValueError("output information object must be provided if owner is not a detector")

        self.oinfo = oinfo
        self.ignore_sim_mask = False

    cpdef get_output(self) :
        self.update_parameter_values()
        if self.fn_c is not None:
            return self.fn_c.func(self)
        elif self.fn_py is not None:
            return self.fn_py(self)
        else:
            return None

    def set_output_fn(self, callback):
        if type(callback) is OutputFuncWrapper:
            self.fn_c = callback
        elif callable(callback):
            self.fn_py = callback
        else:
            raise ValueError(f"Callback function {callback} wasn't of type OutputFuncWrapper or a callable object")


cdef class MaskedDetectorWorkspace(DetectorWorkspace):
    """Specialised workspace for detectors which support masking of modes.

    This workspace provides attributes that are exposed to both C and Python. The
    sections below detail how to use these for some workspace instance ``ws`` which
    inherits from ``MaskedDetectorWorkspace``.

    .. rubric:: Using via Python

    The ``unmasked_indices_arr`` attribute is a :class:`numpy.ndarray`, of dtype
    ``np.intp``, which contains the indices of modes which are not masked. One
    may then simply loop over this array of indices to access the corresponding field
    indices, e.g

    .. code-block:: python

        for k in ws.unmasked_indices_arr:
            # Do something with k, e.g. get field at 0 Hz freq. offset
            # at the given node for the mode index k:
            a_0k = carrier.get_out_fast(ws.dc_node_id, 0, k)
            # use a_0k for some calculation ...

    .. rubric:: Using via Cython

    This workspace also provides a ``unmasked_mode_indices`` pointer (only accessible
    from other Cython code) which corresponds to the data of the ``unmasked_indices_arr``
    NumPy array described above. The attribute ``num_unmasked_homs`` is the size of
    this array; i.e. the number of modes which are not masked.

    One may then write an optimised loop from ``[0, num_unmasked_homs)``, e.g

    .. code-block:: cython

        cdef Py_ssize_t i, k
        cdef complex_t a_0k
        for i in range(ws.num_unmasked_homs):
            k = ws.unmasked_mode_indices[i]
            # Do something with k, e.g. get field at 0 Hz freq. offset
            # at the given node for the mode index k:
            a_0k = carrier.get_out_fast(ws.dc_node_id, 0, k)
            # use a_0k for some calculation ...

    where each ``k`` is then the index of the mode at position ``i`` in the unmasked
    indices array.

    .. note::

        If the detector mask is empty (i.e. no modes are being masked) then
        ``unmasked_indices_arr`` (and, correspondingly, ``unmasked_mode_indices``)
        will simply be an array from ``[0, Nhoms)`` where ``Nhoms`` is the total
        number of modes in the simulation.
    """
    def __init__(self, owner, BaseSimulation sim, values=None, *, oinfo=None, **kwargs):
        super().__init__(owner, sim, values, oinfo=oinfo, **kwargs)

        self.unmasked_mode_indices = NULL
        self.has_mask = False

        self.setup_mask()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef int setup_mask(self) except -1:
        cdef:
            int[:, ::1] mask
            Py_ssize_t N_mask
            Py_ssize_t i
            Py_ssize_t count = 0

            int n, m

        # Check if owner has the right attribute, as some non-masked detectors also own masked
        # detector workspaces, and will otherwise throw an error here
        self.has_mask = getattr(self.owner, "has_mask", False)

        cdef np.ndarray[Py_ssize_t, ndim=1, mode="c"] unmasked
        if not self.has_mask: # no mask so just copy across all mode indices
            self.num_unmasked_HOMs = self.sim.model_settings.num_HOMs
            unmasked = np.arange(self.num_unmasked_HOMs, dtype=np.intp)
            self.unmasked_indices_arr = unmasked
            self.unmasked_mode_indices = &unmasked[0]
        else:
            mask = self.owner.mask
            N_mask = mask.shape[0]
            if N_mask >= self.sim.model_settings.num_HOMs:
                raise RuntimeError(
                    f"Error in detector {self.owner} (Output `{self.oinfo.name}`):\n"
                    f"    Length of mask array ({N_mask}) greater than or equal to "
                    f"number of modes ({self.sim.model_settings.num_HOMs})"
                )

            self.num_unmasked_HOMs = self.sim.model_settings.num_HOMs - N_mask
            unmasked = np.arange(self.num_unmasked_HOMs, dtype=np.intp)
            self.unmasked_indices_arr = unmasked
            self.unmasked_mode_indices = &unmasked[0]

            for i in range(self.sim.model_settings.num_HOMs):
                n = self.sim.model_settings.homs_view[i][0]
                m = self.sim.model_settings.homs_view[i][1]

                if not in_mask(n, m, mask):
                    if count >= self.num_unmasked_HOMs:
                        raise RuntimeError(
                            f"Error in detector {self.owner.name}:\n"
                            f"    One or more modes in the mask array do not exist in "
                            "the model."
                        )
                    self.unmasked_mode_indices[count] = i
                    count += 1

        return 0

    cdef bint hom_in_modes(self, Py_ssize_t hom_idx) noexcept:
        """Check whether a HOM index is in the non-masked modes of the detector."""
        if not self.has_mask:
            return True

        cdef Py_ssize_t i
        for i in range(self.num_unmasked_HOMs):
            if self.unmasked_mode_indices[i] == hom_idx:
                return True

        return False
