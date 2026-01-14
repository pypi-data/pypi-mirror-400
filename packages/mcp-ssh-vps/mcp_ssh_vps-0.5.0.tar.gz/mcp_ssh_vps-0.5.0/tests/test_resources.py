"""Tests for MCP resources."""

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


class TestGetLogs:
    """Tests for get_logs resource."""

    def test_get_logs_success(self, mock_machine):
        """Test successful log retrieval."""
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = (
            "2024-01-01 INFO Starting server\n2024-01-01 INFO Server ready"
        )
        mock_result.stderr = ""

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.logs.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.resources.logs.validate_path", return_value=(True, None)
            ):
                with patch("sshmcp.resources.logs.get_pool", return_value=mock_pool):
                    with patch("sshmcp.resources.logs.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.resources.logs import get_logs

                        result = get_logs("test-server", "/var/log/app.log")

        assert "Starting server" in result
        mock_client.execute.assert_called_once()
        mock_pool.release_client.assert_called_once_with(mock_client)

    def test_get_logs_normalizes_path(self, mock_machine):
        """Test that path without leading slash is normalized."""
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "logs"
        mock_result.stderr = ""

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.logs.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.resources.logs.validate_path", return_value=(True, None)
            ) as mock_validate:
                with patch("sshmcp.resources.logs.get_pool", return_value=mock_pool):
                    with patch("sshmcp.resources.logs.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.resources.logs import get_logs

                        get_logs("test-server", "var/log/app.log")

        # Should be called with normalized path
        mock_validate.assert_called_once()
        args = mock_validate.call_args[0]
        assert args[0] == "/var/log/app.log"

    def test_get_logs_with_filter_error(self, mock_machine):
        """Test log filtering by error level."""
        mock_result = MagicMock()
        mock_result.exit_code = 0
        mock_result.stdout = "ERROR: Something went wrong"
        mock_result.stderr = ""

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.logs.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.resources.logs.validate_path", return_value=(True, None)
            ):
                with patch("sshmcp.resources.logs.get_pool", return_value=mock_pool):
                    with patch("sshmcp.resources.logs.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.resources.logs import get_logs

                        get_logs(
                            "test-server", "/var/log/app.log", filter_level="error"
                        )

        # Check grep pattern was used
        call_args = mock_client.execute.call_args[0][0]
        assert "grep" in call_args
        assert "ERROR" in call_args

    def test_get_logs_host_not_found(self):
        """Test with non-existent host."""
        with patch(
            "sshmcp.resources.logs.get_machine", side_effect=Exception("Host not found")
        ):
            from sshmcp.resources.logs import get_logs

            with pytest.raises(ValueError, match="Host not found"):
                get_logs("nonexistent", "/var/log/app.log")

    def test_get_logs_path_not_allowed(self, mock_machine):
        """Test with disallowed path."""
        with patch("sshmcp.resources.logs.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.resources.logs.validate_path",
                return_value=(False, "Path forbidden"),
            ):
                with patch("sshmcp.resources.logs.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.resources.logs import get_logs

                    with pytest.raises(ValueError, match="Path not allowed"):
                        get_logs("test-server", "/etc/shadow")

    def test_get_logs_file_not_found(self, mock_machine):
        """Test with non-existent log file."""
        mock_result = MagicMock()
        mock_result.exit_code = 1
        mock_result.stdout = ""
        mock_result.stderr = "No such file or directory"

        mock_client = MagicMock()
        mock_client.execute.return_value = mock_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.logs.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.resources.logs.validate_path", return_value=(True, None)
            ):
                with patch("sshmcp.resources.logs.get_pool", return_value=mock_pool):
                    with patch("sshmcp.resources.logs.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.resources.logs import get_logs

                        with pytest.raises(RuntimeError, match="Log file not found"):
                            get_logs("test-server", "/var/log/nonexistent.log")


class TestGetMetrics:
    """Tests for get_metrics resource."""

    def test_get_metrics_success(self, mock_machine):
        """Test successful metrics retrieval."""
        mock_client = MagicMock()

        # CPU result
        cpu_result = MagicMock()
        cpu_result.exit_code = 0
        cpu_result.stdout = "%Cpu(s):  5.0 us,  2.0 sy,  0.0 ni, 93.0 id"

        # Memory result
        mem_result = MagicMock()
        mem_result.exit_code = 0
        mem_result.stdout = "              total        used        free      shared  buff/cache   available\nMem:           7982        2048        3000         100        2934        5500"

        # Disk result
        disk_result = MagicMock()
        disk_result.exit_code = 0
        disk_result.stdout = "/dev/sda1       50G   20G   28G  42% /"

        # Uptime result
        uptime_result = MagicMock()
        uptime_result.exit_code = 0
        uptime_result.stdout = "86400.50 172800.00"

        # Load result
        load_result = MagicMock()
        load_result.exit_code = 0
        load_result.stdout = "0.50 0.75 1.00 1/200 12345"

        mock_client.execute.side_effect = [
            cpu_result,
            mem_result,
            disk_result,
            uptime_result,
            load_result,
        ]

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.metrics.get_machine", return_value=mock_machine):
            with patch("sshmcp.resources.metrics.get_pool", return_value=mock_pool):
                with patch("sshmcp.resources.metrics.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.resources.metrics import get_metrics

                    result = get_metrics("test-server")

        assert result["host"] == "test-server"
        assert result["cpu"]["usage_percent"] == 7.0  # 100 - 93
        assert result["memory"]["total_mb"] == 7982
        assert result["memory"]["used_mb"] == 2048
        assert result["disk"]["usage_percent"] == 42.0
        assert result["uptime_seconds"] == 86400
        assert result["load_average"]["1min"] == 0.50

    def test_get_metrics_host_not_found(self):
        """Test with non-existent host."""
        with patch(
            "sshmcp.resources.metrics.get_machine",
            side_effect=Exception("Host not found"),
        ):
            from sshmcp.resources.metrics import get_metrics

            with pytest.raises(ValueError, match="Host not found"):
                get_metrics("nonexistent")

    def test_get_metrics_ssh_error(self, mock_machine):
        """Test with SSH error."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection failed")

        with patch("sshmcp.resources.metrics.get_machine", return_value=mock_machine):
            with patch("sshmcp.resources.metrics.get_pool", return_value=mock_pool):
                with patch("sshmcp.resources.metrics.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.resources.metrics import get_metrics

                    with pytest.raises(RuntimeError, match="Failed to get metrics"):
                        get_metrics("test-server")


class TestMetricsParsers:
    """Tests for metric parsing helpers."""

    def test_parse_cpu(self):
        """Test CPU parsing."""
        from sshmcp.resources.metrics import _parse_cpu

        result = _parse_cpu("%Cpu(s):  5.0 us,  2.0 sy,  0.0 ni, 93.0 id")
        assert result["usage_percent"] == 7.0

    def test_parse_memory(self):
        """Test memory parsing."""
        from sshmcp.resources.metrics import _parse_memory

        output = """              total        used        free      shared  buff/cache   available
Mem:           8000        2000        4000         100        1900        5000"""
        result = _parse_memory(output)

        assert result["total_mb"] == 8000
        assert result["used_mb"] == 2000
        assert result["available_mb"] == 5000
        assert result["usage_percent"] == 25.0

    def test_parse_disk(self):
        """Test disk parsing."""
        from sshmcp.resources.metrics import _parse_disk

        result = _parse_disk("/dev/sda1       100G   40G   55G  42% /")
        assert result["total_gb"] == 100.0
        assert result["used_gb"] == 40.0
        assert result["available_gb"] == 55.0
        assert result["usage_percent"] == 42.0

    def test_parse_disk_with_terabytes(self):
        """Test disk parsing with TB sizes."""
        from sshmcp.resources.metrics import _parse_disk

        result = _parse_disk("/dev/sda1       1T   500G   400G  56% /")
        assert result["total_gb"] == 1024.0
        assert result["used_gb"] == 500.0

    def test_parse_uptime(self):
        """Test uptime parsing."""
        from sshmcp.resources.metrics import _parse_uptime

        assert _parse_uptime("86400.50 172800.00") == 86400
        assert _parse_uptime("3600.00") == 3600
        assert _parse_uptime("") == 0

    def test_parse_load(self):
        """Test load average parsing."""
        from sshmcp.resources.metrics import _parse_load

        result = _parse_load("0.50 0.75 1.00 1/200 12345")
        assert result["1min"] == 0.50
        assert result["5min"] == 0.75
        assert result["15min"] == 1.00


class TestGetStatus:
    """Tests for get_status resource."""

    def test_get_status_success(self, mock_machine):
        """Test successful status retrieval."""
        # Mock results for various commands
        hostname_result = MagicMock()
        hostname_result.exit_code = 0
        hostname_result.stdout = "test-hostname"

        uname_result = MagicMock()
        uname_result.exit_code = 0
        uname_result.stdout = "Linux test-hostname 5.4.0 #1 SMP x86_64 GNU/Linux"

        os_result = MagicMock()
        os_result.exit_code = 0
        os_result.stdout = "Ubuntu 22.04 LTS"

        services_result = MagicMock()
        services_result.exit_code = 0
        services_result.stdout = "nginx.service loaded active running"

        mock_client = MagicMock()
        mock_client.execute.side_effect = [
            hostname_result,
            uname_result,
            os_result,
            services_result,
        ]

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.resources.status.get_machine", return_value=mock_machine):
            with patch("sshmcp.resources.status.get_pool", return_value=mock_pool):
                with patch("sshmcp.resources.status.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.resources.status import get_status

                    result = get_status("test-server")

        assert result["host"] == "test-server"
        assert result["status"] == "online"
        assert result["hostname"] == "test-hostname"

    def test_get_status_offline(self, mock_machine):
        """Test status when server is offline."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection refused")

        with patch("sshmcp.resources.status.get_machine", return_value=mock_machine):
            with patch("sshmcp.resources.status.get_pool", return_value=mock_pool):
                with patch("sshmcp.resources.status.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.resources.status import get_status

                    result = get_status("test-server")

        assert result["status"] == "offline"
        assert "error" in result
