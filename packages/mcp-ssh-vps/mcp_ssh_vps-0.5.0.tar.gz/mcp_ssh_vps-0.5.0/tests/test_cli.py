"""Tests for CLI interface."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from sshmcp.cli import (
    _parse_ssh_config,
    cli,
    get_config_path,
    load_machines_config,
    save_machines_config,
)
from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    MachinesConfig,
    SecurityConfig,
)


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / ".sshmcp" / "machines.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text('{"machines": []}')
    return config_file


@pytest.fixture
def temp_config_with_server(tmp_path):
    """Create temporary config with a server."""
    config_file = tmp_path / ".sshmcp" / "machines.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        json.dumps(
            {
                "machines": [
                    {
                        "name": "test-server",
                        "host": "192.168.1.1",
                        "port": 22,
                        "user": "testuser",
                        "auth": {"type": "key", "key_path": "~/.ssh/id_rsa"},
                        "security": {
                            "allowed_commands": [".*"],
                            "forbidden_commands": [],
                            "timeout_seconds": 30,
                        },
                        "description": "Test server",
                    }
                ]
            }
        )
    )
    return config_file


class TestGetConfigPath:
    """Tests for get_config_path."""

    def test_default_config_path(self):
        """Test default config path."""
        with patch.dict(os.environ, {}, clear=True):
            if "SSHMCP_CONFIG_PATH" in os.environ:
                del os.environ["SSHMCP_CONFIG_PATH"]
            path = get_config_path()
            assert path == Path.home() / ".sshmcp" / "machines.json"

    def test_env_config_path(self):
        """Test config path from environment variable."""
        with patch.dict(os.environ, {"SSHMCP_CONFIG_PATH": "/custom/path.json"}):
            path = get_config_path()
            assert path == Path("/custom/path.json")


class TestLoadMachinesConfig:
    """Tests for load_machines_config."""

    def test_load_empty_config(self, tmp_path):
        """Test loading empty config."""
        config_file = tmp_path / "machines.json"
        config_file.write_text('{"machines": []}')

        with patch("sshmcp.cli.get_config_path", return_value=config_file):
            config = load_machines_config()

        assert len(config.machines) == 0

    def test_load_config_with_machines(self, temp_config_with_server):
        """Test loading config with machines."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            config = load_machines_config()

        assert len(config.machines) == 1
        assert config.machines[0].name == "test-server"

    def test_load_nonexistent_config(self, tmp_path):
        """Test loading nonexistent config returns empty."""
        nonexistent = tmp_path / "nonexistent.json"

        with patch("sshmcp.cli.get_config_path", return_value=nonexistent):
            config = load_machines_config()

        assert len(config.machines) == 0


class TestSaveMachinesConfig:
    """Tests for save_machines_config."""

    def test_save_config(self, tmp_path):
        """Test saving config."""
        config_file = tmp_path / ".sshmcp" / "machines.json"

        config = MachinesConfig(
            machines=[
                MachineConfig(
                    name="new-server",
                    host="192.168.1.100",
                    port=22,
                    user="deploy",
                    auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
                    security=SecurityConfig(
                        allowed_commands=[".*"],
                        forbidden_commands=[],
                        timeout_seconds=30,
                    ),
                )
            ]
        )

        with patch("sshmcp.cli.get_config_path", return_value=config_file):
            save_machines_config(config)

        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert len(data["machines"]) == 1
        assert data["machines"][0]["name"] == "new-server"


class TestParseSSHConfig:
    """Tests for SSH config parsing."""

    def test_parse_ssh_config(self, tmp_path):
        """Test parsing SSH config file."""
        ssh_config = tmp_path / "config"
        ssh_config.write_text("""
Host myserver
    HostName 192.168.1.50
    User deploy
    Port 2222
    IdentityFile ~/.ssh/mykey

Host another
    HostName 10.0.0.1
    User root
""")
        hosts = _parse_ssh_config(ssh_config)

        assert len(hosts) == 2
        assert hosts[0]["name"] == "myserver"
        assert hosts[0]["hostname"] == "192.168.1.50"
        assert hosts[0]["user"] == "deploy"
        assert hosts[0]["port"] == "2222"
        assert hosts[1]["name"] == "another"
        assert hosts[1]["hostname"] == "10.0.0.1"

    def test_parse_ssh_config_skips_wildcard(self, tmp_path):
        """Test that wildcard host is skipped."""
        ssh_config = tmp_path / "config"
        ssh_config.write_text("""
Host *
    ServerAliveInterval 60

Host myserver
    HostName 192.168.1.50
""")
        hosts = _parse_ssh_config(ssh_config)

        assert len(hosts) == 1
        assert hosts[0]["name"] == "myserver"


class TestServerListCommand:
    """Tests for server list command."""

    def test_list_empty(self, runner, temp_config):
        """Test listing when no servers configured."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            result = runner.invoke(cli, ["server", "list"])

        assert result.exit_code == 0
        assert "No servers configured" in result.output

    def test_list_with_servers(self, runner, temp_config_with_server):
        """Test listing servers."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            result = runner.invoke(cli, ["server", "list"])

        assert result.exit_code == 0
        assert "test-server" in result.output
        assert "192.168.1.1" in result.output

    def test_list_verbose(self, runner, temp_config_with_server):
        """Test verbose listing."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            result = runner.invoke(cli, ["server", "list", "--verbose"])

        assert result.exit_code == 0
        assert "Port:" in result.output
        assert "Description:" in result.output


class TestServerAddCommand:
    """Tests for server add command."""

    def test_add_server_with_key(self, runner, temp_config):
        """Test adding server with key auth."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            with patch("sshmcp.cli.Path.exists", return_value=True):
                result = runner.invoke(
                    cli,
                    ["server", "add"],
                    input=(
                        "new-server\n"
                        "192.168.1.100\n"
                        "22\n"
                        "deploy\n"
                        "key\n"
                        "n\n"  # Don't test connection
                    ),
                )

        assert result.exit_code == 0
        assert "added successfully" in result.output

    def test_add_duplicate_server_fails(self, runner, temp_config_with_server):
        """Test adding duplicate server fails."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            result = runner.invoke(
                cli,
                ["server", "add"],
                input=("test-server\n192.168.1.100\n22\ndeploy\nkey\n"),
            )

        assert result.exit_code == 1
        assert "already exists" in result.output


class TestServerRemoveCommand:
    """Tests for server remove command."""

    def test_remove_server(self, runner, temp_config_with_server):
        """Test removing server."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            result = runner.invoke(cli, ["server", "remove", "test-server", "--force"])

        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_nonexistent_fails(self, runner, temp_config):
        """Test removing nonexistent server fails."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            result = runner.invoke(cli, ["server", "remove", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output


class TestServerTestCommand:
    """Tests for server test command."""

    def test_test_connection_success(self, runner, temp_config_with_server):
        """Test successful connection test."""
        mock_client_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "Connection successful!\nhostname\nuptime"
        mock_client_instance.execute.return_value = mock_result
        mock_client_instance.connect.return_value = None
        mock_client_instance.disconnect.return_value = None

        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            with patch(
                "sshmcp.ssh.client.SSHClient", return_value=mock_client_instance
            ):
                result = runner.invoke(cli, ["server", "test", "test-server"])

        assert result.exit_code == 0
        assert "Connection successful" in result.output

    def test_test_connection_failure(self, runner, temp_config_with_server):
        """Test connection test failure."""
        mock_client_instance = MagicMock()
        mock_client_instance.connect.side_effect = Exception("Connection refused")

        with patch("sshmcp.cli.get_config_path", return_value=temp_config_with_server):
            with patch(
                "sshmcp.ssh.client.SSHClient", return_value=mock_client_instance
            ):
                result = runner.invoke(cli, ["server", "test", "test-server"])

        assert "Connection failed" in result.output

    def test_test_nonexistent_server(self, runner, temp_config):
        """Test testing nonexistent server."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            result = runner.invoke(cli, ["server", "test", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output


class TestImportSSHCommand:
    """Tests for import-ssh command."""

    def test_import_ssh_no_file(self, runner, temp_config):
        """Test import when SSH config doesn't exist."""
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            result = runner.invoke(
                cli, ["server", "import-ssh", "--ssh-config", "/nonexistent/config"]
            )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_import_ssh_success(self, runner, temp_config, tmp_path):
        """Test successful SSH import."""
        ssh_config = tmp_path / "ssh_config"
        ssh_config.write_text("""
Host imported-server
    HostName 192.168.1.200
    User admin
    Port 22
""")
        with patch("sshmcp.cli.get_config_path", return_value=temp_config):
            result = runner.invoke(
                cli,
                ["server", "import-ssh", "--ssh-config", str(ssh_config)],
                input="y\n",  # Confirm import
            )

        assert result.exit_code == 0
        assert "imported-server" in result.output


class TestVersionCommand:
    """Tests for version command."""

    def test_version(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
