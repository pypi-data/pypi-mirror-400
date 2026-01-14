"""SSH connection pool for managing multiple connections."""

import atexit
import threading
import time
from typing import TYPE_CHECKING, Callable

import structlog

from sshmcp.models.machine import MachineConfig

if TYPE_CHECKING:
    from sshmcp.models.machine import MachinesConfig
from sshmcp.ssh.client import SSHClient, SSHConnectionError

logger = structlog.get_logger()


class SSHConnectionPool:
    """
    Pool for managing SSH connections to multiple servers.

    Provides connection reuse, automatic cleanup of idle connections,
    health checks, and background maintenance.
    """

    def __init__(
        self,
        max_connections_per_host: int = 3,
        idle_timeout: int = 300,  # 5 minutes
        cleanup_interval: int = 60,  # 1 minute
        health_check_interval: int = 30,  # 30 seconds
        enable_background_cleanup: bool = True,
    ) -> None:
        """
        Initialize connection pool.

        Args:
            max_connections_per_host: Maximum connections per host.
            idle_timeout: Time in seconds before idle connections are closed.
            cleanup_interval: Interval for background cleanup thread.
            health_check_interval: Interval for health checks on connections.
            enable_background_cleanup: Whether to enable background cleanup thread.
        """
        self.max_connections_per_host = max_connections_per_host
        self.idle_timeout = idle_timeout
        self.cleanup_interval = cleanup_interval
        self.health_check_interval = health_check_interval

        self._connections: dict[str, list[tuple[SSHClient, float]]] = {}
        self._lock = threading.Lock()
        self._machines: dict[str, MachineConfig] = {}
        self._shutdown = threading.Event()
        self._cleanup_thread: threading.Thread | None = None
        self._health_callbacks: list[Callable[[str, bool], None]] = []

        if enable_background_cleanup:
            self._start_background_cleanup()
            atexit.register(self.shutdown)

    def register_machine(self, machine: MachineConfig) -> None:
        """
        Register a machine configuration.

        Args:
            machine: Machine configuration to register.
        """
        with self._lock:
            self._machines[machine.name] = machine
            if machine.name not in self._connections:
                self._connections[machine.name] = []

        logger.info("pool_machine_registered", machine=machine.name)

    def get_client(self, name: str) -> SSHClient:
        """
        Get an SSH client for the specified machine.

        Returns an existing connection if available, or creates a new one.

        Args:
            name: Machine name.

        Returns:
            SSHClient connected to the machine.

        Raises:
            SSHConnectionError: If machine not found or connection fails.
        """
        with self._lock:
            if name not in self._machines:
                raise SSHConnectionError(f"Machine not registered: {name}")

            machine = self._machines[name]

            # Try to get an existing connection
            if name in self._connections:
                connections = self._connections[name]
                while connections:
                    client, last_used = connections.pop(0)
                    if client.is_connected:
                        logger.debug("pool_reusing_connection", machine=name)
                        return client
                    else:
                        # Connection was closed, discard it
                        try:
                            client.disconnect()
                        except Exception:
                            pass

            # Create new connection
            logger.info("pool_creating_connection", machine=name)
            client = SSHClient(machine)
            client.connect()
            return client

    def release_client(self, client: SSHClient) -> None:
        """
        Return a client to the pool for reuse.

        Args:
            client: SSHClient to release.
        """
        name = client.machine.name

        with self._lock:
            if name not in self._connections:
                self._connections[name] = []

            connections = self._connections[name]

            # Check if we have room for more connections
            if len(connections) < self.max_connections_per_host:
                if client.is_connected:
                    connections.append((client, time.time()))
                    logger.debug("pool_connection_released", machine=name)
                    return

            # Pool is full or connection is dead, close it
            try:
                client.disconnect()
            except Exception:
                pass

    def cleanup_idle(self) -> int:
        """
        Close connections that have been idle too long.

        Returns:
            Number of connections closed.
        """
        closed = 0
        current_time = time.time()

        with self._lock:
            for name, connections in self._connections.items():
                active = []
                for client, last_used in connections:
                    if current_time - last_used > self.idle_timeout:
                        try:
                            client.disconnect()
                            closed += 1
                        except Exception:
                            pass
                    else:
                        active.append((client, last_used))
                self._connections[name] = active

        if closed > 0:
            logger.info("pool_cleanup", closed_connections=closed)

        return closed

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for name, connections in self._connections.items():
                for client, _ in connections:
                    try:
                        client.disconnect()
                    except Exception:
                        pass
                connections.clear()

        logger.info("pool_closed_all")

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            Dictionary with pool statistics.
        """
        with self._lock:
            stats = {
                "machines": len(self._machines),
                "connections": {},
                "background_cleanup_active": self._cleanup_thread is not None
                and self._cleanup_thread.is_alive(),
            }
            for name, connections in self._connections.items():
                active = sum(1 for c, _ in connections if c.is_connected)
                stats["connections"][name] = {
                    "total": len(connections),
                    "active": active,
                }
            return stats

    def _start_background_cleanup(self) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread is not None and self._cleanup_thread.is_alive():
            return

        self._shutdown.clear()
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup_loop,
            daemon=True,
            name="ssh-pool-cleanup",
        )
        self._cleanup_thread.start()
        logger.info("pool_background_cleanup_started")

    def _background_cleanup_loop(self) -> None:
        """Background loop for cleanup and health checks."""
        while not self._shutdown.is_set():
            try:
                self.cleanup_idle()
                self._run_health_checks()
            except Exception as e:
                logger.error("pool_background_error", error=str(e))

            # Wait for next iteration or shutdown
            self._shutdown.wait(timeout=self.cleanup_interval)

    def _run_health_checks(self) -> None:
        """Run health checks on all pooled connections."""
        with self._lock:
            for name, connections in self._connections.items():
                for client, _ in connections:
                    is_healthy = client.is_connected
                    for callback in self._health_callbacks:
                        try:
                            callback(name, is_healthy)
                        except Exception:
                            pass

    def register_health_callback(self, callback: Callable[[str, bool], None]) -> None:
        """
        Register a callback for health check results.

        Args:
            callback: Function called with (host_name, is_healthy).
        """
        self._health_callbacks.append(callback)

    def health_check(self, name: str) -> dict:
        """
        Perform health check on a specific host.

        Args:
            name: Machine name to check.

        Returns:
            Dictionary with health status.
        """
        with self._lock:
            if name not in self._machines:
                return {
                    "host": name,
                    "healthy": False,
                    "error": "Machine not registered",
                }

            machine = self._machines[name]

        # Try to connect and execute simple command
        try:
            client = SSHClient(machine)
            client.connect(retry=False)
            result = client.execute("echo ok", timeout=5)
            client.disconnect()

            return {
                "host": name,
                "healthy": result.exit_code == 0,
                "latency_ms": result.duration_ms,
            }
        except Exception as e:
            return {
                "host": name,
                "healthy": False,
                "error": str(e),
            }

    def shutdown(self) -> None:
        """Shutdown the pool and cleanup resources."""
        logger.info("pool_shutting_down")
        self._shutdown.set()

        if self._cleanup_thread is not None:
            self._cleanup_thread.join(timeout=5)

        self.close_all()
        logger.info("pool_shutdown_complete")


# Global connection pool instance
_pool: SSHConnectionPool | None = None
_pool_lock = threading.Lock()


def get_pool() -> SSHConnectionPool:
    """Get or create the global connection pool."""
    global _pool
    with _pool_lock:
        if _pool is None:
            _pool = SSHConnectionPool()
        return _pool


def init_pool(config: "MachinesConfig") -> SSHConnectionPool:  # type: ignore
    """
    Initialize the global connection pool with machines from config.

    Args:
        config: MachinesConfig with machine definitions.

    Returns:
        Initialized SSHConnectionPool.
    """
    pool = get_pool()
    for machine in config.machines:
        pool.register_machine(machine)
    return pool


def reset_pool() -> None:
    """Reset the global pool (useful for testing)."""
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.shutdown()
            _pool = None
