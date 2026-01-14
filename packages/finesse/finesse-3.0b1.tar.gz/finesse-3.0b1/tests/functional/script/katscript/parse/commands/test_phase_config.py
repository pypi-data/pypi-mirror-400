"""Test phase_config command parsing."""

import pytest


@pytest.mark.parametrize(
    "script,zero_k00,zero_tem00_gouy",
    (
        ("", False, True),
        ("true", True, True),
        ("false", False, True),
        ("true, true", True, True),
        ("true, false", True, False),
        ("false, true", False, True),
        ("false, false", False, False),
        ("true, zero_tem00_gouy=false", True, False),
        ("false, zero_tem00_gouy=false", False, False),
        ("true, zero_tem00_gouy=true", True, True),
        ("false, zero_tem00_gouy=true", False, True),
        ("zero_k00=true", True, True),
        ("zero_k00=false", False, True),
        ("zero_k00=true, zero_tem00_gouy=true", True, True),
        ("zero_k00=true, zero_tem00_gouy=false", True, False),
        ("zero_k00=false, zero_tem00_gouy=true", False, True),
        ("zero_k00=false, zero_tem00_gouy=false", False, False),
    ),
)
def test_phase_config(model, script, zero_k00, zero_tem00_gouy):
    """Test that the phase_config command parses correctly."""
    model.parse(f"phase_config({script})")
    assert model._settings.phase_config.zero_k00 == zero_k00
    assert model._settings.phase_config.zero_tem00_gouy == zero_tem00_gouy
