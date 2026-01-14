from pathlib import Path

import pytest

from scripts.extract_extra_requirements import extract_reqs, yield_reqs

ROOT = Path(__file__).parent.parent.parent


@pytest.mark.parametrize(
    "toml_content",
    (
        """
[project.optional-dependencies]
inplacebuild = [
    "foo >= 45",
    "bar >= 8.0.3",
    "baz",
]
""",
        """
[project.optional-dependencies]
inplacebuild = [
    "foo >= 45",
    "bar >= 8.0.3",
    "baz",
]
foo = ["foo"]
""",
        """
[project.optional-dependencies]
inplacebuild = [
    "foo >= 45",
    "bar >= 8.0.3",
    "baz",
]
foo = ["foo"]

[new."section]
""",
    ),
)
def test_extract_reqs(toml_content, tmp_path):
    toml_path = tmp_path / "pyproject.toml"
    with open(toml_path, "w") as f:
        f.write(toml_content)
    assert set(yield_reqs(extract_reqs(toml_path, "inplacebuild"))) == {
        "foo >= 45",
        "bar >= 8.0.3",
        "baz",
    }
