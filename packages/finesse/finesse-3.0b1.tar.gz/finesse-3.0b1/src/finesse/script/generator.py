"""Kat script generator."""

import logging
from io import StringIO
from functools import singledispatchmethod
from itertools import chain
from collections.abc import Iterable
import inspect

import numpy as np

from ..env import warn
from ..model import Model
from ..element import ModelElement
from ..parameter import Parameter, ParameterRef
from ..symbols import OPERATORS, FUNCTIONS, Function, Constant
from ..enums import ModulatorType
from ..components import Port, Node
from ..utilities.functools import flagdispatchmethod
from ..components.general import LocalDegreeOfFreedom
from ..analysis.actions import Action
from .containers import (
    KatCoordinate,
    KatToken,
    KatNumberToken,
    KatStringToken,
    KatWhitespaceToken,
    KatNoneToken,
    KatFixMeToken,
    KatScript,
    KatElement,
    KatFunction,
    KatKwarg,
    KatExpression,
    KatGroupedExpression,
    KatArray,
    FixMeValue,
)
from .tokens import LITERALS
from .adapter import ArgumentDump, ArgumentType, ElementDump, CommandDump, AnalysisDump
from .graph import ROOT_NODE_NAME, KatNodeType, KatEdgeType, KatGraph
from .util import scriptsorted, merge_attributes


LOGGER = logging.getLogger(__name__)


class _empty:
    """Represents an unset value.

    This exists for use when `None` is considered non-default.
    """


def _first_instruction_token(node_data):
    """Get the first occurring token in `node_data`.

    This is usually `node_data["token"]` but for e.g. grouped expressions it is the
    first "(" in `node_data["extra_tokens"]`.
    """
    tokens = []
    if token := node_data.get("token"):
        tokens.append(token)
    if extras := node_data.get("extra_tokens"):
        tokens.extend(extras)
    return next(iter(scriptsorted(tokens)))


class ElementContainer:
    """Container for top level model elements, used by the generator."""

    def __init__(self, element):
        self.element = element

    def __repr__(self):
        return f"<{self.__class__.__name__}({repr(self.element)})>"


class CommandContainer:
    """Container for top level commands, used by the generator."""

    def __init__(self, adapter, params):
        self.adapter = adapter
        self.params = params

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.adapter.full_name})>"


class KatUnbuilder:
    """Model to KatScript converter.

    This class defines single-dispatch methods to recursively fill Finesse objects into
    a :class:`.KatGraph`. The graph is then serialised to KatScript via
    :class:`.KatUnfiller`.

    The single-dispatch uses the type of the object to create appropriate nodes and
    edges in the :class:`.KatGraph`.

    Typically unbuilding starts with the passing of a :class:`.Model` to
    :meth:`~.KatUnbuilder.unbuild` or :meth:`~.KatUnbuilder.unbuild_file`. The
    single-dispatch method that handles models then extracts the elements, commands and
    analyses and passes them recursively to the same single-dispatch, whereupon matching
    fill methods further handle them. The underlying tokens that form Finesse objects
    are eventually reached by recursively calling the fill method, and these are added
    as terminal nodes in the graph and connected to their parents by edges.

    Special behaviour applies in some cases. One such case is the handling of objects
    from containers with corresponding type annotations specifying that they are
    :class:`.Parameter` objects. These are assumed to have *name* KatScript
    representation, rather than value. This is used for example in the dumping of axis
    parameters, which must be written as e.g. `xaxis(m1.phi, ...)` rather than `xaxis(0,
    ...)` (in the case that `m1.phi` has value `0`).
    """

    # Model element types not dumped.
    IGNORED_ELEMENTS = [
        # Models always contain an Fsig. The actual value is dumped as a command.
        "Fsig",
    ]

    # FIXME: move to KatSpec.
    UNARY_OPERATORS = {
        "pos": "+",
        "neg": "-",
    }

    # Reverse dicts for various types.
    LITERAL_MAP = dict((value, key) for key, value in LITERALS.items())

    def __init__(self, spec=None):
        if spec is None:
            from .spec import KATSPEC as spec

        self.spec = spec
        self.graph = None
        self._position = None
        self._stack = None  # Tracks _fill level.
        self._has_fixmes = False
        self.__tmp_regen_warnings = set()  # Warnings for not-yet-implemented regens.

    def unbuild(self, *args, **kwargs):
        fobj = StringIO()
        self.unbuild_file(fobj, *args, **kwargs)
        fobj.seek(0)
        return fobj.read()

    def unbuild_file(
        self,
        fobj,
        item,
        ref_graph=None,
        ref_node=None,
        directive_defaults=False,
        argument_defaults=False,
        prefer_keywords=True,
    ):
        """Generate KatScript for `item` and write to `fobj`.

        Parameters
        ----------
        fobj : :class:`io.FileIO`
            The file object to write KatScript to. This should be opened in text mode.

        item : object
            The object to generate KatScript for. This is normally a :class:`.Model` but
            can be any Finesse object.

        ref_graph : :class:`.KatGraph`, optional
            The reference syntax graph to use during KatScript generation. If specified,
            the nodes representing `item` and any Finesse objects contained therein will
            be copied and updated from it. This preserves formatting such as whitespace
            and comments.

        ref_node : :class:`str`, optional
            The reference node to use when unparsing `item`. This is only used if
            `ref_graph` is specified. If `ref_graph` is given but `ref_node` is not,
            `ref_node` is assumed to be the graph root. If the graph does not contain
            a root node, a :class:`ValueError` is raised.

        directive_defaults : :class:`bool`, optional
            Generate default elements, commands and actions even if they are set to
            their default values and would therefore generate Finesse objects in the
            same state when later parsed. If `ref_graph` is specified and an element,
            command or action is present as a node, however, it is generated regardless
            of whether its value is the default or not. Defaults to `False`.

        argument_defaults : :class:`bool`, optional
            Generate optional arguments that are set to their default values and would
            therefore generate Finesse objects in the same state when later parsed. If
            `ref_graph` is specified and a keyword argument is present as a node,
            however, it is generated regardless of whether its value is the default or
            not. Defaults to `False`.

        prefer_keywords : :class:`bool`, optional
            Prefer generating keyword arguments over positional arguments, where
            allowed. If a parameter can be a keyword argument, i.e. it is not
            positional-only, it is dumped as a keyword argument if this is `True`. This
            setting is ignored if `ref_node` is specified and a reference argument for
            the parameter is found (whereupon the original style is reused). Defaults to
            `True`.
        """
        self._stack = []

        if ref_graph is not None:
            if ref_node is None:
                # Let the user specify the starting node if they know what they're
                # doing.
                if ROOT_NODE_NAME not in ref_graph:
                    raise ValueError(
                        f"if ref_node is not specified, ref_graph must contain a root "
                        f"node named {ROOT_NODE_NAME}"
                    )
                ref_node = ROOT_NODE_NAME

            self._debug(
                f"using {repr(ref_graph)} at node {repr(ref_node)} as a reference to "
                f"unbuild {repr(item)}"
            )

        self.graph = KatGraph()
        self.ref_graph = ref_graph
        self.directive_defaults = directive_defaults
        self.argument_defaults = argument_defaults
        self.prefer_keywords = prefer_keywords
        self.position = KatCoordinate(1, 1)
        self._has_fixmes = False
        self.__tmp_regen_warnings.clear()

        # Fill the graph.
        if self._fill(item, ROOT_NODE_NAME, ref_node=ref_node):
            # Generate KatScript from the graph.
            unfiller = KatUnfiller()
            unfiller.unfill_file(fobj, ROOT_NODE_NAME, self.graph)
        else:
            self._debug(f"no script generated for {repr(item)}")

        # Trigger log messages for unimplemented intent-preserving unparsing behaviours.
        # This should be removed eventually once regeneration works for all KatScript
        # patterns.
        for msg in self.__tmp_regen_warnings:
            # User can't really do anything about this, so trigger a log message instead
            # of a proper warning.
            LOGGER.warning(msg)

        # Trigger a warning if a "fixme" value was dumped.
        if self._has_fixmes:
            warn(
                "The generated script contains invalid values. Search the script for "
                "__FIXME__ placeholders and replace appropriately."
            )

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._debug(f"setting position to {position}")
        self._position = position

    @property
    def lineno(self):
        return self.position.lineno

    @property
    def index(self):
        return self.position.index

    @property
    def _stackpos(self):
        return ".".join([t.__name__ for t in self._stack])

    def _debug(self, msg):
        if not LOGGER.isEnabledFor(logging.DEBUG):
            return
        caller = inspect.getouterframes(inspect.currentframe(), 2)[1][3]  # Sloooow.
        LOGGER.debug(f"[{self._stackpos}::{caller}] {msg}", stacklevel=2)

    def _fill(self, value, path, ref_node=None, **attributes):
        """Fill `value` into the graph at `path`, optionally reusing unchanged tokens
        from an existing graph node."""
        assert path not in self.graph
        self._stack.append(type(value))
        self._debug(f"filling {repr(value)} into graph at {repr(path)}")

        ref_extras = None
        if ref_node is not None:
            #  Get the reference node's extras.
            if node_extras := self.ref_graph.nodes[ref_node].get("extra_tokens"):
                # This object gets mutated by filling methods, so we therefore cast
                # it to a list so we don't run into issues with graph views,
                # generators, etc.
                ref_extras = list(scriptsorted(node_extras))

        if filled_attributes := self._do_fill(
            value, path, ref_node=ref_node, ref_extras=ref_extras
        ):
            attributes = merge_attributes(attributes, filled_attributes)
            self.graph.add_node(path, **attributes)
        else:
            self._debug(f"nothing to add for {value}")

        self._stack.pop()

        return attributes

    @singledispatchmethod
    def _do_fill(self, item, path, ref_node, ref_extras):
        """Get the attributes for `item` to be added to the corresponding node."""
        # This is the default dispatch when the type isn't recognised.
        raise NotImplementedError(
            f"don't know how to generate KatScript for {repr(item.__class__)}"
        )

    @_do_fill.register(Model)
    def _(self, model, path, ref_node, ref_extras):
        extra_tokens = []
        order = 0

        # Ask each registered adapter for its dumps from this model.
        element_dumps = {}
        for adapter in set(self.spec.elements.values()):
            if adapter.getter is None:
                continue

            self._debug(f"dumping items for {adapter.full_name}")
            for dump in adapter.getter(adapter, model):
                element_dumps[dump.element.name] = dump

        singular_function_dumps = {}
        nonsingular_function_dumps = []
        functions = set(self.spec.analyses.values()) | set(self.spec.commands.values())
        for adapter in functions:
            if adapter.getter is None:
                continue

            self._debug(f"dumping items for {adapter.full_name}")
            for dump in adapter.getter(adapter, model):
                if adapter.singular:
                    singular_function_dumps[adapter.full_name] = dump
                else:
                    nonsingular_function_dumps.append(dump)

        if ref_node is not None:
            for node, data in self.ref_graph.sorted_dependent_argument_nodes(
                ref_node, data=True
            ):
                if data["type"] is KatNodeType.ELEMENT:
                    element_name = data["name_token"].raw_value

                    try:
                        dump = element_dumps.pop(element_name)
                    except KeyError:
                        self._debug(
                            f"reference element {repr(element_name)} no longer present"
                        )
                        continue
                    else:
                        self._debug(
                            f"reference element {repr(element_name)} still present"
                        )
                elif data["type"] is KatNodeType.FUNCTION:
                    # Commands and analyses.
                    function_name = data["token"].raw_value
                    adapter = self.spec.function_directives[function_name]

                    if adapter.singular:
                        try:
                            dump = singular_function_dumps.pop(adapter.full_name)
                        except KeyError:
                            self._debug(
                                f"reference function {repr(function_name)} no longer "
                                f"present"
                            )
                            continue
                        else:
                            self._debug(
                                f"reference function {repr(function_name)} still "
                                f"present"
                            )
                    else:
                        self.__tmp_regen_warnings.add(
                            "Intent-preserving regeneration of KatScript for "
                            "nonsingular commands has not been implemented yet. These "
                            "have instead been generated using default formatting "
                            "(this does not affect the validity of the generated "
                            "KatScript)."
                        )
                        continue
                else:
                    raise ValueError("unexpected dependent argument node type")

                # Reuse any extra tokens specified in the argument's parent up until
                # `token`, ensuring there is a delimiter.
                extra_tokens.extend(
                    self._handle_script_arg_extras(order, data["token"], ref_extras)
                )

                argument_path = self.graph.item_node_name(order, path)
                if self._fill(dump, argument_path, node):
                    self.graph.add_edge(
                        argument_path, path, type=KatEdgeType.ARGUMENT, order=order
                    )

                    order += 1

        # Add any remaining extras.
        extra_tokens.extend(self._maybe_reuse_extras(ref_extras))

        ###
        # Now deal with stuff that was added since the last parse.
        ###

        if order > 0 and (
            element_dumps or singular_function_dumps or nonsingular_function_dumps
        ):
            # There were reference items dumped first. Add a comment to say that the
            # next items are new.
            extra_tokens.append(self._use_token(self._newline_token()))
            extra_tokens.append(
                self._use_token(
                    self._comment_token(
                        "Items below could not be matched to original script, or were "
                        "not present when the model was originally parsed."
                    )
                )
            )

        # Components, detectors, etc.
        # Dump the elements in the order in which they were added to the model.
        sorted_element_dumps = sorted(
            element_dumps.values(),
            # if item isn't in the element dict (a model parameter) then use -1?
            key=lambda dump: (
                model.element_order(dump.element)
                if dump.element in model.elements
                else -1
            ),
        )
        for element_dump in sorted_element_dumps:
            if order > 0:
                extra_tokens.append(self._use_token(self._newline_token()))

            element_path = self.graph.item_node_name(order, path)
            if self._fill(element_dump, element_path):
                self.graph.add_edge(
                    element_path, path, type=KatEdgeType.ARGUMENT, order=order
                )

                order += 1

        # Function dumps.
        for dump in chain(singular_function_dumps.values(), nonsingular_function_dumps):
            if order > 0:
                extra_tokens.append(self._use_token(self._newline_token()))

            function_path = self.graph.item_node_name(order, path)
            if self._fill(dump, function_path):
                self.graph.add_edge(
                    function_path, path, type=KatEdgeType.ARGUMENT, order=order
                )

                order += 1

        return {"type": KatNodeType.ROOT, "extra_tokens": extra_tokens}

    @_do_fill.register(ElementDump)
    def _(self, dump, path, ref_node, ref_extras):
        """Model element definitions."""
        if dump.element.__class__.__name__ in self.IGNORED_ELEMENTS:
            self._debug(f"skipping filling of ignored element {dump.element}")
            return

        # Ignore default values unless they were explicitly defined in the reference.
        if not self.directive_defaults and dump.is_default:
            self._debug(
                f"ignoring {repr(dump.item_name)} as its parameters are set to their "
                f"default values (set `directive_defaults` to change this behaviour)"
            )
            return

        extra_tokens = []

        if ref_node is not None:
            data = self.ref_graph.nodes[ref_node]
            ref_token = data["token"]
            ref_name_token = data["name_token"]

            token = self._reuse_token(ref_token)

            # Fill in extras between directive and name.
            extra_tokens.extend(
                self._maybe_reuse_extras(
                    ref_extras,
                    until_token=ref_name_token,
                )
            )

            name_token = self._reuse_token(ref_name_token)

            # Fill in the arguments.
            extra_tokens.extend(
                self._fill_element_args(
                    dump.parameters, path, ref_node=ref_node, ref_extras=ref_extras
                )
            )

            # Add any remaining extras.
            extra_tokens.extend(self._maybe_reuse_extras(ref_extras))
        else:
            token = self._use_token(self._name_token(dump.adapter.full_name))
            extra_tokens.append(self._use_token(self._space_token()))
            name_token = self._use_token(self._name_token(dump.element.name))
            extra_tokens.extend(self._fill_element_args(dump.parameters, path))

        return {
            "token": token,
            "name_token": name_token,
            "type": KatNodeType.ELEMENT,
            "extra_tokens": extra_tokens,
        }

    @_do_fill.register(AnalysisDump)
    @_do_fill.register(CommandDump)
    def _(self, dump, path, ref_node, ref_extras):
        # Ignore default values unless they were explicitly defined in the reference.
        if not self.directive_defaults and dump.is_default:
            self._debug(
                f"ignoring {repr(dump.item_name)} as its parameters are set to their "
                f"default values (set `directive_defaults` to change this behaviour)"
            )
            return

        if ref_node is not None:
            token = self._reuse_token(self.ref_graph.nodes[ref_node]["token"])
        else:
            token = self._use_token(self._name_token(dump.adapter.full_name))

        extra_tokens = self._fill_group(
            dump.parameters,
            path,
            "()",
            self._fill_function_args,
            ref_node=ref_node,
            ref_extras=ref_extras,
        )

        return {
            "token": token,
            "type": KatNodeType.FUNCTION,
            "extra_tokens": extra_tokens,
        }

    @_do_fill.register(Action)
    def _(self, action, path, ref_node, ref_extras):
        """A nested action.

        This is NOT for top level actions, which must be dumped as an
        :class:`.AnalysisDump` object.
        """
        # Ensure this isn't a top level action.
        assert path.count(".") > 1, "disallowed top level action"

        # Find the adapter willing to generate a dump for this action.
        for adapter in self.spec.analyses.values():
            if adapter.getter is None:
                continue

            try:
                return self._fill(
                    next(adapter.getter.dump(adapter, action)), path, ref_node
                )
            except StopIteration:
                pass

        raise NotImplementedError(
            f"don't know how to generate KatScript for {repr(action.__class__)}"
        )

    @_do_fill.register(ArgumentDump)
    def _(self, argument, path, ref_node, ref_extras):
        if argument.reference:
            # This represents a target that should be dumped by name.
            return {
                "token": self._maybe_reuse_value(
                    argument.value.full_name, self._name_token, ref_node=ref_node
                ),
                "type": KatNodeType.VALUE,
            }

        return self._fill(argument.value, path, ref_node)

    @_do_fill.register(Parameter)
    def _(self, parameter, path, ref_node, ref_extras):
        if parameter.is_externally_controlled:
            return self._fill(parameter._get_unset_value(), path, ref_node)
        else:
            return self._fill(parameter.value, path, ref_node)

    @_do_fill.register(ParameterRef)
    def _(self, reference, path, ref_node, ref_extras):
        if reference.parameter.is_default_for_owner:
            # We can generate without the ".value" part.
            value = reference.owner.name
        else:
            value = reference.name

        return {
            "token": self._maybe_reuse_value(
                value, self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.REFERENCE,
        }

    @_do_fill.register(ModelElement)
    def _(self, value, path, ref_node, ref_extras):
        """Reference to a model element.

        Model element definitions are matched as :class:`.ElementContainer`.
        """
        return {
            "token": self._maybe_reuse_value(
                value.name, self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(Port)
    @_do_fill.register(Node)
    def _(self, value, path, ref_node, ref_extras):
        return {
            "token": self._maybe_reuse_value(
                value.full_name, self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(LocalDegreeOfFreedom)
    def _(self, definition, path, ref_node, ref_extras):
        return {
            "token": self._maybe_reuse_value(
                definition.name, self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(ModulatorType)
    def _(self, mod_type, path, ref_node, ref_extras):
        return {
            "token": self._maybe_reuse_value(
                mod_type.name, self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(int)
    @_do_fill.register(np.integer)
    def _(self, value, path, ref_node, ref_extras):
        value = int(value)
        if value < 0:
            return self._fill(FUNCTIONS["neg"](abs(value)), path, ref_node)

        return {
            "token": self._maybe_reuse_value(
                value, self._number_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(float)
    @_do_fill.register(np.floating)
    def _(self, value, path, ref_node, ref_extras):
        # Kinda strange, but isinstance(np.nan, float) == True, so we need to deal with
        # that.
        if np.isnan(value):
            # Dump a "fixme" value instead.
            return self._fill(FixMeValue, path, ref_node)

        value = float(value)
        if value < 0:
            return self._fill(FUNCTIONS["neg"](abs(value)), path, ref_node)

        return {
            "token": self._maybe_reuse_value(
                value, self._number_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(complex)
    def _(self, value, path, ref_node, ref_extras):
        real = value.real
        imag = value.imag

        if not real:
            cplx = complex(f"{abs(imag)}j")
            if imag < 0:
                return self._fill(FUNCTIONS["neg"](cplx), path, ref_node)
            return {
                "token": self._maybe_reuse_value(
                    cplx, self._number_token, ref_node=ref_node
                ),
                "type": KatNodeType.VALUE,
            }
        elif not imag:
            if real < 0:
                return self._fill(FUNCTIONS["neg"](abs(real)), path, ref_node)
            return {
                "token": self._maybe_reuse_value(
                    real, self._number_token, ref_node=ref_node
                ),
                "type": KatNodeType.VALUE,
            }
        else:
            if real < 0:
                real = FUNCTIONS["neg"](abs(real))
            binop = OPERATORS["__add__"] if imag >= 0 else OPERATORS["__sub__"]
            return self._fill(binop(real, complex(f"{abs(imag)}j")), path, ref_node)

    @_do_fill.register(str)
    def _(self, value, path, ref_node, ref_extras):
        if value in self.spec.keywords:
            factory = self._name_token
        else:
            factory = self._string_token

        return {
            "token": self._maybe_reuse_value(value, factory, ref_node=ref_node),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(bool)
    @_do_fill.register(np.bool_)
    def _(self, value, path, ref_node, ref_extras):
        return {
            "token": self._maybe_reuse_value(
                "true" if value else "false", self._name_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(type(None))
    def _(self, value, path, ref_node, ref_extras):
        return {
            "token": self._maybe_reuse_value(None, self._none_token, ref_node=ref_node),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(type(FixMeValue))
    def _(self, value, path, ref_node, ref_extras):
        self._has_fixmes = True

        return {
            "token": self._maybe_reuse_value(
                FixMeValue, self._fixme_token, ref_node=ref_node
            ),
            "type": KatNodeType.VALUE,
        }

    @_do_fill.register(Iterable)
    def _(self, array, path, ref_node, ref_extras):
        extra_tokens = self._fill_group(
            array,
            path,
            "[]",
            self._fill_inline_function_args,
            ref_node=ref_node,
            ref_extras=ref_extras,
        )
        return {"type": KatNodeType.ARRAY, "extra_tokens": extra_tokens}

    @_do_fill.register(Constant)
    def _(self, constant, path, ref_node, ref_extras):
        return self._fill(constant.eval(), path, ref_node)

    @_do_fill.register(Function)
    def _(self, operation, path, ref_node, ref_extras):
        op = operation.name
        extra_tokens = []

        def make_arg(argument, order):
            argument_path = self.graph.item_node_name(order, path)

            # FIXME: add ref_node (should be the argument order child of ref_node, but
            # this is not guaranteed to exist so needs special handling)
            self._fill(argument, argument_path)
            self.graph.add_edge(
                argument_path, path, type=KatEdgeType.ARGUMENT, order=order
            )

        if ref_node is not None:
            self.__tmp_regen_warnings.add(
                "Intent-preserving regeneration of KatScript for operations has not "
                "been implemented yet. These have instead been generated using default "
                "formatting (this does not affect the validity of the generated "
                "KatScript)."
            )

        if op in self.spec.binary_operators:
            if len(operation.args) > 2:
                LOGGER.debug(f"Converting n-ary expression {repr(operation)} to binary")
                operation = operation.to_binary_add_mul()

            assert len(operation.args) == 2
            extra_tokens.append(self._use_token(self._literal_token("(")))
            make_arg(operation.args[0], 0)
            token = self._use_token(self._literal_token(op))
            nodetype = KatNodeType.EXPRESSION
            make_arg(operation.args[1], 1)
            extra_tokens.append(self._use_token(self._literal_token(")")))
        elif unary_op := self.UNARY_OPERATORS.get(op):
            token = self._use_token(self._literal_token(unary_op))
            nodetype = KatNodeType.FUNCTION
            make_arg(operation.args[0], 0)
        elif op in self.spec.expression_functions:
            token = self._use_token(self._name_token(op))
            nodetype = KatNodeType.FUNCTION
            extra_tokens.append(self._use_token(self._literal_token("(")))
            for order, argument in enumerate(operation.args):
                if order > 0:
                    extra_tokens.append(self._use_token(self._literal_token(",")))
                    extra_tokens.append(self._use_token(self._space_token()))
                make_arg(argument, order)
            extra_tokens.append(self._use_token(self._literal_token(")")))
        else:
            raise NotImplementedError(
                f"don't know how to generate KatScript for {repr(op)}"
            )

        return {"token": token, "type": nodetype, "extra_tokens": extra_tokens}

    def _maybe_reuse_value(self, ensure_value, value_factory, ref_node=None):
        """Reuse reference value at `ref_node` if it matches `ensure_value`, otherwise
        create a new token using `value_factory`.

        Returns
        -------
        :class:`.KatToken`
            The token.
        """
        if self.ref_graph and ref_node:
            data = self.ref_graph.nodes[ref_node]

            # The originally parsed string.
            ref_value = data["token"].raw_value

            if ensure_value == data["token"].value:  # NOT raw value!
                self._debug(f"value ({repr(ref_value)}) unchanged")
                return self._reuse_token(data["token"])
            else:
                self._debug(
                    f"value changed from {repr(ref_value)} to {repr(ensure_value)})"
                )

        return self._use_token(value_factory(ensure_value))

    def _maybe_reuse_extras(self, extras, until_token=None, ensure_literal=_empty):
        """Reuse tokens in `extras` in order until `until_token` token position is
        encountered, optionally ensuring `ensure_literal` is present (creating a new
        token using :meth:`._literal_token` if not).

        The `extras` object passed in to this method, if not None, is mutated.

        Yields
        ------
        :class:`.KatToken`
            Reused extra token.
        """
        if not self.ref_graph or not extras:
            extras = []

        seen_value = False

        while extras:
            if until_token and extras[0].start >= until_token.start:
                break

            token = extras.pop(0)

            if ensure_literal == token.value:  # NOT raw value!
                seen_value = True

            yield self._reuse_token(token)

        if ensure_literal is not _empty and not seen_value:
            # We've not seen `ensure_literal` yet, so create one.
            yield self._use_token(self._literal_token(ensure_literal))

    def _use_token(self, token):
        """Put a copy of `token` at the current position, updating the current position
        to the end of the token."""
        out = token.to_new_position(self.position)
        self._debug(f"adding token {out} @ {out.bounds}")

        if nlines := token.raw_value.count("\n"):
            self.position = KatCoordinate(self.lineno + nlines, 1)
        else:
            self.position = out.stop

        return out

    def _reuse_token(self, token):
        self._debug(f"reusing reference token {token} originally @ {token.bounds}")
        return self._use_token(token)

    def _name_token(self, value):
        return KatToken(0, 0, len(value), "NAME", value)

    def _space_token(self, length=1):
        return KatWhitespaceToken(0, 0, length, "WHITESPACE", " " * length)

    def _number_token(self, value):
        value = str(value)
        return KatNumberToken(0, 0, len(value), "NUMBER", value)

    def _string_token(self, value):
        value = repr(value)
        return KatStringToken(0, 0, len(value), "STRING", value)

    def _none_token(self, value):
        assert value is None
        value = "none"
        return KatNoneToken(0, 0, len(value), "NONE", value)

    def _fixme_token(self, value):
        assert value == FixMeValue
        value = "__FIXME__"
        return KatFixMeToken(0, 0, len(value), "FIXME", value)

    def _literal_token(self, literal):
        return KatToken(0, 0, len(literal), self.LITERAL_MAP[literal], literal)

    def _newline_token(self, count=1):
        value = "\n" * count
        return KatToken(0, 0, len(value), "NEWLINE", value)

    def _comment_token(self, comment):
        value = f"# {comment}"
        return KatToken(0, 0, len(value), "COMMENT", value)

    def _fill_element_args(self, parameters, path, **kwargs):
        return self._fill_directive_args(
            parameters, path, self._delimit_element_arg, **kwargs
        )

    def _fill_function_args(self, parameters, path, **kwargs):
        return self._fill_directive_args(
            parameters, path, self._delimit_function_arg, **kwargs
        )

    def _fill_directive_args(
        self, parameters, path, delimiter_handler, ref_node=None, **kwargs
    ):
        """Fill a directive's arguments."""
        ref_args, ref_kwargs = self._directive_ref_args(parameters, ref_node)
        arg_map, var_arg, kwarg_map, var_kwarg = self._deal_dump_parameters(
            parameters,
            prefer_keywords=self.prefer_keywords,
            ref_args=ref_args,
            ref_kwargs=ref_kwargs,
        )

        return self._fill_delimited_args(
            arg_map,
            var_arg,
            kwarg_map,
            var_kwarg,
            path,
            ref_args=ref_args,
            ref_kwargs=ref_kwargs,
            delimiter_handler=delimiter_handler,
            **kwargs,
        )

    def _fill_inline_function_args(self, items, path, ref_node=None, **kwargs):
        """Fill inline function arguments, e.g. those of an array or expression
        function.

        Inline functions always use positional arguments.
        """
        ref_args = self._inline_ref_args(items, ref_node)

        # The function filler expects a dict. Give each item a key that can be used to
        # determine whether a reference item exists.
        items = {index: item for index, item in enumerate(items)}

        # Expression functions always use positional arguments.
        return self._fill_delimited_args(
            items,
            None,
            {},
            None,
            path,
            delimiter_handler=self._delimit_function_arg,
            ref_args=ref_args,
            **kwargs,
        )

    def _fill_group(
        self, arguments, path, delimiters, argument_filler, ref_node, ref_extras
    ):
        """Fill a literal-delimited group containing arguments.

        "Literal-delimited" means that the group's outer delimiters are literal
        characters like "(" and ")" or "[" and "]".
        """
        opening_delimiter, closing_delimiter = delimiters
        assert len(opening_delimiter) == len(closing_delimiter) == 1

        def opening_delimiter_from_extras():
            """Grab the opening delimiter for this group from the reference extras, if
            found."""
            nonlocal ref_extras

            if not ref_extras:
                return

            # Assume the opening delimiter is the first extra.
            first_extra = ref_extras.pop(0)

            assert first_extra.raw_value == opening_delimiter
            return first_extra

        extra_tokens = []

        if first_extra := opening_delimiter_from_extras():
            extra_tokens.append(self._reuse_token(first_extra))
        else:
            extra_tokens.append(self._use_token(self._literal_token(opening_delimiter)))

        # Fill in the arguments.
        extra_tokens.extend(
            argument_filler(arguments, path, ref_node=ref_node, ref_extras=ref_extras)
        )

        # Fill in any remaining extras, ensuring there's a closing delimiter.
        extra_tokens.extend(
            self._maybe_reuse_extras(ref_extras, ensure_literal=closing_delimiter)
        )

        return extra_tokens

    def _directive_ref_args(self, parameters, ref_node):
        ref_args = {}
        ref_kwargs = {}

        # Check if any of the originally parsed arguments are still present.
        if ref_node is not None:
            ref_arguments = self.ref_graph.sorted_dependent_argument_nodes(
                ref_node, data=True
            )

            directive_name = self.ref_graph.nodes[ref_node]["token"].raw_value
            adapter = self.spec.directives[directive_name]

            for position, (node, data) in enumerate(ref_arguments, start=1):
                if key_token := data.get("key_token"):
                    # This is a keyword argument.
                    name = key_token.raw_value
                    if name in parameters:
                        self._debug(
                            f"reference keyword argument {repr(name)} still present"
                        )
                        ref_kwargs[name] = node, data
                else:
                    # This is a positional argument. Figure out the name.
                    argument = self.ref_graph.argument(node, adapter)
                    if argument.name in parameters:
                        self._debug(
                            f"reference positional argument {repr(argument.name)} "
                            f"(position {position}) still present"
                        )
                        ref_args[argument.name] = node, data

        return ref_args, ref_kwargs

    def _inline_ref_args(self, items, ref_node):
        ref_args = {}

        # Check if any of the originally parsed arguments are still present.
        if ref_node is not None:
            ref_arguments = self.ref_graph.sorted_dependent_argument_nodes(
                ref_node, data=True
            )

            for position, (node, data) in enumerate(ref_arguments):
                ref_args[position] = node, data

        return ref_args

    def _deal_dump_parameters(
        self, parameters, prefer_keywords, ref_args=None, ref_kwargs=None
    ):
        """Split mapping of parameters to :class:`.ArgumentDump` in `parameters` into
        positional and keyword argument mappings depending on `prefer_keywords`."""
        positional = {}
        keyword = {}

        if ref_args is None:
            ref_args = {}
        if ref_kwargs is None:
            ref_kwargs = {}

        var_pos = None
        var_keyword = None

        # Check if there is a variadic positional argument. If there is, then any
        has_var_pos = any(
            p.kind is ArgumentType.VAR_POS and p.value for p in parameters.values()
        )

        for arg, dump_param in parameters.items():
            if dump_param.kind is ArgumentType.POS_ONLY:
                positional[arg] = dump_param
            elif dump_param.kind is ArgumentType.KEYWORD_ONLY:
                # Ignore default values unless they were explicitly defined in the
                # reference.
                if (
                    not self.argument_defaults
                    and arg not in ref_kwargs
                    and dump_param.is_default
                ):
                    self._debug(
                        f"ignoring keyword-only argument {repr(arg)} as it is set to "
                        f"its default value (set `argument_defaults` to change this "
                        f"behaviour)"
                    )
                    continue

                keyword[arg] = dump_param
            elif dump_param.kind is ArgumentType.ANY:
                # If there is a variadic positional argument, this has to be positional.
                # Otherwise, if the arg was previously parsed with a certain style, use
                # that. If not, use the preferred form. Furthermore, ignore default
                # values unless they were explicitly defined in the reference.
                if has_var_pos:
                    use_keyword = False
                elif arg in ref_args:
                    use_keyword = False
                elif arg in ref_kwargs:
                    use_keyword = True
                else:
                    use_keyword = prefer_keywords

                if use_keyword:
                    keyword[arg] = dump_param
                else:
                    positional[arg] = dump_param
            elif dump_param.kind is ArgumentType.VAR_POS:
                var_pos = dump_param
            elif dump_param.kind is ArgumentType.VAR_KEYWORD:
                var_keyword = dump_param
            else:
                raise RuntimeError(f"unhandled param kind {repr(dump_param.kind)}")

        if not self.argument_defaults:
            # Remove any trailing default positional arguments. Looping in reverse
            # order lets us remove defaults on the end but keep those between
            # non-defaults.
            for arg, dump_param in reversed(list(positional.items())):
                if arg not in ref_args and dump_param.is_default:
                    self._debug(
                        f"ignoring trailing positional argument {repr(arg)} as it "
                        f"is set to its default value (set `argument_defaults` to "
                        f"change this behaviour)"
                    )

                    del positional[arg]
                else:
                    # We've reached the first non-default positional argument.
                    break

            for kwarg, dump_param in list(keyword.items()):
                if kwarg not in ref_kwargs and dump_param.is_default:
                    self._debug(
                        f"ignoring keyword argument {repr(kwarg)} as it is set to "
                        f"its default value (set `argument_defaults` to change this "
                        f"behaviour)"
                    )

                    del keyword[kwarg]

        return positional, var_pos, keyword, var_keyword

    def _fill_delimited_args(
        self,
        positional,
        var_positional,
        keyword,
        var_keyword,
        path,
        delimiter_handler,
        ref_args=None,
        ref_kwargs=None,
        ref_extras=None,
    ):
        """Fill arguments, either generating new or reusing existing delimiters.

        If `ref_node` is given, the tokens at this node are reused if unchanged,
        otherwise those that have changed are generated anew with default formatting.
        """
        if ref_args is None:
            ref_args = {}
        if ref_kwargs is None:
            ref_kwargs = {}

        self._debug(
            f"Fill delimited argument inputs: {positional=}, {var_positional=}, "
            f"{keyword=}, {var_keyword=}, {ref_args=}, {ref_kwargs=}"
        )

        extra_tokens = []
        order = 0

        # Fill positional arguments.
        for name, value in positional.items():
            arg_ref_node = None
            arg_ref_extras = None
            first_arg_token = None

            if name in ref_args:
                # Reuse delimiter and extras up to the argument's first token.
                arg_ref_node, arg_ref_data = ref_args[name]
                arg_ref_extras = arg_ref_data.get("extra_tokens")
                first_arg_token = _first_instruction_token(arg_ref_data)

            # Reuse any extra tokens specified in the argument's parent up until
            # `token`, ensuring there is a delimiter.
            extra_tokens.extend(
                delimiter_handler(
                    order, until_token=first_arg_token, ref_extras=ref_extras
                )
            )

            self._fill_arg(value, order, path, arg_ref_node, arg_ref_extras)
            order += 1

        if var_positional:
            for value in var_positional.value:
                arg_ref_node = None
                arg_ref_extras = None

                # FIXME: implement reference dumping for variadic positional arguments.

                # Reuse any extra tokens specified in the argument's parent up until
                # `token`, ensuring there is a delimiter.
                extra_tokens.extend(delimiter_handler(order, ref_extras=ref_extras))

                self._fill_arg(value, order, path, arg_ref_node, arg_ref_extras)
                order += 1

        # Fill keyword arguments.
        for name, value in keyword.items():
            arg_ref_node = None
            arg_ref_extras = None
            first_arg_token = None

            if name in ref_kwargs:
                # Reuse delimiter and extras up to the argument's first token.
                arg_ref_node, arg_ref_data = ref_kwargs[name]
                arg_ref_extras = arg_ref_data.get("extra_tokens")
                first_arg_token = _first_instruction_token(arg_ref_data)

            # Reuse any extra tokens specified in the argument's parent up until
            # `token`, ensuring there is a delimiter.
            extra_tokens.extend(
                delimiter_handler(
                    order, until_token=first_arg_token, ref_extras=ref_extras
                )
            )

            self._fill_kwarg(name, value, order, path, arg_ref_node, arg_ref_extras)
            order += 1

        if var_keyword:
            for name, value in var_keyword.value.items():
                arg_ref_node = None
                arg_ref_extras = None

                # FIXME: implement reference dumping for variadic keyword arguments.

                # Reuse any extra tokens specified in the argument's parent up until
                # `token`, ensuring there is a delimiter.
                extra_tokens.extend(delimiter_handler(order, ref_extras=ref_extras))

                self._fill_kwarg(name, value, order, path, arg_ref_node, arg_ref_extras)
                order += 1

        return extra_tokens

    def _handle_script_arg_extras(self, order, until_token=None, ref_extras=None):
        """Yield element style extras, ensuring at least one delimiter is present,
        creating it if necessary."""
        has_delimiter = False

        if until_token and ref_extras:
            for extra in self._maybe_reuse_extras(ref_extras, until_token=until_token):
                if extra.type == "NEWLINE":
                    has_delimiter = True
                yield extra

        # Only prepend a delimiter if this isn't the first argument.
        if order > 0 and not has_delimiter:
            yield self._use_token(self._newline_token())

    def _delimit_element_arg(self, order, until_token=None, ref_extras=None):
        """Yield element style extras, ensuring at least one delimiter is present,
        creating it if necessary."""
        has_delimiter = False

        if until_token and ref_extras:
            for extra in self._maybe_reuse_extras(ref_extras, until_token=until_token):
                if extra.type == "WHITESPACE":
                    has_delimiter = True
                yield extra

        # Always prepend a delimiter because the whitespace between the name and first
        # argument is not added by the element filler.
        if not has_delimiter:
            yield self._use_token(self._space_token())

    def _delimit_function_arg(self, order, until_token=None, ref_extras=None):
        """Yield functional style extras, ensuring at least one delimiter is present,
        creating it if necessary."""
        has_delimiter = False

        if until_token and ref_extras:
            for extra in self._maybe_reuse_extras(ref_extras, until_token=until_token):
                if extra.type == "COMMA":
                    has_delimiter = True
                yield extra

        # Only prepend a delimiter if this isn't the first argument.
        if order > 0 and not has_delimiter:
            yield self._use_token(self._literal_token(","))
            yield self._use_token(self._space_token())

    def _fill_arg(self, value, order, path, ref_node, ref_extras):
        argument_path = self.graph.item_node_name(order, path)
        self._fill(value, argument_path, ref_node)
        self.graph.add_edge(argument_path, path, type=KatEdgeType.ARGUMENT, order=order)

    def _fill_kwarg(self, key, value, order, path, ref_node, ref_extras):
        if ref_node is not None:
            data = self.ref_graph.nodes[ref_node]

            # Reuse the key and '='.
            key_token = self._reuse_token(data["key_token"])
            equals_token = self._reuse_token(data["equals_token"])
        else:
            key_token = self._use_token(self._name_token(key))
            equals_token = self._use_token(self._literal_token("="))

        argument_path = self.graph.item_node_name(order, path)
        self._fill(
            value,
            argument_path,
            ref_node,
            key_token=key_token,
            equals_token=equals_token,
        )
        self.graph.add_edge(argument_path, path, type=KatEdgeType.ARGUMENT, order=order)


class KatUnfiller:
    """KatGraph to kat script."""

    def unfill(self, node, graph):
        fobj = StringIO()
        self.unfill_file(fobj, node, graph)
        fobj.seek(0)
        return fobj.read()

    def unfill_file(self, fobj, node, graph):
        production = self.production(node, graph)
        unparser = KatUnparser()
        unparser.unparse_file(fobj, production)

    def production(self, node, graph):
        data = graph.nodes[node]

        # Create any dependent arguments.
        arguments = scriptsorted(
            [
                self.production(argument_node, graph)
                for argument_node in graph.dependent_argument_nodes(node)
            ]
        )
        # Grab any extra tokens.
        extra = scriptsorted(data.get("extra_tokens", []))

        value = self._do_production(data["type"], data, arguments, extra)

        # Detect kwargs.
        if "key_token" in data:
            value = KatKwarg(
                key=data["key_token"], equals=data["equals_token"], value=value
            )

        return value

    @flagdispatchmethod
    def _do_production(self, nodetype, data, arguments, extra):
        raise NotImplementedError(f"unhandled KatGraph node type {repr(nodetype)}")

    @_do_production.register(KatNodeType.ROOT)
    def _(self, data, arguments, extra):
        return KatScript(arguments=arguments, extra=extra)

    @_do_production.register(KatNodeType.GENERATOR_TERMINAL_NODES)
    def _(self, data, arguments, extra):
        return data["token"]

    @_do_production.register(KatNodeType.ELEMENT)
    def _(self, data, arguments, extra):
        return KatElement(
            directive=data["token"],
            arguments=arguments,
            extra=extra,
            name=data.get("name_token"),
        )

    @_do_production.register(KatNodeType.FUNCTION)
    def _(self, data, arguments, extra):
        return KatFunction(directive=data["token"], arguments=arguments, extra=extra)

    @_do_production.register(KatNodeType.GROUPED_EXPRESSION)
    def _(self, data, arguments, extra):
        return KatGroupedExpression(arguments=arguments, extra=extra)

    @_do_production.register(KatNodeType.EXPRESSION)
    def _(self, data, arguments, extra):
        return KatExpression(operator=data["token"], arguments=arguments, extra=extra)

    @_do_production.register(KatNodeType.ARRAY)
    def _(self, data, arguments, extra):
        return KatArray(arguments=arguments, extra=extra)


class KatUnparser:
    """TokenContainer to kat script."""

    def unparse(self, container):
        fobj = StringIO()
        self.unparse_file(fobj, container)
        fobj.seek(0)
        return fobj.read()

    def unparse_file(self, fobj, container):
        untokenizer = KatUntokenizer()
        untokenizer.untokenize_file(fobj, container.sorted_tokens)


class KatUntokenizer:
    """Token to kat script."""

    def untokenize(self, tokens):
        fobj = StringIO()
        self.untokenize_file(fobj, tokens)
        fobj.seek(0)
        return fobj.read()

    def untokenize_file(self, fobj, tokens):
        for token in tokens:
            fobj.write(token.raw_value)
