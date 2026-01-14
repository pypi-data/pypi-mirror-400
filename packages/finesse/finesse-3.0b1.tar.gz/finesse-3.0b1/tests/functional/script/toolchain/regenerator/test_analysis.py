import pytest
from testutils.text import dedent_multiline
from finesse.symbols import FUNCTIONS


# Override default analysis to take one positional-only, one positional-or-keyword,
# and one keyword-only argument.
@pytest.fixture
def fake_analysis_cls(fake_analysis_cls):
    class FakeAnalysis(fake_analysis_cls):
        def __init__(self, a, /, b=None, *, c=None):
            super().__init__()
            self.a = a
            self.b = b
            self.c = c

    return FakeAnalysis


@pytest.fixture
def spec(spec, set_spec_constructs, fake_analysis_adapter_factory, fake_analysis_cls):
    spec.register_analysis(
        fake_analysis_adapter_factory(fake_analysis_cls, short_name="fake")
    )
    set_spec_constructs("unary_operators", {"-": FUNCTIONS["neg"]})

    return spec


@pytest.mark.parametrize(
    "script",
    (
        ("fake_analysis(none)"),
        ("fake_analysis(None)"),
        ("fake_analysis(1.)"),
        # Aliases and whitespace.
        ("fake_analysis( none )"),
        ("fake(none)"),
        ("fake(  none   )"),
        # Optional-as-positional arguments.
        ("fake_analysis(1, 2)"),
        ("fake_analysis(1., 2)"),
        ("fake_analysis(1., 2.)"),
        ("fake_analysis( 1.,  2. )"),
        # Optional-as-keyword arguments.
        ("fake_analysis(1, b=2)"),
        ("fake_analysis(1.1 , b=2)"),
        ("fake_analysis(1., b=2.)"),
        ("fake_analysis(1.  ,    b=2.)"),
        # Multi-line.
        (
            dedent_multiline(
                """
                fake_analysis(
                    1.234e-5,
                    b=-6
                )
                """
            )
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_analysis(
                    fake_analysis(1, 2),
                    b=-6
                )
                """
            ),
            id="recursive-analyses-1",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_analysis(
                    fake_analysis(
                        1, 2
                    ),
                    b=-6
                )
                """
            ),
            id="recursive-analyses-2",
        ),
        pytest.param(
            dedent_multiline(
                """
                fake_analysis(
                    fake_analysis(
                        1,  # comment 1
                        b=[1, 2, 3],
                        # comment 2
                    ),
                    # comment 3
                    b=-6
                    # comment 4
                )
                # comment 5
                """
            ),
            id="recursive-analyses-3",
        ),
    ),
)
def test_analysis(compiler, regenerate, fake_analysis_cls, script):
    model = compiler.compile(script)
    assert regenerate(model) == script
