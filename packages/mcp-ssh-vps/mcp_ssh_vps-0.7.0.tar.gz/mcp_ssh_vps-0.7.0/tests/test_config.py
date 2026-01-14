"""Tests for configuration loading."""

import json
import tempfile

import pytest

from sshmcp.config import ConfigurationError, load_config
from sshmcp.models.machine import MachineConfig, MachinesConfig


def test_load_valid_config():
    """Test loading a valid configuration file."""
    config_data = {
        "machines": [
            {
                "name": "test-server",
                "host": "192.168.1.1",
                "port": 22,
                "user": "testuser",
                "auth": {"type": "key", "key_path": "~/.ssh/id_rsa"},
                "security": {"allowed_commands": [".*"], "timeout_seconds": 30},
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        f.flush()

        config = load_config(f.name)

        assert isinstance(config, MachinesConfig)
        assert len(config.machines) == 1
        assert config.machines[0].name == "test-server"
        assert config.machines[0].host == "192.168.1.1"


def test_load_invalid_json():
    """Test loading an invalid JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json {")
        f.flush()

        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            load_config(f.name)


def test_load_missing_file():
    """Test loading a non-existent file."""
    with pytest.raises(ConfigurationError, match="not found"):
        load_config("/nonexistent/path/config.json")


def test_machine_config_validation():
    """Test MachineConfig validation."""
    # Valid config
    machine = MachineConfig(
        name="test-server",
        host="192.168.1.1",
        user="testuser",
        auth={"type": "key", "key_path": "~/.ssh/id_rsa"},
    )
    assert machine.name == "test-server"
    assert machine.port == 22  # default

    # Invalid name
    with pytest.raises(ValueError):
        MachineConfig(
            name="invalid name with spaces",
            host="192.168.1.1",
            user="testuser",
            auth={"type": "key", "key_path": "~/.ssh/id_rsa"},
        )


def test_machines_config_get_machine():
    """Test getting machine by name."""
    config = MachinesConfig(
        machines=[
            MachineConfig(
                name="server1",
                host="192.168.1.1",
                user="user1",
                auth={"type": "key", "key_path": "~/.ssh/id_rsa"},
            ),
            MachineConfig(
                name="server2",
                host="192.168.1.2",
                user="user2",
                auth={"type": "key", "key_path": "~/.ssh/id_rsa"},
            ),
        ]
    )

    machine = config.get_machine("server1")
    assert machine is not None
    assert machine.host == "192.168.1.1"

    machine = config.get_machine("nonexistent")
    assert machine is None

    assert config.has_machine("server1")
    assert not config.has_machine("nonexistent")
    assert config.get_machine_names() == ["server1", "server2"]
