import pytest
from testutils.tokens import IMPLICITLINEEND, ENDMARKER, NAME


@pytest.mark.parametrize(
    "string",
    (
        "m1",
        "m2.T",
        "m3.phi",
        "m4.p1.o.q",
    ),
)
def test_reference(tokenizer, string):
    assert list(tokenizer.tokenize(string)) == [
        NAME(1, 1, string),
        IMPLICITLINEEND(1, 1 + len(string)),
        ENDMARKER(2),
    ]
