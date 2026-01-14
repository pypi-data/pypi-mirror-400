"""CLI config command tests."""

import pytest
from finesse.__main__ import config
from finesse.config import config_instance, _FinesseConfig
from testutils.cli import sanitized_output


@pytest.fixture
def dumped_config(request, cli):
    """The dumped configuration table."""
    return sanitized_output(cli.invoke(config, ["--dump"]))


def test_paths(cli):
    """Test printing the config paths."""
    cli_result = cli.invoke(config)
    output = sanitized_output(cli_result)

    for path in config_instance().user_config_paths().values():
        assert str(path.resolve()) in output

    assert cli_result.exit_code == 0


@pytest.mark.parametrize(
    "key,value",
    [
        (k, v)
        for s in config_instance().sections()
        for k, v in config_instance().items(s)
    ],
)
def test_dump(dumped_config, key, value):
    """Test config dump."""
    assert key in dumped_config
    assert value in dumped_config


def test_user_config_reset(monkeypatch, tmp_path, cli):
    """Test user config reset."""
    config_inst = config_instance()

    # Mock the user config location and write the default user config there.
    # Note that since 'user_config_dir' is a class method, we have to mock the class
    # attribute, not the instance attribute.
    monkeypatch.setattr(_FinesseConfig, "user_config_dir", lambda: tmp_path)
    config_inst.write_user_config()

    # String to write into the current (temporary) config to verify it gets reset.
    test_message = "# __TEST__"

    # Add test message to existing config and verify it's there.
    with config_inst.user_config_path().open("w") as fobj:
        fobj.writelines([test_message])
    with config_inst.user_config_path().open("r") as fobj:
        lines = fobj.readlines()
    assert test_message in lines

    # Reset the config and verify the test message is gone.
    cli_result = cli.invoke(config, args=["--reset"], input="y")
    assert cli_result.exit_code == 0
    with config_inst.user_config_path().open("r") as fobj:
        lines = fobj.readlines()
    assert test_message not in lines
