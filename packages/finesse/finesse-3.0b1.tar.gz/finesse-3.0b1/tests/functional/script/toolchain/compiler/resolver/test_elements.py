import pytest
from finesse.script.exceptions import KatScriptError
from testutils.text import dedent_multiline, escape_full
from finesse.warnings import KeywordUsedWarning


# Override default command to take two arguments.
@pytest.fixture
def fake_command_func():
    def fake_command(model, a, b):
        pass

    return fake_command


@pytest.fixture
def spec(
    spec,
    set_spec_constructs,
    fake_element_adapter_factory,
    fake_element_cls,
    fake_command_adapter_factory,
    fake_command_func,
):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.register_command(fake_command_adapter_factory(fake_command_func))
    set_spec_constructs(
        "constants", {"fake_constant": None}, "keywords", {"fake_keyword"}
    )

    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "__undefined__ myelement 1 a=2",
            "\nline 1: unknown element '__undefined__'\n"
            "-->1: __undefined__ myelement 1 a=2\n"
            "      ^^^^^^^^^^^^^",
            id="element",
        ),
        pytest.param(
            "fakke_element myelement 1 a=2",
            "\nline 1: unknown element 'fakke_element'."
            " Did you mean 'fake_element'?\n"
            "-->1: fakke_element myelement 1 a=2\n"
            "      ^^^^^^^^^^^^^",
            id="element suggestion",
        ),
        pytest.param(
            "__undefined__(1, a=2)",
            "\nline 1: unknown function '__undefined__'\n"
            "-->1: __undefined__(1, a=2)\n"
            "      ^^^^^^^^^^^^^",
            id="function",
        ),
        pytest.param(
            "fakke_command(1, a=2)",
            "\nline 1: unknown function 'fakke_command'."
            " Did you mean 'fake_command'?\n"
            "-->1: fakke_command(1, a=2)\n"
            "      ^^^^^^^^^^^^^",
            id="function suggestion",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_command(
                    1,
                    __undefined__(1, a=2)
                )
                """
            ),
            "\nline 3: unknown function '__undefined__'\n"
            "   2:     1,\n"
            "-->3:     __undefined__(1, a=2)\n"
            "          ^^^^^^^^^^^^^\n"
            "   4: )",
            id="nested function",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_command(
                    1,
                    fakke_command(1, a=2)
                )
                """
            ),
            "\nline 3: unknown function 'fakke_command'."
            " Did you mean 'fake_command'?\n"
            "   2:     1,\n"
            "-->3:     fakke_command(1, a=2)\n"
            "          ^^^^^^^^^^^^^\n"
            "   4: )",
            id="nested function suggestion",
        ),
    ),
)
def test_unknown_directive_error(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_element myelement
                fake_element myelement
                """
            ),
            (
                "\nlines 1-2: multiple elements with name 'myelement'\n"
                "-->1: fake_element myelement\n"
                "                   ^^^^^^^^^\n"
                "-->2: fake_element myelement\n"
                "                   ^^^^^^^^^"
            ),
            id="two elements with same name",
        ),
    ),
)
def test_duplicate_name_error(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "fake_element fake_constant",
            (
                "\nline 1: constant 'fake_constant' cannot be used as an element name\n"
                "-->1: fake_element fake_constant\n"
                "                   ^^^^^^^^^^^^^"
            ),
            id="constant-as-a-name",
        ),
    ),
)
def test_invalid_name_error(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)


def test_name_warning(compiler):
    warning_text = (
        r"element name 'fake_keyword' \(line 1\) is also the name of a keyword, which "
        r"may lead to confusion"
    )
    with pytest.warns(KeywordUsedWarning, match=warning_text):
        compiler.compile("fake_element fake_keyword")
