"""Tests for port forwarding."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
from sshmcp.ssh.forwarding import (
    LocalForwarder,
    PortForwardingError,
    RemoteForwarder,
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
def mock_ssh_client():
    """Create a mock SSH client."""
    client = MagicMock()
    client.is_connected = True
    client._client = MagicMock()
    client._client.get_transport.return_value = MagicMock()
    return client


class TestLocalForwarder:
    """Tests for LocalForwarder."""

    def test_init(self, mock_ssh_client):
        """Test forwarder initialization."""
        forwarder = LocalForwarder(
            ssh_client=mock_ssh_client,
            local_port=8080,
            remote_host="db.internal",
            remote_port=5432,
        )

        assert forwarder.local_port == 8080
        assert forwarder.remote_host == "db.internal"
        assert forwarder.remote_port == 5432
        assert forwarder.local_bind == "127.0.0.1"

    def test_start_not_connected_raises(self, mock_ssh_client):
        """Test that starting without connection raises error."""
        mock_ssh_client.is_connected = False

        forwarder = LocalForwarder(
            ssh_client=mock_ssh_client,
            local_port=8080,
            remote_host="db.internal",
            remote_port=5432,
        )

        with pytest.raises(PortForwardingError, match="not connected"):
            forwarder.start()

    def test_stop(self, mock_ssh_client):
        """Test stopping forwarder."""
        forwarder = LocalForwarder(
            ssh_client=mock_ssh_client,
            local_port=8080,
            remote_host="db.internal",
            remote_port=5432,
        )

        # Should not raise even if not started
        forwarder.stop()

    def test_context_manager(self, mock_ssh_client):
        """Test context manager usage."""
        with patch.object(LocalForwarder, "start"):
            with patch.object(LocalForwarder, "stop") as mock_stop:
                forwarder = LocalForwarder(
                    ssh_client=mock_ssh_client,
                    local_port=8080,
                    remote_host="db.internal",
                    remote_port=5432,
                )

                with forwarder:
                    pass

                mock_stop.assert_called_once()


class TestRemoteForwarder:
    """Tests for RemoteForwarder."""

    def test_init(self, mock_ssh_client):
        """Test forwarder initialization."""
        forwarder = RemoteForwarder(
            ssh_client=mock_ssh_client,
            remote_port=8000,
            local_host="127.0.0.1",
            local_port=3000,
        )

        assert forwarder.remote_port == 8000
        assert forwarder.local_host == "127.0.0.1"
        assert forwarder.local_port == 3000

    def test_init_default_local_port(self, mock_ssh_client):
        """Test default local port (same as remote)."""
        forwarder = RemoteForwarder(
            ssh_client=mock_ssh_client,
            remote_port=8000,
        )

        assert forwarder.local_port == 8000

    def test_start_not_connected_raises(self, mock_ssh_client):
        """Test that starting without connection raises error."""
        mock_ssh_client.is_connected = False

        forwarder = RemoteForwarder(
            ssh_client=mock_ssh_client,
            remote_port=8000,
        )

        with pytest.raises(PortForwardingError, match="not connected"):
            forwarder.start()

    def test_stop(self, mock_ssh_client):
        """Test stopping forwarder."""
        forwarder = RemoteForwarder(
            ssh_client=mock_ssh_client,
            remote_port=8000,
        )

        # Should not raise even if not started
        forwarder.stop()

    def test_context_manager(self, mock_ssh_client):
        """Test context manager usage."""
        with patch.object(RemoteForwarder, "start"):
            with patch.object(RemoteForwarder, "stop") as mock_stop:
                forwarder = RemoteForwarder(
                    ssh_client=mock_ssh_client,
                    remote_port=8000,
                )

                with forwarder:
                    pass

                mock_stop.assert_called_once()


class TestCreateTunnel:
    """Tests for create_tunnel function."""

    def test_create_tunnel(self, mock_machine):
        """Test creating a tunnel."""
        from sshmcp.ssh.forwarding import create_tunnel

        with patch("sshmcp.ssh.forwarding.SSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_connected = True
            mock_client._client = MagicMock()
            mock_client_class.return_value = mock_client

            forwarder = create_tunnel(
                mock_machine,
                local_port=5433,
                remote_host="db.internal",
                remote_port=5432,
            )

            assert isinstance(forwarder, LocalForwarder)
            assert forwarder.local_port == 5433
            assert forwarder.remote_port == 5432
            mock_client.connect.assert_called_once()
