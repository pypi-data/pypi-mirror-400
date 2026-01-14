"""Tests for command execution tools."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.models.command import CommandResult
from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    MachinesConfig,
    SecurityConfig,
)


@pytest.fixture
def mock_machine():
    """Create a mock machine configuration."""
    return MachineConfig(
        name="test-server",
        host="192.168.1.1",
        port=22,
        user="testuser",
        auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
        security=SecurityConfig(
            allowed_commands=[".*"],
            forbidden_commands=[r".*rm\s+-rf\s+/$"],
            timeout_seconds=30,
        ),
        tags=["test", "web"],
    )


@pytest.fixture
def mock_config(mock_machine):
    """Create a mock config with machines."""
    return MachinesConfig(machines=[mock_machine])


@pytest.fixture
def mock_command_result():
    """Create a mock command result."""
    result = MagicMock(spec=CommandResult)
    result.exit_code = 0
    result.stdout = "command output"
    result.stderr = ""
    result.duration_ms = 100
    result.to_dict.return_value = {
        "exit_code": 0,
        "stdout": "command output",
        "stderr": "",
        "duration_ms": 100,
        "success": True,
    }
    return result


class TestExecuteCommand:
    """Tests for execute_command function."""

    def test_execute_command_success(self, mock_machine, mock_command_result):
        """Test successful command execution."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.commands.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                with patch(
                    "sshmcp.tools.commands.validate_command", return_value=(True, None)
                ):
                    with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.commands import execute_command

                        # Use detailed format to get full response
                        result = execute_command(
                            "test-server", "echo hello", response_format="detailed"
                        )

        assert result["exit_code"] == 0
        assert result["stdout"] == "command output"
        mock_client.execute.assert_called_once()
        mock_pool.release_client.assert_called_once_with(mock_client)

    def test_execute_command_host_not_found(self):
        """Test execution with non-existent host."""
        with patch(
            "sshmcp.tools.commands.get_machine", side_effect=Exception("Host not found")
        ):
            with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                mock_audit.return_value = MagicMock()

                from sshmcp.tools.commands import execute_command

                with pytest.raises(ValueError, match="Host not found"):
                    execute_command("nonexistent", "echo hello")

    def test_execute_command_not_allowed(self, mock_machine):
        """Test execution with disallowed command."""
        with patch("sshmcp.tools.commands.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.tools.commands.validate_command",
                return_value=(False, "Command forbidden"),
            ):
                with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.commands import execute_command

                    with pytest.raises(ValueError, match="Command not allowed"):
                        execute_command("test-server", "rm -rf /")

    def test_execute_command_ssh_error(self, mock_machine):
        """Test execution with SSH error."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection failed")

        with patch("sshmcp.tools.commands.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.tools.commands.validate_command", return_value=(True, None)
            ):
                with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.commands import execute_command

                        # Now returns error dict instead of raising
                        result = execute_command("test-server", "echo hello")
                        assert result["success"] is False
                        assert "error" in result

    def test_execute_command_with_custom_timeout(
        self, mock_machine, mock_command_result
    ):
        """Test execution with custom timeout."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.commands.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                with patch(
                    "sshmcp.tools.commands.validate_command", return_value=(True, None)
                ):
                    with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.commands import execute_command

                        execute_command("test-server", "echo hello", timeout=60)

        mock_client.execute.assert_called_once_with("echo hello", timeout=60)


class TestExecuteOnMultiple:
    """Tests for execute_on_multiple function."""

    def test_execute_on_all_servers(self, mock_config, mock_command_result):
        """Test execution on all servers with wildcard."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.commands.list_machines", return_value=["test-server"]):
            with patch(
                "sshmcp.tools.commands.get_machine",
                return_value=mock_config.machines[0],
            ):
                with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                    with patch(
                        "sshmcp.tools.commands.validate_command",
                        return_value=(True, None),
                    ):
                        with patch(
                            "sshmcp.tools.commands.get_audit_logger"
                        ) as mock_audit:
                            mock_audit.return_value = MagicMock()

                            from sshmcp.tools.commands import execute_on_multiple

                            # Use detailed format to get full response
                            result = execute_on_multiple(
                                ["*"], "uptime", response_format="detailed"
                            )

        assert result["total"] == 1
        assert result["successful"] == 1
        assert result["failed"] == 0
        assert "test-server" in result["results"]

    def test_execute_on_tagged_servers(self, mock_config, mock_command_result):
        """Test execution on servers filtered by tag."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.commands.get_config", return_value=mock_config):
            with patch(
                "sshmcp.tools.commands.get_machine",
                return_value=mock_config.machines[0],
            ):
                with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                    with patch(
                        "sshmcp.tools.commands.validate_command",
                        return_value=(True, None),
                    ):
                        with patch(
                            "sshmcp.tools.commands.get_audit_logger"
                        ) as mock_audit:
                            mock_audit.return_value = MagicMock()

                            from sshmcp.tools.commands import execute_on_multiple

                            result = execute_on_multiple(
                                ["tag:web"], "uptime", response_format="detailed"
                            )

        assert result["total"] == 1
        assert result["successful"] == 1

    def test_execute_on_nonexistent_tag(self, mock_config):
        """Test execution with non-existent tag."""
        with patch("sshmcp.tools.commands.get_config", return_value=mock_config):
            from sshmcp.tools.commands import execute_on_multiple

            result = execute_on_multiple(["tag:nonexistent"], "uptime")

        assert result["success"] is False
        assert "No servers found" in result["error"]

    def test_execute_on_empty_hosts(self):
        """Test execution with empty hosts list."""
        with patch("sshmcp.tools.commands.list_machines", return_value=[]):
            from sshmcp.tools.commands import execute_on_multiple

            result = execute_on_multiple([], "uptime")

        assert result["success"] is False
        assert "No hosts specified" in result["error"]

    def test_execute_on_multiple_stop_on_error(self, mock_config):
        """Test stop on first error."""
        with patch(
            "sshmcp.tools.commands.list_machines", return_value=["server1", "server2"]
        ):
            with patch(
                "sshmcp.tools.commands.get_machine",
                side_effect=Exception("Host not found"),
            ):
                with patch("sshmcp.tools.commands.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.commands import execute_on_multiple

                    result = execute_on_multiple(
                        ["server1", "server2"],
                        "uptime",
                        stop_on_error=True,
                        parallel=False,
                        response_format="detailed",
                    )

        assert result["failed"] >= 1

    def test_execute_on_multiple_parallel(self, mock_config, mock_command_result):
        """Test parallel execution."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        # Create config with multiple machines
        machines = [
            MachineConfig(
                name=f"server{i}",
                host=f"192.168.1.{i}",
                port=22,
                user="testuser",
                auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
                security=SecurityConfig(
                    allowed_commands=[".*"],
                    forbidden_commands=[],
                    timeout_seconds=30,
                ),
            )
            for i in range(3)
        ]
        MachinesConfig(machines=machines)

        def get_machine_by_name(name):
            for m in machines:
                if m.name == name:
                    return m
            raise Exception("Host not found")

        with patch(
            "sshmcp.tools.commands.list_machines",
            return_value=["server0", "server1", "server2"],
        ):
            with patch(
                "sshmcp.tools.commands.get_machine", side_effect=get_machine_by_name
            ):
                with patch("sshmcp.tools.commands.get_pool", return_value=mock_pool):
                    with patch(
                        "sshmcp.tools.commands.validate_command",
                        return_value=(True, None),
                    ):
                        with patch(
                            "sshmcp.tools.commands.get_audit_logger"
                        ) as mock_audit:
                            mock_audit.return_value = MagicMock()

                            from sshmcp.tools.commands import execute_on_multiple

                            result = execute_on_multiple(
                                ["*"],
                                "uptime",
                                parallel=True,
                                response_format="detailed",
                            )

        assert result["total"] == 3
        assert result["successful"] == 3


class TestGetAllTags:
    """Tests for _get_all_tags helper."""

    def test_get_all_tags(self, mock_config):
        """Test getting all unique tags."""
        with patch("sshmcp.tools.commands.get_config", return_value=mock_config):
            from sshmcp.tools.commands import _get_all_tags

            tags = _get_all_tags()

        assert "test" in tags
        assert "web" in tags

    def test_get_all_tags_empty(self):
        """Test getting tags when no machines have tags."""
        empty_config = MachinesConfig(machines=[])

        with patch("sshmcp.tools.commands.get_config", return_value=empty_config):
            from sshmcp.tools.commands import _get_all_tags

            tags = _get_all_tags()

        assert tags == []
