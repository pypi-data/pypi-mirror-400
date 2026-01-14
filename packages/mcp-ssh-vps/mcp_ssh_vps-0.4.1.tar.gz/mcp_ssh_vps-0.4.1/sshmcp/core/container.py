"""Dependency injection container for sshmcp."""

import threading
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

import structlog

from sshmcp.models.machine import MachinesConfig
from sshmcp.security.audit import AuditLogger
from sshmcp.security.rate_limiter import RateLimiter
from sshmcp.ssh.pool import SSHConnectionPool
from sshmcp.ssh.shell import ShellManager

logger = structlog.get_logger()

T = TypeVar("T")


class Provider(Generic[T]):
    """Lazy provider for dependency instances."""

    def __init__(self, factory: Callable[[], T]) -> None:
        """
        Initialize provider.

        Args:
            factory: Factory function to create instance.
        """
        self._factory = factory
        self._instance: T | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """Get or create the instance."""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance

    def reset(self) -> None:
        """Reset the instance."""
        with self._lock:
            self._instance = None

    @property
    def is_initialized(self) -> bool:
        """Check if instance is initialized."""
        return self._instance is not None


@dataclass
class ContainerConfig:
    """Configuration for the container."""

    # Pool settings
    max_connections_per_host: int = 3
    idle_timeout: int = 300
    cleanup_interval: int = 60
    health_check_interval: int = 30
    enable_background_cleanup: bool = True

    # Rate limiter settings
    requests_per_minute: int = 60
    requests_per_hour: int = 1000

    # Audit settings
    audit_log_path: str | None = None
    audit_retention_days: int = 30


class Container:
    """
    Dependency injection container.

    Manages lifecycle of shared services like connection pool,
    shell manager, audit logger, rate limiter, etc.
    """

    def __init__(self, config: ContainerConfig | None = None) -> None:
        """
        Initialize container.

        Args:
            config: Optional configuration.
        """
        self.config = config or ContainerConfig()
        self._providers: dict[str, Provider[Any]] = {}
        self._machines_config: MachinesConfig | None = None
        self._lock = threading.Lock()

        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register default providers."""
        self._providers["pool"] = Provider(self._create_pool)
        self._providers["shell_manager"] = Provider(self._create_shell_manager)
        self._providers["audit_logger"] = Provider(self._create_audit_logger)
        self._providers["rate_limiter"] = Provider(self._create_rate_limiter)

    def _create_pool(self) -> SSHConnectionPool:
        """Create connection pool."""
        pool = SSHConnectionPool(
            max_connections_per_host=self.config.max_connections_per_host,
            idle_timeout=self.config.idle_timeout,
            cleanup_interval=self.config.cleanup_interval,
            health_check_interval=self.config.health_check_interval,
            enable_background_cleanup=self.config.enable_background_cleanup,
        )

        # Register machines if config available
        if self._machines_config:
            for machine in self._machines_config.machines:
                pool.register_machine(machine)

        logger.info("container_pool_created")
        return pool

    def _create_shell_manager(self) -> ShellManager:
        """Create shell manager."""
        logger.info("container_shell_manager_created")
        return ShellManager()

    def _create_audit_logger(self) -> AuditLogger:
        """Create audit logger."""
        logger.info("container_audit_logger_created")
        return AuditLogger(log_file=self.config.audit_log_path)

    def _create_rate_limiter(self) -> RateLimiter:
        """Create rate limiter."""
        from sshmcp.security.rate_limiter import RateLimitConfig

        logger.info("container_rate_limiter_created")
        config = RateLimitConfig(
            requests_per_minute=self.config.requests_per_minute,
            requests_per_hour=self.config.requests_per_hour,
        )
        return RateLimiter(config=config)

    def set_machines_config(self, config: MachinesConfig) -> None:
        """
        Set machines configuration.

        Args:
            config: Machines configuration.
        """
        self._machines_config = config

        # If pool already exists, register machines
        if self._providers["pool"].is_initialized:
            pool = self.pool
            for machine in config.machines:
                pool.register_machine(machine)

    @property
    def pool(self) -> SSHConnectionPool:
        """Get connection pool."""
        return self._providers["pool"].get()

    @property
    def shell_manager(self) -> ShellManager:
        """Get shell manager."""
        return self._providers["shell_manager"].get()

    @property
    def audit_logger(self) -> AuditLogger:
        """Get audit logger."""
        return self._providers["audit_logger"].get()

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get rate limiter."""
        return self._providers["rate_limiter"].get()

    def register(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a custom provider.

        Args:
            name: Provider name.
            factory: Factory function.
        """
        with self._lock:
            self._providers[name] = Provider(factory)

    def get(self, name: str) -> Any:
        """
        Get a service by name.

        Args:
            name: Service name.

        Returns:
            Service instance.

        Raises:
            KeyError: If service not registered.
        """
        if name not in self._providers:
            raise KeyError(f"Service not registered: {name}")
        return self._providers[name].get()

    def reset(self, name: str | None = None) -> None:
        """
        Reset service(s).

        Args:
            name: Service name to reset, or None to reset all.
        """
        with self._lock:
            if name:
                if name in self._providers:
                    self._providers[name].reset()
            else:
                for provider in self._providers.values():
                    provider.reset()

    def shutdown(self) -> None:
        """Shutdown all services."""
        logger.info("container_shutting_down")

        # Shutdown pool
        if self._providers["pool"].is_initialized:
            self.pool.shutdown()

        # Close shell sessions
        if self._providers["shell_manager"].is_initialized:
            self.shell_manager.close_all()

        # Reset all
        self.reset()
        logger.info("container_shutdown_complete")

    def __enter__(self) -> "Container":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.shutdown()


# Global container instance
_container: Container | None = None
_container_lock = threading.Lock()


def get_container() -> Container:
    """Get or create the global container."""
    global _container
    with _container_lock:
        if _container is None:
            _container = Container()
        return _container


def init_container(
    config: ContainerConfig | None = None,
    machines: MachinesConfig | None = None,
) -> Container:
    """
    Initialize the global container.

    Args:
        config: Container configuration.
        machines: Machines configuration.

    Returns:
        Initialized Container.
    """
    global _container
    with _container_lock:
        if _container is not None:
            _container.shutdown()

        _container = Container(config=config)

        if machines:
            _container.set_machines_config(machines)

        return _container


def reset_container() -> None:
    """Reset the global container."""
    global _container
    with _container_lock:
        if _container is not None:
            _container.shutdown()
            _container = None
