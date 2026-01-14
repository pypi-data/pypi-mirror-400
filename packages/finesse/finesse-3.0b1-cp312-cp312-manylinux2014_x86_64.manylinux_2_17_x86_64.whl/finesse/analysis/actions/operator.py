"""Operator based Actions to extract operators and perform operator based analyes, such
as calculating eigenmodes."""

from more_itertools import pairwise
from scipy.sparse import diags
import numpy as np

from ...components import Cavity
from ...solutions import BaseSolution
from .base import Action


class EigenmodesSolution(BaseSolution):
    """Contains the result of an Eigenmodes action. The start node is defined by the
    Cavity starting point.

    Attributes
    ----------
    connections : tuple((Node, Node))
        Node connections used in the round trip propagator

    roundtrip_matrix : array
        Combined round trip matrix operator for the cavity

    matrices : list[array]
        A list of operators for each connection

    eigvalues, eigvectors : array, array
        Eigen values and vectors of the round trip matrix

    cavity_planewave_loss : float
        Round trip loss for a planewave

    homs : array_like
        Array of HOMs used in the model at the time this was computed
    """

    def loss(self, remove_planewave_loss=False):
        """Computes the round trip loss of all the eigenmodes of the cavity. Eigenmodes
        are ordered by loss. Lowest loss may not be the fundamental mode.

        Parameters
        ----------
        remove_planewave_loss : bool, optional
            Whether to remove the roundtrip loss a plane wave would experience
            to see the loss induced from HOM effects.

        Returns
        -------
        index : array_like
            Indicies of ordering for the eigvalues and eigvectors of this solution
        loss : array_like
            Roundtrip loss of modes
        """
        idx = np.argsort(1 - abs(self.eigvalues) ** 2)
        eigx_values = self.eigvalues[idx]
        loss = 1 - abs(eigx_values) ** 2
        if remove_planewave_loss:
            loss = loss - self.cavity_planewave_loss
        return idx, loss

    def plot_roundtrip_loss(self, remove_planewave_loss=False, ax=None, **kwargs):
        """Plots the roundtrip loss of the cavity for each eigenmode.

        Parameters
        ----------
        remove_planewave_loss : bool, optional
            If True, remove the loss a planewave would experience to just see the
            effects from higher order modes.

        ax : Matplotlib.Axis, optional
            The axis to plot on to, if `None` a new figure is made

        **kwargs
            Keyword arguments passed to matplotlib.pyplot.semilogy for styling trace
        """
        import matplotlib.pyplot as plt

        if ax is not None:
            plt.sca(ax)

        idx = np.argsort(1 - abs(self.eigvalues) ** 2)
        eigx_values = self.eigvalues[idx]
        loss = 1 - abs(eigx_values) ** 2
        if remove_planewave_loss:
            loss = loss - self.cavity_planewave_loss

        plt.semilogy(loss / 1e-6, **kwargs)
        plt.xlabel("Eigenvalue index")
        if not remove_planewave_loss:
            plt.ylabel("Roundtrip loss [ppm]")
        else:
            plt.ylabel("Loss excess from planewave [ppm]")

    def plot_phase(self, scale=None, ax=None, **kwargs):
        """Plots the eigenmode phases.

        Parameters
        ----------
        scale : float
            Scale of scatter point size

        ax : Matplotlib.Axis, optional
            The axis to plot on to, if `None` a new figure is made

        **kwargs
            Keyword arguments passed to matplotlib.pyplot.scatter for styling trace
        """
        import matplotlib.pyplot as plt

        if ax is not None:
            plt.sca(ax)

        idx = np.argsort(1 - abs(self.eigvalues) ** 2)
        eigx_values = self.eigvalues[idx]
        eigx_phase = np.angle(eigx_values)
        eigx_phase = eigx_phase - eigx_phase[0]
        plt.scatter(np.arange(eigx_values.size), eigx_phase, scale, **kwargs)
        plt.xlabel("Eigenvalue index")
        plt.ylabel("Eigenvalue phase [rad]")

    def plot_field(
        self,
        mode_idx,
        *,
        x=None,
        y=None,
        samples=100,
        scale=3,
        ax=None,
        colorbar=True,
        **kwargs,
    ):
        """Plots a 2D optical field for one of the eigenmodes.

        x and y dimensions can be specified if required, otherwise it
        will return an area of `scale` times the spot sizes. When `x` and
        `y` are provided `scale` and `samples` will not do anything.

        Parameters
        ----------
        mode_idx : int
            index of the mode to plot
        x, y : ndarray, optional
            Specify x and y coordinates to plot beam
        samples : int, optional
            Number of sample points to use in x and y
        scale : float, optional
            Number of sample points to use in x and y
        ax : Axis, optional
            A Matplotlib axis to put the image on. If None,
            a new figure will be made.
        colorbar : bool
            When True the colorbar will be added
        **kwargs
            Extra keyword arguments will be passed to the
            pcolormesh plotting function.
        """
        from ...plotting import plot_field

        plot_field(
            modes=self.homs,
            amplitudes=self.eigvectors[:, mode_idx],
            qs=self.q,
            x=x,
            y=y,
            samples=samples,
            scale=scale,
            ax=ax,
            colorbar=colorbar,
            **kwargs,
        )


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Eigenmodes(Action):
    """For a given Cavity defined in a model, this action will compute the roundtrip
    operator and calculate the eigen-values and -vectors of the cavity. This will not
    give correct solutions for coupled cavities as these need to include additional
    effects.

    This can be used to determine what modes combination of modes are resonating in a
    cavity and the required tuning to make that mode resonate.

    Parameters
    ----------
    cavity : str or :class:`.Cavity`
        cavity name or :class:`.Cavity` instance
    frequency : float
        Optical carrier or signal frequency to use for calculating the operators
    name : str, optional
        Name of the solution generated by this action
    """

    def __init__(self, cavity: Cavity, frequency, *, name="eigenmodes"):
        super().__init__(name)
        self.cavity = cavity
        self.frequency = frequency

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        use_signal = False
        sim = state.sim
        model = state.model
        cav = model.elements[
            self.cavity if isinstance(self.cavity, str) else self.cavity.name
        ]
        # Get the connections (node) forming this cavity
        nodes = cav.path.nodes
        # need to complete the loop by adding the first element
        # to the end again
        nodes.append(nodes[0])
        f_idx = None
        # find the right frequency index
        for freq in state.sim.carrier.optical_frequencies.frequencies:
            if freq.f == float(self.frequency):
                f_idx = freq.index
                break

        if state.sim.signal is not None:
            for freq in state.sim.signal.optical_frequencies.frequencies:
                if freq.f == float(self.frequency):
                    use_signal = True
                    f_idx = freq.index
                    break

        if f_idx is None:
            raise RuntimeError(
                f"Could not find an optical carrier frequency with a value of {self.frequency}Hz"
            )

        sol = EigenmodesSolution(self.name)
        sol.cavity_planewave_loss = cav.loss
        sol.homs = model.homs.copy()
        sol.q = cav.source.q
        sol.connections = tuple(
            (n1.full_name, n2.full_name) for n1, n2 in pairwise(nodes)
        )
        sol.roundtrip_matrix = None
        sol.matrices = []
        # update sim
        if sim.is_modal:
            sim.modal_update()
        sim.carrier.refill()

        if use_signal:
            sim.signal.refill()
            sim_to_use = sim.signal
        else:
            sim_to_use = sim.carrier

        for _ in pairwise(nodes):
            # if we have a 1D array it's just a diagonal matrix
            # so convert it to a sparse array for easy multiplying
            # later
            if sim_to_use.connections[_][f_idx].view.ndim == 1:
                M = diags(sim_to_use.connections[_][f_idx][:])
            else:
                M = sim_to_use.connections[_][f_idx].view.copy()
            # Keep reference to each coupling we come across
            sol.matrices.append(M)
            # Compute roundtrip matrix as we go
            if sol.roundtrip_matrix is None:
                sol.roundtrip_matrix = M
            else:
                sol.roundtrip_matrix = M @ sol.roundtrip_matrix

        # Find eigen values and vectors of roundtrip
        sol.eigvalues, sol.eigvectors = np.linalg.eig(sol.roundtrip_matrix)
        return sol


class OperatorSolution(BaseSolution):
    connections: tuple[tuple[str, str], ...]
    operator: np.ndarray
    """Contains solution to the Operator action. The main result is the `operator`
    attribute which describes the operator taking the field from start to end node.

    Attributes
    ----------
    connections : [(Node, Node)]
        A list of node pairs describing the connections
        traversed to compute this operator

    operator : ndarray(ndim=2, dtype=complex)
        The operator describing the propagation from start
        to end node.
    """
    connections: tuple[tuple[str, str], ...]
    operator: np.ndarray


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Operator(Action):
    """This action can be used to extract operators out from a simulation for external
    use. The operators are defined by a path in the network between two nodes (via some
    other if more direction is required).

    The `model.path` method can be used to test which nodes are traversed before using
    this to extract operators if needed.

    Parameters
    ----------
    start_node : str
        Start node name
    end_node : str
        End node name
    via : str, optional
        Via node to use to specify a path with multiple options
    frequency : float, optional
        Optical carrier or signal frequency to use for calculating the operators
    name : str, optional
        Name of the solution generated by this action
    """

    def __init__(self, start_node, end_node, via=None, frequency=0, *, name="operator"):
        super().__init__(name)
        self.start_node = start_node
        self.end_node = end_node
        self.via = via
        self.frequency = frequency

    def _requests(self, model, memo, first=True):
        memo["input_nodes"].append(model.get(self.start_node))
        memo["output_nodes"].append(model.get(self.end_node))
        if self.via is not None:
            memo["input_nodes"].append(model.get(self.via))

    def _do(self, state):
        use_signal = False
        sim = state.sim
        model = state.model
        key = id(self)
        f_idx = None
        sol = OperatorSolution(self.name)
        # Try and get data already computed for this action
        ws = state.action_workspaces.get(key, None)
        if ws:
            nodes = ws["nodes"]
            connections = ws["connections"]
            f_idx = ws["f_idx"]
        else:
            try:
                frequency = float(self.frequency)
            except TypeError:
                frequency = float(self.frequency.value)
            # find the right frequency index
            for freq in state.sim.carrier.optical_frequencies.frequencies:
                if freq.f == frequency:
                    f_idx = freq.index
                    break

            if state.sim.signal is not None:
                for freq in state.sim.signal.optical_frequencies.frequencies:
                    if freq.f == float(self.frequency):
                        use_signal = True
                        f_idx = freq.index
                        break

            if f_idx is None:
                raise RuntimeError(
                    f"Could not find an optical carrier or signal frequency with a value of {self.frequency}Hz"
                )
            nodes = model.path(self.start_node, self.end_node, via_node=self.via).nodes
            connections = tuple(
                (n1.full_name, n2.full_name) for n1, n2 in pairwise(nodes)
            )
            ws = {
                "nodes": nodes,
                "connections": connections,
                "f_idx": f_idx,
            }
            state.action_workspaces[key] = ws

        # update sim
        if sim.is_modal:
            sim.modal_update()
        sim.carrier.refill()

        if use_signal:
            sim.signal.refill()
            sim_to_use = sim.signal
        else:
            sim_to_use = sim.carrier

        sol.connections = connections
        sol.operator = np.eye(sim.model_settings.num_HOMs)
        for _ in pairwise(nodes):
            # if we have a 1D array it's just a diagonal matrix
            # so convert it to a sparse array for easy multiplying
            # later
            # TODO can have some option to select between different
            # frequencies or signal/carrier at some point
            Mview = sim_to_use.connections[_]

            if Mview.ndim == 2:
                # We have a frequency scattering matrix
                # TODO : not sure on user interface for getting
                # different frequency couplings yet, for now it's
                # just same freq in and out
                M = Mview[f_idx, f_idx]
            else:
                # no frequency coupling
                M = Mview[f_idx]

            if M.view.ndim == 1:
                # TODO can probably write something faster
                # than making a sparse diagonal matrix here
                sol.operator = diags(M.view) @ (-sol.operator)
            else:
                sol.operator = M.view @ (-sol.operator)

        return sol
