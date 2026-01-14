"""Optical components performing modulation of beams."""

import logging
import finesse
import numpy as np

from finesse.tracing import abcd
from finesse.components.general import InteractionType, Connector, FrequencyGenerator
from finesse.components.node import NodeType, NodeDirection
from finesse.parameter import (
    float_parameter,
    int_parameter,
    bool_parameter,
    enum_parameter,
    ParameterState,
)
from finesse.symbols import Variable, Matrix
from finesse.enums import ModulatorType

LOGGER = logging.getLogger(__name__)


@float_parameter("f", "Frequency", units="Hz")
@float_parameter("midx", "Modulation index")
@float_parameter("phase", "Phase", units="degrees")
@int_parameter(
    "order",
    "Maximum modulation order",
    changeable_during_simulation=False,
    validate="_check_order",
)
@enum_parameter(
    "mod_type",
    f"Modulation type {tuple(_ for _ in ModulatorType.__members__.keys())}",
    ModulatorType,
    changeable_during_simulation=False,
    validate="_check_mod_type",
)
@bool_parameter("positive_only", "Positive only", changeable_during_simulation=False)
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Modulator(Connector, FrequencyGenerator):
    """Represents a modulator optical component with associated properties such as
    modulation frequency, index and order.

    Parameters
    ----------
    name : str
        Name of newly created modulator.

    f : float or :class:`.Frequency`, optional
        Frequency of the modulation (in Hz) or :class:`.Frequency` object.

    midx : float
        Modulation index, >= 0.

    order : int, optional
        Maximum order of modulations to produce. Must be 1 for
        amplitude modulation. Defaults to 1.

    mod_type : str, optional
        Modulation type, either 'am' (:ref:`amplitude
        modulation<amp_mod>`) or 'pm' (:ref:`phase
        modulation<phase_mod>`). Defaults to 'pm'.

    phase : float, optional
        Relative phase of modulation (in degrees). Defaults to 0.0.

    positive_only : bool, optional
        If True, only produce positive-frequency sidebands. Defaults to False.
    """

    def __init__(
        self,
        name,
        f,
        midx,
        order=1,
        mod_type=ModulatorType.pm,
        phase=0.0,
        positive_only=False,
    ):
        Connector.__init__(self, name)
        FrequencyGenerator.__init__(self)

        self.f = f
        self.midx = midx
        self.phase = phase
        self.order = order
        self.mod_type = mod_type
        self.positive_only = positive_only

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        self._add_port("amp", NodeType.ELECTRICAL)
        self.amp._add_node("i", NodeDirection.INPUT)
        self._add_port("phs", NodeType.ELECTRICAL)
        self.phs._add_node("i", NodeDirection.INPUT)

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

        self._register_node_coupling("amp_P1o", self.amp.i, self.p1.o)
        self._register_node_coupling("amp_P2o", self.amp.i, self.p2.o)

    def optical_equations(self):
        settings = self._model._settings

        with finesse.symbols.simplification():
            if self.mod_type == ModulatorType.pm:
                jv = finesse.symbols.FUNCTIONS["jv"]
                _k_ = Variable("_k_")  # modulation order of the operator

                # Scalar for a phase modulation operator
                scalar = (1j) ** _k_ * jv(_k_, self.midx.ref)

                if settings.is_modal:
                    return {
                        f"{self.name}.P1i_P2o": scalar * Matrix(f"{self.name}.K12"),
                        f"{self.name}.P2i_P1o": scalar * Matrix(f"{self.name}.K21"),
                    }
                else:
                    return {
                        f"{self.name}.P1i_P2o": scalar,
                        f"{self.name}.P2i_P1o": scalar,
                    }
            else:
                raise NotImplementedError()

    def _modulation_frequencies(self):
        order = self.order.eval()
        if order - int(order) != 0:
            raise ValueError(
                f"Modulation order for {self.name} must be an integer not {order}"
            )
        order = int(order)
        orders = list(range(-order, 1 + order))
        orders.pop(order)  # remove 0
        fm = np.dot(self.f.ref, orders)
        return fm

    def _couples_frequency(self, ws, connection, f_in, f_out):
        if connection in ("P2i_P1o", "P1i_P2o"):
            if f_in == f_out:
                return True
            elif (f_in, f_out) in ws.carrier_frequency_couplings:
                return True
            elif (f_out, f_in) in ws.carrier_frequency_couplings:
                return True
            elif (f_in, f_out) in ws.signal_frequency_couplings:
                return True
            elif (f_out, f_in) in ws.signal_frequency_couplings:
                return True
            else:
                return False
        else:  # any other signal connection
            return True

    def _check_order(self, value):
        if self.mod_type == ModulatorType.am and int(value) != 1:
            raise ValueError(
                "Modulation order must be 1 when using amplitude modulation"
            )
        return value

    def _check_mod_type(self, value):
        try:
            value = ModulatorType(value)
        except ValueError:
            try:
                value = ModulatorType[value]  # cast input into enum
            except KeyError:
                raise ValueError(
                    f"'{value}' is not a valid Modulator type, options are {tuple(_ for _ in ModulatorType.__members__.keys())}"
                )

        if self.order.state == ParameterState.Numeric:
            if value == ModulatorType.am and self.order > 1:
                raise ValueError("Amplitude modulation can only be used with order 1")
        return value

    @property
    def f(self):
        """Source frequency representing modulation.

        Returns
        -------
        :class:`float` or :class:`.Frequency`
            The modulation frequency.
        """
        return self.__f

    @f.setter
    def f(self, value):
        self.__f = value

    @property
    def order(self):
        """The maximum order of modulations produced by the modulator.

        Returns
        -------
        int
            The maximum modulation order.
        """
        return self.__order

    @order.setter
    def order(self, value):
        self.__order = int(value)

    def _resymbolise_ABCDs(self):
        M_sym = abcd.none()
        for direction in ["x", "y"]:
            # Matrices same for both node couplings
            self.register_abcd_matrix(
                M_sym,
                (self.p1.i, self.p2.o, direction),
                (self.p2.i, self.p1.o, direction),
            )

    def _get_workspace(self, sim):
        from finesse.components.modal.modulator import (
            ModulatorWorkspace,
            modulator_carrier_fill,
            modulator_signal_optical_fill,
            modulator_signal_phase_fill,
            modulator_signal_amp_fill,
        )

        ws = ModulatorWorkspace(self, sim)
        changing = (
            self.midx.is_changing
            or self.phase.is_changing
            or self.f.is_changing
            or sim.is_component_in_mismatch_couplings(self)
            or self in sim.trace_forest
            or sim.carrier.any_frequencies_changing
        )

        ws.carrier.add_fill_function(
            modulator_carrier_fill,
            changing,
        )

        if sim.signal:
            # modulator for signals doesn't actually need refilling each time if
            # signal frequency is changing, as the coupling depends on the
            ws.signal.add_fill_function(
                modulator_signal_optical_fill,
                self.midx.is_changing or self.phase.is_changing,
            )

            if ws.amp_signal_enabled:
                # Amplitude signal elements do not depend on the signal frequency
                ws.signal.add_fill_function(
                    modulator_signal_amp_fill,
                    self.midx.is_changing or self.phase.is_changing,
                )

            if ws.phs_signal_enabled:
                # Phase signal elements do not depend on the signal frequency
                ws.signal.add_fill_function(
                    modulator_signal_phase_fill,
                    self.midx.is_changing or self.phase.is_changing,
                )
        return ws
