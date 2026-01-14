"""Collection of Actions that deal linear time invariant (LTI) modelling tasks."""

from finesse.analysis.runners import (
    run_fsig_sweep,
    run_fsig_sweep2,
    run_fsig_sweep3,
    run_fsig_sweep4,
)
from finesse.solutions import BaseSolution
from finesse.components import DegreeOfFreedom
from finesse.analysis.actions.base import Action, names_to_nodes
import numpy as np
import logging

from finesse.components.node import NodeType
from finesse.exceptions import FinesseException
import collections.abc
from finesse.utilities.misc import deprecation_warning
from typing import List, Tuple

LOGGER = logging.getLogger(__name__)


class FrequencyResponseSolution(BaseSolution):
    """A solution from running a :class:`.FrequencyResponse` action on a model. This
    solution contains the frequency vector and potentially multiple input and output
    transfer function matrix.

    Attributes
    ----------
    f : array_like
        Frequency vector [Hz]
    inputs : array_like
        The input names injected into for this analysis
    outputs : array_like
        The output names read out for this analysis
    out : arrray_like[dtype=np.complex128]
        A matrix of transfer functions for each input to every output over the
        array of frequencies requested. Depending on which frequency response
        action was run will decide what shape this output matrix actually is.
        The shape of out is dependent on the analysis done:

            - FrequencyResponse - (N_f, N_outputs, N_inputs)
            - FrequencyResponse2 - (N_f, N_outputs, N_inputs, N_hom)
            - FrequencyResponse3 - (N_f, N_outputs, N_inputs, N_hom, N_hom)
            - FrequencyResponse4 - (N_f, N_outputs, N_inputs, N_hom)
    type : type
        Type of FrequencyResponse that was used to generate this solution

    Examples
    --------
    Note that the name indexing below is only available when used with the
    :class:`.FrequencyResponse` action, the other frequency-response actions
    must be accessed using the `out` attribute.

    Results from a `FrequencyResponseSolution` can be retrieved in two ways, first
    through the `FrequencyResponseSolution.out` array or by name using
    `[outputs, inputs]`. As an example we will create a fake solution:

    >>> from finesse.analysis.actions.lti import FrequencyResponseSolution
    >>> sol = FrequencyResponseSolution("name")
    >>> sol.inputs = ("A", "B", "C")
    >>> sol.outputs = ("D", "E", "F", "G")
    >>> sol.out = np.random.rand(3, len(sol.outputs), len(sol.inputs))

    The names will map to those provided in the `FrequencyResponse` action you
    called to generate the solution.

    The following will work to select single transfer functions between some input
    and output by name:

    >>> sol["D", "A"] # Select A -> D
    >>> sol["D", "C"] # Select C -> D
    >>> sol["F", "C"] # Select C -> F

    Transfer function matrices can be extracted by providing multiple

    >>> sol["F", ("C", "A")]
    >>> sol[("F", "G"), ("C", "A")]

    Slicing can also be used:

    >>> sol["D", :]   # Select all inputs to "D"
    >>> sol["D", ::2] # Select every other input to "D"
    >>> sol[:, "B"]   # Select "B" to all outputs
    >>> sol[1:, "B"]  # Select "B" to all but the first output
    """

    def outputs_inputs_indices(
        self, outputs: List[str], inputs: List[str], *, reversed: bool = False
    ) -> Tuple[int, int]:
        """Returns the indices to use for selecting certain inputs and outputs from the
        `out` attribute of this solution object.

        Parameters
        ----------
        outputs : List[str]
            List of names of outputs, see `outputs` attribute for options
        inputs : List[str]
            List of names of inputs, see `inputs` attribute for options
        reversed : bool, optional
            Should not be used by the user, this is an internal flag used for
            checking if the reverse case should be tried, ie. inputs specified
            first rather than outputs. This is for backwards compatibility
            before FrequencyResponse was fixed.

        Returns
        -------
        output_index, input_index
            Indices for the outputs and inputs

        Raises
        ------
        KeyError
            Raised when no input or output name can be found.
        """
        out_idx = []
        inp_idx = []

        try:
            out_keys = outputs
            inp_keys = inputs
            out_keys = np.atleast_1d(out_keys)
            inp_keys = np.atleast_1d(inp_keys)

            if type(out_keys) is slice:
                out_idx = out_keys  # just use the slice provided
            else:
                for out_key in out_keys:
                    if isinstance(out_key, slice):
                        out_idx.append(out_key)
                    elif out_key not in self.outputs:
                        raise KeyError(
                            f"This solution does not have an output called '{out_key} {type(out_key)}'. Allowable OUTPUTS={self.outputs}"
                        )
                    else:
                        out_idx.append(self.outputs.index(out_key))
                # single element doesn't need to be an iterable
                if len(out_idx) == 1:
                    out_idx = out_idx[0]

            if type(inp_keys) is slice:
                inp_idx = inp_keys  # just use the slice provided
            else:
                for inp_key in inp_keys:
                    if isinstance(inp_key, slice):
                        inp_idx.append(inp_key)
                    elif inp_key not in self.inputs:
                        raise KeyError(
                            f"This solution does not have an input called '{inp_key} {type(inp_key)}'. Allowable INPUTS={self.inputs}"
                        )
                    else:
                        inp_idx.append(self.inputs.index(inp_key))
                # single element doesn't need to be an iterable
                if len(inp_idx) == 1:
                    inp_idx = inp_idx[0]

            slices = out_idx, inp_idx
            return slices

        except KeyError as ex:
            if reversed:
                return None  # we're trying the reverse, don't keep trying

            # Try and get the transpose [input, output]. eventually this should
            # be deprecated
            result = self.outputs_inputs_indices(inputs, outputs, reversed=True)
            if result is None:
                raise ex  # If the reversed failed then re-raise original exception
            else:
                deprecation_warning(
                    "FrequencyResponseSolution has changed to use [output, input], you seemed to have used [input, output] so returning that.",
                    "3.0",
                )
            return result

    def __getitem__(self, key, *, reversed=False):
        if isinstance(key, str) and self.name == key:
            return self
        elif (
            isinstance(key, (str, bytes))
            or not isinstance(key, collections.abc.Iterable)
            or len(key) != 2
        ):
            raise KeyError(
                """Provide 2 keys [output, input] to select a transfer function
                for indexing this FrequencyResponseSolution, if you want to
                select all of one input or output use a color `:`. Otherwise use the
                `out` attribute to access the underlying data. Shape of `out` is:
                - FrequencyResponse - (N_f, N_outputs, N_inputs)
                - FrequencyResponse2 - (N_f, N_outputs, N_inputs, N_hom)
                - FrequencyResponse3 - (N_f, N_outputs, N_inputs, N_hom, N_hom)
                - FrequencyResponse4 - (N_f, N_outputs, N_inputs, N_hom)
                """
            )
        else:
            o_idx, i_idx = self.outputs_inputs_indices(key[0], key[1])
            return self.out[slice(None), o_idx, i_idx]

    def plot_inputs(self, *inputs, axs=None, max_width=12, show_unity=False, **kwargs):
        """Plot all transfer functions on a NxM grid with a max_width.

        Parameters
        ----------
        inputs*,
            Names of inputs for each subplot
        axs : _type_, optional
            Matplotlib axes to draw on
        max_width : int, optional
            Maximum number of subplots in width
        show_unity : bool, optional
            Plot a line where unity is

        Returns
        -------
        figure, axes
            Matplotlib figure and axes to plot on
        """

        import matplotlib.pyplot as plt
        import numpy as np

        if "show" in kwargs:
            del kwargs["show"]

        if len(inputs) == 0:
            inputs = self.inputs

        inputs = np.atleast_1d(inputs)

        if axs is None:
            # if no axes are given then grab the figure
            # and any axes that are in it
            fig = plt.gcf()
            axs = np.atleast_2d(fig.axes)
        else:
            axs = np.atleast_2d(axs)
            fig = axs[0, 0].figure()

        N = len(inputs)
        W = min(5, max_width / N)
        if np.prod(axs.shape) != N:
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )

        if "label" not in kwargs:
            kwargs["label"] = self.outputs

        for i, input in enumerate(inputs):
            axs[0, i].loglog(self.f, abs(self[:, input]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(input)
            axs[0, i].legend()
            if show_unity:
                axs[0, i].hlines(
                    1, min(self.f), max(self.f), color="k", ls=":", zorder=-10
                )

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs

    plot = plot_inputs  # Default plot option

    def plot_outputs(self, *outputs, axs=None, max_width=12, **kwargs):
        """Plot all transfer functions on a NxM grid with a max_width.

        Parameters
        ----------
        outputs*,
            Names of outputs for each subplot
        axs : _type_, optional
            Matplotlib axes to draw on
        max_width : int, optional
            Maximum number of subplots in width
        show_unity : bool, optional
            Plot a line where unity is

        Returns
        -------
        figure, axes
            Matplotlib figure and axes to plot on
        """

        import matplotlib.pyplot as plt

        if len(outputs) == 0:
            outputs = self.outputs

        outputs = np.atleast_1d(outputs)

        if axs is None:
            N = len(outputs)
            W = min(5, max_width / N)
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )
        else:
            fig = plt.gcf()

        if "label" not in kwargs:
            kwargs["label"] = self.inputs

        for i, output in enumerate(outputs):
            axs[0, i].loglog(self.f, abs(self[output, :]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(output)
            axs[0, i].legend()

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse(Action):
    """Computes the frequency response of a signal injected at various nodes to compute
    transfer functions to multiple output nodes. Inputs and outputs should be electrical
    or mechanical nodes. It does this in an efficient way by using the same model and
    solving for multiple RHS input vectors.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Produces an output transfer matrix from each input node to some readout output.
    The shape of the output matrix is:

    [frequencies, inputs, outputs]

    To inject into optical nodes please see :class:`.FrequencyResponse2` and
    :class:`.FrequencyResponse3`. To readout optical nodes please see
    :class:`.FrequencyResponse3` and :class:`.FrequencyResponse4`.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[str or Element]
        Mechanical or electrical node to inject signal at
    outputs : iterable[str or Element]
        Mechanical or electrical nodes to measure output at
    open_loop : bool, optional
        Computes open loop transfer functions if the system has closed
    name : str, optional
        Solution name

    Examples
    --------
    Here we measure a set of transfer functions from DARM and CARM
    to four readouts for a particular `model`,

    >>> sol = model.run(FrequencyResponse(np.geomspace(0.1, 50000, 100),
    ...         ('DARM', 'CARM'),
    ...         ('AS.DC', 'AS45.I', 'AS45.Q', 'REFL9.I'),
    ... ))

    Single inputs and outputs can also be specified

    >>> model.run(FrequencyResponse(np.geomspace(0.1, 50000, 100), 'DARM', AS.DC'))

    The transfer functions can then be accessed like a 2D array by name,
    the ordering of inputs to outputs does not matter.

    >>> sol['DARM'] # DARM to all outputs
    >>> sol['DARM', 'AS.DC'] # DARM to AS.DC
    >>> sol['DARM', ('AS.DC', 'AS45.I')]
    >>> sol['AS.DC'] # All inputs to AS.DC readout
    """

    def __init__(
        self, f, inputs, outputs, *, open_loop=False, name="frequency_response"
    ):
        super().__init__(name)
        inputs = np.atleast_1d(inputs)
        outputs = np.atleast_1d(outputs)
        if f is None:
            raise FinesseException("A frequency vector must be provided")

        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except TypeError:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        def process(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.inputs = list(process(i, True) for i in inputs)
        self.outputs = list(process(o, False) for o in outputs)
        self.open_loop = open_loop

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_node_indices = np.zeros(len(self.inputs), dtype=np.dtype("long"))
        output_node_indices = np.zeros(len(self.outputs), dtype=np.dtype("long"))

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.inputs), dtype=float)
        output_scaling = np.ones(len(self.outputs), dtype=float)

        for i, node in enumerate(
            names_to_nodes(state.model, self.inputs, default_hints=("input",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the FrequencyResponse action"
                )
            else:
                # set scaling for mechanical input signals
                if node.type is NodeType.MECHANICAL:
                    input_scaling[i] /= state.sim.model_settings.x_scale

                input_node_indices[i] = state.sim.signal.node_id(node)

        for i, node in enumerate(
            names_to_nodes(state.model, self.outputs, default_hints=("output",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the FrequencyResponse action"
                )
            else:
                # set scaling for mechanical output signals
                if node.type is NodeType.MECHANICAL:
                    output_scaling[i] *= state.sim.model_settings.x_scale

                output_node_indices[i] = state.sim.signal.node_id(node)

        sol = FrequencyResponseSolution(self.name)
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep(
            state.sim,
            self.f,
            input_node_indices,
            output_node_indices,
            input_scaling,
            output_scaling,
            None,
            self.open_loop,
            (
                tuple(fsig_independant_outputs)
                if fsig_independant_outputs is not None
                else None
            ),
            (
                tuple(fsig_dependant_outputs)
                if fsig_dependant_outputs is not None
                else None
            ),
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["input_nodes"].extend((_, ("input",)) for _ in self.inputs)
        memo["output_nodes"].extend((_, ("output",)) for _ in self.outputs)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse2(Action):
    """Computes the frequency response of a signal injected at an optical port at a
    particular optical frequency. This differs from :class:`.FrequencyResponse` in the
    way the inputs and outputs are prescribed. For :class:`.FrequencyResponse2` you
    specify optical input nodes and a signal output node.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Produces an output transfer matrix from each HOM at a particular frequency and
    optical node to some readout output. The shape of the output matrix is:

    [frequencies, outputs, inputs, HOMs]

    It should be noted that when exciting a lower signal sideband frequency it will
    actually return the operator for propagating the conjugate of the lower sideband.
    This is because FINESSE is internally solving for the conjugate of the lower sideband
    to linearise non-linear optical effects.

    To inject into mechanical and electrical nodes please see :class:`.FrequencyResponse`
    and :class:`.FrequencyResponse4`. To readout optical nodes please see
    :class:`.FrequencyResponse3` and :class:`.FrequencyResponse4`.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to inject at. A symbolic refence to the
        model's fsig.f parameter should always be used when defining a frequency to
        look at.
    outputs : iterable[str or Element]
        Mechanical or electrical (signal)nodes to measure output to
    name : str, optional
        Solution name

    Examples
    --------
    It is advisable to use always use a reference to the symbolic reference to
    the signal frequency `model.fsig.f.ref` instead of a fixed number incase it
    changes. This action will look for an initial frequency bin of X Hz to track
    during the frequency response analysis. A symbolic reference will always
    ensure the right bin is used, in cases such as looking at RF signal sidebands,
    `10e6+model.fsig.f.ref` and `10e6-model.fsig.f.ref` will always look at the
    upper and lower signal sideband around the +10MHz sideband.

    >>> import finesse
    >>> from finesse.analysis.actions import FrequencyResponse2
    >>> model = finesse.script.parse('''
    ... l l1
    ... bs bs1 R=1 T=0 xbeta=1e-6 ybeta=1e-9
    ... readout_dc A
    ... link(l1, bs1, A)
    ... fsig(1)
    ... modes(maxtem=1)
    ... gauss g1 l1.p1.o w=1m Rc=inf
    ... ''')
    >>> sol = model.run(
    ...     FrequencyResponse2(
    ...         [1, 10, 100],
    ...         [
    ...             ('bs1.p2.o', +model.fsig.f.ref),
    ...             ('bs1.p2.o', -model.fsig.f.ref)
    ...         ],
    ...         ['A.DC']
    ...     )
    ... )
    """

    def __init__(self, f, inputs, outputs, *, name="frequency_response2"):
        super().__init__(name)

        if f is None:
            raise FinesseException("A frequency vector must be provided")
        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except TypeError:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        self.inputs = inputs
        self.outputs = outputs

        self.input_nodes = []
        self.input_freqs = []
        for node, freq in inputs:
            self.input_nodes.append(node)
            self.input_freqs.append(freq)

        self.output_nodes = []
        for node in outputs:
            self.output_nodes.append(node)

        def process_node(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.input_nodes = list(process_node(i, True) for i in self.input_nodes)
        self.output_nodes = list(process_node(o, False) for o in self.output_nodes)

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_node_indices = np.zeros(len(self.input_nodes), dtype=np.dtype("long"))
        input_freq_indices = np.zeros(len(self.input_nodes), dtype=np.dtype("long"))
        output_node_indices = np.zeros(len(self.output_nodes), dtype=np.dtype("long"))

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.input_nodes), dtype=float)
        output_scaling = np.ones(len(self.output_nodes), dtype=float)

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(state.model, self.input_nodes, default_hints=("input",)),
                self.input_freqs,
            )
        ):
            freq_obj = state.sim.signal.get_frequency_object(freq, node)
            input_freq_indices[i] = freq_obj.index

            if node.type is NodeType.OPTICAL:
                input_node_indices[i] = state.sim.signal.node_id(node)
            else:
                if input_freq_indices[i] != 0:
                    raise FinesseException(
                        f"Input frequency for {node} should be the signal frequency"
                    )
                # set scaling for mechanical input signals
                if node.type is NodeType.MECHANICAL:
                    input_scaling[i] /= state.sim.model_settings.x_scale
                input_node_indices[i] = state.sim.signal.node_id(node)

        for i, node in enumerate(
            names_to_nodes(state.model, self.output_nodes, default_hints=("output",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the FrequencyResponse2 action"
                )
            else:
                # set scaling for mechanical output signals
                if node.type is NodeType.MECHANICAL:
                    output_scaling[i] *= state.sim.model_settings.x_scale
                output_node_indices[i] = state.sim.signal.node_id(node)

        sol = FrequencyResponseSolution(self.name)
        sol.type = FrequencyResponse2
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep2(
            state.sim,
            self.f,
            input_node_indices,
            input_freq_indices,
            output_node_indices,
            input_scaling,
            output_scaling,
            None,
            (
                tuple(fsig_independant_outputs)
                if fsig_independant_outputs is not None
                else None
            ),
            (
                tuple(fsig_dependant_outputs)
                if fsig_dependant_outputs is not None
                else None
            ),
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        for freq in self.input_freqs:
            try:
                if model.fsig.f.ref not in freq.parameters():
                    raise IndexError()
            except (AttributeError, IndexError):  # catch if freq not a symbol
                raise FinesseException(
                    f"{self} requires frequencies to be specified as a symbolic expression which must include `model.fsig.f.ref`, not {freq}."
                )

        memo["changing_parameters"].append("fsig.f")
        memo["input_nodes"].extend((_, ("input",)) for _ in self.input_nodes)
        memo["output_nodes"].extend((_, ("output",)) for _ in self.output_nodes)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse3(Action):
    """Computes the frequency response of a signal injected at an optical port at a
    particular optical frequency. This differs from :class:`.FrequencyResponse` in the
    way the inputs and outputs are prescribed. For :class:`.FrequencyResponse3` you
    specify optical input nodes and optical output nodes.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Produces an output transfer matrix from each HOM at a particular frequency and
    optical node to some other optical node and frequency. The shape of the output
    matrix is:

    [frequencies, outputs, inputs, HOMs, HOMs]

    It should be noted that when exciting a lower signal sideband frequency it will
    actually return the operator for propagating the conjugate of the lower sideband.
    This is because FINESSE is internally solving for the conjugate of the lower sideband
    to linearise non-linear optical effects.

    To inject into mechanical and electrical nodes please see :class:`.FrequencyResponse`
    and :class:`.FrequencyResponse4`. To readout mechanical and electrical nodes
    please see :class:`.FrequencyResponse` and :class:`.FrequencyResponse2`.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to inject at. A symbolic reference to the
        model's fsig.f parameter should always be used when defining a frequency to
        look at.
    outputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to measure output at. A symbolic reference to the
        model's fsig.f parameter should always be used when defining a frequency to
        look at.
    name : str, optional
        Solution name

    Examples
    --------
    It is advisable to use always use a reference to the symbolic reference to
    the signal frequency `model.fsig.f.ref` instead of a fixed number incase it
    changes. This action will look for an initial frequency bin of X Hz to track
    during the frequency response analysis. A symbolic reference will always
    ensure the right bin is used, in cases such as looking at RF signal sidebands,
    `10e6+model.fsig.f.ref` and `10e6-model.fsig.f.ref` will always look at the
    upper and lower signal sideband around the +10MHz sideband.

    >>> import finesse
    >>> from finesse.analysis.actions import FrequencyResponse3
    >>> model = finesse.script.parse('''
    ... l l1
    ... bs bs1 R=1 T=0 xbeta=1e-6 ybeta=1e-9
    ... readout_dc A
    ... link(l1, bs1, A)
    ... fsig(1)
    ... modes(maxtem=1)
    ... gauss g1 l1.p1.o w=1m Rc=inf
    ... ''')
    >>> sol = model.run(
    ...     FrequencyResponse3(
    ...         [1, 10, 100],
    ...         [
    ...             ('bs1.p2.o', +model.fsig.f.ref),
    ...             ('bs1.p2.o', -model.fsig.f.ref)
    ...         ],
    ...         [
    ...             ('A.p1.i', +model.fsig.f.ref),
    ...             ('A.p1.i', -model.fsig.f.ref)
    ...         ]
    ...     )
    ... )
    """

    def __init__(self, f, inputs, outputs, *, name="frequency_response3"):
        super().__init__(name)

        if f is None:
            raise FinesseException("A frequency vector must be provided")
        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except TypeError:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        self.inputs = inputs
        self.outputs = outputs

        self.input_nodes = []
        self.input_freqs = []
        for node, freq in inputs:
            self.input_nodes.append(node)
            self.input_freqs.append(freq)

        self.output_nodes = []
        self.output_freqs = []
        for node, freq in outputs:
            self.output_nodes.append(node)
            self.output_freqs.append(freq)

        def process_node(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.input_nodes = list(process_node(i, True) for i in self.input_nodes)
        self.output_nodes = list(process_node(o, False) for o in self.output_nodes)

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_node_indices = np.zeros(len(self.input_nodes), dtype=np.dtype("long"))
        input_freq_indices = np.zeros(len(self.input_nodes), dtype=np.dtype("long"))
        output_node_indices = np.zeros(len(self.output_nodes), dtype=np.dtype("long"))
        output_freq_indices = np.zeros(len(self.output_nodes), dtype=np.dtype("long"))

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.input_nodes), dtype=float)
        output_scaling = np.ones(len(self.output_nodes), dtype=float)

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(state.model, self.input_nodes, default_hints=("input",)),
                self.input_freqs,
            )
        ):
            if node.type is NodeType.OPTICAL:
                freq_obj = state.sim.signal.get_frequency_object(freq, node)
                input_freq_indices[i] = freq_obj.index
                input_node_indices[i] = state.sim.signal.node_id(node)
            else:
                raise FinesseException(
                    f"Optical nodes ({node}) must be used with the FrequencyResponse3 action"
                )

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(
                    state.model, self.output_nodes, default_hints=("output",)
                ),
                self.output_freqs,
            )
        ):
            if node.type is NodeType.OPTICAL:
                freq_obj = state.sim.signal.get_frequency_object(freq, node)
                output_freq_indices[i] = freq_obj.index
                output_node_indices[i] = state.sim.signal.node_id(node)
            else:
                raise FinesseException(
                    f"Optical nodes ({node}) must be used with the FrequencyResponse3 action"
                )

        sol = FrequencyResponseSolution(self.name)
        sol.type = FrequencyResponse3
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep3(
            state.sim,
            self.f,
            input_node_indices,
            input_freq_indices,
            output_node_indices,
            output_freq_indices,
            input_scaling,
            output_scaling,
            None,
            (
                tuple(fsig_independant_outputs)
                if fsig_independant_outputs is not None
                else None
            ),
            (
                tuple(fsig_dependant_outputs)
                if fsig_dependant_outputs is not None
                else None
            ),
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        for flist in [self.input_freqs, self.output_freqs]:
            for freq in flist:
                try:
                    if model.fsig.f.ref not in freq.parameters():
                        raise IndexError()
                except (AttributeError, IndexError):  # catch if freq not a symbol
                    raise FinesseException(
                        f"{self} requires frequencies to be specified as a symbolic expression which must include `model.fsig.f.ref`, not {repr(freq)}."
                    )

        memo["changing_parameters"].append("fsig.f")
        memo["input_nodes"].extend((_, ("input",)) for _ in self.input_nodes)
        memo["output_nodes"].extend((_, ("output",)) for _ in self.output_nodes)


class FrequencyResponse4(Action):
    """Computes the frequency response of a signal injected at an electrical or
    mechanical port. This differs from :class:`.FrequencyResponse` in the way the inputs
    and outputs are prescribed. For :class:`.FrequencyResponse4` you specify signal
    input nodes and optical output nodes.

    This action does not alter the model state. This action will ignore any currently
    defined signal generator elements in the model.

    Produces an output transfer matrix from each signal node to each HOM at a
    particular frequency and optical node. The shape of the output
    matrix is:

    [frequencies, outputs, inputs, HOMs]

    It should be noted that when exciting a lower signal sideband frequency it will
    actually return the operator for propagating the conjugate of the lower sideband.
    This is because FINESSE is internally solving for the conjugate of the lower sideband
    to linearise non-linear optical effects.

    To inject into optical nodes please see :class:`.FrequencyResponse2` and
    :class:`.FrequencyResponse3`. To readout mechanical and electrical nodes
    please see :class:`.FrequencyResponse` and :class:`.FrequencyResponse2`.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[str or Element]
        Mechanical or electrical node to inject signal at
    outputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to measure output at. A symbolic reference to the
        model's fsig.f parameter should always be used when defining a frequency to
        look at.
    name : str, optional
        Solution name

    Examples
    --------
    It is advisable to use always use a reference to the symbolic reference to
    the signal frequency `model.fsig.f.ref` instead of a fixed number incase it
    changes. This action will look for an initial frequency bin of X Hz to track
    during the frequency response analysis. A symbolic reference will always
    ensure the right bin is used, in cases such as looking at RF signal sidebands,
    `10e6+model.fsig.f.ref` and `10e6-model.fsig.f.ref` will always look at the
    upper and lower signal sideband around the +10MHz sideband.

    >>> sol = model.run(
    ...     FrequencyResponse(
    ...         [1, 10, 100],
    ...         [model.ETM.mech.z],
    ...         [
    ...             (model.ITM.p2.o, +model.fsig.f.ref),
    ...             (model.ITM.p2.o, -model.fsig.f.ref)
    ...         ]
    ...     )
    ... )
    """

    def __init__(self, f, inputs, outputs, *, name="frequency_response4"):
        super().__init__(name)

        if f is None:
            raise FinesseException("A frequency vector must be provided")
        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except TypeError:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                f"Frequency vector: {f} must contain values greater than 0"
            )

        self.inputs = inputs
        self.outputs = outputs

        self.input_nodes = []
        for node in inputs:
            self.input_nodes.append(node)

        self.output_nodes = []
        self.output_freqs = []
        for node, freq in outputs:
            self.output_nodes.append(node)
            self.output_freqs.append(freq)

        def process_node(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.input_nodes = list(process_node(i, True) for i in self.input_nodes)
        self.output_nodes = list(process_node(o, False) for o in self.output_nodes)

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_node_indices = np.zeros(len(self.input_nodes), dtype=np.dtype("long"))
        output_node_indices = np.zeros(len(self.output_nodes), dtype=np.dtype("long"))
        output_freq_indices = np.zeros(len(self.output_nodes), dtype=np.dtype("long"))

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.input_nodes), dtype=float)
        output_scaling = np.ones(len(self.output_nodes), dtype=float)

        for i, node in enumerate(
            names_to_nodes(state.model, self.inputs, default_hints=("input",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"This optical node ({node}) cannot be used with the FrequencyResponse4 action make sure you're using the correct input and outputs."
                )
            else:
                # set scaling for mechanical input signals
                if node.type is NodeType.MECHANICAL:
                    input_scaling[i] /= state.sim.model_settings.x_scale

                input_node_indices[i] = state.sim.signal.node_id(node)

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(
                    state.model, self.output_nodes, default_hints=("output",)
                ),
                self.output_freqs,
            )
        ):
            if node.type is NodeType.OPTICAL:
                freq_obj = state.sim.signal.get_frequency_object(freq, node)
                output_freq_indices[i] = freq_obj.index
                output_node_indices[i] = state.sim.signal.node_id(node)
            else:
                raise FinesseException(
                    f"Optical nodes ({node}) must be used with the FrequencyResponse4 action"
                )

        sol = FrequencyResponseSolution(self.name)
        sol.type = FrequencyResponse4
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep4(
            state.sim,
            self.f,
            input_node_indices,
            output_node_indices,
            output_freq_indices,
            input_scaling,
            output_scaling,
            None,
            (
                tuple(fsig_independant_outputs)
                if fsig_independant_outputs is not None
                else None
            ),
            (
                tuple(fsig_dependant_outputs)
                if fsig_dependant_outputs is not None
                else None
            ),
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        for freq in self.output_freqs:
            try:
                if model.fsig.f.ref not in freq.parameters():
                    raise IndexError()
            except (AttributeError, IndexError):  # catch if freq not a symbol
                raise FinesseException(
                    f"{self} requires frequencies to be specified as a symbolic expression which must include `model.fsig.f.ref`, not {repr(freq)}."
                )

        memo["changing_parameters"].append("fsig.f")
        memo["input_nodes"].extend((_, ("input",)) for _ in self.input_nodes)
        memo["output_nodes"].extend((_, ("output",)) for _ in self.output_nodes)
