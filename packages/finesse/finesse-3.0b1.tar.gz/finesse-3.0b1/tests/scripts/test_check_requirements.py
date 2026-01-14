import re
from contextlib import contextmanager
from pathlib import Path

import pytest

import scripts.check_requirements as check_reqs


@contextmanager
def modify_file(path: Path, pattern: str, sub: str, count: int = 0):
    with open(path, "r") as f:
        orig_content = f.read()
    try:
        new = re.sub(pattern=pattern, string=orig_content, repl=sub, count=count)
        assert new != orig_content
        with open(path, "w") as f:
            f.write(new)
        yield
    finally:
        with open(path, "w") as f:
            f.write(orig_content)


@pytest.mark.parametrize(
    "line, expected",
    [
        ("numpy", ("numpy", "")),
        ("numpy    ", ("numpy", "")),
        ("n-u-._m-p-y", ("n-u-._m-p-y", "")),
        ("n-u-m-p-y", ("n-u-m-p-y", "")),
        ("numpy>3", ("numpy", ">3")),
        ("numpy >  3  ", ("numpy", ">3")),
        ("numpy >= 1.20, < 2.0", ("numpy", ">=1.20,<2.0")),
    ],
)
def test_parse_req_line(line, expected):
    assert check_reqs.parse_req_line(line) == expected


@pytest.mark.parametrize("deps", (["numpy", "numpy==1"], ["numpy==2", "numpy==1"]))
def test_check_version_mismatch(deps):
    with pytest.raises(check_reqs.VersionMismatchError):
        check_reqs.check_version_mismatch(deps, source=Path())


@pytest.mark.parametrize(
    "pattern, sub, exc",
    (
        pytest.param(
            "numpy",
            "non-existing",
            check_reqs.BuildReqMismatchError,
            id="Build-req-mismatch",
        ),
        # possibly remove this variant when there are no duplicate requirements in
        # pyproject.toml file anymore
        pytest.param(
            r"black",
            "black==25",
            check_reqs.VersionMismatchError,
            id="version-mismatch",
        ),
    ),
)
def test_check_pyproject_toml(pattern, sub, exc):
    # check build requirements not matching
    with modify_file(check_reqs.PYPROJECT_TOML, pattern, sub, 1):
        with pytest.raises(exc):
            check_reqs.check_pyproject_toml()
