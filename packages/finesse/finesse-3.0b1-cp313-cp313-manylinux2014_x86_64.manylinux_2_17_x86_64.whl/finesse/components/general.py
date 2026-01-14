"""Top-level objects which specific optical, and otherwise, components should inherit
from."""

from copy import copy
from collections import OrderedDict
import enum
import logging
import numbers

import numpy as np

from finesse.components.node import NodeType, Port
from finesse.exceptions import (
    ComponentNotConnected,
    NoCouplingError,
    NoABCDCoupling,
    DoubleConnectionError,
)
from finesse.utilities import check_name, is_iterable
from finesse.element import ModelElement
from finesse.utilities.misc import DeprecationHelper


LOGGER = logging.getLogger(__name__)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Variable(ModelElement):
    """The variable element acts slightly different to other elements. When added to a
    model it creates a new :class:`finesse.parameter.Parameter` in the model it has been
    added to. This does the same as calling
    :meth:`finesse.model.Model.add_parameter`. This new parameter can be used like a
    variable for making symbolic links to or for storing some useful number about the
    model.

    See :meth:`finesse.model.Model.add_parameter` for more details.
    """

    def __init__(
        self,
        name: str,
        value,
        description: str = None,
        units: str = "",
        is_geometric: bool = False,
        changeable_during_simulation: bool = True,
    ):
        super().__init__(name)
        self.value = value
        self.description = description
        self.units = units
        self.is_geometric = is_geometric
        self.changeable_during_simulation = changeable_during_simulation


class LocalDegreeOfFreedom:
    """A local degree of freedom definition that combines a DC parameter and AC nodes at
    some element. For example, this can pair a mirror tuning and it the AC mechanical
    nodes into one "Degree of Freedom" that can be referenced to scan, drive, or
    readout. Some DOFs do not have a DC equivalent so the DC part may be `None`. A DOF
    can have a different input (drive) and output (readout) signal node. This is used in
    more advanced cases such as suspension systems, where you drive some motion through
    a force/torque actuation on some part of the suspension but the readout is in
    displacement/rotation of the final optic.

    Parameters
    ----------
    name : str
        Name should be the full-name of the definition for a particular
        element, e.g. `m1.dofs.z` if this is wrong, then unparsing will not work
        correctly
    DC : Parameter, optional
        The DC equivlent of the AC signal node of an element, setting to `None` means
        no DC actuation happens.
    AC_IN : SignalNode
        The node that is driven for this degree of freedom, cannot be None.
    DC_2_AC_scaling : float, optional
        Scaling factor relating the DC and AC parameter and nodes. For example, the
        scaling between phi (degrees) and `mirror.mech.z` (meters).
    AC_OUT : SignalNode, optional
        The node that is read out to describe this degree of freedom, if `None` there is
        nothing to readout here.
    """

    def __init__(self, name, DC=None, AC_IN=None, DC_2_AC_scaling=None, AC_OUT=None):
        self.name = name
        self.DC = DC
        self.AC_IN = AC_IN
        self.DC_2_AC_scaling = DC_2_AC_scaling
        if AC_OUT is None:
            self.AC_OUT = AC_IN
        else:
            self.AC_OUT = AC_OUT

        # if self.AC_IN.type != self.AC_OUT.type:
        #     raise FinesseException(
        #         f"Nodes {self.AC_IN} and {self.AC_OUT} must be of the same type: {self.AC_IN.type}!={self.AC_OUT.type}"
        #     )

    @property
    def AC_IN_type(self):
        if self.AC_IN:
            return self.AC_IN.type
        else:
            return None

    @property
    def AC_OUT_type(self):
        if self.AC_OUT:
            return self.AC_OUT.type
        else:
            return None

    def __repr__(self):
        return f"<'{self.name}' @ {hex(id(self))} ({self.__class__.__name__}) DC={self.DC} AC_IN={self.AC_IN} AC_OUT={self.AC_OUT}>"


DOFDefinition = DeprecationHelper(
    "DOFDefinition",
    "finesse.components.general.LocalDegreeOfFreedom",
    LocalDegreeOfFreedom,
    "3.b0",
)


def unique_element():
    """Flags that this element type is unique in a model.

    In other words, only one of these element types can be in a single model.
    """

    def func(cls):
        cls._unique_element = True
        return cls

    return func


def borrows_nodes():
    """Flags that a ModelElement will be making references to nodes owner by other
    elements, or borrows a reference."""

    def func(cls):
        cls._borrows_nodes = True
        return cls

    return func


@enum.unique
class CouplingType(enum.Enum):
    """An enum describing the type of coupling between two nodes."""

    OPTICAL_TO_OPTICAL = 0
    OPTICAL_TO_ELECTRICAL = 1
    OPTICAL_TO_MECHANICAL = 2
    ELECTRICAL_TO_ELECTRICAL = 3
    ELECTRICAL_TO_OPTICAL = 4
    ELETRICAL_TO_MECHANICAL = 5
    MECHANICAL_TO_MECHANICAL = 6
    MECHANICAL_TO_OPTICAL = 7
    MECHANICAL_TO_ELECTRICAL = 8


@enum.unique
class NoiseType(enum.Enum):
    """An enum describing the type of noise a component generates."""

    QUANTUM = 0


def determine_coupling_type(from_node, to_node):
    """Retrieves the type of coupling (see :class:`.CouplingType`) between two nodes.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node which couples into `to_node`.

    to_node : :class:`.Node`
        Node which has a coupling from `from_node`.

    Returns
    -------
    coupling_t : :class:`.CouplingType`
        The type of coupling between the two given nodes.
    """
    convert = {
        (NodeType.OPTICAL, NodeType.OPTICAL): CouplingType.OPTICAL_TO_OPTICAL,
        (NodeType.OPTICAL, NodeType.ELECTRICAL): CouplingType.OPTICAL_TO_ELECTRICAL,
        (NodeType.OPTICAL, NodeType.MECHANICAL): CouplingType.OPTICAL_TO_MECHANICAL,
        (
            NodeType.ELECTRICAL,
            NodeType.ELECTRICAL,
        ): CouplingType.ELECTRICAL_TO_ELECTRICAL,
        (NodeType.ELECTRICAL, NodeType.OPTICAL): CouplingType.ELECTRICAL_TO_OPTICAL,
        (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ): CouplingType.ELETRICAL_TO_MECHANICAL,
        (
            NodeType.MECHANICAL,
            NodeType.MECHANICAL,
        ): CouplingType.MECHANICAL_TO_MECHANICAL,
        (NodeType.MECHANICAL, NodeType.OPTICAL): CouplingType.MECHANICAL_TO_OPTICAL,
        (
            NodeType.MECHANICAL,
            NodeType.ELECTRICAL,
        ): CouplingType.MECHANICAL_TO_ELECTRICAL,
    }
    return convert[(from_node.type, to_node.type)]


@enum.unique
class InteractionType(enum.Enum):
    """An enum describing the type of interaction between two nodes."""

    REFLECTION = 0
    TRANSMISSION = 1


class FrequencyGenerator:
    """The base class for components which generate optical frequencies.

    A component inheriting from this class will allow the model to query the component
    to ask what frequencies it wants to use. Frequency generation comes in the form of
    either a laser or something that modulates.
    """

    def _couples_frequency(self, ws, connection, frequency_in, frequency_out):
        """This method returns whether this element is coupling frequencies for a
        particular connection.

        For example, a modulator would modulator frequencies when a field
        passes through it. Or a suspended mirror would couple the upper and
        lower sidebands on reflection due to radiation pressure effects.

        Parameters
        ----------
        ws : :class:`.ElementWorkspace`
            Workspace for this particular component
        connection : str
            Name of the connection being queried
        frequency_in : :class:`.Frequency`
            Input frequency
        frequency_out : :class:`.Frequency`
            Output frequency

        Returns
        -------
        bool
            True if frequencies couple at this element
        """
        return False

    def _modulation_frequencies(self):
        return []

    def _source_frequencies(self):
        return []

    def _on_response(self, freqWeakRef):
        """Callback function that model calls to say whether requested frequency was
        granted or not. If so a weak reference to the frequency object is returned.

        Parameters
        ----------
        freqWeakRef: Weakref.ref
            Weak reference to the assigned Frequency object

        Raises
        ------
        Exception
            If passed a name to a frequency this element did not
            ask for originally.
        """
        # if freqWeakRef() in self.__requested_frequencies:
        self.__frequencies.append(freqWeakRef)
        # else:
        #    raise Exception(f"{self} never requested a frequency {freqWeakRef()}")


class NoiseGenerator:
    """The base class for components which generate some kind of noise.

    A component inheriting from this class will allow the model to query the component
    to ask what noise it generates.
    """

    def __init__(self):
        self.__noises = {}

    def _register_noise_output(
        self,
        name,
        node,
        noise_type,
    ):
        if noise_type not in self.__noises.keys():
            self.__noises[noise_type] = []

        self.__noises[noise_type].append((name, node))

    def _couples_noise(self, ws, node, noise_type, frequency_in, frequency_out):
        """This method returns whether the noise sidebands this element produces are
        covariant for the specified frequencies at this node.

        Parameters
        ----------
        ws : :class:`.ElementWorkspace`
            Workspace for this particular component
        node : :class:`.Node`
            Node to check.
        noise_type : :class:`.NoiseType`
            NoiseType to check.
        frequency_in : :class:`.Frequency`
            Input frequency
        frequency_out : :class:`.Frequency`
            Output frequency

        Returns
        -------
        bool
            True if the specified sidebands are covariant.
        """
        return frequency_in.index == frequency_out.index

    @property
    def noises(self):
        return self.__noises


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Connector(ModelElement):
    """Base class for any component which connects nodes together.

    Internally it stores the nodes and the connections associated with the component. During the
    matrix build this class will then ensure that the matrix elements for each coupling requested
    are allocated and and the required matrix view for editing their values is retrieved.

    The inheriting class should call ``_register_node`` and ``_register_coupling`` to define the
    connections it wants to use.

    Parameters
    ----------
    name : str
        Name of the new `Connector` instance.
    """

    _borrows_nodes = False

    def __init__(self, name):
        super().__init__(name)

        self.__connections = OrderedDict()
        self.__enabled_checks = OrderedDict()
        self.__ports = OrderedDict()
        self.__interaction_types = {}
        self.__nodes = OrderedDict()
        self._abcd_matrices = {}
        self.__abcds_symbolised = False
        self._trace_through = True

    def __nodes_of(self, *node_types):
        return tuple([node for node in self.nodes.values() if node.type in node_types])

    @property
    def borrows_nodes(self):
        """Whether this element borrows node references from another.

        When this is True the element may not create all of its own nodes and just link
        into one that already exists and is owned by another element.
        """
        return self._borrows_nodes

    @property
    def optical_nodes(self):
        """The optical nodes stored by the connector.

        :`getter`: Returns a list of the stored optical nodes (read-only).
        """
        return self.__nodes_of(NodeType.OPTICAL)

    @property
    def signal_nodes(self):
        """The signal nodes stored by the connector.

        :`getter`: Returns a list of the stored signal nodes (read-only).
        """
        return self.__nodes_of(NodeType.ELECTRICAL, NodeType.MECHANICAL)

    @property
    def ports(self):
        """Retrieves the ports available at the object.

        Returns
        -------
        tuple
            Read-only tuple of the ports available at this object.
        """
        return tuple(self.__ports.values())

    def _add_port(self, name, type):
        """Creates either an electrical, mechanical, or optical port for this component.

        Each port can then have multiple different nodes associated with - each node
        being an equation to solve for in the linear system.

        For example, the input and output optical field at one part of a component
        would be one port, i.e. reflection from one side of a mirror.

        The port is added to the component object directly to be referenced at a later
        time when the users is connecting components or definining couplings in a component.

        Parameters
        ----------
        name : str
            Name of the port
        type : NodeType
            Type of nodes this port holds

        Returns
        -------
        Port object added
        """
        check_name(name)

        if name in self.ports:
            raise Exception("Port %s already exists for this object" % name)

        if hasattr(self, name):
            raise Exception(
                "Port name %s already exists as an attribute in of this object" % name
            )

        p = Port(name, self, type)
        self.__ports[name] = p

        # self._unfreeze()
        assert not hasattr(self, name)
        setattr(self, name, p)
        # self._freeze()
        return p

    @property
    def _enabled_checks(self):
        return copy(self.__enabled_checks)

    @property
    def _registered_connections(self):
        return copy(self.__connections)

    @property
    def all_internal_optical_connections(self):
        """A dictionary of all the optical connections this element is making between
        its nodes."""
        return {
            k: (self.nodes[v[0]], self.nodes[v[1]])
            for k, v in self.__connections.items()
            if (
                self.coupling_type(self.nodes[v[0]], self.nodes[v[1]])
                == CouplingType.OPTICAL_TO_OPTICAL
            )
        }

    @property
    def all_internal_connections(self):
        """A dictionary of all the connections this element is making between its
        nodes."""
        return {
            k: (self.nodes[v[0]], self.nodes[v[1]])
            for k, v in self.__connections.items()
        }

    def coupling_type(self, from_node, to_node):
        """Obtains the type of coupling (see :class:`.CouplingType`) between the two
        specified nodes at this component.

        Parameters
        ----------
        from_node : :class:`.Node`
            Node which has a forwards coupling to `to_node`.

        to_node : :class:`.Node`
            Node which has a backwards coupling from `from_node`.

        Returns
        -------
        coupling_t : :class:`.CouplingType`
            The type of coupling between the specified nodes.
        """
        try:
            return determine_coupling_type(from_node, to_node)
        except KeyError:
            return None

    def interaction_type(self, from_node, to_node):
        """Obtains the type of interaction (see :class:`.InteractionType`) between the
        two specified nodes at this component.

        Parameters
        ----------
        from_node : :class:`.Node`
            Node which has a forwards coupling to `to_node`.

        to_node : :class:`.Node`
            Node which has a backwards coupling from `from_node`.

        Returns
        -------
        interaction_t : :class:`.InteractionType`
            The type of interaction between the specified nodes.
        """
        try:
            if hasattr(from_node, "full_name"):
                from_node = from_node.full_name
            if hasattr(to_node, "full_name"):
                to_node = to_node.full_name
            return self.__interaction_types[(from_node, to_node)]
        except KeyError:
            return None

    @property
    def nodes(self):
        """All the nodes of all the ports at this component. Order is likely to be the
        order in which the ports and nodes were created, but this is not guaranteed.

        Returns
        -------
        nodes : tuple(:class:`.Node`)
            Copy of nodes dictionary
        """
        return copy(self.__nodes)

    def _register_node_coupling(
        self,
        connection_id: str,
        from_node,
        to_node,
        interaction_type=None,
        forced_name=None,
        enabled_check=None,
    ):
        """Registers that this element will connect the output of one of its nodes to
        the input of another.

        Each element is responsible for requesting connections
        to be made within a Model. In practice this means the
        model will allocate the required matrix elements for
        this element to fill in.

        Parameters
        ----------
        connection_id : str
            A unique string ID for this element which is used to identify this connection.

        from_node : :class:`.Node`
            The input node

        to_node : :class:`.Node`
            The output node

        interaction_type : :class:`.InteractionType`, optional
            The type of interaction between the nodes if applicable.

        forced_name : str, optional
            Can force the name of a connection. Used by spaces/wires for
            using the correct name as it doesn't own the node

        enabled_check : function, optional
            A function that returns a True/False if this connection should be enabled
            when a simulation is built from a model. The default value None means True.
        """
        from finesse.components import Space, Wire

        if forced_name is None:
            name = "{}->{}".format(from_node.full_name, to_node.full_name)
        else:
            name = forced_name

        try:
            if self._model is not None:
                raise Exception("Component has already been added to a model")
        except ComponentNotConnected:
            pass

        if name in self.__connections:
            raise Exception(
                "Connection called {} already set at component {}".format(
                    self.name, name
                )
            )

        # TODO: decide whether we actually need this - shouldn't be possible
        #       to connect non-existing ports without python complaining about
        #       an undefined parameter first anyway
        if isinstance(self, Space) or isinstance(self, Wire):
            if from_node.port not in from_node.port.component.ports:
                raise Exception()
            if to_node.port not in to_node.port.component.ports:
                raise Exception()
        else:
            if from_node.full_name not in self.nodes:
                raise Exception(
                    "Node {}.{} is not available at component `{}`".format(
                        from_node.port.name, from_node.name, self.name
                    )
                )
            if to_node.full_name not in self.nodes:
                raise Exception(
                    "Node {}.{} is not available at component `{}`".format(
                        to_node.port.name, to_node.name, self.name
                    )
                )
        if (from_node.full_name, to_node.full_name) in self.__connections.values():
            raise Exception(
                f"Connection between {(from_node.full_name, to_node.full_name)} already exists"
            )

        self.__connections[connection_id] = (from_node.full_name, to_node.full_name)
        if enabled_check:
            self.__enabled_checks[connection_id] = enabled_check

        if interaction_type is not None:
            self.__interaction_types[(from_node.full_name, to_node.full_name)] = (
                interaction_type
            )

    def is_valid_coupling(self, from_node, to_node):
        """Flags whether the provided node coupling exists at this connector."""
        return (from_node.full_name, to_node.full_name) in self.__connections.values()

    def check_coupling(self, from_node, to_node):
        """Checks that a coupling exists between `from_node` -> `to_node` and raises a
        ``ValueError`` if not."""
        fname, tname = from_node.full_name, to_node.full_name
        if (fname, tname) not in self.__connections.values():
            raise NoCouplingError(f"No coupling exists between {fname} -> {tname}")

    def _parse_from_to_nodes(self, from_node, to_node):
        if isinstance(from_node, numbers.Integral):
            from_node = getattr(self, f"p{from_node}")
        if isinstance(to_node, numbers.Integral):
            to_node = getattr(self, f"p{to_node}")

        if isinstance(from_node, Port):
            from_node = from_node.i
        if isinstance(to_node, Port):
            to_node = to_node.o

        return from_node, to_node

    def _resymbolise_ABCDs(self):
        # By default components will not have to resymbolise optical ABCD matrices
        pass

    def register_abcd_matrix(self, M_sym, *couplings):
        """Register an ABCD matrix of the given symbolic form for a sequence of
        coupling(s).

        Specifying several couplings for one `M_sym` means that all these
        node couplings will point to the same reference ABCDs --- i.e. the
        matrices kept in the underlying ABCD matrix store will be the same
        blocks of memory.

        .. warning::

            This should only be used in the ``_resymbolise_ABCDs`` method of Connectors,
            when implementing a new component.

        Parameters
        ----------
        M_sym : :class:`numpy.ndarray`
            A 2x2 matrix of symbolic elements describing the analytic form of
            the ABCD matrix for the given coupling(s).

        couplings : sequence of tuples
            Arguments of tuples giving the node couplings which are described by
            the given symbolic ABCD matrix `M_sym`.

            These tuples can be of size two or three, with the first two elements
            always as the `from_node` -> `to_node` instances. The former case implies that
            both the tangential and sagittal plane ABCD matrix couplings are equal
            and so both directions 'x' and 'y' in the underlying matrices store will
            be set to the same values. Whilst the latter case, where the third element is
            either 'x' or 'y', sets just these direction keys to this matrix.
        """
        M_num = np.array(M_sym, dtype=np.float64)

        for coupling in couplings:
            if not is_iterable(coupling) or len(coupling) < 2 or len(coupling) > 3:
                raise ValueError(
                    f"Expected coupling {coupling} passed to _register_abcd_matrix "
                    "to be an iterable of length two (from_node, to_node) or "
                    "length three (from_node, to_node, direction)."
                )

            # No plane given, so same matrix will be used for
            # both planes at this given node coupling
            if len(coupling) == 2:
                from_node, to_node = coupling
                direction = ("x", "y")
            # Otherwise use the specified plane
            else:
                from_node, to_node, direction = coupling
                if direction != "x" and direction != "y":
                    raise ValueError(
                        f"Expected direction argument of coupling {coupling} to "
                        f"be either 'x' or 'y' but got {direction}."
                    )

                direction = (direction,)

            # Check that the node coupling actually exists on this connector
            self.check_coupling(from_node, to_node)

            for d in direction:
                key = (from_node, to_node, d)
                if key in self._abcd_matrices:
                    raise ValueError(
                        f"There is already an ABCD matrix defined for the coupling "
                        f"{from_node.full_name} -> {to_node.full_name} in the "
                        f"plane '{d}'!"
                    )

                LOGGER.debug(
                    "For node coupling %s -> %s, in plane %s, registered "
                    "ABCD matrix:\n Symbolic: %s, Current Numeric: %s",
                    from_node.full_name,
                    to_node.full_name,
                    d,
                    M_sym.tolist(),
                    M_num.tolist(),
                )
                self._abcd_matrices[(from_node, to_node, d)] = M_sym, M_num

    def _re_eval_abcds(self):
        for M_sym, M_num in self._abcd_matrices.values():
            M_num[:] = np.array(M_sym, dtype=np.float64)

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
        """
        Parameters
        ----------
        from_node : :class:`.OpticalNode` or :class:`.Port` or str or int
            Input node. If a port, or string repr of a port, is given then
            the *input* optical node of that port will be used.

        to_node : :class:`.OpticalNode` or :class:`.Port` or str or int
            Output node. If a port, or string repr of a port, is given then
            the *output* optical node of that port will be used.

        direction : str, optional; default: 'x'
            Direction of ABCD matrix computation, default is 'x' for tangential plane.

        symbolic : bool, optional; default: False
            Whether to return the symbolic matrix (as given by equations above). Defaults
            to False such that the numeric matrix is returned.

        copy : bool, optional; default: True
            Whether to return a copy of ABCD matrix (or matrices if `retboth` is true). Defaults
            to True so that the internal matrix cannot be accidentally altered. Use caution
            if switching this flag off.

        retboth : bool, optional; default: False
            Whether to return both the symbolic and numeric matrices as a tuple
            in that order.

        allow_reverse : bool, optional
            When True, if the coupling does not exist at the component from_node->to_node
            but to_node->from_node does exist, it will return the ABCD from that.
            Otherwise a NoCouplingError will be raised.

        Returns
        -------
        M : :class:`numpy.ndarray`
            The ABCD matrix of the specified coupling for the mirror. This is symbolic
            if either of `symbolic` or `retboth` flags are True.

        M2 : :class:`numpy.ndarray`
            Only returned if `retboth` is True, otherwise just `M` above is returned. This
            will always be the numeric matrix.

        Raises
        ------
        :class:`finesse.exceptions.NoCouplingError`
            If no coupling exists between `from_node` and `to_node`.
        :class:`finesse.exceptions.NoABCDCoupling`
            If no ABCD matrix has been defined for the requested coupling.
        :class:`finesse.exceptions.TotalReflectionError`
            Total reflection of a beam at a component when performing beam tracing.
        """
        from_node, to_node = self._parse_from_to_nodes(from_node, to_node)
        for n in (from_node, to_node):
            if n.type is not NodeType.OPTICAL:
                raise TypeError(
                    f"ABCD matrix only defined between optical nodes, not {n}"
                )
        try:
            self.check_coupling(from_node, to_node)
        except NoCouplingError:
            if allow_reverse:
                self.check_coupling(to_node.opposite, from_node.opposite)
            else:
                raise

        if not self.__abcds_symbolised:
            self._resymbolise_ABCDs()
            self.__abcds_symbolised = True

        key = (from_node, to_node, direction)

        if key not in self._abcd_matrices:
            if allow_reverse:
                return self.ABCD(
                    to_node.opposite,
                    from_node.opposite,
                    direction=direction,
                    symbolic=symbolic,
                    copy=copy,
                    retboth=retboth,
                    allow_reverse=False,
                )
            else:
                raise NoABCDCoupling(
                    f"ABCD matrix for coupling {from_node.full_name} -> {to_node.full_name} "
                    f"has not been defined for direction '{direction}' ({type(from_node.component)})"
                )
        else:
            M_sym, M_num = self._abcd_matrices[key]
            if M_sym is None:
                # mkolk: currently only the beamsplitter saves an exception in the
                # _abcd_matrices dict.
                # Symbolic M is None if an error occurred during the tracing
                # In such a case M_num is a TotalReflectionError or
                # some other exception instance
                raise M_num

            # Evaluate M_sym and assign to memory of M_num so that
            # M_num always corresponds to current parameter state
            M_num[:] = np.array(M_sym, dtype=np.float64)

        if copy:
            Ms = M_sym.copy()
            Mn = M_num.copy()
        else:
            Ms = M_sym
            Mn = M_num

        if retboth:
            return Ms, Mn

        if symbolic:
            return Ms

        return Mn


class MechanicalConnector(Connector):

    def __init__(
        self, name: str, connected_to: Connector | Port, port_name: str = "mech"
    ):
        """Base class for mechanical components that copy over mechanical ports from
        optics

        Parameters
        ----------
        name : str
            Element name
        connected_to : Connector | Port
            Mechanical port or element to attach this component to
        port_name : str
            Name of the port that is created, where the mechanical nodes of
            'connected_to' will be copied into. Defaults to 'mech'.

        Raises
        ------
        Exception
            When passing in a component instead of port and this component has more
            than 1 mechanical port
        FinesseException
            When the component
        """
        super().__init__(name)

        # Handle different types of elements or mech ports to connect to
        if isinstance(connected_to, Connector):
            mech_ports = [
                p for p in connected_to.ports if p.type == NodeType.MECHANICAL
            ]
            if len(mech_ports) > 1:
                raise Exception(
                    f"{connected_to} has more than one mechanical node so please specify which to use."
                )
            self.__mech_port = mech_ports[0]
            self.__connected_to = connected_to
        elif isinstance(connected_to, Port):
            self.__mech_port = connected_to
            self.__connected_to = connected_to.component
        else:
            raise TypeError(f"{connected_to} must be {Port} or {Connector}")

        if self.mech_port.mechanical_connection is not None:
            raise DoubleConnectionError(
                "A Port cannot be connected to two mechanical components "
                f"at the same time. "
                f"'{self.mech_port.full_name}' is used in mechanical "
                f"component '{self.mech_port.mechanical_connection.name}'. "
                f"It cannot also be used with '{self.name}'"
            )
        else:
            self.mech_port.mechanical_connection = self

        # Add motion and force nodes to the mechanical port. We copy over (by reference)
        # the mechanical nodes of the port that we are attaching to. This simplifies
        # the matrix (as opposed to creating unity connections between the mechanical
        # nodes this component and the one we are attaching it to)
        mech_port = self._add_port(port_name, NodeType.MECHANICAL)
        mech_port._add_node("z", None, self.mech_port.z)
        mech_port._add_node("yaw", None, self.mech_port.yaw)
        mech_port._add_node("pitch", None, self.mech_port.pitch)
        mech_port._add_node("F_z", None, self.mech_port.F_z)
        mech_port._add_node("F_yaw", None, self.mech_port.F_yaw)
        mech_port._add_node("F_pitch", None, self.mech_port.F_pitch)

    @property
    def connected_to(self) -> Connector:
        """Component that this mechanical element is connected to"""
        return self.__connected_to

    @property
    def mech_port(self) -> Port:
        """Mechanical port that this component is using the nodes from"""
        return self.__mech_port
