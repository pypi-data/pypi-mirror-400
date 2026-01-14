"""SSH port forwarding and tunneling support."""

import select
import socket
import threading

import paramiko
import structlog

from sshmcp.models.machine import MachineConfig
from sshmcp.ssh.client import SSHClient

logger = structlog.get_logger()


class PortForwardingError(Exception):
    """Error in port forwarding."""

    pass


class LocalForwarder:
    """
    Local port forwarding (SSH tunnel).

    Forwards connections from a local port to a remote host:port via SSH.
    Use case: Access remote database through SSH tunnel.
    """

    def __init__(
        self,
        ssh_client: SSHClient,
        local_port: int,
        remote_host: str,
        remote_port: int,
        local_bind: str = "127.0.0.1",
    ) -> None:
        """
        Initialize local port forwarder.

        Args:
            ssh_client: Connected SSH client.
            local_port: Local port to listen on.
            remote_host: Remote host to forward to.
            remote_port: Remote port to forward to.
            local_bind: Local address to bind (default: localhost).
        """
        self.ssh_client = ssh_client
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_bind = local_bind

        self._server_socket: socket.socket | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._active_channels: list[paramiko.Channel] = []

    def start(self) -> None:
        """Start the local port forwarding."""
        if self._running:
            return

        if not self.ssh_client.is_connected:
            raise PortForwardingError("SSH client not connected")

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._server_socket.bind((self.local_bind, self.local_port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
        except OSError as e:
            raise PortForwardingError(
                f"Failed to bind to {self.local_bind}:{self.local_port}: {e}"
            )

        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

        logger.info(
            "local_forward_started",
            local=f"{self.local_bind}:{self.local_port}",
            remote=f"{self.remote_host}:{self.remote_port}",
        )

    def stop(self) -> None:
        """Stop the local port forwarding."""
        self._running = False

        # Close all active channels
        for channel in self._active_channels:
            try:
                channel.close()
            except Exception:
                pass
        self._active_channels.clear()

        # Close server socket
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        # Wait for thread
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        logger.info("local_forward_stopped")

    def _accept_loop(self) -> None:
        """Accept incoming connections and forward them."""
        while self._running and self._server_socket:
            try:
                client_socket, client_addr = self._server_socket.accept()
                logger.debug("local_forward_connection", client=client_addr)

                # Start forwarding thread for this connection
                thread = threading.Thread(
                    target=self._forward_connection,
                    args=(client_socket, client_addr),
                    daemon=True,
                )
                thread.start()

            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.error("local_forward_accept_error", error=str(e))

    def _forward_connection(
        self, client_socket: socket.socket, client_addr: tuple
    ) -> None:
        """Forward a single connection."""
        channel = None
        try:
            transport = self.ssh_client._client.get_transport()  # type: ignore
            if not transport:
                raise PortForwardingError("No SSH transport")

            channel = transport.open_channel(
                "direct-tcpip",
                (self.remote_host, self.remote_port),
                client_addr,
            )
            self._active_channels.append(channel)

            # Forward data bidirectionally
            while self._running:
                r, w, x = select.select([client_socket, channel], [], [], 1.0)

                if client_socket in r:
                    data = client_socket.recv(4096)
                    if len(data) == 0:
                        break
                    channel.send(data)

                if channel in r:
                    data = channel.recv(4096)
                    if len(data) == 0:
                        break
                    client_socket.send(data)

        except Exception as e:
            logger.debug("local_forward_error", error=str(e))
        finally:
            if channel:
                try:
                    self._active_channels.remove(channel)
                    channel.close()
                except Exception:
                    pass
            try:
                client_socket.close()
            except Exception:
                pass

    def __enter__(self) -> "LocalForwarder":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


class RemoteForwarder:
    """
    Remote port forwarding (reverse tunnel).

    Forwards connections from a remote port on SSH server to local host:port.
    Use case: Expose local service to remote server.
    """

    def __init__(
        self,
        ssh_client: SSHClient,
        remote_port: int,
        local_host: str = "127.0.0.1",
        local_port: int = 0,
        remote_bind: str = "127.0.0.1",
    ) -> None:
        """
        Initialize remote port forwarder.

        Args:
            ssh_client: Connected SSH client.
            remote_port: Remote port to listen on.
            local_host: Local host to forward to.
            local_port: Local port to forward to (0 = same as remote).
            remote_bind: Remote address to bind.
        """
        self.ssh_client = ssh_client
        self.remote_port = remote_port
        self.local_host = local_host
        self.local_port = local_port or remote_port
        self.remote_bind = remote_bind

        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the remote port forwarding."""
        if self._running:
            return

        if not self.ssh_client.is_connected:
            raise PortForwardingError("SSH client not connected")

        transport = self.ssh_client._client.get_transport()  # type: ignore
        if not transport:
            raise PortForwardingError("No SSH transport")

        try:
            transport.request_port_forward(self.remote_bind, self.remote_port)
        except paramiko.SSHException as e:
            raise PortForwardingError(f"Failed to request remote port forward: {e}")

        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

        logger.info(
            "remote_forward_started",
            remote=f"{self.remote_bind}:{self.remote_port}",
            local=f"{self.local_host}:{self.local_port}",
        )

    def stop(self) -> None:
        """Stop the remote port forwarding."""
        self._running = False

        if self.ssh_client.is_connected:
            try:
                transport = self.ssh_client._client.get_transport()  # type: ignore
                if transport:
                    transport.cancel_port_forward(self.remote_bind, self.remote_port)
            except Exception:
                pass

        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

        logger.info("remote_forward_stopped")

    def _accept_loop(self) -> None:
        """Accept incoming reverse tunnel connections."""
        transport = self.ssh_client._client.get_transport()  # type: ignore

        while self._running and transport and transport.is_active():
            try:
                channel = transport.accept(timeout=1.0)
                if channel is None:
                    continue

                # Start forwarding thread
                thread = threading.Thread(
                    target=self._forward_connection,
                    args=(channel,),
                    daemon=True,
                )
                thread.start()

            except Exception as e:
                if self._running:
                    logger.debug("remote_forward_accept_error", error=str(e))

    def _forward_connection(self, channel: paramiko.Channel) -> None:
        """Forward a single reverse tunnel connection."""
        local_socket = None
        try:
            local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_socket.connect((self.local_host, self.local_port))

            while self._running:
                r, w, x = select.select([local_socket, channel], [], [], 1.0)

                if local_socket in r:
                    data = local_socket.recv(4096)
                    if len(data) == 0:
                        break
                    channel.send(data)

                if channel in r:
                    data = channel.recv(4096)
                    if len(data) == 0:
                        break
                    local_socket.send(data)

        except Exception as e:
            logger.debug("remote_forward_error", error=str(e))
        finally:
            if local_socket:
                try:
                    local_socket.close()
                except Exception:
                    pass
            try:
                channel.close()
            except Exception:
                pass

    def __enter__(self) -> "RemoteForwarder":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


def create_tunnel(
    machine: MachineConfig,
    local_port: int,
    remote_host: str,
    remote_port: int,
) -> LocalForwarder:
    """
    Create a local SSH tunnel.

    Convenience function to create a tunnel to access remote services.

    Args:
        machine: Machine configuration for SSH server.
        local_port: Local port to listen on.
        remote_host: Remote host to connect to through tunnel.
        remote_port: Remote port to connect to.

    Returns:
        LocalForwarder instance (not started).

    Example:
        >>> with create_tunnel(machine, 5433, "db.internal", 5432) as tunnel:
        ...     # Connect to localhost:5433 to reach db.internal:5432
        ...     pass
    """
    client = SSHClient(machine)
    client.connect()
    return LocalForwarder(client, local_port, remote_host, remote_port)
