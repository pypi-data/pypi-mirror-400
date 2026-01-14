"""Tests for async SSH client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sshmcp.models.command import CommandResult
from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig


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


class TestAsyncSSHClient:
    """Tests for AsyncSSHClient."""

    @pytest.mark.anyio
    async def test_async_client_connect(self, mock_machine):
        """Test async client connection."""
        from sshmcp.ssh.async_client import AsyncSSHClient

        with patch("sshmcp.ssh.async_client.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_instance.is_connected = True
            mock_ssh.return_value = mock_instance

            client = AsyncSSHClient(mock_machine)
            await client.connect()

            assert client.is_connected
            mock_instance.connect.assert_called_once()

    @pytest.mark.anyio
    async def test_async_client_disconnect(self, mock_machine):
        """Test async client disconnection."""
        from sshmcp.ssh.async_client import AsyncSSHClient

        with patch("sshmcp.ssh.async_client.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_instance.is_connected = True
            mock_ssh.return_value = mock_instance

            client = AsyncSSHClient(mock_machine)
            await client.connect()
            await client.disconnect()

            mock_instance.disconnect.assert_called_once()

    @pytest.mark.anyio
    async def test_async_client_execute(self, mock_machine):
        """Test async command execution."""
        from sshmcp.ssh.async_client import AsyncSSHClient

        mock_result = MagicMock(spec=CommandResult)
        mock_result.exit_code = 0
        mock_result.stdout = "hello"

        with patch("sshmcp.ssh.async_client.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_instance.is_connected = True
            mock_instance.execute.return_value = mock_result
            mock_ssh.return_value = mock_instance

            client = AsyncSSHClient(mock_machine)
            result = await client.execute("echo hello")

            assert result.exit_code == 0
            mock_instance.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_async_context_manager(self, mock_machine):
        """Test async context manager."""
        from sshmcp.ssh.async_client import AsyncSSHClient

        with patch("sshmcp.ssh.async_client.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_instance.is_connected = True
            mock_ssh.return_value = mock_instance

            async with AsyncSSHClient(mock_machine) as client:
                assert client.is_connected

            mock_instance.disconnect.assert_called_once()


class TestExecuteOnHostsAsync:
    """Tests for execute_on_hosts_async function."""

    @pytest.mark.anyio
    async def test_execute_on_multiple_hosts(self, mock_machine):
        """Test executing on multiple hosts."""
        from sshmcp.ssh.async_client import execute_on_hosts_async

        mock_result = MagicMock(spec=CommandResult)
        mock_result.exit_code = 0
        mock_result.to_dict.return_value = {"exit_code": 0, "stdout": "ok"}

        with patch("sshmcp.ssh.async_client.AsyncSSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.execute = AsyncMock(return_value=mock_result)
            mock_client_class.return_value = mock_client

            machines = [mock_machine]
            results = await execute_on_hosts_async(machines, "uptime")

            assert "test-server" in results
            assert results["test-server"]["success"] is True

    @pytest.mark.anyio
    async def test_execute_handles_errors(self, mock_machine):
        """Test error handling in parallel execution."""
        from sshmcp.ssh.async_client import execute_on_hosts_async
        from sshmcp.ssh.client import SSHConnectionError

        with patch("sshmcp.ssh.async_client.AsyncSSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(
                side_effect=SSHConnectionError("Connection failed")
            )
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            machines = [mock_machine]
            results = await execute_on_hosts_async(machines, "uptime")

            assert "test-server" in results
            assert results["test-server"]["success"] is False
            assert "error" in results["test-server"]


class TestHealthCheckHostsAsync:
    """Tests for health_check_hosts_async function."""

    @pytest.mark.anyio
    async def test_health_check(self, mock_machine):
        """Test async health check."""
        from sshmcp.ssh.async_client import health_check_hosts_async

        mock_result = MagicMock(spec=CommandResult)
        mock_result.exit_code = 0
        mock_result.to_dict.return_value = {"exit_code": 0, "stdout": "ok"}

        with patch("sshmcp.ssh.async_client.AsyncSSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.execute = AsyncMock(return_value=mock_result)
            mock_client_class.return_value = mock_client

            machines = [mock_machine]
            results = await health_check_hosts_async(machines)

            assert "test-server" in results
            assert results["test-server"]["success"] is True
