"""Wire-type objects representing electrical connections between components."""

import logging

import numpy as np

from finesse.exceptions import FinesseException

from .general import Connector, borrows_nodes
from .node import NodeType, SignalNode, Port
from .workspace import ConnectorWorkspace
from ..env import warn
from ..parameter import float_parameter


LOGGER = logging.getLogger(__name__)


class WireWorkspace(ConnectorWorkspace):
    pass


@float_parameter("delay", "Delay", validate="_check_delay", units="s")
@float_parameter("gain", "Gain", units=None)
@borrows_nodes()
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Wire(Connector):
    """A wire represents a flow of information between signal nodes. It connects two
    specific signal nodes. Signal nodes have a direction associated with them: input,
    output, or bidirectional. Depending on what direction each node has depends on what
    the wire will setup when it is connected. When connecting ports the wire will look
    at the name of each node in the port and connect nodes with the same name.

    Parameters
    ----------
    name : str, optional
        Name of newly created wire.

    nodeA, nodeB : :class:`.SignalNode`
        Signal nodes to connect together.

    delay : float, optional
        A delay time for the signal to flow from A to B in seconds

    gain : float, optional
        An scaling factor that can be used to scale the output relative to the
        input.
    """

    def __init__(self, name, nodeA, nodeB, delay=0, gain=1):
        # Override None name with auto https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/251
        if (nodeA is None) != (nodeB is None):
            warn(
                "Cannot construct a wire with only one port connected; ignoring ports."
            )
            nodeA = None
            nodeB = None

        if nodeA is not None and nodeA.type not in (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ):
            raise RuntimeError(
                f"{nodeA!r} is not an electrical or mechanical port or node"
            )
        if nodeB is not None and nodeB.type not in (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ):
            raise RuntimeError(
                f"{nodeB!r} is not an electrical or mechanical port or node"
            )

        if name is None:
            auto_generated = True
            if nodeA is not None and nodeB is not None:
                compA = nodeA.component.name
                compB = nodeB.component.name
                name = f"{compA}_{nodeA.name}__{compB}_{nodeB.name}"
            else:
                raise ValueError(
                    "Cannot create an unconnected wire without " "providing a name"
                )

            self._auto_generated = auto_generated
            self._auto_generated_name = name
        else:
            self._auto_generated = False
            self._auto_generated_name = None

        if self._auto_generated:
            super().__init__(self._auto_generated_name)
            self._namespace = (".wires",)
        else:
            super().__init__(name)
            # Also put into main namespace if it has a specific name
            self._namespace = (".", ".wires")

        self.delay = delay
        self.gain = gain
        self.__nodeA = None
        self.__nodeB = None

        if nodeA is not None and nodeB is not None:
            self.connect(nodeA, nodeB)

    @property
    def nodeA(self):
        return self.__nodeA

    @property
    def nodeB(self):
        return self.__nodeB

    def _check_delay(self, value):
        if value < 0:
            raise ValueError("Delay of a wire must not be negative.")

        return value

    def connect(self, A, B):
        """Connects A to B signal nodes together with a :class:`Wire` element. If A or B
        are ports then the first node is selected from the port to connect. If A or B
        have more than one node then you should specify.

        explicitly which one to use - an exception will be raised in this case.

        Parameters
        ----------
        A : :class:`.SignalNode` or :class:`.Port`
            First signal node or Electrical port with a single node
        B : :class:`.SignalNode` or :class:`.Port`
            Second signal node or Electrical port with a single node
        """
        if self.nodeA is not None or self.nodeB is not None:
            raise FinesseException(
                f"{self!r} is already connecting {self.nodeA!r} to {self.nodeB!r}"
            )

        if isinstance(A, Port) and A.type == NodeType.ELECTRICAL:
            if len(A.nodes) != 1:
                raise FinesseException(
                    f"{A!r} has more than one node, please specify which to use: {A.nodes}"
                )
            else:
                A = A.nodes[0]

        if isinstance(B, Port) and B.type == NodeType.ELECTRICAL:
            if len(B.nodes) != 1:
                raise FinesseException(
                    f"{B!r} has more than one node, please specify which to use: {B.nodes}"
                )
            else:
                B = B.nodes[0]

        if not (isinstance(A, SignalNode) and isinstance(B, SignalNode)):
            raise FinesseException(
                f"Wires can only connect two SignalNodes, not {A!r} to {B!r}. If one is a Port type object then please specify which Node at the port to use."
            )

        self.__nodeA = A
        self.__nodeB = B

        pA = self._add_port("pA", self.nodeA.type)
        A = pA._add_node("A", None, self.nodeA)
        pB = self._add_port("pB", self.nodeB.type)
        B = pB._add_node("B", None, self.nodeB)
        self._register_node_coupling("WIRE", A, B)

    def _get_workspace(self, sim):
        if sim.signal:
            self._eval_parameters()
            # Most wires are zero delay, so don't bother refilling them all the time
            refill = (
                (sim.model.fsig.f.is_changing or sim.signal.any_frequencies_changing)
                and self.delay.is_changing
                and self.delay != 0
            ) or self.gain.is_changing

            ws = WireWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            return ws
        else:
            return None

    def fill(self, ws):
        # scale appropriately if input and output are different types
        # scale up if going from electrical to mechanical
        # scale down if going from mechanical to electrical
        if (
            self.nodeA.type == NodeType.ELECTRICAL
            and self.nodeB.type == NodeType.MECHANICAL
        ):
            ws.scaling = 1 / ws.sim.model_settings.x_scale
        elif (
            self.nodeA.type == NodeType.MECHANICAL
            and self.nodeB.type == NodeType.ELECTRICAL
        ):
            ws.scaling = ws.sim.model_settings.x_scale
        else:
            ws.scaling = 1

        delay = np.exp(-1j * ws.values.delay * ws.sim.model_settings.fsig)
        key = (ws.owner_id, 0, 0, 0)
        if key in ws.sim.signal._submatrices:
            ws.sim.signal._submatrices[key][:] = delay * ws.scaling * ws.values.gain
