"""Text processing utilities for tests."""

from textwrap import dedent
import re


def dedent_multiline(text):
    """Dedent multiline text, stripping preceding and succeeding newlines.

    This is useful for specifying multiline strings in tests without having to
    compensate for the indentation.
    """
    return dedent(text).strip()


def escape_full(pattern):
    """Escape regex `pattern`, adding start (`^`) and end (`$`) markers.

    This is useful in combination with the `match` argument to pytest's `raises` context
    manager. It can be used to escape error messages that are intended to be matched
    exactly.
    """
    return "^" + re.escape(pattern) + "$"


def stringify_list(array):
    if isinstance(array, list):
        return f"[{', '.join(stringify_list(item) for item in array)}]"
    return str(array)
