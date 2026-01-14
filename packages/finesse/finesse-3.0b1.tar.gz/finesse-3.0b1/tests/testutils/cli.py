"""CLI utilities for tests."""


def sanitized_lines(cli_result):
    """The CLI output lines with leading and trailing whitespace removed."""
    return [line.strip() for line in cli_result.output.splitlines()]


def sanitized_output(cli_result):
    """The CLI output with leading and trailing whitespace removed."""
    return "\n".join(sanitized_lines(cli_result))
