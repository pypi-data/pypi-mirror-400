

import logging

cimport numpy as np
import numpy as np
import cython
from libc.stdlib cimport free, calloc
from cpython.ref cimport PyObject
from finesse.cymath cimport complex_t
import finesse
from finesse.parameter cimport Parameter
from finesse.simulations.sparse.simulation cimport BaseSimulation
from finesse.simulations.homsolver cimport HOMSolver
from finesse.solutions.array import ArraySolution
from finesse.solutions.array cimport ArraySolution
from finesse.detectors.workspace import DetectorWorkspace
from finesse.detectors.workspace cimport DetectorWorkspace

from tqdm.auto import tqdm

LOGGER = logging.getLogger(__name__)


ctypedef object (*fptr_callback)(BaseSimulation)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep(
        BaseSimulation sim,
        double[::1] axis,
        long[::1] input_node_indices,
        long[::1] output_node_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, ::1] out,
        bint compute_open_loop,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ):
    """Runs a simulation to sweep over a signal frequency axis. It does this in an
    optimised way for multiple inputs and outputs. It does not use detectors to
    compute outputs, it will just solve the matrix and return transfer functions
    between nodes. This is so it can be used internally for computing TFs without
    need to add detectors everywhere which the user has not specified.

    Parameters
    ----------
    sim : BaseSimulation
        The simulation object.
    axis : numpy.ndarray
        The signal frequency axis.
    input_node_indices : numpy.ndarray
        The indices of the input nodes.
    output_node_indices : numpy.ndarray
        The indices of the output nodes.
    input_scaling : numpy.ndarray
        The scaling factors for the input nodes.
    output_scaling : numpy.ndarray
        The scaling factors for the output nodes.
    out : numpy.ndarray
        The output array to store the transfer functions.
    compute_open_loop : bool
        A flag indicating whether to compute open loop transfer functions.
    fsig_independant_outputs : tuple, optional
        A tuple of fsig independent outputs.
    fsig_dependant_outputs : tuple, optional
        A tuple of fsig dependent outputs.

    Returns
    -------
    out : numpy.ndarray
        The transfer functions between nodes.
    other_outputs : dict, optional
        A dictionary of other outputs if fsig independent or dependent outputs are provided.
    """
    cdef:
        HOMSolver signal = sim.signal
        int Na = len(axis)
        int Ni = len(input_node_indices)
        int No = len(output_node_indices)
        int i, o, j
        complex_t denom
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    for i in range(Ni):
        if not (0 <= input_node_indices[i] < signal.num_nodes):
            raise Exception(f"Input node index error: 0 <= {input_node_indices[i]} < {signal.num_nodes}")
    for o in range(No):
        if not (0 <= output_node_indices[o] < signal.num_nodes):
            raise Exception(f"Output node index error: 0 <= {output_node_indices[o]} < {signal.num_nodes}")

    if out is None:
        out = np.zeros((Na, No, Ni), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Na)
        assert(out.shape[1] == No)
        assert(out.shape[2] == Ni)

    if (fsig_independant_outputs is not None) or (fsig_dependant_outputs is not None):
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            signal.clear_rhs()
            signal.set_source_fast(
                input_node_indices[i], 0, 0, input_scaling[i], 0
            )
            signal.solve()
            if not compute_open_loop:
                signal.get_out_fast
                for o in range(No):
                    out[j][o][i] = signal.get_out_fast(output_node_indices[o], 0, 0)

                    # scale output
                    out[j][o][i] = out[j][o][i] * output_scaling[o]
            else:
                for o in range(No):
                    out[j][o][i] = signal.get_out_fast(output_node_indices[o], 0, 0)

                    if input_node_indices[i] == output_node_indices[o]:
                        out[j][o][i] = out[j][o][i] - 1 # remove injected signal
                        out[j][o][i] = out[j][o][i]/(1+out[j][o][i])
                    else:
                        # We can divide out the 1/(1-H) closed loop behaviours by
                        # using the coupling computed back into the same input node
                        denom = signal.get_out_fast(input_node_indices[i], 0, 0) / input_scaling[i]
                        if denom.real == denom.imag == 0:
                            out[j][o][i] = 0
                        else:
                            out[j][o][i] = out[j][o][i] / denom

                    # scale output
                    out[j][o][i] = out[j][o][i] * output_scaling[o]

    signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep2(
        BaseSimulation sim,
        double[::1] axis,
        long[::1] input_node_indices,
        long[::1] input_freq_indices,
        long[::1] output_node_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, :, ::1] out,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ):
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.

    `run_fsig_sweep2` differs to `run_fsig_sweep` in that the inputs should be
    optical nodes. The transfer functions from each HOM at the input to every
    output will then be calculated. Outputs should be some readout signal nodes.

    Transfer functions for lower audio sides must be requested to conjugate, as
    internally the conjugate of the lower is solved for.

    Returns
    -------
    transfer_functions : array_like
        shape of (frequencies, outputs, inputs, HOMs)
    """
    cdef:
        HOMSolver signal = sim.signal
        int Nm = signal.nhoms
        int Na = len(axis)
        int Ni = len(input_node_indices)
        int No = len(output_node_indices)
        int i, o, j, k
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if len(input_node_indices) != len(input_freq_indices):
        raise Exception("input node and frequency indices should be the same length")

    for i in range(Ni):
        if not (0 <= input_node_indices[i] < signal.num_nodes):
            raise Exception(f"Input node index error: 0 <= {input_node_indices[i]} < {signal.num_nodes}")
        if not (0 <= input_freq_indices[i] < signal.optical_frequencies.size):
            raise Exception(f"Input frequency index error: 0 <= {input_freq_indices[i]} < {signal.optical_frequencies.size}")

    for o in range(No):
        if not (0 <= output_node_indices[o] < signal.num_nodes):
            raise Exception(f"Output node index error: 0 <= {output_node_indices[o]} < {signal.num_nodes}")

    if out is None:
        out = np.zeros((Na, No, Ni, Nm), dtype=np.complex128)
        cast_out = True
    else:
        assert out.shape[0] == Ni
        assert out.shape[1] == Na
        assert out.shape[2] == No
        assert out.shape[3] == Nm

    if (fsig_independant_outputs is not None) or (fsig_dependant_outputs is not None):
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            for k in range(Nm):
                signal.clear_rhs()
                # Loop over each mode at this node
                signal.set_source_fast(
                    input_node_indices[i], input_freq_indices[i], k, input_scaling[i], 0,
                )
                signal.solve()
                for o in range(No):
                    out[j][o][i][k] = signal.get_out_fast(output_node_indices[o], 0, 0)
                    # scale output
                    out[j][o][i][k] = out[j][o][i][k] * output_scaling[o]

    out *= np.sqrt(2) # normalise for the correct amplitude
    signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep3(
        BaseSimulation sim,
        double[::1] axis,
        long[::1] input_node_indices,
        long[::1] input_freq_indices,
        long[::1] output_node_indices,
        long[::1] output_freq_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, :, :, ::1] out,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ) :
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.

    `run_fsig_sweep3` differs to `run_fsig_sweep` in that the input and output nodes
    should be optical nodes. The transfer functions from each HOM at the input to every
    output will then be calculated.

    Transfer functions for lower audio sides must be requested to conjugate, as
    internally the conjugate of the lower is solved for.

    Returns
    -------
    transfer_functions : array_like
        shape of (frequencies, outputs, inputs, HOMs, HOMs)
    """
    cdef:
        HOMSolver signal = sim.signal
        int Nm = signal.nhoms
        int Na = len(axis)
        int Ni = len(input_node_indices)
        int No = len(output_node_indices)
        int i, o, j, k, l
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if len(input_node_indices) != len(input_freq_indices):
        raise Exception("Input node and frequency indices should be the same length")
    if len(output_node_indices) != len(output_freq_indices):
        raise Exception("Output node and frequency indices should be the same length")

    for i in range(Ni):
        if not (0 <= input_node_indices[i] < signal.num_nodes):
            raise Exception(f"Input node index error: 0 <= {input_node_indices[i]} < {signal.num_nodes}")
        if not (0 <= input_freq_indices[i] < signal.optical_frequencies.size):
            raise Exception(f"Input frequency index error: 0 <= {input_freq_indices[i]} < {signal.optical_frequencies.size}")

    for o in range(No):
        if not (0 <= output_node_indices[o] < signal.num_nodes):
            raise Exception(f"Output node index error: 0 <= {output_node_indices[o]} < {signal.num_nodes}")
        if not (0 <= output_freq_indices[o] < signal.optical_frequencies.size):
            raise Exception(f"Output frequency index error: 0 <= {output_freq_indices[i]} < {signal.optical_frequencies.size}")

    if out is None:
        out = np.zeros((Na, No, Ni, Nm, Nm), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Na)
        assert(out.shape[1] == No)
        assert(out.shape[2] == Ni)
        assert(out.shape[3] == Nm) # output nodes
        assert(out.shape[4] == Nm) # input nodes

    if (fsig_independant_outputs is not None) or (fsig_dependant_outputs is not None):
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            for k in range(Nm):
                signal.clear_rhs()
                # Loop over each mode at this node
                signal.set_source_fast(
                    input_node_indices[i], input_freq_indices[i], k, 1 * input_scaling[i], 0
                )
                signal.solve()
                for o in range(No):
                    for l in range(Nm):
                        # select output mode and scale output
                        out[j][o][i][l][k] = signal.get_out_fast(output_node_indices[o], output_freq_indices[o], l) * output_scaling[o]

    signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep4(
        BaseSimulation sim,
        double[::1] axis,
        long[::1] input_node_indices,
        long[::1] output_node_indices,
        long[::1] output_freq_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, :, ::1] out,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ):
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.

    `run_fsig_sweep4` differs to `run_fsig_sweep` in that the input nodes are signal nodes
    and output nodes should be optical nodes. The transfer functions from each HOM at the
    input to every output will then be calculated.

    Transfer functions for lower audio sides must be requested to conjugate, as
    internally the conjugate of the lower is solved for.

    Returns
    -------
    transfer_functions : array_like
        shape of (frequencies, outputs, inputs, HOMs)
    """
    cdef:
        HOMSolver signal = sim.signal
        int Nm = signal.nhoms
        int Na = len(axis)
        int Ni = len(input_node_indices)
        int No = len(output_node_indices)
        int i, o, j, k
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if len(output_node_indices) != len(output_freq_indices):
        raise Exception("Output node and frequency indices should be the same length")

    for o in range(No):
        if not (0 <= output_node_indices[o] < signal.num_nodes):
            raise Exception(f"Output node index error: 0 <= {output_node_indices[o]} < {signal.num_nodes}")
        if not (0 <= output_freq_indices[o] < signal.optical_frequencies.size):
            raise Exception(f"Output frequency index error: 0 <= {output_freq_indices[o]} < {signal.optical_frequencies.size}")

    if out is None:
        out = np.zeros((Na, No, Ni, Nm), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Na)
        assert(out.shape[1] == No)
        assert(out.shape[2] == Ni)
        assert(out.shape[3] == Nm)

    if (fsig_independant_outputs is not None) or (fsig_dependant_outputs is not None):
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            signal.clear_rhs()
            signal.set_source_fast(
                input_node_indices[i], 0, 0, input_scaling[i], 0
            )
            signal.solve()
            for o in range(No):
                # Loop over each mode at this node
                for k in range(Nm):
                    # select output mode and scale output
                    out[j][o][i][k] = signal.get_out_fast(output_node_indices[o], output_freq_indices[o], k) * output_scaling[o]

    out /= np.sqrt(2) # normalise for the correct amplitude
    signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
def run_axes_scan(
        object state,
        tuple axes,
        tuple params,
        double[:] offsets,
        tuple out_shape,
        ArraySolution solution,
        object pre_step,
        object post_step,
        bint progress_bar = False,
        str progress_bar_desc = ""
    ):
    cdef:
        BaseSimulation sim = state.sim
        int Np = len(params)
        int No = len(offsets)
        int Na = len(axes)
        int Nos = len(out_shape)
        int i, step
        np.ndarray[double, ndim=1, mode="c"] narr
        double** ptr_axes = NULL
        int* ptr_axes_len = NULL
        PyObject** ptr_params = NULL
        bint mask_this_point = False
        int[::1] IDX = np.zeros(Nos, dtype=np.int32)
        int Ntot

        Parameter param

    if(not (Np == No == Na == Nos)):
        raise Exception("Param, offsets, axes, and out_shape lengths are not the same")

    for p in params:
        if p.datatype not in (float, np.float64):
            raise Exception(f"Can only vary parameters with datatype float, not {p.full_name} with {p.datatype}")

    try:
        # Can't have a memory view of typed ndarray apparently.
        # So here we check the axes are double c-continuous and
        # then save the double pointer
        ptr_axes = <double**> calloc(Na, sizeof(double*))
        if not ptr_axes:
            raise MemoryError()

        ptr_axes_len = <int*> calloc(Na, sizeof(int))
        if not ptr_axes_len:
            raise MemoryError()

        for i in range(Na):
            narr = <np.ndarray[double, ndim=1, mode="c"]?> axes[i]
            if narr.size != out_shape[i]:
                raise Exception(f"Out shape[{i}]={out_shape[i]} is not the correct size for the axes[i]={narr.size}")

            ptr_axes[i] = &narr[0]
            ptr_axes_len[i] = narr.size

        # Then to get around some annoying python referencing and issues
        # with accessing cdefs of extension types in a memory view we
        # make an array of PyObjects
        ptr_params = <PyObject**> calloc(Np, sizeof(PyObject*))
        if not ptr_params:
            raise MemoryError()
        for i in range(Np):
            ptr_params[i] = <PyObject*>(<Parameter?>params[i])

        Ntot = np.prod(out_shape)

        if progress_bar:
            pbar = tqdm(range(Ntot), leave=False, desc=progress_bar_desc, disable=not finesse.config.show_progress_bars)
        else:
            pbar = None

        # Now iterate over the all the axes
        #for step in range(Ntot):
        #for idx in np.ndindex(*out_shape):
        for step in range(Ntot):
            for i in range(Np):
                (<Parameter>ptr_params[i]).set_double_value(ptr_axes[i][IDX[i]] + offsets[i])
            # ------------------------------------------------------
            # PRE STEP
            # ------------------------------------------------------
            if pre_step is not None:
                pre_step._do(state)
            # ------------------------------------------------------
            # DO STEP
            # ------------------------------------------------------
            mask_this_point = not sim.run_carrier()

            if not mask_this_point and sim.signal is not None:
                sim.run_signal()

            if progress_bar:
                pbar.update()
            # ------------------------------------------------------
            # POST STEP
            # ------------------------------------------------------
            if mask_this_point:
                values_str = ""
                for i in range(Np):
                    param = <Parameter>ptr_params[i]
                    if param.__units is not None:
                        param_units = " " + param.__units
                    else:
                        param_units = ""

                    values_str += (
                        param.__full_name
                        + " = "
                        + str(ptr_axes[i][IDX[i]] + offsets[i])
                        + param_units
                    )
                    if i != Np - 1:
                        values_str += ", "

                LOGGER.error("Masking simulation outputs at: %s", values_str)

            if solution.update(step, mask_this_point) == -1:
                raise RuntimeError("Exception calling solution update")

            if post_step is not None:
                post_step._do(state)

            # ------------------------------------------------------

            # Increment the index vector
            for i in range(No):
                i = Nos-i-1
                IDX[i] += 1
                if IDX[i] >= ptr_axes_len[i]:
                    IDX[i] = 0
                else:
                    break

    finally:
        # This forces pbar to show, even when leave=False
        if progress_bar:
            pbar.refresh()
            pbar.close()
        if ptr_axes != NULL: free(ptr_axes)
        if ptr_axes_len != NULL: free(ptr_axes_len)
        if ptr_params != NULL: free(ptr_params)
