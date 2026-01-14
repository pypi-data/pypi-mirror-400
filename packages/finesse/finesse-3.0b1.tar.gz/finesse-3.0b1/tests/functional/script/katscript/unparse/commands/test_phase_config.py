import pytest
from finesse.script import KATSPEC, unparse


@pytest.mark.parametrize(
    "kwargs,directive_defaults,argument_defaults,prefer_keywords,expected",
    (
        # empty
        ({}, False, False, False, ""),
        ({}, False, False, True, ""),
        ({}, False, True, False, ""),
        ({}, False, True, True, ""),
        ({}, True, False, False, "phase_config()"),
        ({}, True, False, True, "phase_config()"),
        ({}, True, True, False, "phase_config(false, true)"),
        (
            {},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=true)",
        ),  # 7
        # zero_k00 only
        ({"zero_k00": True}, False, False, False, "phase_config(true)"),
        ({"zero_k00": True}, False, False, True, "phase_config(zero_k00=true)"),
        ({"zero_k00": True}, False, True, False, "phase_config(true, true)"),
        (
            {"zero_k00": True},
            False,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=true)",
        ),
        ({"zero_k00": True}, True, False, False, "phase_config(true)"),
        ({"zero_k00": True}, True, False, True, "phase_config(zero_k00=true)"),
        ({"zero_k00": True}, True, True, False, "phase_config(true, true)"),
        (
            {"zero_k00": True},
            True,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=true)",
        ),  # 15
        ({"zero_k00": False}, False, False, False, ""),
        ({"zero_k00": False}, False, False, True, ""),
        ({"zero_k00": False}, False, True, False, ""),
        (
            {"zero_k00": False},
            False,
            True,
            True,
            "",
        ),  # 19
        ({"zero_k00": False}, True, False, False, "phase_config()"),
        ({"zero_k00": False}, True, False, True, "phase_config()"),
        ({"zero_k00": False}, True, True, False, "phase_config(false, true)"),
        (
            {"zero_k00": False},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=true)",
        ),
        # zero_tem00_gouy only
        ({"zero_tem00_gouy": True}, False, False, False, ""),
        ({"zero_tem00_gouy": True}, False, False, True, ""),
        ({"zero_tem00_gouy": True}, False, True, False, ""),
        ({"zero_tem00_gouy": True}, False, True, True, ""),
        ({"zero_tem00_gouy": True}, True, False, False, "phase_config()"),
        ({"zero_tem00_gouy": True}, True, False, True, "phase_config()"),
        (
            {"zero_tem00_gouy": True},
            True,
            True,
            False,
            "phase_config(false, true)",
        ),  # 30
        (
            {"zero_tem00_gouy": True},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=true)",
        ),
        ({"zero_tem00_gouy": False}, False, False, False, "phase_config(false, false)"),
        (
            {"zero_tem00_gouy": False},
            False,
            False,
            True,
            "phase_config(zero_tem00_gouy=false)",
        ),
        ({"zero_tem00_gouy": False}, False, True, False, "phase_config(false, false)"),
        (
            {"zero_tem00_gouy": False},
            False,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=false)",
        ),  # 35
        ({"zero_tem00_gouy": False}, True, False, False, "phase_config(false, false)"),
        (
            {"zero_tem00_gouy": False},
            True,
            False,
            True,
            "phase_config(zero_tem00_gouy=false)",
        ),
        ({"zero_tem00_gouy": False}, True, True, False, "phase_config(false, false)"),
        (
            {"zero_tem00_gouy": False},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=false)",
        ),
        # both
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            False,
            False,
            False,
            "phase_config(true)",
        ),  # 40
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            False,
            False,
            True,
            "phase_config(zero_k00=true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            False,
            True,
            False,
            "phase_config(true, true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            False,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            True,
            False,
            False,
            "phase_config(true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            True,
            False,
            True,
            "phase_config(zero_k00=true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            True,
            True,
            False,
            "phase_config(true, true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": True},
            True,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=true)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            False,
            False,
            False,
            "phase_config(true, false)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            False,
            False,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=false)",
        ),  # 49
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            False,
            True,
            False,
            "phase_config(true, false)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            False,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=false)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            True,
            False,
            False,
            "phase_config(true, false)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            True,
            False,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=false)",
        ),  # 53
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            True,
            True,
            False,
            "phase_config(true, false)",
        ),
        (
            {"zero_k00": True, "zero_tem00_gouy": False},
            True,
            True,
            True,
            "phase_config(zero_k00=true, zero_tem00_gouy=false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            False,
            False,
            False,
            "",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            False,
            False,
            True,
            "",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            False,
            True,
            False,
            "",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            False,
            True,
            True,
            "",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            True,
            False,
            False,
            "phase_config()",
        ),  # 60
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            True,
            False,
            True,
            "phase_config()",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            True,
            True,
            False,
            "phase_config(false, true)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": True},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=true)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            False,
            False,
            False,
            "phase_config(false, false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            False,
            False,
            True,
            "phase_config(zero_tem00_gouy=false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            False,
            True,
            False,
            "phase_config(false, false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            False,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            True,
            False,
            False,
            "phase_config(false, false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            True,
            False,
            True,
            "phase_config(zero_tem00_gouy=false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            True,
            True,
            False,
            "phase_config(false, false)",
        ),
        (
            {"zero_k00": False, "zero_tem00_gouy": False},
            True,
            True,
            True,
            "phase_config(zero_k00=false, zero_tem00_gouy=false)",
        ),
    ),
)
def test_phase_config(
    model,
    kwargs,
    directive_defaults,
    argument_defaults,
    prefer_keywords,
    expected,
):
    adapter = KATSPEC.commands["phase_config"]

    if kwargs:
        adapter.setter(model, ((), kwargs))

    dump = next(iter(adapter.getter(adapter, model)))
    script = unparse(
        dump,
        directive_defaults=directive_defaults,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
