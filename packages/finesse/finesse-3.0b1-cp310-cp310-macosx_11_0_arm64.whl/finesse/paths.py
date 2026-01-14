"""Containers for paths traversed through a configuration."""

from .utilities.tables import Table
from .symbols import simplification
from finesse.utilities.misc import deprecation_warning


class OpticalPath:
    """Represents a path traversing through optical connections of a :class:`.Model`
    instance.

    The underlying data stored by instances of this class are lists of two-element
    tuples containing optical nodes and the components that they connect into. This list
    is formatted as `[(from_node, to_comp)]` where `from_node` is an
    :class:`.OpticalNode` instance and `to_comp` can be any sub-class instance of
    :class:`.Connector`; `from_node` is then an input node to `to_comp`.

    A handle to the underlying list can be obtained through accessing the property
    :attr:`OpticalPath.data`. This is not required for iterating through the path
    entries however, as this class provides iterator access itself.

    Parameters
    ----------
    path : list
        A list of 2-tuples containing the path data; first element stores the
        :class:`.OpticalNode`, second element stores the component this node feeds into.

    symbolic : bool, optional
        Whether to compute symbolic lengths
    """

    def __init__(self, path, symbolic=False):
        self.__path = path
        self.symbolic = symbolic

    def __str__(self):
        return str(self.table())

    def table(self):
        """Show the components of the path in a table."""
        return Table(
            [("From optical node", "Into component")]
            + [(node.full_name, comp.name) for node, comp in self.__path],
            headerrow=True,
            headercolumn=False,
        )

    def __iter__(self):
        return iter(self.__path)

    def __next__(self):
        return next(self.__path)

    @property
    def data(self):
        """A handle to the underlying path data.

        :`getter`: Returns the list of 2-tuples containing the path data.
        """
        return self.__path

    @property
    def nodes(self):
        """The path data with only the :class:`.OpticalNode` sequence.

        :`getter`: Returns a list of the sequence of traversed optical nodes.
        """
        return [pair[0] for pair in self.__path]

    @property
    def nodes_only(self):
        """The path data with only the :class:`.OpticalNode` sequence.

        :`getter`: Returns a list of the sequence of traversed optical nodes.
        """
        deprecation_warning("Use .nodes instead of .nodes_only", "3.0")
        return self.nodes

    @property
    def components(self):
        """The path data with only the component sequence.

        :`getter`: Returns a list of the sequence of traversed components.
        """
        return [pair[1] for pair in self.__path if pair[1] is not None]

    @property
    def components_only(self):
        """The path data with only the component sequence.

        :`getter`: Returns a list of the sequence of traversed components.
        """
        deprecation_warning("Use .components instead of .components_only", "3.0")
        return self.components

    @property
    def spaces(self):
        """The spaces in the optical path.

        :`getter`: Yields the spaces in the optical path.
        """
        from finesse.components import Space

        for _, to_comp in self.__path:
            if isinstance(to_comp, Space):
                yield to_comp

    @property
    def optical_length(self):
        """This returns the optical path length, i.e. the geometric length of each space
        scaled by its refractive index.

        :`getter`: Returns the total traversed length of the optical path (in metres).
        """
        if self.symbolic:
            with simplification(allow_flagged=True):
                return sum([space.L.ref * space.nr.ref for space in self.spaces])
        else:
            return sum([space.L * space.nr for space in self.spaces])

    @property
    def physical_length(self):
        """This returns the physical path length.

        :`getter`: Returns the total length (in metres).
        """
        if self.symbolic:
            with simplification(allow_flagged=True):
                return sum([space.L.ref for space in self.spaces])
        else:
            return sum([space.L for space in self.spaces])
