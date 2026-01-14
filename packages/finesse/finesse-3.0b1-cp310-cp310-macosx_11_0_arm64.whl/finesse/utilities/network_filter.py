from __future__ import annotations

import abc
import warnings
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, Iterable

import networkx as nx

from finesse.components import Node
from finesse.components.general import ModelElement
from finesse.utilities import option_list
from finesse.utilities.text import get_close_matches

if TYPE_CHECKING:
    from finesse import Model


class NetworkType(Enum):
    OPTICAL = "optical"
    COMPONENT = "component"
    FULL = "full"

    @classmethod
    def _missing_(cls, value: object) -> NetworkType:
        name = str(value).lower().strip()
        for member in cls:
            if member.value == name:
                return member

        raise ValueError(
            f"'{value}' is not a valid {cls.__name__}, options: "
            f"{[str(val) for val in cls.__members__.values()]}"
        )

    def get_network(self, model: Model, add_edge_info: bool = False) -> nx.Graph:
        """Retrieve the relevant network for this network type.

        Parameters
        ----------
        model : Model
            Model to retrieve the netwrok from
        add_edge_info : bool, optional
            Add metadata to the component network on via which ports components are
            connected, by default False. Ignore for any type other than
            ``NetworkType.COMPONENT``

        Returns
        -------
        nx.Graph
            The relevant model graph

        Raises
        ------
        NotImplementedError
            If there is no implementation for newly added network types.
        """
        if self is NetworkType.FULL:
            if add_edge_info:
                warnings.warn("Ignoring 'add_edge_info'", stacklevel=2)
            return model.network
        elif self is NetworkType.COMPONENT:
            return model.to_component_network(add_edge_info)
        elif self is NetworkType.OPTICAL:
            if add_edge_info:
                warnings.warn("Ignoring 'add_edge_info'", stacklevel=2)
            # TODO optional copying to get an editable graph?
            return nx.DiGraph(model.optical_network)
        else:
            raise NotImplementedError

    @property
    def filter_class(self) -> type[NetworkFilterBase]:
        """Get the relevant filter class for this network type.

        Returns
        -------
        type[NetworkFilterBase]
            The relevant filter class
        """
        return {
            NetworkType.OPTICAL: OpticalNetworkFilter,
            NetworkType.COMPONENT: ComponentNetworkFilter,
            NetworkType.FULL: FullNetworkFilter,
        }[self]


@dataclass
class NetworkFilterBase(abc.ABC):
    """Abstract base class that implements distance based filtering of a model graph.
    Should mostly be used to directly call the ``run`` method after initialization, not
    guaranteed that the state makes sense if it is kept alive.

    Used by :meth:`.finesse.model.Model.plot_graph` and
    :meth:`.finesse.model.Model.component_tree`, see also their docstrings for more
    clarification on the arguments.
    """

    model: Model
    root: str | ModelElement | Node | None = None
    radius: int | None = None
    undirected: bool = True
    add_edge_info: bool = False
    add_detectors: bool = False
    network_type: ClassVar[NetworkType]

    def __post_init__(self):
        # triggers call to _check_root
        self.root_str

    @cached_property
    def root_str(self) -> str:
        """Transforms the ``root`` argument into a string that represents a node in the
        relevant graph. Must implement `_root_to_str` and `_root_options` in the
        subclass to makes this work.

        Returns
        -------
        str
            Root node as the string name in the graph
        """
        self._check_root(self._root_to_str, self._root_options)
        return self._root_to_str

    @cached_property
    @abc.abstractmethod
    def _root_to_str(self) -> str:
        # Convert whatever is passed as `root` argument to the name of the relevant
        # node in the graph.
        pass

    @cached_property
    @abc.abstractmethod
    def _root_options(self) -> Iterable[str]:
        # Options to pull suggestions from in case ``root`` is not found in the network
        pass

    def _check_root(self, root: str, options: Iterable[str]) -> None:
        if self.root is None and self.radius is None:
            return
        if root not in options:
            msg = f"Root '{root}' is not a valid root in '{self.network_type}' network"
            if suggestions := get_close_matches(root, options):
                suggestions_text = option_list(suggestions, quotechar="'", sort=True)
                msg += f"\n\nDid you mean {suggestions_text}?"
            raise KeyError(msg)

    @cached_property
    def network(self) -> nx.Graph:
        """
        Returns
        -------
        nx.Graph
            The relevant network for this filter
        """
        return self.network_type.get_network(self.model, self.add_edge_info)

    def _add_detectors(self) -> None:
        # Adds detector nodes and connects them to the relevant node in the network
        if not self.add_detectors:
            return
        for node in self.model.optical_nodes + self.model.signal_nodes:
            for detector in node.used_in_detector_output:
                node_name = self._convert_node(node)
                self.network.add_node(detector.name, **self._get_edge_info(node))
                self.network.add_edge(node_name, detector.name)

    @abc.abstractmethod
    def _convert_node(self, node: Node) -> str:
        # Pulls the relevant name from a Node, e.g. the component it belongs to in case
        # oc a component network
        pass

    def _get_edge_info(self, node: Node) -> dict[str, str]:
        return {}

    def _filter_by_radius(self) -> None:
        if self.radius is not None:
            if self.radius < 1:
                raise ValueError(
                    f"Radius must be a positive integer, not {self.radius}"
                )
            self.network = nx.generators.ego.ego_graph(
                self.network, self.root_str, self.radius, undirected=self.undirected
            )

    def run(self) -> nx.Graph:
        """Runs the filter and returns the filtered graph. Modifies ``self.network`` in
        place, so can not be called repeatedly.

        Returns
        -------
        nx.Graph
            The filtered graph.
        """
        self._add_detectors()
        self._filter_by_radius()
        return self.network


class ComponentNetworkFilter(NetworkFilterBase):
    network_type = NetworkType.COMPONENT

    @cached_property
    def _root_to_str(self) -> str:
        if self.root is None:
            from finesse.components import Laser

            if lasers := self.model.get_elements_of_type(Laser):
                return lasers[0].name
            else:
                if self.radius is None:
                    return ""
                else:
                    raise ValueError(
                        "No 'root' was passed and model contains no Lasers"
                    )

        elif isinstance(self.root, ModelElement):
            return self.root.name
        elif isinstance(self.root, str):
            return self.root
        else:
            raise TypeError(
                f"Root needs to be of type {ModelElement} or str, received {self.root}"
            )

    @cached_property
    def _root_options(self):
        return [comp.name for comp in self.model.components]

    def _convert_node(self, node: Node) -> str:
        return node.component.name

    def _get_edge_info(self, node: Node) -> dict[str, str]:
        if self.add_edge_info:
            node_name = self._convert_node(node)
            return {node_name: f"{node_name}.{node.port_name}"}
        else:
            return super()._get_edge_info(node)


class NodeNetworkFilter(NetworkFilterBase):

    def _convert_node(self, node: Node) -> str:
        return node.full_name

    @cached_property
    def _root_to_str(self) -> str:
        if isinstance(self.root, str):
            return self.root
        elif isinstance(self.root, Node):
            return self._convert_node(self.root)
        elif self.root is None and self.radius is None:
            return ""
        else:
            raise TypeError(
                f"Root needs to be of type {Node} or str, received {self.root}"
            )


class FullNetworkFilter(NodeNetworkFilter):
    network_type = NetworkType.FULL

    @cached_property
    def _root_options(self):
        return self.network.nodes


class OpticalNetworkFilter(NodeNetworkFilter):
    network_type = NetworkType.OPTICAL

    @cached_property
    def _root_options(self):
        return self.model.optical_network.nodes
