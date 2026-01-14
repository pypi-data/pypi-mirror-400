import pytest
from finesse.script.exceptions import KatParsingError
from testutils.text import dedent_multiline, escape_full


@pytest.fixture
def spec(spec, fake_analysis_adapter_factory, fake_analysis_cls):
    spec.register_analysis(
        fake_analysis_adapter_factory(fake_analysis_cls, full_name="fake_analysis1")
    )
    spec.register_analysis(
        fake_analysis_adapter_factory(fake_analysis_cls, full_name="fake_analysis2")
    )
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            dedent_multiline(
                """
                fake_analysis1()
                fake_analysis2()
                """
            ),
            "\nlines 1-2: duplicate analysis trees (combine with 'series' or 'parallel')\n"
            "-->1: fake_analysis1()\n"
            "      ^^^^^^^^^^^^^^\n"
            "-->2: fake_analysis2()\n"
            "      ^^^^^^^^^^^^^^",
            id="xaxis",
        ),
    ),
)
def test_multiple_analyses_invalid(compiler, script, error):
    with pytest.raises(KatParsingError, match=escape_full(error)):
        compiler.compile(script)
