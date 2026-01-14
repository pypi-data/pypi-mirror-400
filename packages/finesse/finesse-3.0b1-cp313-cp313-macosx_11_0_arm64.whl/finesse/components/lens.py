"""Transmissive optical components which focus or disperse light beams."""

import logging
import numpy as np

from finesse.components.general import Connector, InteractionType, NoiseType
from finesse.components.node import NodeDirection, NodeType
from finesse.parameter import float_parameter
from finesse.utilities import refractive_index
from finesse.tracing import abcd
from finesse.symbols import Matrix, Constant
from finesse.exceptions import FinesseException

from finesse.env import warn
from finesse.warnings import UnreasonableComponentValueWarning

from abc import ABC

LOGGER = logging.getLogger(__name__)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class BaseLens(Connector, ABC):
    """Represents a thin lens optical component with an associated focal length.

    Notes
    -----
    The specified focal length `f` is only accurate when the lens is attached to spaces with index
    of refraction close to 1. This component exists so that one can use the intuitive focal length
    parameter instead of having to set radii of curvature as with e.g. :class:`.Mirror`.

    Parameters
    ----------
    name : str
        Name of newly created lens.

    f : float, optional
        Focal length of the lens in metres; defaults to infinity.

    Attributes
    ----------
    OPD_map : :class:`finesse.knm.maps.Map`
        A map that is used to describe the transverse spatial amplitude and phase
        variations beyond a simple lensing. Typically the map applied is describing
        the dnr/dT temperature effects in some substrate.
    """

    def __init__(
        self,
        name,
    ):
        super().__init__(name)
        self.OPD_map = None

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

    def optical_equations(self):
        if self._model._settings.is_modal:
            return {
                f"{self.name}.P1i_P2o": Matrix(f"{self.name}.K12"),
                f"{self.name}.P2i_P1o": Matrix(f"{self.name}.K21"),
            }
        else:
            return {
                f"{self.name}.P1i_P2o": Constant(1),
                f"{self.name}.P2i_P1o": Constant(1),
            }

    def _check_f(self, value):
        if value == 0:
            raise ValueError("Focal length of lens must be non-zero.")

        # check for unreasonable focal length and suggest alternative
        if abs(value) < 10e-3:
            warn(
                f"Lens '{self.name}' has a small focal length. The 'lens' ABCD "
                "matrix is valid for focal lengths >> thickness of the lens."
                "This lens may be better modelled as two mirrors and a space.",
                UnreasonableComponentValueWarning,
            )

        return value

    def _resymbolise_ABCDs(self):
        self._symbolise_ABCDs("x")
        self._symbolise_ABCDs("y")

    def ABCD(
        self,
        from_node,
        to_node,
        direction="x",
        symbolic=False,
        copy=True,
        retboth=False,
        allow_reverse=False,
    ):
        r"""Returns the ABCD matrix of the lens for the specified coupling.

        .. _fig_abcd_lens_transmission:
        .. figure:: ../images/abcd_lenst.*
            :align: center

        This is given by,

        .. math::
            M = \begin{pmatrix}
                    1 & 0 \\
                    -\frac{1}{f} & 1
                \end{pmatrix},

        where :math:`f` is the focal length of the lens.

        See :meth:`.Connector.ABCD` for descriptions of parameters, return values and possible
        exceptions.
        """
        return super().ABCD(
            from_node, to_node, direction, symbolic, copy, retboth, allow_reverse
        )

    def _fill_optical_matrix(self, ws, matrix, connections):
        for freq in matrix.optical_frequencies.frequencies:
            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P1i_P2o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.K12.data

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.K21.data

    def _fill_carrier(self, ws):
        self._fill_optical_matrix(ws, ws.sim.carrier, ws.carrier.connections)

    def _fill_signal(self, ws):
        self._fill_optical_matrix(ws, ws.sim.signal, ws.signal.connections)

    def _get_baselens_workspace(self, sim, ws_type):
        from finesse.components.modal.lens import lens_fill_qnoise

        _, is_changing = self._eval_parameters()
        refill = sim.is_component_in_mismatch_couplings(self) or len(is_changing)

        ws = ws_type(self, sim)
        # This assumes that nr1/nr2 cannot change during a simulation
        ws.nr1 = refractive_index(self.p1)
        ws.nr2 = refractive_index(self.p2)
        # TODO ddb refractive index should be equal on
        # both sides of the lens as we are using the thin
        # lens approximation
        if not np.allclose(ws.nr1, ws.nr2, rtol=1e-13):
            raise FinesseException(
                "Refractive index on both sides of the lens must be equal"
            )

        ws.carrier.add_fill_function(self._fill_carrier, refill)
        ws.signal.add_fill_function(self._fill_signal, refill)

        if sim.is_modal:
            ws.abcd_x = self.ABCD(self.p1.i, self.p2.o, "x", copy=False)
            ws.abcd_y = self.ABCD(self.p1.i, self.p2.o, "y", copy=False)

            # Set the coupling matrix information
            # ABCDs are same in each direction
            ws.set_knm_info(
                "P1i_P2o",
                abcd_x=ws.abcd_x,
                abcd_y=ws.abcd_y,
                nr_from=ws.nr1,
                nr_to=ws.nr2,
                is_transmission=True,
                apply_map=self.OPD_map,
                map_phase_factor=1,
                map_fliplr=False,
            )
            # TODO nr reversed here for now until it's forced to be same on both sides
            ws.set_knm_info(
                "P2i_P1o",
                abcd_x=ws.abcd_x,
                abcd_y=ws.abcd_y,
                nr_from=ws.nr2,
                nr_to=ws.nr1,
                is_transmission=True,
                apply_map=self.OPD_map,
                map_phase_factor=1,
                map_fliplr=True,
            )

            if sim.signal:
                ws.signal.set_fill_noise_function(NoiseType.QUANTUM, lens_fill_qnoise)
        return ws


@float_parameter(
    "f",
    "Focal length",
    validate="_check_f",
    units="m",
    is_geometric=True,
)
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Lens(BaseLens):
    """Represents a thin lens optical component with an associated focal length.

    Notes
    -----
    The specified focal length `f` is only accurate when the lens is attached to spaces with index
    of refraction close to 1. This component exists so that one can use the intuitive focal length
    parameter instead of having to set radii of curvature as with e.g. :class:`.Mirror`.

    Parameters
    ----------
    name : str
        Name of newly created lens.

    f : float, optional
        Focal length of the lens in metres; defaults to infinity.

    Attributes
    ----------
    OPD_map : :class:`finesse.knm.maps.Map`
        A map that is used to describe the transverse spatial amplitude and phase
        variations beyond a simple lensing. Typically the map applied is describing
        the dnr/dT temperature effects in some substrate.
    """

    def __init__(self, name, f=np.inf):
        super().__init__(name)
        self.f = f
        self.OPD_map = None

    def _symbolise_ABCDs(self, direction):
        M_sym = abcd.lens(self.f.ref)

        # Matrices same for both node couplings
        self.register_abcd_matrix(
            M_sym,
            (self.p1.i, self.p2.o, direction),
            (self.p2.i, self.p1.o, direction),
        )

    def _get_workspace(self, sim):
        from finesse.simulations.sparse.simulation import SparseMatrixSimulation

        if isinstance(sim, SparseMatrixSimulation):
            from finesse.components.modal.lens import LensWorkspace

            return self._get_baselens_workspace(sim, LensWorkspace)


@float_parameter(
    "fx",
    "Focal length (x-z plane)",
    validate="_check_f",
    units="m",
    is_geometric=True,
)
@float_parameter(
    "fy",
    "Focal length (y-z plane)",
    validate="_check_f",
    units="m",
    is_geometric=True,
)
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class AstigmaticLens(BaseLens):
    """Represents a thin astigmatic lens optical component with an associated focal
    lengths.

    Notes
    -----
    The specified focal length `f` is only accurate when the lens is attached to spaces with index
    of refraction close to 1. This component exists so that one can use the intuitive focal length
    parameter instead of having to set radii of curvature as with e.g. :class:`.Mirror`.

    Parameters
    ----------
    name : str
        Name of newly created lens.

    fx : float, optional
        Focal length in x-z plane of the lens in metres; defaults to infinity.
    fy : float, optional
        Focal length of y-z plane the lens in metres; defaults to infinity.

    Attributes
    ----------
    OPD_map : :class:`finesse.knm.maps.Map`
        A map that is used to describe the transverse spatial amplitude and phase
        variations beyond a simple lensing. Typically the map applied is describing
        the dnr/dT temperature effects in some substrate.
    """

    def __init__(self, name, fx=np.inf, fy=np.inf):
        super().__init__(name)
        self.fx = fx
        self.fy = fy
        self.OPD_map = None

    def _symbolise_ABCDs(self, direction):
        if direction == "x":
            M_sym = abcd.lens(self.fx.ref)
        elif direction == "y":
            M_sym = abcd.lens(self.fy.ref)
        else:
            raise ValueError(f"Invalid direction: {direction}")

        # Matrices same for both node couplings
        self.register_abcd_matrix(
            M_sym,
            (self.p1.i, self.p2.o, direction),
            (self.p2.i, self.p1.o, direction),
        )

    def _get_workspace(self, sim):
        from finesse.simulations.sparse.simulation import SparseMatrixSimulation

        if isinstance(sim, SparseMatrixSimulation):
            from finesse.components.modal.lens import AstigmaticLensWorkspace

            return self._get_baselens_workspace(sim, AstigmaticLensWorkspace)
