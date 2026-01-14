#!/usr/bin/env python

from __future__ import annotations

try:
    import tomllib

    # tomllib not available in python < 3.11
except ImportError:
    try:
        import tomli as tomllib
    except ImportError as e:
        raise ImportError("This pre-commit hook requires tomli on python < 3.11") from e

import re
from pathlib import Path

ROOT = Path(__file__).absolute().parent.parent
PYPROJECT_TOML = ROOT / "pyproject.toml"
ENVIRONMENT_YML = ROOT / "environment.yml"
ENVIRONMENT_WIN_YML = ROOT / "environment-win.yml"


class VersionMismatchError(ValueError):
    "Package mentioned twice with different versions"


class BuildReqMismatchError(ValueError):
    "Build requirements and 'inplacebuild' requirements not identical"


def parse_req_line(line: str) -> tuple[str, str]:
    """Parse a requirement spec into package name and requirement.

    "numpy > 1" -> ("numpy", ">1")

    Parameters
    ----------
    line : str
        Line from a requirement file, e.g. "numpy > 1"

    Returns
    -------
    tuple[str, str]
        Name, Requirement
    """
    line = re.sub(r"\s", repl="", string=line)
    # see https://peps.python.org/pep-0508/#names
    match = re.match(
        r"""(^
            [A-Z0-9] # start with at least 1 alpha-numerical character
            [A-Z0-9._-]* # any number of alphanumericals, dots, underscores or hyphens
            [A-Z0-9] # Final character can not be a dot, underscore or hyphen
            )
            (.*) # followed by possible requirements specifier
            """,
        line,
        flags=re.I | re.VERBOSE,
    )
    assert match is not None
    name = match.groups()[0].lower()
    if match.groups()[1]:
        req = match.groups()[1].lower()
    else:
        req = ""
    return name, req


def check_version_mismatch(deps: list[str], source: Path) -> None:
    versions = {}
    for dep in deps:
        name, req = parse_req_line(dep)
        if name in versions and versions[name] != req:
            raise VersionMismatchError(
                f"Dependency {name} specified twice with different versions in {source}"
                f"\n Version 1: '{req}'"
                f"\n Version 2: '{versions[name]}'"
            )
        else:
            versions[name] = req


def check_pyproject_toml() -> set[str]:
    """Checks whether the build requirements in the pyproject.toml are identical to the
    'inplacebuild' optional dependencies, and whether there are any packages listed
    twice with a different version requirement.

    Returns
    -------
    set[str]
        Set of all python requirements in the pyproject.toml file

    Raises
    ------
    ValueError
        When there is a mismatch between build requirements and 'inplacebuild'
        requirements
    """
    with open(PYPROJECT_TOML, "rb") as f:
        cfg = tomllib.load(f)
    build_system = set(cfg["build-system"]["requires"])
    inplacebuild = set(cfg["project"]["optional-dependencies"]["inplacebuild"])
    mismatch = build_system.symmetric_difference(inplacebuild)
    if mismatch:
        raise BuildReqMismatchError(
            f"Mismatch between build system requirements in pyproject.toml "
            f"and 'inplacebuild' optional requirements, "
            f" symmetric difference: {mismatch}"
        )
    optional_deps = sum(cfg["project"]["optional-dependencies"].values(), start=[])
    all_deps = cfg["project"]["dependencies"] + optional_deps
    check_version_mismatch(all_deps, PYPROJECT_TOML)
    return set(all_deps)


def main():
    check_pyproject_toml()


if __name__ == "__main__":
    main()
