import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import pytest

ROOT = Path(__file__).parent

SCRIPT = ROOT / "raise_exc.py"
NOTEBOOK = ROOT / "raise_exc.ipynb"
REPORT_NAME = "bug_report.md"


class CodeBlock(NamedTuple):
    code: str
    lang: str


# we can not directly compare bug reports against a reference file, because
# the report content depends on the environment where it is created
def check_bug_report(report: str, code_blocks: list[CodeBlock], exc: str):
    # check for source code
    for code_block in code_blocks:
        # more robust than complicated regex
        assert code_block.lang in report
        assert code_block.code in report
    # check for exception
    assert re.search(
        pattern=f"## Stack trace\n\n```text\nTraceback.*?{exc}\n*?```",
        string=report,
        flags=re.S,
    )
    # check for list of packages
    assert re.search(
        pattern=r"## Package versions\n+```text\n(\w+ == .+\n)+\n```",
        string=report,
    )


def test_regular_python_module(tmp_path, monkeypatch):
    report_path = tmp_path / REPORT_NAME
    script_path = tmp_path / "script.py"
    monkeypatch.chdir(tmp_path)
    shutil.copy(SCRIPT, script_path)
    subprocess.run(f"python {script_path}", shell=True, check=True)

    check_bug_report(
        report_path.read_text(),
        code_blocks=[CodeBlock(code=script_path.read_text(), lang="python")],
        exc="ZeroDivisionError: division by zero",
    )


def test_repl_try_except(tmp_path, monkeypatch):
    report_path = tmp_path / REPORT_NAME
    monkeypatch.chdir(tmp_path)
    # start up a repl session in a new process
    p = subprocess.Popen("python", stdin=subprocess.PIPE, text=True)

    script = """\
from finesse.utilities.bug_report import bug_report

if __name__ == "__main__":
    try:
        1 / 0
    except Exception:
        bug_report(file="bug_report.md", include_source=False)
"""
    p.communicate(script)
    check_bug_report(
        report_path.read_text(),
        code_blocks=[],
        exc="ZeroDivisionError: division by zero",
    )


# unnecessarily complicated to test on other platforms
@pytest.mark.linux
def test_ipython_notebook(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report_path = tmp_path / REPORT_NAME
    nb_path = tmp_path / "nb.ipynb"

    shutil.copy(NOTEBOOK, nb_path)

    nb = nbformat.read(nb_path, as_version=4)
    ep = ExecutePreprocessor(timeout=60, kernel_name="python3", allow_errors=True)
    ep.preprocess(nb)

    nb = json.loads(nb_path.read_text())
    blocks = []
    for cell in nb["cells"]:
        blocks.append(
            CodeBlock(
                code="".join(cell["source"]),
                lang="python" if cell["cell_type"] == "code" else "markdown",
            )
        )
    check_bug_report(
        report_path.read_text(),
        code_blocks=blocks,
        exc="ZeroDivisionError: division by zero",
    )
