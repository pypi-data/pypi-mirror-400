"""CLI syntax command tests."""

import pytest
from finesse.__main__ import syntax
from finesse.script.spec import KATSPEC
from testutils.cli import sanitized_output


@pytest.mark.parametrize("directive", KATSPEC.directives)
@pytest.mark.parametrize("exact", (False, True))
def test_directive(cli, directive, exact):
    """Search for the specified directive."""
    pieces = [directive]
    if exact:
        pieces.append("--exact")

    cli_result = cli.invoke(syntax, pieces)
    output = sanitized_output(cli_result)
    assert cli_result.exit_code == 0
    assert directive in output
