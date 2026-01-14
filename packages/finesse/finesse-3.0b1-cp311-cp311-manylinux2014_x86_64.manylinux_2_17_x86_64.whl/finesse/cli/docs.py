import click
from .util import KatState


@click.command()
@click.argument("query", required=False, nargs=-1)
@click.option(
    "--elements/--no-elements",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show elements.",
)
@click.option(
    "--commands/--no-commands",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show commands.",
)
@click.option(
    "--analyses/--no-analyses",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show analyses.",
)
@click.option(
    "--keyword/--positional",
    "keyword_arguments",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show keyword arguments where supported.",
)
@click.option(
    "--exact",
    is_flag=True,
    default=False,
    show_default=True,
    help=("Don't append `*` to search queries."),
)
@click.option(
    "--no-suggestions",
    "suggestions",
    is_flag=True,
    default=True,
    show_default=True,
    help=("Don't show suggestions."),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show extended documentation for each directive.",
)
@click.pass_context
def syntax(
    ctx,
    query,
    elements,
    commands,
    analyses,
    keyword_arguments,
    exact,
    suggestions,
    verbose,
):
    """Query the KatScript syntax documentation for `query`.

    Supports simple wildcard characters:
      - ``*`` matches 0 or more characters
      - ``?`` matches any single character
      - ``[abc]`` matches any characters in abc
      - ``[!abc]`` matches any characters not in abc

    If there is a ``.`` in `query`, everything before that is assumed to be a directive
    and everything after to be a parameter.

    A ``*`` is added to the end of each query term, pass `--exact` to prevent this.

    If no match is found some suggestions will be shown. Pass `--no-suggestions` to
    disable suggestions.

    If `directive` is an empty string all syntax documentation will be shown.

    For more detailed help try `kat3 help`.
    """
    from ..script import syntax

    ctx.ensure_object(KatState)

    # give all
    if len(query) == 0:
        query = ("",)

    for q in query:
        syntax(
            q,
            None,
            verbose,
            elements,
            commands,
            analyses,
            keyword_arguments,
            exact,
            suggestions,
        )


@click.command()
@click.argument("query", required=False, nargs=-1)
@click.pass_context
def help(ctx, query):
    """Detailed help for KatScript directives.

    Supports simple wildcard characters, see `kat3 syntax --help` for details.
    """
    from ..script import help_

    ctx.ensure_object(KatState)

    # give all
    if len(query) == 0:
        query = ("",)

    for q in query:
        help_(q, None)


if __name__ == "__main__":
    syntax()
