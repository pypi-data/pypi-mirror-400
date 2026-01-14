"""Extract extra dependencies from `pyproject.toml`.

Call with the path to `pyproject.toml` and the extras section name(s) to extract as
arguments.

This is used by the CI to install build dependencies without the need for a separate
`requirements-build.txt` file.

Note that we are using a regular expression here, since a toml parsers was only added to
the python standard library in 3.11, for older version you would have to install a
separate package to run this script, complicating the build process.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Generator


def yield_reqs(reqs: str) -> Generator[str, None, None]:
    for line in reqs.splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        line = line[line.index('"') + 1 :]
        line = line[: line.index('"')]
        yield line


def extract_reqs(pyproject_path: Path, section: str) -> str:
    with open(pyproject_path, "r") as f:
        cfg = f.read()
    match = re.search(
        r"""
        (\[project\.optional-dependencies\]  # Optional dependencies section
        .*?)  # any characters inside of it
        (\Z|^\[)  # until we reach the end of the string or a new section
        """,
        cfg,
        flags=re.S | re.M | re.X,
    )
    if match is None:
        raise ValueError("Project optional dependencies not found in pyproject.toml")
    optional_deps = match.group()

    section_matches = re.finditer(
        pattern=r"""(^\w.*?)  # name of the section
                    \s?=\s?   # equal sign possibly surrounded by spaces
                    (\[.*?\]) # any multiline string in between square brackets
                """,
        string=optional_deps,
        flags=re.S | re.M | re.X,
    )
    for section_match in section_matches:
        name, reqs = section_match.groups()
        if name == section:
            return reqs
    raise ValueError(f"Section {section} not found")


def main(pyproject_path: Path, section: str) -> None:
    for line in yield_reqs(extract_reqs(pyproject_path, section)):
        print(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extra extra requirments section from pyproject.toml file"
    )
    parser.add_argument("pyproject_path", type=Path, help="Path to pyproject.toml file")
    parser.add_argument(
        "section", type=str, help="Section of optional dependencies to extract"
    )
    args = parser.parse_args()
    main(pyproject_path=args.pyproject_path, section=args.section)
