
import logging

cimport cython

from finesse.cymath.cmatrix import SubCCSView
from finesse.cymath.cmatrix cimport SubCCSView
from ..components.workspace cimport ConnectorWorkspace, FillFuncWrapper
from ..components.workspace import Connections
from ..cymath cimport complex_t
from ..components import Connector, NodeType, NodeDirection
from ..parameter import float_parameter
from ..components.general import LocalDegreeOfFreedom
from finesse.exceptions import FinesseException
from ..utilities import zpk_fresp
from finesse.components.general import MechanicalConnector

from libc.stdlib cimport free, calloc

cimport numpy as np
import numpy as np

import types
import itertools


LOGGER = logging.getLogger(__name__)

cdef extern from "constants.h":
    long double PI


cdef class MIMOTFWorkspace(ConnectorWorkspace):
    """Workspace that contains MIMO transfer functions stored
    in a numerator/denominator basis.
    """

    cdef:
        double[::1] denom
        Py_ssize_t N_num_allocd
        Py_ssize_t total_numerators
        double** numerators
        int* numerator_sizes
        complex_t curr_denom
        complex_t s

    def __cinit__(self, owner, sim, bint refill, unsigned int N_numerators):
        self.N_num_allocd = N_numerators
        self.numerators = <double**>calloc(N_numerators, sizeof(double*))
        if not self.numerators:
            raise MemoryError()
        self.numerator_sizes = <int*>calloc(N_numerators, sizeof(int))
        if not self.numerator_sizes:
            raise MemoryError()
        self.total_numerators = 0
        self.curr_denom = 0

    def __init__(self, owner, sim, bint refill, unsigned int N_numerators):
        super().__init__(
            owner,
            sim,
            Connections(),
            Connections()
        )
        self.signal.add_fill_function(mimo_fill, refill)

    def __dealloc__(self):
        if self.numerators:
            free(self.numerators)
        if self.numerator_sizes:
            free(self.numerator_sizes)

    @property
    def num_numerators(self):
        return self.total_numerators

    def set_denominator(self, double[::1] denom):
        self.denom = denom

    def add_numerator(self, double[::1] num):
        if self.total_numerators == self.N_num_allocd:
            raise Exception("Added more numerators than were allocated for.")
        self.numerators[self.total_numerators] = &num[0]
        self.numerator_sizes[self.total_numerators] = len(num)
        self.total_numerators += 1

    cpdef void set_s(self, complex_t s) noexcept:
        self.s = s
        self.curr_denom = eval_tf_term(s, &self.denom[0], len(self.denom))

    cpdef complex_t H(self, int numerator_idx) noexcept:
        if not (0 <= numerator_idx < self.total_numerators):
            raise Exception("Unexpected index")

        return eval_tf(
            self.s,
            self.numerators[numerator_idx],
            self.numerator_sizes[numerator_idx],
            self.curr_denom
        )


@cython.wraparound(False)
@cython.boundscheck(False)
@cython.initializedcheck(False)
cdef inline complex_t eval_tf_term(complex_t s, const double* coeffs, int N) noexcept:
    cdef:
        int i
        complex res = 0
    for i in range(N):
        res = res * s + coeffs[i]

    return res


@cython.wraparound(False)
@cython.boundscheck(False)
@cython.initializedcheck(False)
cdef inline complex_t eval_tf(complex_t s, const double* num, int N, complex_t den) noexcept:
    return eval_tf_term(s, num, N)/den


@cython.wraparound(False)
@cython.boundscheck(False)
@cython.initializedcheck(False)
cpdef eval_tf_vec(const complex_t[::1] s, const double[::1] num, const double[::1] den, complex_t[::1] out) :
    cdef:
        int i
        int N = len(s)
        int Nn = len(num)
        int Nd = len(den)

    if len(out) != len(s):
        raise Exception("Length of `s` differs from output `out`")

    for i in range(N):
        out[i] = eval_tf_term(s[i], &num[0], Nn)/eval_tf_term(s[i], &den[0], Nd)

    return 0

mimo_fill = FillFuncWrapper.make_from_ptr(c_mimo_fill)
@cython.wraparound(False)
@cython.boundscheck(False)
@cython.initializedcheck(False)
cdef c_mimo_fill(ConnectorWorkspace cws) :
    cdef MIMOTFWorkspace ws = <MIMOTFWorkspace>cws
    cdef complex_t s = 0
    cdef tuple key
    s.imag = 2 * PI * ws.sim.model_settings.fsig
    # Sets the complex s value for this step and precomputes the denominator
    ws.set_s(s)
    for i in range(ws.total_numerators):
        key = (ws.owner_id, i, 0, 0)
        if key in ws.sim.signal._submatrices:
            (<SubCCSView>ws.sim.signal._submatrices[key]).fill_negative_za(ws.H(i))


class FreeMassWorkspace(ConnectorWorkspace):
    pass


@float_parameter("mass", "Mass", units="kg")
@float_parameter("I_pitch", "Moment of inertia (pitch)", units="kg·m^2")
@float_parameter("I_yaw", "Moment of inertia (yaw)", units="kg·m^2")
class FreeMass(MechanicalConnector):
    """Simple free mass suspension of an object.

    The object being suspended must have a mechanical port with
    nodes z, pitch, and yaw and forces F_z, F_pitch, and F_yaw.
    """

    def __init__(self, name, connected_to, mass=np.inf, I_yaw=np.inf, I_pitch=np.inf):
        super().__init__(name, connected_to)
        self.mass = mass
        self.I_yaw = I_yaw
        self.I_pitch = I_pitch

        # We just have direct coupling between DOF, no cross-couplings
        self._register_node_coupling(
            "F_to_Z", self.mech.F_z, self.mech.z,
            enabled_check=lambda: float(self.mass) < np.inf or self.mass.is_changing
        )
        self._register_node_coupling(
            "F_to_YAW", self.mech.F_yaw, self.mech.yaw,
            enabled_check=lambda: float(self.I_yaw) < np.inf or self.I_yaw.is_changing
        )
        self._register_node_coupling(
            "F_to_PITCH", self.mech.F_pitch, self.mech.pitch,
            enabled_check=lambda: float(self.I_pitch) < np.inf or self.I_pitch.is_changing
        )
        # Define typical degrees of freedom for this component
        import types
        self.dofs = types.SimpleNamespace()
        self.dofs.z = LocalDegreeOfFreedom(f"{self.name}.dofs.z" ,None, self.mech.z, 1)
        self.dofs.F_z = LocalDegreeOfFreedom(f"{self.name}.dofs.F_z", None, self.mech.F_z, 1, AC_OUT=self.mech.z)
        self.dofs.yaw = LocalDegreeOfFreedom(f"{self.name}.dofs.yaw", None, self.mech.yaw, 1)
        self.dofs.F_yaw = LocalDegreeOfFreedom(f"{self.name}.dofs.F_yaw", None, self.mech.F_yaw, 1, AC_OUT=self.mech.yaw)
        self.dofs.pitch = LocalDegreeOfFreedom(f"{self.name}.dofs.pitch", None, self.mech.pitch, 1)
        self.dofs.F_pitch = LocalDegreeOfFreedom(f"{self.name}.dofs.F_pitch", None, self.mech.F_pitch, 1, AC_OUT=self.mech.pitch)


    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing or any(p.is_changing for p in self.parameters)
            ws = FreeMassWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            return ws
        else:
            return None

    def fill(self, ws):
        f = ws.sim.model_settings.fsig
        if ws.signal.connections.F_to_Z_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_Z_idx, 0, 0,
            ) as mat:
                mat[:] = -1 / (ws.values.mass * (2*PI*f)**2)

        if ws.signal.connections.F_to_YAW_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_YAW_idx, 0, 0,
            ) as mat:
                mat[:] = -1 / (ws.values.I_yaw * (2*PI*f)**2)

        if ws.signal.connections.F_to_PITCH_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_PITCH_idx, 0, 0,
            ) as mat:
                mat[:] = -1 / (ws.values.I_pitch * (2*PI*f)**2)


class PendulumMassWorkspace(ConnectorWorkspace):
    pass


@float_parameter("mass", "Mass", units="kg")
@float_parameter("Qz", "Qz", units="")
@float_parameter("fz", "fz", units="Hz")
@float_parameter("I_pitch", "Moment of inertia (pitch)", units="kg·m^2")
@float_parameter("Qyaw", "Qyaw", units="")
@float_parameter("fyaw", "fyaw", units="Hz")
@float_parameter("I_yaw", "Moment of inertia (yaw)", units="kg·m^2")
@float_parameter("Qpitch", "Qpitch", units="")
@float_parameter("fpitch", "fpitch", units="Hz")
class Pendulum(MechanicalConnector):
    """Simple pendulum suspension of an object.

    The object being suspended must have a mechanical port with
    nodes z, pitch, and yaw and forces F_z, F_pitch, and F_yaw.
    """

    def __init__(self, name, connected_to, mass=np.inf, Qz=1000, fz=1, I_yaw=np.inf, Qyaw=1000, fyaw=1, I_pitch=np.inf, Qpitch=1000, fpitch=1):
        super().__init__(name, connected_to)
        self.mass = mass
        self.Qz = Qz
        self.fz = fz
        self.Qyaw = Qyaw
        self.fyaw = fyaw
        self.Qpitch = Qpitch
        self.fpitch = fpitch
        self.I_yaw = I_yaw
        self.I_pitch = I_pitch

        # We just have direct coupling between DOF, no cross-couplings
        self._register_node_coupling(
            "F_to_Z", self.mech.F_z, self.mech.z,
            enabled_check=lambda: float(self.mass) < np.inf or self.mass.is_changing
        )
        self._register_node_coupling(
            "F_to_YAW", self.mech.F_yaw, self.mech.yaw,
            enabled_check=lambda: float(self.I_yaw) < np.inf or self.I_yaw.is_changing
        )
        self._register_node_coupling(
            "F_to_PITCH", self.mech.F_pitch, self.mech.pitch,
            enabled_check=lambda: float(self.I_pitch) < np.inf or self.I_pitch.is_changing
        )

        self.dofs = types.SimpleNamespace()
        self.dofs.z = LocalDegreeOfFreedom(
            f"{self.name}.dofs.z", None, self.mech.z, 1
        )
        self.dofs.F_z = LocalDegreeOfFreedom(
            f"{self.name}.dofs.F_z", None, self.mech.F_z, 1, AC_OUT=self.mech.z
        )
        self.dofs.pitch = LocalDegreeOfFreedom(
            f"{self.name}.dofs.pitch", None, self.mech.pitch, 1
        )
        self.dofs.F_pitch= LocalDegreeOfFreedom(
            f"{self.name}.dofs.F_pitch", None, self.mech.F_pitch, 1, AC_OUT=self.mech.pitch
        )
        self.dofs.yaw = LocalDegreeOfFreedom(
            f"{self.name}.dofs.yaw", None, self.mech.yaw, 1
        )
        self.dofs.F_yaw= LocalDegreeOfFreedom(
            f"{self.name}.dofs.F_yaw", None, self.mech.F_yaw, 1, AC_OUT=self.mech.yaw
        )

    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing or any(p.is_changing for p in self.parameters)
            ws = PendulumMassWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            return ws
        else:
            return None

    def fill(self, ws):
        cdef:
            complex_t s = 2j* PI * ws.sim.model_settings.fsig
            double omega0

        if ws.signal.connections.F_to_Z_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_Z_idx, 0, 0,
            ) as mat:
                omega0 = 2 * PI * ws.values.fz
                mat[:] = 1 / ws.values.mass * 1/(s**2  + s * omega0/ws.values.Qz + omega0**2)

        if ws.signal.connections.F_to_YAW_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_YAW_idx, 0, 0,
            ) as mat:
                omega0 = 2 * PI * ws.values.fyaw
                mat[:] = 1 / ws.values.I_yaw * 1/(s**2  + s * omega0/ws.values.Qyaw + omega0**2)

        if ws.signal.connections.F_to_PITCH_idx >= 0:
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, ws.signal.connections.F_to_PITCH_idx, 0, 0,
            ) as mat:
                omega0 = 2 * PI * ws.values.fpitch
                mat[:] = 1 / ws.values.I_pitch * 1/(s**2  + s * omega0/ws.values.Qpitch + omega0**2)


class SuspensionZPKWorkspace(ConnectorWorkspace):
    pass


class SuspensionZPK(MechanicalConnector):
    """A suspension that models multiple poles and zeros for the z, yaw, or pitch motion of an optic.
    The user must ensure that minus signs are correct for this transfer function as well as defining
    complex conjugae pairs for physically correct behaviour.

    ZPK terms are in units of radians/s.

    Parameters
    ----------
    name : str
        Element name
    connected_to : Element or mechanical port
        Mechanical port or element to attach this suspension to
    zpk_plant : dict
        Dictionary of {(output, input):(z,p,k)}

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import finesse
    >>> from finesse.components.mechanical import SuspensionZPK
    >>>
    >>> model = finesse.Model()
    >>> model.fsig.f = 1
    >>> model.parse("m m1 R=1 T=0")
    >>> zpk_plant = {}
    >>> # F_z to z (longitudinal force to displacement)
    >>> zpk_plant['z', 'F_z'] = ([], [10], 1)
    >>> model.add(SuspensionZPK('sus', model.m1.mech, zpk_plant))
    >>> out = model.run("frequency_response(geomspace(1m, 100, 100), m1.mech.F_z, m1.mech.z)")
    >>> plt.loglog(out.f, abs(out['m1.mech.F_z', 'm1.mech.z']))
    """

    def __init__(self, name, connected_to, zpk_plant):
        super().__init__(name, connected_to)
        self.zpk_plant = zpk_plant
        self.zpks = []

        for (output, input), zpk in zpk_plant.items():
            self._register_node_coupling(
                f"{input}_to_{output}",
                getattr(self.mech, input),
                getattr(self.mech, output),
            )
            self.zpks.append(zpk) # store ordered zpks

    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing
            ws = SuspensionZPKWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            ws.zpks = [(np.array(z), np.array(p), float(k)) for z,p,k in self.zpks]
            return ws
        else:
            return None

    def fill(self, ws):
        w = 2 * np.pi * ws.sim.model_settings.fsig

        for i, (z, p, k) in enumerate(ws.zpks):
            H = zpk_fresp(z, p, k, w)
            with ws.sim.signal.component_edge_fill3(
                ws.owner_id, i, 0, 0,
            ) as mat:
                mat[:] = H


class SuspensionTFPlant(Connector):
    """A customised suspension element that accepts arbitrary input and output
    nodes and a 2D array of `control.TransferFunction` objects that define
    a transfer function between each of them. See the Python Control package for
    more details on these.

    - Inputs and outputs must be named in the format `port.name`
    - Inputs must be unique to outputs
    - All plant transfer functions must have the same denominators

    The mechanical port of other optical elements can be connected to this suspension
    by using the `connections_to` dictionary input. This takes the name of a port
    defined in this suspension and maps it to the mechanical port of another element.

    The plant, inputs, and outputs cannot be changed once initialised. There is no
    KatScript interface for this component.

    Parameters
    ----------
    name : str
        Name of element
    inputs : array_like, list
        Sequence of inputs for this plant, should be strings of the format `port.node`
    outputs : array_like, list
        Sequence of outputs for this plant, should be strings of the format `port.node`
    plant : array_like, list[list]
        A 2D array of `control.TransferFunction` that describe the transfer function between
        each input to every output. Shape should be `[len(outputs), len(inputs)]`. Elements
        can also be `None` which means no coupling between each transfer function.
    connections_to : dict[str: SignalNode], optional
        Dict of port names at this suspension component and a mechanical port of some
        other element. Names of nodes at in each port should be identical. Keys of the
        dict should be in the format `port.node`. Values should be mechanical nodes of
        other elements.
    """

    def __init__(self, name, inputs, outputs, plant, connections_to=None):
        super().__init__(name)
        self.__inputs = np.atleast_1d(inputs).tolist()
        self.__outputs = np.atleast_1d(outputs).tolist()
        self.__plant = np.atleast_2d(plant).tolist()
        self.__connections_to = {} if connections_to is None else connections_to

        Ni = len(inputs)
        No = len(outputs)

        if len(inputs) != len(set(inputs)):
            raise ValueError("Inputs should all be unique")
        if len(outputs) != len(set(outputs)):
            raise ValueError("Outputs should all be unique")

        if not all(len(_.split(".")) == 2 for _ in inputs):
            raise ValueError("Inputs should all be in the format `port.node`")
        if not all(len(_.split(".")) == 2 for _ in outputs):
            raise ValueError("Outputs should all be in the format `port.node`")
        if np.array(plant).shape != (No, Ni):
            raise ValueError("Mechanical plant should be an N_outputs x N_inputs matrix of transfer functions")

        self.__input_indices = {n:i for i,n in enumerate(inputs)}
        self.__output_indices = {n:i for i,n in enumerate(outputs)}

        split_inputs = tuple(_.split(".") for _ in inputs)
        split_outputs = tuple(_.split(".") for _ in outputs)
        # Get the unique ports
        ports = list(set(port for port, _ in itertools.chain.from_iterable((split_inputs, split_outputs))))
        # replace with actual port
        ports = {port: self._add_port(port, NodeType.MECHANICAL) for port in ports}
        nodes = {}

        for port, node in itertools.chain.from_iterable((split_inputs, split_outputs)):
            p = ports[port]
            port_name = f"{port}.{node}"

            if port in connections_to:

                other_port = connections_to[port]
                if other_port.type != NodeType.MECHANICAL:
                    raise FinesseException(f"{other_port!r} is not a mechanical port")
                try:
                    other_node = other_port.node(node)
                except KeyError as ex:
                    raise FinesseException(f"Problem mapping `{port}.{node}` to {port!r}. It does not have a node called `{node}`.")
                if port_name in self.__input_indices:
                    self.__input_indices[other_node.port_name] = self.__input_indices[port_name]
                else:
                    self.__output_indices[other_node.port_name] = self.__output_indices[port_name]
                nodes[port_name] = p._add_node(node, None, other_node)
            else:
                nodes[port_name] = p._add_node(node, NodeDirection.BIDIRECTIONAL)

        for i, I in enumerate(inputs):
            for o, O in enumerate(outputs):
                # If there is a connection between the nodes...
                if plant[o][i] is not None and plant[o][i].dcgain():
                    self._register_node_coupling(
                        f"{I}__{O}".replace(".", "_"), nodes[I], nodes[O]
                    )

    def bode(self, f, input_node, output_node, **kwargs):
        """Make a bode plot for a particular node coupling for this suspension.
        See `finesse.plotting.bode` for the actual plotting method.
        """

        from finesse.plotting.plot import bode
        try:
            i = self.__input_indices[input_node]
        except KeyError as ex:
            i = self.__input_indices[input_node.port_name]
        try:
            o = self.__output_indices[output_node]
        except KeyError as ex:
            o = self.__output_indices[output_node.port_name]

        if self.plant[o][i] is None:
            raise FinesseException(f"No connection between {input_node!r} and  {output_node!r}")
        Y = np.squeeze(self.plant[o][i].horner(2j*np.pi*f))
        return bode(f, Y, **kwargs)

    @ property
    def connections_to(self):
        return self.__connections_to.copy()

    @property
    def inputs(self):
        return self.__inputs

    @property
    def outputs(self):
        return self.__outputs

    @property
    def plant(self):
        return self.__plant

    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing  # Need to recompute H(f)
            N = len(self._registered_connections)
            ws = MIMOTFWorkspace(self, sim, refill, N)
            den_set = False
            # All TFs should have same denominators
            for tf in itertools.chain.from_iterable(self.plant):
                if tf is not None:
                    den_set = True
                    ws.set_denominator(tf.den[0][0])
                    break
            if not den_set :
                raise FinesseException("No denominators for setting up MIMO workspace")
            # Setup the TFs for filling
            for j, (i, o) in enumerate(self._registered_connections.values()):
                i = self.nodes[i]
                o = self.nodes[o]
                idx = self.__input_indices[i.port_name]
                odx = self.__output_indices[o.port_name]
                # Check if these nodes are actually being modelled or not, might have
                # been removed if not needed.
                if i.full_name in sim.signal.nodes and o.full_name in sim.signal.nodes:
                    if self.plant[odx][idx] is not None:
                        ws.add_numerator(self.plant[odx][idx].num[0][0])
            return ws
        else:
            return None
