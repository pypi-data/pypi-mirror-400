"""Simulation output"""

import numpy as np
cimport numpy as np
import logging
import cython

from finesse.env import warn
from finesse.plotting import Plotter
from finesse.detectors.workspace cimport DetectorWorkspace
from finesse.solutions.base cimport BaseSolution
from finesse.exceptions import FinesseException

from cpython.ref cimport PyObject, Py_XINCREF, Py_XDECREF
from libc.stdlib cimport calloc, free

LOGGER = logging.getLogger(__name__)

from collections.abc import Set, Iterable


class ArraySolutionSet(Set):
    """
    A set of Arraysolution. Outputs from mutliple similar ArraySolutions
    can be returned.
    """
    def __init__(self, solutions):
        if not isinstance(solutions, Iterable):
            raise Exception(f"{solutions} is not iterable")
        if not all(isinstance(_, ArraySolution) for _ in solutions):
            raise Exception(f"Solutions {solutions} must all be of type ArraySolution")
        if not all(_.outputs == solutions[0].outputs for _ in solutions[1:]):
            raise Exception(f"Solutions {solutions} must have the same outputs")

        self.solutions = lst = []
        for value in solutions:
            if value not in lst:
                lst.append(value)

    def __iter__(self):
        return iter(self.solutions)

    def __contains__(self, value):
        return value in self.solutions

    def __len__(self):
        return len(self.solutions)

    def __getitem__(self, key):
        return np.vstack(tuple(_[key] for _ in self.solutions))

    @property
    def outputs(self):
        return self.solutions[0].outputs


cdef class ArraySolution(BaseSolution):
    """Holds outputs from running a simulation.

    This is essentially a wrapped up Numpy structured array whose named elements are the names of
    outputs in a model.

    Detectors are stored in the array by their name. So you can use::

        output['detector_name']

    or, if the key has an attribute called `name` (as all Finesse.detectors do)
    it will use that, so using::

        output[ifo.detector]

    will return the same values.

    The underlying storage format is a Numpy structured array. You can select
    runs by::

        output[ifo.detector][a:b:c]

    where `a:b:c` is your slice. Or you can select multiple outputs with::

        output[['det1', 'det2']][a:b:c]

    Attributes
    ----------
    name : str
        Name to give to this analysis

    parent : :class:`.BaseSolution`
        Parent solutions that have preceded this solution being calculated.
        Can be `None`.

    x : tuple(ndarray)
        Array of axes that have been scanned over


    shape : :class:`numpy.ndarray`
        The shape of the underlying data array. use a single integer for 1D
        outputs, N-dimensional outputs can be specified by using tuples, i.e.
        (10,5,100) for a 3D array with the requested sizes.

    params : [array_like(objects)|array_like(str)]
        Parameters associtated with each dimension of the data
    """

    def __cinit__(self, *args, **kwargs):
        self.workspaces = NULL
        self.masked = False
        self.enabled = False

    def __reduce__(self):
        return deserialize, (
                (
                    self.name,
                    None,
                    self.shape,
                    self.x,
                    self.params,
                ),
                self.dtype,
                self.masked,
                self._data,
                self.detectors,
                self._axes,
                self._num,
                self.trace_info,
                self.axis_info,
            )


    def __dealloc__(self):
        if self.workspaces != NULL:
            for i in range(self.num_workspaces):
                if self.workspaces[i] != NULL:
                    Py_XDECREF(self.workspaces[i])
            free(self.workspaces)
            self.workspaces = NULL

    def __init__(self, name, parent, shape, xs, params):
        super().__init__(name, parent)
        self._num = -1
        self.empty = False  # tree drawing fill circle
        self.shape = shape
        self.trace_info = {}
        self.axis_info = {}
        self.x = tuple(xs)
        self.params = tuple((p if isinstance(p, str) else p.full_name for p in params))

        # A quirk of the serialisation of these objects means the first time we
        # create the solution we need to compute the axis info for plotting
        # but when we are loading this solution then just use the existing data
        if len(params) > 0 and not isinstance(params[0], str):
            for p in params:
                self.axis_info[p.full_name] = {
                    "name" : p.full_name,
                    "component" : p.owner.name if hasattr(p.owner, "name") else "",
                    "unit" : p.units
                }

        if hasattr(shape, "__getitem__"):
            self._axes = len(shape)
        else:
            self._axes = 1

    cpdef enable_update(self, detector_workspaces) :
        """This method will setup this solution to allow for fast C access for
        updating the solution in simulations. It must be called before any update
        calls are made. This will allocate memory for the workspaces to write
        data too.

        Parameters
        ----------
        detector_workspaces : iterable[:class:`finesse.detectors.workspace.DetectorWorkspace`]
            A collection of detector workspaces that should be called and the
            output saved into this solution.
        """
        if self.enabled:
            raise FinesseException("Solution has already enabled updates")

        names = []
        dtypes = []

        for ws in detector_workspaces:
            oinfo = ws.oinfo
            self.trace_info[oinfo.name] = {
                "name": oinfo.name,
                "detector_type": oinfo.detector_type,
                "dtype": oinfo.dtype,
                "unit": oinfo.unit,
                "label": oinfo.label,
            }
            names.append(oinfo.name)
            dtypes.append((oinfo.name, oinfo.dtype, oinfo.dtype_shape))

            # Some detectors need extra information about what they are plotting
            # it seems so here we call back to the object and get them
            if hasattr(ws.owner, "_set_plotting_variables"):
                ws.owner._set_plotting_variables(self.trace_info[oinfo.name])

        self.detectors = tuple(names)
        self.dtype = np.dtype(dtypes)
        self._data = np.zeros(self.shape, dtype=self.dtype)
        # Setup the workspace pointers
        self.num_workspaces = len(detector_workspaces)

        if self.num_workspaces > 0:
            if self.workspaces != NULL:
                raise MemoryError()
            self.workspaces = <PyObject**>calloc(self.num_workspaces, sizeof(PyObject*))
            if not self.workspaces:
                raise MemoryError()

            self.flatiters = np.empty(self.num_workspaces, dtype=object)

            for i in range(self.num_workspaces):
                oinfo = detector_workspaces[i].oinfo
                self.workspaces[i] = <PyObject*>detector_workspaces[i]
                Py_XINCREF(self.workspaces[i])
                self.flatiters[i] = self._data[oinfo.name].flat

        self.enabled = True

    def __getattr__(self, key):
        try:
            if key[0] == "x":
                idx = int(key[1:])
                if 1 < idx > len(self.x):
                    raise IndexError(f"Can only select x1 to x{len(self.x)}")
                return self.x[idx-1]
            if key[0] == "p":
                idx = int(key[1:])
                if 1 < idx > len(self.params):
                    raise IndexError(f"Can only select p1 to p{len(self.params)}")
                return self.params[idx-1]
        except ValueError:
            pass

    @property
    def data(self):
        return self._data

    @property
    def axes(self):
        return self._axes

    @property
    def entries(self):
        """
        The number of outputs that have been stored in here so far
        """
        return self._num + 1

    @property
    def outputs(self):
        """
        Returns all the outputs that have been stored.
        """
        return self._data.dtype.names

    def expand(self, shape):
        """
        Expands the output buffer by `shape` elements. This will be slow if you
        call repeatedly to increase by just a few elements as the whole array
        is copied into a new block of memory.

        Parameters
        ----------
        shape
            Shape of new array to make
        """
        self._data = np.append(self._data, np.empty(shape, dtype=self.dtype))

    def __getitem__(self, key):
        try:
            if not isinstance(key, str) and isinstance(key, Iterable) and len(key) == 1:
                key = key[0]

            if hasattr(key, "name"):
                key = key.name

            # NOTE: indexing with empty tuple here to handle noxaxis type outputs
            out = self._data[key][()]
            if self.masked:
                if out.dtype == object:
                    return np.ma.masked_object(out, np.nan)[()]
                else:
                    return np.ma.masked_invalid(out)[()]
            else:
                return out

        except (ValueError, IndexError, TypeError):
            # If no item for the given key can be found try the
            # base class get item to look for outputs
            return super().__getitem__(key)

    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.wraparound(False)
    cpdef int update(self, int index, bint mask,) except -1:
        """
        Calling this will compute all detector outputs and add an entry to
        the outputs stored. Calling it multiple times without re-running
        the simulation will result in duplicate entries.

        `enable_update` must be called to setup which detectors will be
        written to this solution object.

        Parameters
        ----------
        index : (int, ...)
           Index to calculate the outputs for, use tuples of N-size for
           N-dimensional outputs

        mask : boolean
            Sets the `index` of all outputs to `np.nan` if true. This should
            be used when a recoverable invalidity has occurred at some point
            in the scan of a parameter of a simulation - e.g. invalid beam
            tracing due to instabilities.

        Returns
        -------
        num : int
            Number of entries updated so far.
        """
        if not self.enabled:
            raise FinesseException("Update cannot be called on an ArraySolution which is not associated with a running simulation.")
        if self.num_workspaces > 0 and self.workspaces == NULL:
            raise MemoryError("workspaces NULL")
        if self.num_workspaces == 0:
            return 0

        cdef:

            Py_ssize_t i, block_size
            DetectorWorkspace dws

            # Indices for start and end of blocks for
            # detectors with array-like outputs
            Py_ssize_t block_i, block_f

        self.masked |= mask
        for i in range(self.num_workspaces):
            dws = <DetectorWorkspace> self.workspaces[i]

            # Detector output is an array so flatten it and assign to correct slice
            # Using __dtype_size for direct access
            if dws.oinfo.__dtype_size > 1:
                block_size = dws.oinfo.__dtype_size
                block_i = index * block_size
                block_f = (index + 1) * block_size

                if mask and not dws.ignore_sim_mask:
                    self.flatiters[i][block_i : block_f] = np.nan
                else:
                    # TODO (sjr) This relies on get_output returning a ndarray currently,
                    #            it would be good to change this a bit so that a memoryview
                    #            is also accepted (and flattened automatically).
                    self.flatiters[i][block_i : block_f] = dws.get_output().flat[:]

            else:
                if mask and not dws.ignore_sim_mask:
                    self.flatiters[i][index] = np.nan
                else:
                    dws_output = dws.get_output()
                    # if both self.flatiters[i][index] and dws.get_output() are
                    # numpy arrays or both are not, we can directly assign.
                    # Otherwise, dws output is a 1-element array and we need to
                    # take its value instead, since we can no longer rely on
                    # automatic conversion since numpy 2.4, see
                    # https://numpy.org/doc/stable/release/2.4.0-notes.html#raise-typeerror-on-attempt-to-convert-array-with-ndim-0-to-scalar
                    if (
                        isinstance(self.flatiters[i][index], np.ndarray)
                        or not isinstance(dws_output, np.ndarray)
                    ):
                        self.flatiters[i][index] = dws_output
                    else:
                        assert dws_output.shape == (1,), \
                            f"Unexpected shape of dws_output == {dws_output.shape}) prevents conversion to scalar"
                        self.flatiters[i][index] = dws_output[0]

        self._num += 1
        return self._num

    def plot(
        self,
        *detectors,
        log=False,
        logx=None,
        logy=None,
        degrees=True,
        cmap=None,
        figsize_scale=1,
        tight_layout=True,
        show=True,
        separate=True,
        _test_fig_handles=None,
    ):
        """
        See :mod:`finesse.plotting.plot`.
        """
        plotter = Plotter(self)
        plotter.scale = figsize_scale
        plotter.tight_layout = tight_layout

        return plotter.plot(*detectors, log=log, logx=logx, logy=logy, degrees=degrees, cmap=cmap, show=show, separate=separate, _test_fig_handles=_test_fig_handles)

    def get_legacy_data(self, model):
        """Get legacy style data

        This produces a Numpy array and set of headers which is equivelent to parsing a
        Finesse 2 output file.

        See Also
        --------
        :meth:`.write_legacy_data`

        Parameters
        ----------
        model : finesse.model.Model
           The Model used to produce this output file.

        Returns
        -------
        legacy_data : :class:`numpy.ndarray`
            The data array

        column_names : :class:`list`
            List of column names

        plot_type : '2D plot' or '3D plot'
            String indicating if the data should represent 2D or 3D scan.
        """
        import finesse

        # This first block creates the x axes in a Finesse 2 style

        axes = []
        column_names = []
        i = 1

        # Create a list with the same length
        # as the number of axes (i.e. 1 for xaxis, 2 for x2axis etc)
        while True:
            try:
                axes.append(getattr(self, f"x{i}"))
                column_names.append(f"x{i}")
                i += 1
            except IndexError:
                break

        outfile = [[] for ax in axes]
        for idx in np.ndindex(self.shape):
            for ax, val in enumerate(idx):
                outfile[ax].append(axes[ax][val])
        for idx, ax in enumerate(outfile):
            outfile[idx] = np.array(ax)

        if not outfile:
            # noxaxis in finesse2 produces a single 0
            outfile = [np.zeros(1)]


        data = []
        def add_yaxis(el, d):

            def check_real(el):
                #real = (
                #    isinstance(el, finesse.detectors.FieldPixel)
                #    or isinstance(el, finesse.detectors.FieldScanLine)
                #    or isinstance(el, finesse.detectors.FieldCamera)
                #    or isinstance(el, finesse.detectors.Gouy)
                #    or isinstance(el, finesse.detectors.BeamPropertyDetector)
                #    or isinstance(el, finesse.detectors.PowerDetector)
                #)
                #if isinstance(el, finesse.detectors.PowerDetectorDemod1):
                #    real = (el.phase.value is not None)
                #if isinstance(el, finesse.detectors.PowerDetectorDemod2):
                #    real = (el.phase2.value is not None)
                return el.dtype != np.complex128

            real = check_real(el)
            axis = model.yaxis or {"axes": ["abs"]}
            if real:
                any_complex = False
                for el2 in model.detectors:
                    any_complex = any_complex or not check_real(el2)

                if "abs" in axis["axes"]:
                    data.append(np.real(d))
                    column_names.append(str(name)+" abs")
                if "deg" in axis["axes"] and any_complex:
                    data.append(np.angle(d, deg=True))
                    column_names.append(str(name)+" deg")
                if "db" in axis["axes"]:
                    data.append(20 * np.log10(np.abs(d)))
                    column_names.append(str(name)+" db")
                if "re" in axis["axes"]:
                    data.append(np.real(d))
                    column_names.append(str(name)+" re")
                if "im" in axis["axes"]:
                    data.append(np.imag(d))
                    column_names.append(str(name)+" im")
            else:
                if "abs" in axis["axes"]:
                    data.append(np.abs(d))
                    column_names.append(str(name)+" abs")
                if "deg" in axis["axes"]:
                    data.append(np.angle(d, deg=True))
                    column_names.append(str(name)+" deg")
                if "db" in axis["axes"]:
                    data.append(20 * np.log10(np.abs(d)))
                    column_names.append(str(name)+" db")
                if "re" in axis["axes"]:
                    data.append(np.real(d))
                    column_names.append(str(name)+" re")
                if "im" in axis["axes"]:
                    data.append(np.imag(d))
                    column_names.append(str(name)+" im")


        plot_type = "2D plot"
        for name, el in model.elements.items():
            if isinstance(el, finesse.detectors.CCDScanLine) or isinstance(
                el, finesse.detectors.FieldScanLine
            ):
                # The scanline is a little weird, as it's really a beam
                # sweep, so we have to do some rearranging of the data.
                axes = [el.x, *axes]
                outfile = [[] for ax in axes]
                d = np.stack(self[name]).T
                for idx in np.ndindex(d.shape):
                    for ax, val in enumerate(idx):
                        outfile[ax].append(axes[ax][val])
                for idx, ax in enumerate(outfile):
                    outfile[idx] = np.array(ax)
                add_yaxis(el, data, np.ravel(d))
                plot_type = "3D plot"
                break

            if isinstance(el, finesse.detectors.CCDCamera) or isinstance(
                el, finesse.detectors.FieldCamera
            ):
                # Same for the camera
                # Finesse 2 seems to put a 2D beam sweep last, even if the sweeps are the
                # first two axes (see e.g. random/astigmatic_mc02.kat)
                axes = [*axes, el.x, el.y]
                outfile = [[] for ax in axes]
                d = np.stack(self[name])
                for idx in np.ndindex(d.shape):
                    for ax, val in enumerate(idx):
                        outfile[ax].append(axes[ax][val])
                for idx, ax in enumerate(outfile):
                    outfile[idx] = np.array(ax)
                for idx, point in enumerate(data):
                    data[idx] = point * np.ones(np.ravel(d).shape)
                add_yaxis(el, np.ravel(d))
                plot_type = "3D plot"
                break
            if isinstance(el, finesse.detectors.Detector):
                d = np.array(self[name]).flatten()
                add_yaxis(el, d)

        outfile.extend(data)

        return np.array(outfile).T, column_names, plot_type


    def write_legacy_data(
        self,
        model,
        filename="data.out",
        legacy_data=None,
        column_names=None,
        plot_type=None
    ):
        """Write Finesse 2 style ASCII output file

        See Also
        --------
        :meth:`.get_legacy_data`

        Parameters
        ----------
        model : :class:`.Model`
           The model used to produce this output file.

        filename : :class:`str`, optional
            The path of the output file.

        legacy_data : :class:`numpy.ndarray`, optional
            The legacy output data to be written.

        column_names : :class:`list`, optional
            The colomn names which correspond to the legacy data.

        plot_type : "2D plot" or "3D plot", optional
            String indicating if the data should represent 2D or 3D scan.

        Notes
        -----
        If any of legacy_data, column_names or plot_type are None then all three will be
        automatically computed.
        """
        from os import path
        import finesse

        filename = path.abspath(path.expanduser(filename))

        if legacy_data is None or column_names is None or plot_type is None:
            if not (legacy_data is None and column_names is None and plot_type is None):
                warn(
                    "legacy_data, column_names and plot_type are being recomputed."
                )
            legacy_data, column_names, plot_type = self.get_legacy_data(model)

        hdr = "Finesse3 "+"({})\n".format(finesse.__version__)
        hdr += str(plot_type) + "\n"
        hdr += ", ".join([_n for _n in column_names]) + "\n"
        hdr += "\n"

        np.savetxt(filename, legacy_data, header=hdr,comments=r"%")


#---------------------------------------------------------------------------------------
# Deserialisation methods
#---------------------------------------------------------------------------------------
from finesse.utilities.storage import (
    np_dtype_from_json, np_dtype_to_json,
    type_from_json, type_to_json,
    dict_to_json
)
from copy import deepcopy
import json
from finesse.utilities.storage import dump_mapping, load_mapping

def deserialize(
    args, dtype, masked, _data, detectors, _axes, _num, trace_info, axis_info
):
    """Generic deserialiser that maps a bunch of data back into an ArraySolution"""
    assert(isinstance(dtype, np.dtype))
    sol = ArraySolution(
        args[0],
        None,
        args[2],
        args[3],
        args[4],
    )
    sol.dtype = dtype
    sol.masked =  bool(masked)
    sol._data = _data
    sol.detectors = tuple(detectors)
    sol.trace_info = trace_info
    sol.axis_info = axis_info
    sol._axes = _axes
    sol._num = _num
    sol.workspaces = NULL
    sol.num_workspaces = 0
    return sol


def from_array_solution_hdf(data, parent):
    _axes = data.attrs["_axes"]
    x = tuple(data.attrs[f"x{i}"] for i in range(_axes))
    args = ( # __init__ args for ArraySolution
        data.attrs["__solution__.name"],
        parent,
        tuple(data.attrs["shape"].tolist()),
        x,
        tuple(json.loads(data.attrs["params"]))
    )
    trace_info = json.loads(data.attrs["trace_info"])
    for det in trace_info:
        trace_info[det]["detector_type"] = type_from_json(trace_info[det]["detector_type"])
        trace_info[det]["dtype"] = type_from_json(trace_info[det]["dtype"])
    dtype = np_dtype_from_json(data.attrs["dtype"])
    return deserialize(
        args,
        dtype,
        data.attrs["masked"],
        np.asarray(data["data"], dtype=dtype),
        json.loads(data.attrs["detectors"]),
        _axes,
        data.attrs["_num"],
        trace_info,
        json.loads(data.attrs["axis_info"]),
    )


def to_array_solution_hdf(sol, grp):
    def plot_info_to_json(info):
        info = deepcopy(info)
        for key in info:
            # Replace objects with string representation
            info[key]["detector_type"] = type_to_json(info[key]["detector_type"])
            info[key]["dtype"] = type_to_json(info[key]["dtype"])
        return json.dumps(info)

    grp.attrs["axis_info"] = dict_to_json(sol.axis_info)
    grp.attrs["trace_info"] = plot_info_to_json(sol.trace_info)
    grp.attrs["dtype"] = np_dtype_to_json(sol.dtype)
    grp.attrs["masked"] = sol.masked
    grp.attrs["shape"] = sol.shape
    grp.attrs["detectors"] = json.dumps(sol.detectors)
    grp.attrs["params"] = json.dumps(sol.params)
    for i in range(sol._axes):
        grp.attrs[f"x{i}"] = sol.x[i]
    grp.attrs["_num"] = sol._num
    grp.attrs["_axes"] = sol._axes
    grp.create_dataset("data", data=sol.data)

# Set that this type should use these load/dump methods
dump_mapping[ArraySolution] = to_array_solution_hdf
load_mapping[ArraySolution] = from_array_solution_hdf
#---------------------------------------------------------------------------------------
