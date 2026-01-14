from __future__ import annotations

import enum
import inspect
from io import StringIO
import json
import platform
import re

try:
    import readline

    readline_available = True
    # probably Mac
except ImportError:
    readline_available = False
import sys
import traceback
import warnings
from pathlib import Path
from types import ModuleType

import finesse
from finesse import is_interactive

# General note for this entire file: multiline strings that have zero indentation
# cause issues with the docs build. Please don't change the ugly multiline strings
# without checking!


class SourceType(enum.Enum):
    INTERACTIVE = "Interactive"
    SCRIPT = "Script"
    REPL = "REPL"
    STDIN = "stdin"


def get_package_versions() -> str:
    """Report all currently imported package version by looping over :attr:`sys.modules`
    and looking for '__version__' attributes. Explicitly avoids calling into conda/pip
    since there are too many package managers to accommodate for.

    Returns
    -------
    str
        list of <package> == <version> for every package
    """
    versions = ""
    for mod in sys.modules.values():
        if isinstance(mod, ModuleType):
            if not any(char in mod.__name__ for char in (".", "/")) and hasattr(
                mod, "__version__"
            ):
                versions += f"{mod.__name__} == {mod.__version__}\n"
    return versions


def get_source() -> str:
    """Get source of the '__main__' module. Supports Ipython (Jupyter Notebook, VSCode),
    interactive interpreter and regular python modules.

    Returns
    -------
    str
        Source code
    """
    main = sys.modules["__main__"]
    source_type = get_source_type()
    if source_type == SourceType.INTERACTIVE:
        # Undocumented module attributes that might store the file path
        for file_attr in ("__file__", "__vsc_ipynb_file__", "__session__"):
            if source_fn := getattr(main, file_attr, False):
                source_fn = Path(str(source_fn))
                if source_fn.suffix == ".ipynb":
                    with open(source_fn, "r") as f:
                        return ipynb_to_md(json.load(f))
        # otherwise concatenate lines from code cells (without markdown cells)
        source = "\n".join(main.In)
    # interactive interpreter: no distinction in history file between different sessions
    elif source_type == SourceType.REPL:
        warnings.warn(
            "Using last 20 commands to generate bug report from interactive interpreter",
            stacklevel=1,
        )
        if not readline_available:
            warnings.warn(
                "Can not read REPL history!",
                stacklevel=1,
            )
            return ""
        source = ""
        hist_length = readline.get_current_history_length()
        n_lines = min(hist_length, 20)
        for i in range(hist_length - n_lines, hist_length):
            source += str(readline.get_history_item(i)) + "\n"
    # normal .py file
    elif source_type == SourceType.SCRIPT:
        source = inspect.getsource(main)
    elif source_type == SourceType.STDIN:
        # Should maybe be an exception, but we don't really want to raise exceptions
        # in code meant to handle exceptions
        warnings.warn(
            RuntimeWarning("Can not get source when passing python code via stdin"),
            stacklevel=2,
        )
        source = ""
    else:
        raise ValueError(f"Unknown source type {source_type}")
    return source.strip()


def get_source_type() -> SourceType:
    """Type of source for the python code currently being executed.

    Returns
    -------
    SourceType
        Interactive environment (jupyter), terminal REPL or plain python script
    """
    if is_interactive():
        return SourceType.INTERACTIVE
    elif not hasattr(sys.modules["__main__"], "__file__"):
        return SourceType.REPL
    elif sys.modules["__main__"].__file__ == sys.stdin.name:
        return SourceType.STDIN
    else:
        return SourceType.SCRIPT


def ipynb_to_md(ipynb: dict) -> str:
    """Converts notebook json object to markdown. Extracts markdown cells as raw text
    and code blocks wrapped in a python code block.

    Parameters
    ----------
    ipynb : dict
        notebook json dict

    Returns
    -------
    str
        Markdown representing notebook
    """
    md = ""
    for cell in ipynb["cells"]:
        if cell["cell_type"] == "code":
            lang = "python"
        elif cell["cell_type"] == "markdown":
            lang = "markdown"
        source = "".join(cell["source"])
        md += wrap_block(source, lang=lang)

    return md


def wrap_block(code: str, lang: str = "python") -> str:
    """Wraps a string in a markdown code block like.

    ```python
    print('foo')
    ```

    Parameters
    ----------
    code : str
        code to wrap
    lang : str, optional
        language of code, by default "python"

    Returns
    -------
    str
        Markdown code block
    """
    return f"```{lang}\n{code}\n```\n"


def get_formatted_traceback() -> str:
    if sys.version_info.minor < 12:
        try:
            io = StringIO()
            traceback.print_last(file=io)
            return io.getvalue()
        except ValueError:
            pass
    if exc := getattr(sys, "last_exc", False):
        assert isinstance(exc, BaseException)
        return "\n".join(traceback.format_exception(exc))
    else:
        return traceback.format_exc()


def get_formatted_argv() -> str:
    args = [f"`{arg}`" for arg in sys.argv if len(arg)]
    if len(args):
        return "### Arguments\n\n" + " ".join(args)
    else:
        return ""


def get_formatted_source() -> str:
    source = get_source()
    if len(source) > 1:
        return (
            f"### Source [{get_source_type()}]\n" "\n" "Showing last 20 lines\n"
            if get_source_type() == SourceType.REPL
            else ""
            f"{source if get_source_type() == SourceType.INTERACTIVE else wrap_block(source)}\n"
        )
    else:
        return ""


def bug_report(
    title: str | None = None,
    file: str | Path | None = None,
    include_source: bool = False,
):
    """Generate a markdown bug report, suitable for copy-pasting into chatrooms or
    GitLab issues. Contains the source code, the triggered exception (if any) and
    machine and python environment information.

    Parameters
    ----------
    title : str | None, optional
        Title to insert on top of markdown, by default None
    file : str | Path | None, optional
        Whether to write the report to file. Will silently overwrite existing files,
        by default None
    include_source : bool, optional
        Wether to include the source code that caused the exception (the contents of the
        Jupyter notebook or Python script file) into the bug report. Be careful when
        including source with proprietary/confidential information source in bug reports
        shared in public spaces like Gitlab or the Matrix channel. Defaults to False
    """
    # 4 spaces is equal to a code block in gitlab markdown!
    report = (
        f"# {title if title else 'Finesse3 bug report'}\n"
        "\n"
        "## Environment\n"
        "\n"
        f"- **Finesse version:** `{finesse.__version__}`\n"
        f"- **Python version:** `{sys.version}`\n"
        f"- **Platform:** `{platform.system()} {platform.machine()}`\n"
        "\n"
        "## Entry point\n"
        "\n"
        f"`{sys.executable}`\n"
        "\n"
        f"{get_formatted_argv()}\n"
        "\n"
        f"{get_formatted_source() if include_source else ''}\n"
        "\n"
        "## Stack trace\n"
        "\n" + wrap_block(get_formatted_traceback(), lang="text") + "\n"
        "## Package versions\n"
        "\n" + wrap_block(get_package_versions(), lang="text")
    )
    # remove excessive empty lines due to removed sections
    report = re.sub(r"\n{2,}", repl=r"\n\n", string=report)
    if file:
        file = Path(file)
        file.write_text(report)
        print(f"Bug report written to {Path.cwd() / file}\n")
    return report
