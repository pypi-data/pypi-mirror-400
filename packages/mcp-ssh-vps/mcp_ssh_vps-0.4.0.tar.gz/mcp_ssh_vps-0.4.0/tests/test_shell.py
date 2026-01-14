"""Tests for interactive shell sessions."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
from sshmcp.ssh.shell import (
    InteractiveShell,
    ShellError,
    ShellManager,
    ShellNotConnected,
    ShellOutput,
    ShellSession,
    ShellTimeout,
    get_shell_manager,
)


@pytest.fixture
def mock_machine():
    """Create mock machine config."""
    return MachineConfig(
        name="test-server",
        host="192.168.1.1",
        port=22,
        user="testuser",
        auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
        security=SecurityConfig(),
    )


@pytest.fixture
def mock_ssh_client(mock_machine):
    """Create mock SSH client."""
    client = MagicMock()
    client.machine = mock_machine
    client.is_connected = True
    return client


@pytest.fixture
def mock_channel():
    """Create mock paramiko channel."""
    channel = MagicMock()
    channel.closed = False
    channel.recv_ready.return_value = False
    channel.recv_stderr_ready.return_value = False
    channel.exit_status_ready.return_value = False
    return channel


class TestShellOutput:
    """Tests for ShellOutput."""

    def test_create_output(self):
        """Test creating shell output."""
        output = ShellOutput(data="hello")
        assert output.data == "hello"
        assert output.is_stderr is False

    def test_output_to_dict(self):
        """Test output to_dict."""
        output = ShellOutput(data="test", is_stderr=True)
        data = output.to_dict()
        assert data["data"] == "test"
        assert data["is_stderr"] is True
        assert "timestamp" in data


class TestShellSession:
    """Tests for ShellSession."""

    def test_create_session(self):
        """Test creating session info."""
        session = ShellSession(
            session_id="test_123",
            host="server",
            started_at=datetime.now(timezone.utc),
            terminal="xterm",
            width=80,
            height=24,
        )
        assert session.session_id == "test_123"
        assert session.is_active is True

    def test_session_to_dict(self):
        """Test session to_dict."""
        session = ShellSession(
            session_id="test_123",
            host="server",
            started_at=datetime.now(timezone.utc),
            terminal="xterm",
            width=80,
            height=24,
        )
        data = session.to_dict()
        assert data["session_id"] == "test_123"
        assert data["terminal"] == "xterm"


class TestInteractiveShell:
    """Tests for InteractiveShell."""

    def test_init(self, mock_ssh_client):
        """Test shell initialization."""
        shell = InteractiveShell(mock_ssh_client)
        assert shell.term == "xterm"
        assert shell.width == 80
        assert shell.height == 24
        assert shell.is_active is False

    def test_init_custom_params(self, mock_ssh_client):
        """Test shell with custom parameters."""
        shell = InteractiveShell(
            mock_ssh_client,
            term="vt100",
            width=120,
            height=40,
        )
        assert shell.term == "vt100"
        assert shell.width == 120
        assert shell.height == 40

    def test_start_already_active(self, mock_ssh_client, mock_channel):
        """Test starting already active shell."""
        shell = InteractiveShell(mock_ssh_client)
        shell._channel = mock_channel
        shell._running = True

        with pytest.raises(ShellError, match="already active"):
            shell.start()

    def test_start_not_connected(self, mock_ssh_client):
        """Test start when not connected."""
        from sshmcp.ssh.client import SSHConnectionError

        mock_ssh_client.is_connected = False
        mock_ssh_client.connect.side_effect = SSHConnectionError("Connection failed")

        shell = InteractiveShell(mock_ssh_client)

        with pytest.raises(ShellError, match="Cannot connect"):
            shell.start()

    def test_start_success(self, mock_ssh_client, mock_channel):
        """Test successful shell start."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        shell = InteractiveShell(mock_ssh_client)
        session = shell.start()

        assert session is not None
        assert session.host == "test-server"
        assert shell.is_active is True
        mock_channel.get_pty.assert_called_once()
        mock_channel.invoke_shell.assert_called_once()

        shell.stop()

    def test_stop(self, mock_ssh_client, mock_channel):
        """Test stopping shell."""
        shell = InteractiveShell(mock_ssh_client)
        shell._channel = mock_channel
        shell._running = True

        shell.stop()

        assert shell._running is False
        mock_channel.close.assert_called_once()

    def test_send_not_active(self, mock_ssh_client):
        """Test send when not active."""
        shell = InteractiveShell(mock_ssh_client)

        with pytest.raises(ShellNotConnected):
            shell.send("test")

    def test_send_success(self, mock_ssh_client, mock_channel):
        """Test successful send."""
        shell = InteractiveShell(mock_ssh_client)
        shell._channel = mock_channel
        shell._running = True

        shell.send("test data")

        mock_channel.send.assert_called_with("test data")

    def test_send_line(self, mock_ssh_client, mock_channel):
        """Test send_line adds newline."""
        shell = InteractiveShell(mock_ssh_client)
        shell._channel = mock_channel
        shell._running = True

        shell.send_line("ls -la")

        mock_channel.send.assert_called_with("ls -la\n")

    def test_recv_empty(self, mock_ssh_client):
        """Test recv with no output."""
        shell = InteractiveShell(mock_ssh_client)
        shell._running = True

        outputs = shell.recv(timeout=0.1)

        assert outputs == []

    def test_recv_with_data(self, mock_ssh_client):
        """Test recv with queued data."""
        shell = InteractiveShell(mock_ssh_client)
        shell._running = True

        # Add data to queue
        shell._output_queue.put(ShellOutput(data="hello"))
        shell._output_queue.put(ShellOutput(data="world"))

        outputs = shell.recv(timeout=0.5)

        assert len(outputs) == 2
        assert outputs[0].data == "hello"
        assert outputs[1].data == "world"

    def test_recv_until_found(self, mock_ssh_client):
        """Test recv_until finds pattern."""
        shell = InteractiveShell(mock_ssh_client)
        shell._running = True

        # Add data with pattern
        shell._output_queue.put(ShellOutput(data="output line\n"))
        shell._output_queue.put(ShellOutput(data="$ "))

        result = shell.recv_until("$ ", timeout=1.0)

        assert "output line" in result
        assert result.endswith("$ ")

    def test_recv_until_timeout(self, mock_ssh_client):
        """Test recv_until timeout."""
        shell = InteractiveShell(mock_ssh_client)
        shell._running = True

        with pytest.raises(ShellTimeout):
            shell.recv_until("nonexistent", timeout=0.1)

    def test_resize(self, mock_ssh_client, mock_channel):
        """Test terminal resize."""
        shell = InteractiveShell(mock_ssh_client)
        shell._channel = mock_channel
        shell._running = True

        shell.resize(120, 40)

        assert shell.width == 120
        assert shell.height == 40
        mock_channel.resize_pty.assert_called_with(width=120, height=40)

    def test_resize_not_active(self, mock_ssh_client):
        """Test resize when not active."""
        shell = InteractiveShell(mock_ssh_client)

        with pytest.raises(ShellNotConnected):
            shell.resize(120, 40)

    def test_register_callback(self, mock_ssh_client):
        """Test callback registration."""
        shell = InteractiveShell(mock_ssh_client)
        callback = MagicMock()

        shell.register_callback(callback)

        assert callback in shell._callbacks

    def test_context_manager(self, mock_ssh_client, mock_channel):
        """Test context manager."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        with InteractiveShell(mock_ssh_client) as shell:
            assert shell.is_active is True

        assert shell._running is False

    def test_session_info(self, mock_ssh_client, mock_channel):
        """Test getting session info."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        shell = InteractiveShell(mock_ssh_client)

        # Before start
        assert shell.session_info is None

        shell.start()

        # After start
        info = shell.session_info
        assert info is not None
        assert info.host == "test-server"
        assert info.terminal == "xterm"

        shell.stop()


class TestShellManager:
    """Tests for ShellManager."""

    def test_init(self):
        """Test manager initialization."""
        manager = ShellManager()
        assert manager._sessions == {}

    def test_create_session(self, mock_ssh_client, mock_channel):
        """Test creating session."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        manager = ShellManager()
        session = manager.create_session(mock_ssh_client)

        assert session is not None
        assert session.host == "test-server"
        assert len(manager._sessions) == 1

        # Cleanup
        manager.close_all()

    def test_get_session(self, mock_ssh_client, mock_channel):
        """Test getting session by ID."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        manager = ShellManager()
        session = manager.create_session(mock_ssh_client)

        shell = manager.get_session(session.session_id)
        assert shell is not None

        # Non-existent
        assert manager.get_session("nonexistent") is None

        manager.close_all()

    def test_list_sessions(self, mock_ssh_client, mock_channel):
        """Test listing sessions."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        manager = ShellManager()
        manager.create_session(mock_ssh_client)

        sessions = manager.list_sessions()
        assert len(sessions) == 1

        manager.close_all()

    def test_close_session(self, mock_ssh_client, mock_channel):
        """Test closing specific session."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        manager = ShellManager()
        session = manager.create_session(mock_ssh_client)

        result = manager.close_session(session.session_id)
        assert result is True
        assert len(manager._sessions) == 0

        # Already closed
        result = manager.close_session(session.session_id)
        assert result is False

    def test_close_all(self, mock_ssh_client, mock_channel):
        """Test closing all sessions."""
        mock_transport = MagicMock()
        mock_transport.open_session.return_value = mock_channel
        mock_ssh_client._client.get_transport.return_value = mock_transport

        manager = ShellManager()
        manager.create_session(mock_ssh_client)

        count = manager.close_all()
        assert count == 1
        assert len(manager._sessions) == 0


class TestGlobalShellManager:
    """Tests for global shell manager."""

    def test_get_shell_manager(self):
        """Test getting global manager."""
        manager = get_shell_manager()
        assert isinstance(manager, ShellManager)

        # Same instance
        manager2 = get_shell_manager()
        assert manager is manager2
