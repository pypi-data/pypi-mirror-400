"""Tests for process management tools."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
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
            forbidden_commands=[],
            timeout_seconds=30,
        ),
    )


@pytest.fixture
def mock_command_result():
    """Create a mock command result."""
    result = MagicMock()
    result.exit_code = 0
    result.stdout = "active (running)"
    result.stderr = ""
    return result


class TestManageProcess:
    """Tests for manage_process function."""

    def test_manage_process_restart_systemd(self, mock_machine, mock_command_result):
        """Test restarting service with systemd."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.processes.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.processes.get_pool", return_value=mock_pool):
                with patch("sshmcp.tools.processes.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()
                    with patch(
                        "sshmcp.tools.processes._detect_service_manager",
                        return_value="systemd",
                    ):
                        from sshmcp.tools.processes import manage_process

                        result = manage_process("test-server", "restart", "nginx")

        assert result["success"] is True
        assert result["action"] == "restart"
        assert result["process"] == "nginx"
        assert result["service_manager"] == "systemd"
        mock_client.execute.assert_called_with("systemctl restart nginx")

    def test_manage_process_status_systemd(self, mock_machine, mock_command_result):
        """Test getting status with systemd."""
        mock_client = MagicMock()
        mock_client.execute.return_value = mock_command_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.processes.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.processes.get_pool", return_value=mock_pool):
                with patch("sshmcp.tools.processes.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()
                    with patch(
                        "sshmcp.tools.processes._detect_service_manager",
                        return_value="systemd",
                    ):
                        from sshmcp.tools.processes import manage_process

                        result = manage_process("test-server", "status", "nginx")

        assert result["status"] == "running"
        mock_client.execute.assert_called_with("systemctl status nginx")

    def test_manage_process_pm2(self, mock_machine):
        """Test process management with pm2."""
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "online"
        mock_result.stderr = ""

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.processes.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.processes.get_pool", return_value=mock_pool):
                with patch("sshmcp.tools.processes.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.processes import manage_process

                    result = manage_process(
                        "test-server", "status", "app", service_manager="pm2"
                    )

        assert result["service_manager"] == "pm2"
        assert result["status"] == "running"
        mock_client.execute.assert_called_with("pm2 describe app")

    def test_manage_process_supervisor(self, mock_machine):
        """Test process management with supervisor."""
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "RUNNING"
        mock_result.stderr = ""

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.processes.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.processes.get_pool", return_value=mock_pool):
                with patch("sshmcp.tools.processes.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.processes import manage_process

                    result = manage_process(
                        "test-server", "restart", "myapp", service_manager="supervisor"
                    )

        assert result["service_manager"] == "supervisor"
        mock_client.execute.assert_called_with("supervisorctl restart myapp")

    def test_manage_process_invalid_action(self, mock_machine):
        """Test with invalid action."""
        from sshmcp.tools.processes import manage_process

        with pytest.raises(ValueError, match="Invalid action"):
            manage_process("test-server", "invalid", "nginx")

    def test_manage_process_host_not_found(self):
        """Test with non-existent host."""
        with patch(
            "sshmcp.tools.processes.get_machine",
            side_effect=Exception("Host not found"),
        ):
            from sshmcp.tools.processes import manage_process

            with pytest.raises(ValueError, match="Host not found"):
                manage_process("nonexistent", "restart", "nginx")

    def test_manage_process_ssh_error(self, mock_machine):
        """Test with SSH error."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection failed")

        with patch("sshmcp.tools.processes.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.processes.get_pool", return_value=mock_pool):
                with patch("sshmcp.tools.processes.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.processes import manage_process

                    with pytest.raises(RuntimeError, match="SSH error"):
                        manage_process("test-server", "restart", "nginx")


class TestDetectServiceManager:
    """Tests for _detect_service_manager helper."""

    def test_detect_systemd(self):
        """Test detecting systemd."""
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "enabled"
        mock_client.execute.return_value = mock_result

        from sshmcp.tools.processes import _detect_service_manager

        result = _detect_service_manager(mock_client, "nginx")

        assert result == "systemd"

    def test_detect_pm2(self):
        """Test detecting pm2."""
        mock_client = MagicMock()

        # First call for systemd fails
        systemd_result = MagicMock()
        systemd_result.exit_code = 1
        systemd_result.stdout = ""

        # pm2 which succeeds
        pm2_which = MagicMock()
        pm2_which.exit_code = 0

        # pm2 describe succeeds
        pm2_describe = MagicMock()
        pm2_describe.exit_code = 0

        mock_client.execute.side_effect = [systemd_result, pm2_which, pm2_describe]

        from sshmcp.tools.processes import _detect_service_manager

        result = _detect_service_manager(mock_client, "app")

        assert result == "pm2"

    def test_detect_supervisor(self):
        """Test detecting supervisor."""
        mock_client = MagicMock()

        # systemd fails
        systemd_result = MagicMock()
        systemd_result.exit_code = 1
        systemd_result.stdout = ""

        # pm2 which fails
        pm2_which = MagicMock()
        pm2_which.exit_code = 1

        # supervisor which succeeds
        supervisor_which = MagicMock()
        supervisor_which.exit_code = 0

        mock_client.execute.side_effect = [systemd_result, pm2_which, supervisor_which]

        from sshmcp.tools.processes import _detect_service_manager

        result = _detect_service_manager(mock_client, "app")

        assert result == "supervisor"

    def test_detect_fallback_systemd(self):
        """Test fallback to systemd when nothing detected."""
        mock_client = MagicMock()
        mock_client.execute.side_effect = Exception("Command failed")

        from sshmcp.tools.processes import _detect_service_manager

        result = _detect_service_manager(mock_client, "app")

        assert result == "systemd"


class TestBuildProcessCommand:
    """Tests for _build_process_command helper."""

    def test_build_systemd_commands(self):
        """Test building systemd commands."""
        from sshmcp.tools.processes import _build_process_command

        assert (
            _build_process_command("systemd", "start", "nginx")
            == "systemctl start nginx"
        )
        assert (
            _build_process_command("systemd", "stop", "nginx") == "systemctl stop nginx"
        )
        assert (
            _build_process_command("systemd", "restart", "nginx")
            == "systemctl restart nginx"
        )
        assert (
            _build_process_command("systemd", "status", "nginx")
            == "systemctl status nginx"
        )

    def test_build_pm2_commands(self):
        """Test building pm2 commands."""
        from sshmcp.tools.processes import _build_process_command

        assert _build_process_command("pm2", "start", "app") == "pm2 start app"
        assert _build_process_command("pm2", "stop", "app") == "pm2 stop app"
        assert _build_process_command("pm2", "restart", "app") == "pm2 restart app"
        assert _build_process_command("pm2", "status", "app") == "pm2 describe app"

    def test_build_supervisor_commands(self):
        """Test building supervisor commands."""
        from sshmcp.tools.processes import _build_process_command

        assert (
            _build_process_command("supervisor", "start", "app")
            == "supervisorctl start app"
        )
        assert (
            _build_process_command("supervisor", "stop", "app")
            == "supervisorctl stop app"
        )
        assert (
            _build_process_command("supervisor", "restart", "app")
            == "supervisorctl restart app"
        )
        assert (
            _build_process_command("supervisor", "status", "app")
            == "supervisorctl status app"
        )

    def test_build_unknown_service_manager(self):
        """Test with unknown service manager."""
        from sshmcp.tools.processes import _build_process_command

        with pytest.raises(ValueError, match="Unknown service manager"):
            _build_process_command("unknown", "start", "app")


class TestParseStatus:
    """Tests for _parse_status helper."""

    def test_parse_systemd_running(self):
        """Test parsing systemd running status."""
        from sshmcp.tools.processes import _parse_status

        assert _parse_status("systemd", "Active: active (running)", 0) == "running"
        assert _parse_status("systemd", "inactive (dead)", 0) == "stopped"
        assert _parse_status("systemd", "failed", 1) == "failed"
        assert _parse_status("systemd", "activating (start)", 0) == "starting"
        assert _parse_status("systemd", "something else", 0) == "unknown"

    def test_parse_pm2_status(self):
        """Test parsing pm2 status."""
        from sshmcp.tools.processes import _parse_status

        assert _parse_status("pm2", "status: online", 0) == "running"
        assert _parse_status("pm2", "status: stopped", 0) == "stopped"
        assert _parse_status("pm2", "status: errored", 1) == "failed"
        assert _parse_status("pm2", "something else", 0) == "unknown"

    def test_parse_supervisor_status(self):
        """Test parsing supervisor status."""
        from sshmcp.tools.processes import _parse_status

        assert _parse_status("supervisor", "RUNNING", 0) == "running"
        assert _parse_status("supervisor", "STOPPED", 0) == "stopped"
        assert _parse_status("supervisor", "FATAL", 1) == "failed"
        assert _parse_status("supervisor", "ERROR:", 1) == "failed"
        assert _parse_status("supervisor", "something else", 0) == "unknown"
