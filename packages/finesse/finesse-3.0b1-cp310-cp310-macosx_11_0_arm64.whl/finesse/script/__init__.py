"""Parsing and unparsing of Finesse kat files and models."""

import inspect
import pydoc
import re
import textwrap
from fnmatch import fnmatch
from functools import reduce

from spellchecker import SpellChecker

from ..env import INDENT, TERMINAL_WIDTH
from ..parameter import parameterproperty
from ..utilities import opened_file
from .spec import KATSPEC

# Match fnmatch wildcards.
WILDCARDS_PATTERN = re.compile(r"[\*\?]|\[.*\]")


def parse(text, model=None, spec=None):
    """Parse KatScript into a model.

    Parameters
    ----------
    text : str
        The KatScript to parse.

    model : :class:`.Model`, optional
        The Finesse model to add the parsed objects to. Defaults to a new, empty model.

    spec : :class:`.KatSpec`, optional
        The language specification to use. Defaults to the shared :class:`.KatSpec`
        instance.

    Returns
    -------
    :class:`.Model`
        The parsed model.
    """
    from .compiler import KatCompiler

    compiler = KatCompiler(spec=spec)
    return compiler.compile(text, model=model)


def parse_file(path, model=None, spec=None):
    """Parse KatScript from a file into a model.

    Parameters
    ----------
    path : str or :py:class:`io.FileIO`
        The path or file object to read KatScript from. If an open file object is
        passed, it will be read from and left open. If a path is passed, it will be
        opened, read from, then closed.

    model : :class:`.Model`, optional
        The Finesse model to add the parsed objects to. Defaults to a new, empty model.

    spec : :class:`.KatSpec`, optional
        The language specification to use. Defaults to the shared :class:`.KatSpec`
        instance.

    Returns
    -------
    :class:`.Model`
        The parsed model.
    """
    from .compiler import KatCompiler

    compiler = KatCompiler(spec=spec)
    with opened_file(path, "r") as fobj:
        return compiler.compile_file(fobj, model=model)


def parse_legacy(text, model=None, ignored_blocks=None):
    """Parse KatScript into a model.

    Parameters
    ----------
    text : str
        The KatScript to parse.

    model : :class:`.Model`
        The Finesse model to add the parsed objects to.

    ignored_blocks : list, optional
        A list of names of ``FTBLOCK`` sections in the kat code to leave out of the
        model; defaults to empty list.

    Returns
    -------
    :class:`.Model`
        The parsed model.

    Raises
    ------
    NotImplementedError
        If `model` contains any non-default elements. Parsing into existing models is
        unsupported.
    """
    from .legacy import KatParser

    if model:
        # Newly-created models contain an fsig, so we need to account for that
        if len(model.elements) > 1:
            raise NotImplementedError(
                "Legacy parsing of extra commands with an existing model is "
                "unsupported. Please switch to the new syntax, or only call "
                "'parse_legacy' on a complete kat file."
            )
    parser = KatParser()
    return parser.parse(text, model=model, ignored_blocks=ignored_blocks)


def parse_legacy_file(path, model=None, ignored_blocks=None):
    """Parse KatScript from a file into a model.

    Parameters
    ----------
    path : str or :py:class:`io.FileIO`
        The path or file object to read KatScript from. If an open file object is
        passed, it will be read from and left open. If a path is passed, it will be
        opened, read from, then closed.

    model : :class:`.Model`
        The Finesse model to add the parsed objects to.

    ignored_blocks : list, optional
        A list of names of ``FTBLOCK`` sections in the kat code to leave out of the
        model; defaults to empty list.

    Returns
    -------
    :class:`.Model`
        The parsed model.

    Raises
    ------
    NotImplementedError
        If `model` contains any non-default elements. Parsing into existing models is
        unsupported.
    """
    from .legacy import KatParser

    if model:
        # Newly-created models contain an fsig, so we need to account for that
        if len(model.elements) > 1:
            raise NotImplementedError(
                "Legacy parsing of extra commands with an existing model is "
                "unsupported. Please switch to the new syntax, or only call "
                "'parse_legacy' on a complete kat file."
            )

    parser = KatParser()
    with opened_file(path, "r") as fobj:
        return parser.parse(fobj.read(), model=model, ignored_blocks=ignored_blocks)


def unparse(item, **kwargs):
    """Serialise a Finesse object (such as a model) to KatScript.

    Parameters
    ----------
    item : object
        A Finesse object (such as a :class:`.Model`) to generate KatScript for.

    Returns
    -------
    str
        The generated KatScript.
    """
    from .generator import KatUnbuilder

    unbuilder = KatUnbuilder()
    return unbuilder.unbuild(item, **kwargs)


def unparse_file(path, item, **kwargs):
    """Serialise a model to KatScript in a file.

    Parameters
    ----------
    path : str
        The kat file path to parse.

    item : object
        A Finesse object (such as a :class:`.Model`) to generate KatScript for.

    Returns
    -------
    str
        The generated KatScript.
    """
    from .generator import KatUnbuilder

    unbuilder = KatUnbuilder()
    with opened_file(path, "w") as fobj:
        return unbuilder.unbuild_file(fobj, item, **kwargs)


def _search_syntax(
    query,
    directives,
    exact=False,
):
    """Find all KatScript directives that could be meant by `query`.

    \b
    Supports simple wildcard characters:
      - ``*`` matches 0 or more characters
      - ``?`` matches any single character
      - ``[abc]`` matches any characters in abc
      - ``[!abc]`` matches any characters not in abc

    If there is a ``.`` in `query`, everything before that is assumed to be a directive
    and everything after to be a parameter.

    A ``*`` is added to the end of each query term, set `exact` to `False` to prevent
    this.

    Parameters
    ----------
    query : str
        A directive or a directive.parameter pair

    directives : dict
        Keys must be KatScript directives with their adapter as value.
        `query` will only be searched in the directives.

    exact : bool, default False
        If `True` only documentation for an exact match will be shown.

    Returns
    -------
    list
        Tuples of :class:`ItemAdapter` objects that match
        and either matching parameters or None if no `.` was present
    """

    # split off possible parameters
    parts = query.split(".")
    directive = parts[0]
    if len(parts) > 1:
        parameter = parts[1]
    else:
        parameter = None

    if not exact:
        directive += "*"

    matches = set()

    try:
        # see if its an exact match
        matches.add(directives[directive])
    except KeyError:
        pass

    # find all matching directives
    for key, adapter in directives.items():
        if fnmatch(key, directive):
            matches.add(adapter)
    # Sort the directives in order they appear in the spec. This is better
    # than alphabetic sort, which puts `x2axis` ahead of `xaxis`.
    matches = sorted(
        matches, key=lambda adapter: list(directives.keys()).index(adapter.full_name)
    )

    full_matches = []
    if not parameter:
        for match in matches:
            full_matches.append((match, None))
    else:
        for adapter in matches:
            # find matching parameters for matched directives
            matched_params = []
            for attr in dir(adapter.documenter.item_type):
                # filter for only parameters, I'm not sure if this matches exactly
                # what we want here, but it seems to give reasonable results
                if isinstance(
                    reduce(getattr, [attr], adapter.documenter.item_type),
                    parameterproperty,
                ):
                    if attr == parameter or fnmatch(attr, parameter + "*"):
                        matched_params.append(attr)
            if matched_params:
                full_matches.append((adapter, tuple(matched_params)))

    return tuple(full_matches)


def _syntax(matches, spec=None, verbosity=0, keyword_arguments=True, **kwargs):
    """Create a string containing syntax help out of the adapters.

    Parameters
    ----------
    matches : list
        Tuples containing an `ItemAdapter` object and either parameter strings or `None`

    spec : :class:`.KatSpec`, optional
        The language specification to use. Defaults to the shared :class:`.KatSpec`
        instance.

    verbosity : int, default 0
        Determines verbosity level:
            - ``0`` shows only the name and parameters
            - ``1`` adds a short summary and parameter explanations if they are defined
            - ``2`` shows the complete docstring

    keyword_arguments : bool, default True
        Show keyword arguments where supported.

    Other Parameters
    ----------------
    kwargs : dict, optional
        Keyword arguments supported by :meth:`.ItemDocumenter.syntax`.

    Returns
    -------
    str
        The syntax for all objects in matches.
    """
    if spec is None:
        from .spec import KATSPEC as spec

    pieces = []
    for adapter, parameters in matches:
        syntax = adapter.documenter.syntax(
            spec, adapter, optional_as_positional=not keyword_arguments, **kwargs
        )
        pieces.append(
            " / ".join(sorted(adapter.aliases, key=lambda alias: len(alias)))
            + ": "
            + syntax
        )
        if parameters:
            for parameter in parameters:
                doc = inspect.getdoc(
                    reduce(getattr, [parameter], adapter.documenter.item_type)
                )
                if doc is None:
                    doc = parameter
                pieces.append(textwrap.indent(doc, prefix=INDENT))
        elif verbosity == 1:
            # Add the instruction summary and descriptions of its arguments.
            summary = adapter.documenter.summary()
            if summary is not None:
                pieces.append(
                    textwrap.indent(
                        "\n".join(
                            textwrap.wrap(summary, width=TERMINAL_WIDTH - len(INDENT))
                        ),
                        prefix=INDENT,
                    )
                )
            extended_summary = adapter.documenter.extended_summary()
            if extended_summary is not None:
                pieces.append(
                    textwrap.indent(
                        "\n".join(
                            textwrap.wrap(
                                extended_summary, width=TERMINAL_WIDTH - len(INDENT)
                            )
                        ),
                        prefix=INDENT,
                    )
                )

            if params := adapter.documenter.argument_descriptions():
                paramsection = "Parameters\n----------\n"
                paramlines = []

                for name, (_, description) in params.items():
                    paramlines.append(name)
                    if description is not None:
                        wrapped = textwrap.wrap(
                            description,
                            initial_indent=INDENT,
                            subsequent_indent=INDENT,
                            width=TERMINAL_WIDTH
                            - len(INDENT),  # Compensate for indent.
                        )
                        paramlines.append("\n".join(wrapped))
                    else:
                        paramlines.append(
                            textwrap.indent("<no description>", prefix=INDENT)
                        )

                paramsection += "\n".join(paramlines)
                pieces.append(textwrap.indent(paramsection, prefix=INDENT))
        elif verbosity == 2:
            doc = inspect.getdoc(adapter.documenter.item_type)
            if doc is None:
                doc = ""
            pieces.append(doc)

    return "\n\n".join(pieces)


def syntax(
    query="",
    spec=None,
    verbose=False,
    elements=True,
    commands=True,
    analyses=True,
    keyword_arguments=True,
    exact=False,
    suggestions=True,
    **kwargs,
):
    """Query the KatScript syntax documentation for `query`.

    \b
    Supports simple wildcard characters:
      - ``*`` matches 0 or more characters
      - ``?`` matches any single character
      - ``[abc]`` matches any characters in abc
      - ``[!abc]`` matches any characters not in abc

    If there is a ``.`` in `query`, everything before that is assumed to be a directive
    and everything after to be a parameter.

    A ``*`` is added to the end of each query term, set `exact` to `False` to prevent
    this.

    If no match is found some suggestions will be shown. Set `suggestions` to `False`
    to disable suggestions.

    If `query` is an empty string all syntax documentation will be shown.

    For more detailed help try :func:`finesse.help`.

    Parameters
    ----------
    query : str
        The directive to retrieve syntax for.

    spec : :class:`.KatSpec`, optional
        The language specification to use. Defaults to the shared :class:`.KatSpec`
        instance.

    verbose : bool, default False
        Show documentation for the directive.

    elements : bool, default True
        Whether to search for elements.

    commands : bool, default True
        Whether to search for commands.

    analyses : bool, default True
        Whether to search for analyses.

    keyword_arguments : bool, default True
        Show keyword arguments where supported.

    exact : bool, default False
        If `True` only documentation for an exact match will be shown.

    suggestions : bool, default True
        Whether to show suggestions if no match is found.

    Other Parameters
    ----------------
    kwargs : dict, optional
        Keyword arguments supported by :meth:`.ItemDocumenter.syntax`.

    Returns
    -------
    str
        The syntax for `query`.
    """
    if not isinstance(query, str):
        raise TypeError(
            f"""Directive must be of type str, not {type(query)}. For information
         on finesse objects use `finesse.help`"""
        )

    if spec is None:
        from .spec import KATSPEC as spec

    directives = {}

    if elements:
        directives.update(spec.elements)
    if commands:
        directives.update(spec.commands)
    if analyses:
        directives.update(spec.analyses)

    matches = _search_syntax(
        query,
        directives,
        exact,
    )

    candidates = set()
    if suggestions and not matches:
        spell = SpellChecker(language=None, case_sensitive=True)
        spell.word_frequency.load_words(directives)
        for word in spell.edit_distance_1(query):
            if exact:
                candidates = candidates.union(_search_syntax(word, directives))
            else:
                candidates = candidates.union(_search_syntax(word + "*", directives))
        candidates = candidates.difference(matches)

    pieces = []
    pieces.append(_syntax(matches, spec, verbose, keyword_arguments, **kwargs))
    if candidates:
        pieces.append("Did you mean:")
        pieces.append(_syntax(candidates, spec, 0, keyword_arguments, **kwargs))
    pydoc.pager("\n\n".join(pieces))


def help_(directive, spec=None):
    """Get help for `directive`, which can be any of a KatScript instruction, a
    KatScript path (e.g. `mirror.T`), or a Finesse or Python object or type.

    Strings are interpreted as attempted KatScript and supports simple wildcard
     characters, see :func:`finesse.syntax` for details.

    For other Python objects this shows the same as builtin :func:`help` but adds a
    reference to the relevant KatScript where applicable.

    Like the Python builtin :func:`help`, this opens a pager containing the help text in
    the current console.

    Parameters
    ----------
    directive : any
        The directive to retrieve help for.

    spec : :class:`.KatSpec`, optional
        The language specification to use. Defaults to the shared :class:`.KatSpec`
        instance.

    Raises
    ------
    ValueError
        If `directive` cannot be recognised as a valid Finesse or KatScript item.
    """

    if spec is None:
        from .spec import KATSPEC as spec

    if isinstance(directive, str):
        # treat strings as (attempted) KatScript
        matches = _search_syntax(directive, spec.directives, exact=False)
        pydoc.pager(_syntax(matches, spec, verbosity=2, keyword_arguments=True))

    else:
        # This seems to be a Python object; use its docstring.
        pieces = []

        if inspect.isclass(directive):
            signature = str(inspect.signature(directive.__init__)).replace("self, ", "")
            pieces.append(f"{directive.__name__}{signature}")
        else:
            text = type(directive).__name__ + " object\n"
            text += repr(directive)
            pieces.append(text)

            # from now on we want the class
            directive = type(directive)

        # Add the object's docstring.
        doc = inspect.getdoc(directive)
        if doc is None:
            doc = ""
        pieces.append(doc)

        # Look for a KatScript directive producing this type.
        for adapter in spec.directives.values():
            if adapter is None or adapter.factory is None:
                continue

            if directive != adapter.factory.item_type:
                continue

            # Add the corresponding KatScript syntax.
            pieces.append(
                (
                    f'KatScript (use \'finesse.help("{adapter.full_name}" or'
                    f' kat3 help "{adapter.full_name})" for '
                    f"more information):\n"
                )
                + textwrap.indent(
                    adapter.documenter.syntax(spec, adapter), prefix=INDENT
                )
            )

            break

        pydoc.pager("\n\n".join(pieces))


__all__ = (
    "KATSPEC",
    "KatParserError",
    "KatReferenceError",
    "parse",
    "parse_file",
    "parse_legacy",
    "parse_legacy_file",
    "unparse",
    "unparse_file",
    "syntax",
)
