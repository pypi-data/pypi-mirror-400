"""Interactive SSH shell sessions."""

import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import paramiko
import structlog

from sshmcp.ssh.client import SSHClient, SSHConnectionError

logger = structlog.get_logger()


class ShellError(Exception):
    """Error with shell session."""

    pass


class ShellNotConnected(ShellError):
    """Shell is not connected."""

    pass


class ShellTimeout(ShellError):
    """Shell operation timed out."""

    pass


@dataclass
class ShellOutput:
    """Output from shell session."""

    data: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_stderr: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "is_stderr": self.is_stderr,
        }


@dataclass
class ShellSession:
    """Information about a shell session."""

    session_id: str
    host: str
    started_at: datetime
    terminal: str
    width: int
    height: int
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "host": self.host,
            "started_at": self.started_at.isoformat(),
            "terminal": self.terminal,
            "width": self.width,
            "height": self.height,
            "is_active": self.is_active,
        }


class InteractiveShell:
    """Interactive SSH shell with PTY support."""

    def __init__(
        self,
        ssh_client: SSHClient,
        term: str = "xterm",
        width: int = 80,
        height: int = 24,
    ) -> None:
        """
        Initialize interactive shell.

        Args:
            ssh_client: Connected SSH client.
            term: Terminal type.
            width: Terminal width in characters.
            height: Terminal height in characters.
        """
        self.ssh_client = ssh_client
        self.term = term
        self.width = width
        self.height = height

        self._channel: paramiko.Channel | None = None
        self._output_queue: queue.Queue[ShellOutput] = queue.Queue()
        self._reader_thread: threading.Thread | None = None
        self._running = False
        self._session_id = f"{ssh_client.machine.name}_{int(time.time())}"
        self._started_at: datetime | None = None
        self._callbacks: list[Callable[[ShellOutput], None]] = []
        self._lock = threading.Lock()

    @property
    def is_active(self) -> bool:
        """Check if shell is active."""
        if self._channel is None:
            return False
        return not self._channel.closed and self._running

    @property
    def session_info(self) -> ShellSession | None:
        """Get session information."""
        if not self._started_at:
            return None
        return ShellSession(
            session_id=self._session_id,
            host=self.ssh_client.machine.name,
            started_at=self._started_at,
            terminal=self.term,
            width=self.width,
            height=self.height,
            is_active=self.is_active,
        )

    def start(self) -> ShellSession:
        """
        Start interactive shell session.

        Returns:
            ShellSession with session details.

        Raises:
            ShellError: If shell cannot be started.
        """
        if self.is_active:
            raise ShellError("Shell already active")

        if not self.ssh_client.is_connected:
            try:
                self.ssh_client.connect()
            except SSHConnectionError as e:
                raise ShellError(f"Cannot connect: {e}")

        try:
            transport = self.ssh_client._client.get_transport()
            if transport is None:
                raise ShellError("No transport available")

            self._channel = transport.open_session()
            self._channel.get_pty(
                term=self.term,
                width=self.width,
                height=self.height,
            )
            self._channel.invoke_shell()
            self._channel.settimeout(0.1)

            self._running = True
            self._started_at = datetime.now(timezone.utc)

            # Start reader thread
            self._reader_thread = threading.Thread(
                target=self._read_output,
                daemon=True,
                name=f"shell-reader-{self._session_id}",
            )
            self._reader_thread.start()

            logger.info(
                "shell_started",
                host=self.ssh_client.machine.name,
                session_id=self._session_id,
                terminal=self.term,
            )

            return self.session_info  # type: ignore

        except paramiko.SSHException as e:
            raise ShellError(f"Failed to start shell: {e}")
        except Exception as e:
            raise ShellError(f"Shell error: {e}")

    def stop(self) -> None:
        """Stop shell session."""
        self._running = False

        if self._channel:
            try:
                self._channel.close()
            except Exception:
                pass
            self._channel = None

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=2.0)

        logger.info(
            "shell_stopped",
            host=self.ssh_client.machine.name,
            session_id=self._session_id,
        )

    def send(self, data: str) -> None:
        """
        Send data to shell.

        Args:
            data: Data to send.

        Raises:
            ShellNotConnected: If shell is not active.
        """
        if not self.is_active or self._channel is None:
            raise ShellNotConnected("Shell not active")

        try:
            self._channel.send(data)
        except Exception as e:
            raise ShellError(f"Failed to send: {e}")

    def send_line(self, line: str) -> None:
        """
        Send line to shell (with newline).

        Args:
            line: Line to send.
        """
        self.send(line + "\n")

    def recv(self, timeout: float = 1.0) -> list[ShellOutput]:
        """
        Receive available output from shell.

        Args:
            timeout: Maximum time to wait for output.

        Returns:
            List of ShellOutput items.
        """
        outputs: list[ShellOutput] = []
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                output = self._output_queue.get(timeout=0.1)
                outputs.append(output)
            except queue.Empty:
                if outputs:
                    break
                continue

        return outputs

    def recv_until(
        self,
        pattern: str,
        timeout: float = 30.0,
        include_pattern: bool = True,
    ) -> str:
        """
        Receive output until pattern is found.

        Args:
            pattern: Pattern to wait for.
            timeout: Maximum time to wait.
            include_pattern: Include pattern in result.

        Returns:
            Collected output.

        Raises:
            ShellTimeout: If pattern not found in time.
        """
        collected = ""
        deadline = time.time() + timeout

        while time.time() < deadline:
            outputs = self.recv(timeout=0.5)
            for output in outputs:
                collected += output.data
                if pattern in collected:
                    if include_pattern:
                        idx = collected.find(pattern) + len(pattern)
                    else:
                        idx = collected.find(pattern)
                    return collected[:idx]

        raise ShellTimeout(f"Pattern '{pattern}' not found in {timeout}s")

    def execute_and_wait(
        self,
        command: str,
        prompt: str = "$ ",
        timeout: float = 30.0,
    ) -> str:
        """
        Execute command and wait for prompt.

        Args:
            command: Command to execute.
            prompt: Shell prompt to wait for.
            timeout: Maximum time to wait.

        Returns:
            Command output.
        """
        self.send_line(command)
        output = self.recv_until(prompt, timeout=timeout)
        # Remove command echo and prompt
        lines = output.split("\n")
        if lines and command in lines[0]:
            lines = lines[1:]
        if lines and prompt in lines[-1]:
            lines[-1] = lines[-1].replace(prompt, "")
        return "\n".join(lines).strip()

    def resize(self, width: int, height: int) -> None:
        """
        Resize terminal.

        Args:
            width: New width in characters.
            height: New height in characters.
        """
        if not self.is_active or self._channel is None:
            raise ShellNotConnected("Shell not active")

        self.width = width
        self.height = height

        try:
            self._channel.resize_pty(width=width, height=height)
            logger.info(
                "shell_resized",
                session_id=self._session_id,
                width=width,
                height=height,
            )
        except Exception as e:
            raise ShellError(f"Failed to resize: {e}")

    def register_callback(self, callback: Callable[[ShellOutput], None]) -> None:
        """
        Register callback for output.

        Args:
            callback: Function called with each output.
        """
        with self._lock:
            self._callbacks.append(callback)

    def _read_output(self) -> None:
        """Background thread to read shell output."""
        while self._running and self._channel:
            try:
                if self._channel.recv_ready():
                    data = self._channel.recv(4096).decode("utf-8", errors="replace")
                    if data:
                        output = ShellOutput(data=data, is_stderr=False)
                        self._output_queue.put(output)
                        self._notify_callbacks(output)

                if self._channel.recv_stderr_ready():
                    data = self._channel.recv_stderr(4096).decode(
                        "utf-8", errors="replace"
                    )
                    if data:
                        output = ShellOutput(data=data, is_stderr=True)
                        self._output_queue.put(output)
                        self._notify_callbacks(output)

                if self._channel.exit_status_ready():
                    break

                time.sleep(0.01)

            except Exception as e:
                if self._running:
                    logger.warning(
                        "shell_read_error",
                        session_id=self._session_id,
                        error=str(e),
                    )
                break

        self._running = False

    def _notify_callbacks(self, output: ShellOutput) -> None:
        """Notify registered callbacks."""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(output)
                except Exception as e:
                    logger.warning(
                        "shell_callback_error",
                        session_id=self._session_id,
                        error=str(e),
                    )

    def __enter__(self) -> "InteractiveShell":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()


class ShellManager:
    """Manage multiple shell sessions."""

    def __init__(self) -> None:
        """Initialize shell manager."""
        self._sessions: dict[str, InteractiveShell] = {}
        self._lock = threading.Lock()

    def create_session(
        self,
        ssh_client: SSHClient,
        term: str = "xterm",
        width: int = 80,
        height: int = 24,
    ) -> ShellSession:
        """
        Create new shell session.

        Args:
            ssh_client: Connected SSH client.
            term: Terminal type.
            width: Terminal width.
            height: Terminal height.

        Returns:
            ShellSession with session details.
        """
        shell = InteractiveShell(
            ssh_client=ssh_client,
            term=term,
            width=width,
            height=height,
        )
        session = shell.start()

        with self._lock:
            self._sessions[session.session_id] = shell

        return session

    def get_session(self, session_id: str) -> InteractiveShell | None:
        """Get shell by session ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def list_sessions(self) -> list[ShellSession]:
        """List all active sessions."""
        sessions = []
        with self._lock:
            for shell in self._sessions.values():
                info = shell.session_info
                if info:
                    sessions.append(info)
        return sessions

    def close_session(self, session_id: str) -> bool:
        """
        Close shell session.

        Args:
            session_id: Session ID to close.

        Returns:
            True if session was closed.
        """
        with self._lock:
            shell = self._sessions.pop(session_id, None)

        if shell:
            shell.stop()
            return True
        return False

    def close_all(self) -> int:
        """
        Close all sessions.

        Returns:
            Number of sessions closed.
        """
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()

        for shell in sessions:
            shell.stop()

        return len(sessions)


# Global shell manager
_shell_manager: ShellManager | None = None


def get_shell_manager() -> ShellManager:
    """Get global shell manager."""
    global _shell_manager
    if _shell_manager is None:
        _shell_manager = ShellManager()
    return _shell_manager
