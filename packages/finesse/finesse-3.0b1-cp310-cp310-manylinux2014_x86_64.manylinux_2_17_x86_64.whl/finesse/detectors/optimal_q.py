"""Single-frequency array of complex amplitudes detector."""

import logging

import numpy as np

from finesse import BeamParam
from finesse.components.node import Node, NodeType
from finesse.detectors.general import Detector
from finesse.exceptions import ConvergenceException, FinesseException
from finesse.parameter import float_parameter, bool_parameter
from finesse.detectors.workspace import DetectorWorkspace
from finesse.gaussian import optimise_HG00_q_scipy

LOGGER = logging.getLogger(__name__)


class OptimalQWorkspace(DetectorWorkspace):
    """Workspace for calculating the output of the optimial beamparameter (q) detectors.

    Parameters
    ----------
    owner : OptimalQ
        Detector which owns this workspace
    sim
        Simulation this workspace should be created for
    """

    def __init__(self, owner, sim):
        needs_carrier = False
        needs_signal = False
        self.is_f_changing = owner.f.is_changing
        if owner.f.eval() is None:
            raise ValueError(
                f"{owner.f}: frequency value is `None`, check values have been set correctly."
            )
        fval = float(owner.f)
        fs = []

        if sim.carrier:
            f = sim.carrier.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_carrier = True
                fs.append((f, sim.carrier))

        if sim.signal:
            f = sim.signal.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_signal = True
                fs.append((f, sim.signal))

        if len(fs) == 0:
            raise Exception(
                f"Error in OptimalQ detector {owner.name}:\n"
                f"    Could not find a frequency bin at {owner.f}"
            )
        elif len(fs) > 1:
            raise Exception(
                f"Error in OptimalQ detector {owner.name}:\n"
                f"    Found multiple frequency bins at {owner.f}"
            )

        super().__init__(
            owner, sim, needs_carrier=needs_carrier, needs_signal=needs_signal
        )
        freq, self.mtx = fs[0]
        self.node_idx = self.mtx.node_id(owner.node)
        self.f_idx = freq.index

        self.set_output_fn(self.__output)
        self.fix_spot_size = bool(owner.fix_spot_size.value)
        self.astigmatic = bool(owner.astigmatic.value)
        self.accuracy = owner.accuracy
        self.direction = owner.direction

    def __output(self, ws):
        E = np.asarray(ws.mtx.node_field_vector(ws.node_idx, ws.f_idx))
        # Directly accessing the node q doesn't work during
        # a simulation as they are not updated
        # qx = ws.oinfo.nodes[0].qx
        # qy = ws.oinfo.nodes[0].qy
        # Neither does accessing the last trace
        # qx = ws.sim.model.last_trace[ws.oinfo.nodes[0]].qx
        # qy = ws.sim.model.last_trace[ws.oinfo.nodes[0]].qy
        qx, qy = ws.sim.get_q(ws.oinfo.nodes[0])
        try:
            result = np.asarray(
                optimise_HG00_q_scipy(
                    E,
                    (qx, qy),
                    ws.sim.model.homs,
                    fix_spot_size=ws.fix_spot_size,
                    astigmatic=ws.astigmatic,
                    accuracy=self.accuracy,
                    full_output=False,
                )
            )
        except ConvergenceException:
            q = BeamParam(w0=np.nan, z=np.nan)
            result = np.array([q, q])

        if ws.direction == "both":
            return result
        elif ws.direction == "x":
            return result[0]
        else:
            return result[1]


@float_parameter("f", "Frequency", units="Hz")
@bool_parameter(
    "fix_spot_size",
    "Fix spot size",
    units="",
)
@bool_parameter(
    "astigmatic",
    "Astigmatic",
    units="",
)
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class OptimalQ(Detector):
    """This detector tries to compute an optimal beam parameter (:math:`q`) for a
    specified optical frequency at a node.

    Output of this detector into an array solution will be a tuple
    of :class:`.BeamParam` in each transverse direction, (qx, qy).
    If the optimisation process fails beam parameter objects will
    NaN values will be returned.

    Parameters
    ----------
    name : str
        Name of the detector
    node : [str | finesse.components.node]
        Node name or object to put this detector at
    f : float
        Frequency component tro compute the optimal beam parameter for.
    fix_spot_size : bool, optional
        When True the optimised will keep the current spot size at the node
        fixed and just optimise the curvature.
    astigmatic : bool, optional
        When True qx and qy will be optimised separately
    accuracy : float, optional
        Approximate mismatch accuracy to try and compute the optimised beam
        parameter to. mismatch(q_actual, q_optimal) < accuracy
    direction : str, optional
        Return either `both` or just the `x` or `y` modes

    Notes
    -----
    This method uses the :func:`finesse.gaussian.optimise_HG00_q`
    or :func:`finesse.gaussian.optimise_HG00_q_scipy` for optimising the HG mode amplitudes at
    the node and frequency requested. This particular method finds a new
    set of {qx, qy} values which maximise the HG00 mode content, whilst
    reducing the HG20 and HG02 mode content.

    ``Failure``

    If the optical field being optimised does not have a HG00 like
    appearance then. For example, trying to optimise the shape of
    an RF sideband field inside a cavity that it is not resonant in.
    """

    def __init__(
        self,
        name,
        node: Node,
        f,
        *,
        fix_spot_size=False,
        astigmatic=False,
        accuracy=1e-9,
        direction="both",
    ):
        if node.type is not NodeType.OPTICAL:
            raise Exception(f"Must be an optical node used for OptimalQ {name}")
        Detector.__init__(
            self, name, node, shape=(2,), dtype=BeamParam, label="Optimal q"
        )
        self.f = f
        self.fix_spot_size = fix_spot_size
        self.astigmatic = astigmatic
        self.accuracy = accuracy
        self.direction = direction

    @property
    def direction(self):
        """Sets the output of the detector.

        If `both` then both qx and qy are returned. if `x` or `y` are used then only the
        required one is returned.
        """
        return self.__direction

    @direction.setter
    def direction(self, value):
        if value not in ("both", "x", "y"):
            raise FinesseException("Direction should be `both`, `x`, or `y`")
        self.__direction = value
        if value == "both":
            self._update_dtype_shape((2,))
        else:
            self._update_dtype_shape((1,))

    def _get_workspace(self, sim):
        if not sim.is_modal:
            raise FinesseException(
                f"OptimalQ detector {self} needs higher order modes to be enabled."
            )
        if (2, 0) not in sim.model.mode_index_map:
            raise FinesseException(
                f"OptimalQ detector {self} needs HG20 mode in the simulation"
            )
        if (0, 2) not in sim.model.mode_index_map:
            raise FinesseException(
                f"OptimalQ detector {self} needs HG02 mode in the simulation"
            )
        return OptimalQWorkspace(self, sim)
