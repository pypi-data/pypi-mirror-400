"""Tests for SSH client."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
from sshmcp.ssh.client import SSHClient, SSHConnectionError


@pytest.fixture
def machine_config():
    """Create a test machine configuration."""
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


class TestSSHClient:
    """Tests for SSHClient."""

    def test_client_initialization(self, machine_config):
        """Test SSH client initializes correctly."""
        client = SSHClient(machine_config)
        assert client.machine == machine_config
        assert client._client is None
        assert not client.is_connected

    def test_is_connected_false_when_no_client(self, machine_config):
        """Test is_connected returns False when no client."""
        client = SSHClient(machine_config)
        assert not client.is_connected

    def test_is_connected_false_when_transport_inactive(self, machine_config):
        """Test is_connected returns False when transport inactive."""
        client = SSHClient(machine_config)
        mock_client = MagicMock()
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = False
        mock_client.get_transport.return_value = mock_transport
        client._client = mock_client

        assert not client.is_connected

    def test_is_connected_true_when_active(self, machine_config):
        """Test is_connected returns True when transport active."""
        client = SSHClient(machine_config)
        mock_client = MagicMock()
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_client.get_transport.return_value = mock_transport
        client._client = mock_client

        assert client.is_connected

    def test_connect_skips_if_already_connected(self, machine_config):
        """Test connect does nothing if already connected."""
        client = SSHClient(machine_config)

        # Mock as connected
        mock_client = MagicMock()
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_client.get_transport.return_value = mock_transport
        client._client = mock_client

        # Should not raise or do anything
        client.connect()

    @patch("sshmcp.ssh.client.paramiko.SSHClient")
    @patch("sshmcp.ssh.client.Path")
    def test_connect_with_key_auth(self, mock_path, mock_ssh_client, machine_config):
        """Test connect with key authentication."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value.expanduser.return_value = mock_path_instance

        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        client = SSHClient(machine_config)

        with patch.object(client, "_load_private_key") as mock_load_key:
            mock_load_key.return_value = MagicMock()
            client.connect(retry=False)

        mock_client_instance.connect.assert_called_once()

    @patch("sshmcp.ssh.client.paramiko.SSHClient")
    def test_connect_with_password_auth(self, mock_ssh_client):
        """Test connect with password authentication."""
        machine = MachineConfig(
            name="test-server",
            host="192.168.1.1",
            port=22,
            user="testuser",
            auth=AuthConfig(type="password", password="secret123"),
            security=SecurityConfig(
                allowed_commands=[".*"],
                forbidden_commands=[],
                timeout_seconds=30,
            ),
        )

        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        client = SSHClient(machine)
        client.connect(retry=False)

        mock_client_instance.connect.assert_called_once()
        call_kwargs = mock_client_instance.connect.call_args[1]
        assert call_kwargs["password"] == "secret123"

    def test_disconnect_closes_connections(self, machine_config):
        """Test disconnect closes SFTP and SSH."""
        client = SSHClient(machine_config)
        mock_client = MagicMock()
        mock_sftp = MagicMock()
        client._client = mock_client
        client._sftp = mock_sftp

        client.disconnect()

        mock_sftp.close.assert_called_once()
        mock_client.close.assert_called_once()
        assert client._client is None
        assert client._sftp is None


class TestSSHClientRetry:
    """Tests for SSH client retry logic."""

    def test_retry_configuration(self, machine_config):
        """Test retry configuration defaults."""
        client = SSHClient(machine_config)
        assert client.MAX_RETRIES == 3
        assert client.RETRY_DELAY == 1.0
        assert client.RETRY_BACKOFF == 2.0

    @patch("sshmcp.ssh.client.time.sleep")
    def test_connect_retries_on_failure(self, mock_sleep, machine_config):
        """Test connect retries on connection failure."""
        client = SSHClient(machine_config)

        with patch.object(client, "_connect_once") as mock_connect:
            # Fail twice, succeed on third
            mock_connect.side_effect = [
                SSHConnectionError("Connection refused"),
                SSHConnectionError("Connection refused"),
                None,
            ]

            client.connect(retry=True)

        assert mock_connect.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between retries

    @patch("sshmcp.ssh.client.time.sleep")
    def test_connect_fails_after_max_retries(self, mock_sleep, machine_config):
        """Test connect fails after max retries exhausted."""
        client = SSHClient(machine_config)

        with patch.object(client, "_connect_once") as mock_connect:
            mock_connect.side_effect = SSHConnectionError("Connection refused")

            with pytest.raises(SSHConnectionError) as exc_info:
                client.connect(retry=True)

            assert "Failed to connect after 3 attempts" in str(exc_info.value)

        assert mock_connect.call_count == 3

    def test_connect_no_retry_when_disabled(self, machine_config):
        """Test connect does not retry when retry=False."""
        client = SSHClient(machine_config)

        with patch.object(client, "_connect_once") as mock_connect:
            mock_connect.side_effect = SSHConnectionError("Connection refused")

            with pytest.raises(SSHConnectionError):
                client.connect(retry=False)

        assert mock_connect.call_count == 1
