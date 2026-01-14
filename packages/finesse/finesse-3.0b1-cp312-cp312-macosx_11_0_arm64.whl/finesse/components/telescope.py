import numpy as np
from finesse.components.general import Connector, InteractionType
from finesse.components.node import NodeType, NodeDirection
from finesse.components.workspace import ConnectorWorkspace


class TelescopeWorkspace(ConnectorWorkspace):
    def __init__(self, owner, sim):
        super().__init__(owner, sim, False, False)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Telescope(Connector):
    """This component represents a perfectly matching and adapting telescope. It will
    not change the beam parameter on transmission of the component and any field coming
    in will be transmitted to the other side into the other beam parameter. This should
    be used in cases when you want to connect to optical systems but do not want to
    design a complicated optical telescope system to mode-match them both, or in cases
    where one system has a changing parameter but you don't care about the details of
    the telescope.

    No beam is traced through the telescope so you must specify a beam parameter
    or a cavity on both sides of the telescope. If not, a tracing error will
    occur.

    Currently no losses, mismatch, or misalignments can be induced at this
    telescope. There is no accumulated Gouy phase or plane-wave propagation
    phase.

    Parameters
    ----------
    name : str
        Name of newly created telescope
    """

    def __init__(self, name):
        super().__init__(name)
        # This is usually True, but we don't want any tracing to happen through
        # this component so that either side is not affected by optical systems
        # on the other side. This is important for the telescope to be
        # perfectly matching and adapting.
        self._trace_through = False

        # Here we register that fact this component will
        # want to have some ports and nodes as well as
        # the couplings between them
        self._add_port("p1", NodeType.OPTICAL)  # front
        self._add_port("p2", NodeType.OPTICAL)  # back
        # input and output optical fields at port 1 (Front face)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)
        # input and output optical fields at port 2 (Back face)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)
        # Optic to optic couplings
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
        ws = TelescopeWorkspace(self, sim)
        ws.I = np.eye(sim.model_settings.num_HOMs, dtype=np.complex128)

        # It is never changing as there is currently no mismatch
        # or misalignment in the telescope, if this ever changes
        # it needs to be updated
        ws.carrier.add_fill_function(self._fill_carrier, False)
        ws.signal.add_fill_function(self._fill_signal, False)
        return ws

    def _fill_optical_matrix(self, ws, matrix, connections):
        for freq in matrix.optical_frequencies.frequencies:
            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P1i_P2o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.I

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.I

    def _fill_carrier(self, ws):
        self._fill_optical_matrix(ws, ws.sim.carrier, ws.carrier.connections)

    def _fill_signal(self, ws):
        self._fill_optical_matrix(ws, ws.sim.signal, ws.signal.connections)
