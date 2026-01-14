"""Optical components performing directional suppression of beams."""

import logging
import finesse
import numpy as np

from finesse.components.node import NodeType, NodeDirection
from finesse.components.general import (
    Connector,
    InteractionType,
)
from finesse.parameter import float_parameter
from finesse.utilities import refractive_index
from finesse.symbols import Matrix
from finesse.tracing import abcd

LOGGER = logging.getLogger(__name__)


@float_parameter("S", "Power suppression")
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Isolator(Connector):
    """Represents an isolator optical component with a suppression factor. Suppresses
    the light field transmitted from p2 to p1. The field from p1 to p2 is.

    Parameters
    ----------
    name : str
        Name of newly created isolator.

    S : float
        Power suppression in dB. Defaults to 0
    """

    def __init__(self, name, S=0.0):
        super().__init__(name)
        self.S = S

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

    def _resymbolise_ABCDs(self):
        M_sym = abcd.none()
        for direction in ["x", "y"]:
            # Matrices same for both node couplings
            self.register_abcd_matrix(
                M_sym,
                (self.p1.i, self.p2.o, direction),
                (self.p2.i, self.p1.o, direction),
            )

    @property
    def suppression_factor(self) -> float:
        """Factor by which the light field transmitted from p2 to p1 is supressed."""
        if self._model and self._model.is_built:
            S = self._eval_parameters()[0]["S"]
        else:
            S = self.S.ref
        return 10 ** (-S / 20)

    def optical_equations(self):
        with finesse.symbols.simplification():
            S = self.suppression_factor
            if self._model._settings.is_modal:
                return {
                    f"{self.name}.P1i_P2o": S * Matrix(f"{self.name}.K12"),
                    f"{self.name}.P2i_P1o": S * Matrix(f"{self.name}.K21"),
                }
            else:
                return {
                    f"{self.name}.P1i_P2o": S,
                    f"{self.name}.P2i_P1o": S,
                }

    def _get_workspace(self, sim):
        from finesse.components.modal.isolator import IsolatorWorkspace

        _, is_changing = self._eval_parameters()
        refill = sim.is_component_in_mismatch_couplings(self) or len(is_changing)

        ws = IsolatorWorkspace(self, sim)
        # This assumes that nr1/nr2 cannot change during a simulation
        ws.nr1 = refractive_index(self.p1)
        ws.nr2 = refractive_index(self.p2)
        ws.carrier.add_fill_function(self._fill_carrier, refill)
        if sim.signal:
            ws.signal.add_fill_function(self._fill_signal, refill)

        if sim.is_modal:
            ws.set_knm_info(
                "P1i_P2o", nr_from=ws.nr1, nr_to=ws.nr2, is_transmission=True
            )
            ws.set_knm_info(
                "P2i_P1o", nr_from=ws.nr2, nr_to=ws.nr1, is_transmission=True
            )

        return ws

    def _fill_carrier(self, ws):
        self._fill_matrix(ws, ws.sim.carrier, ws.carrier.connections)

    def _fill_signal(self, ws):
        self._fill_matrix(ws, ws.sim.signal, ws.signal.connections)

    def _fill_matrix(self, ws, mtx, connections):
        for freq in mtx.optical_frequencies.frequencies:
            with mtx.component_edge_fill3(
                ws.owner_id, connections.P1i_P2o_idx, freq.index, freq.index
            ) as mat:
                mat[:] = ws.K12.data

            with mtx.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                np.multiply(self.suppression_factor, ws.K21.data, out=mat[:])
