"""A component that introduces some loss for particular frequencies or light, relative
to the carrier frequency.

This can be used to introduce sideband imbalance, for example.
"""

import logging

import numpy as np

from finesse.components.general import Connector, InteractionType
from finesse.components.node import NodeType, NodeDirection
from finesse.components.workspace import ConnectorWorkspace
from finesse.parameter import float_parameter

LOGGER = logging.getLogger(__name__)


class FrequencyLossWorkspace(ConnectorWorkspace):
    def __init__(self, owner, sim):
        super().__init__(owner, sim, False, False)


@float_parameter("loss", "Loss")
@float_parameter(
    "phase",
    "Phase",
    units="Degrees",
)
@float_parameter(
    "f",
    "Frequency",
    units="Hz",
)
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyLoss(Connector):
    """Represents an unphysical element which introduces a loss and/or phase for a
    particular frequency.

    Parameters
    ----------
    name : str
        Name of newly created lens.

    f : float, optional
        Frequency to apply loss and phase to.

    loss : float, optional
        Fractional loss at the frequency

    phase : float, optional
        Phase change at the frequency
    """

    def __init__(self, name, f, loss=0, phase=0):
        super().__init__(name)

        self.f = f
        self.loss = loss
        self.phase = phase

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        # optic to optic couplings
        self._register_node_coupling(
            "P1i_P2o",
            self.p1.i,
            self.p2.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P2i_P1o",
            self.p2.i,
            self.p1.o,
            interaction_type=InteractionType.TRANSMISSION,
        )

    def _get_workspace(self, sim):
        ws = FrequencyLossWorkspace(self, sim)
        ws.I = np.eye(sim.model_settings.num_HOMs, dtype=np.complex128)
        ws.carrier.add_fill_function(self._fill_carrier, False)
        ws.signal.add_fill_function(self._fill_signal, False)
        return ws

    def _fill_optical_matrix(self, ws, matrix, connections, signal_fill):
        for freq in matrix.optical_frequencies.frequencies:
            M = ws.I
            # Suppress carrier and it's signal sidebands
            if freq.f == ws.values.f or (
                signal_fill and freq.audio_carrier.f == ws.values.f
            ):
                M *= (1 - ws.values.loss) * np.exp(1j * np.radians(ws.values.phase))

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P1i_P2o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = M

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = M

    def _fill_carrier(self, ws):
        self._fill_optical_matrix(ws, ws.sim.carrier, ws.carrier.connections, False)

    def _fill_signal(self, ws):
        self._fill_optical_matrix(ws, ws.sim.signal, ws.signal.connections, True)
