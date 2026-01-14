"""Tests for dependency injection container."""

from unittest.mock import MagicMock

import pytest

from sshmcp.core.container import (
    Container,
    ContainerConfig,
    Provider,
    get_container,
    init_container,
    reset_container,
)
from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    MachinesConfig,
    SecurityConfig,
)
from sshmcp.security.audit import AuditLogger
from sshmcp.security.rate_limiter import RateLimiter
from sshmcp.ssh.pool import SSHConnectionPool
from sshmcp.ssh.shell import ShellManager


class TestProvider:
    """Tests for Provider class."""

    def test_lazy_initialization(self):
        """Test lazy initialization."""
        factory = MagicMock(return_value="value")
        provider = Provider(factory)

        # Factory not called yet
        factory.assert_not_called()
        assert not provider.is_initialized

        # First get calls factory
        result = provider.get()
        assert result == "value"
        factory.assert_called_once()
        assert provider.is_initialized

        # Second get returns cached
        result2 = provider.get()
        assert result2 == "value"
        factory.assert_called_once()  # Still once

    def test_reset(self):
        """Test resetting provider."""
        factory = MagicMock(return_value="value")
        provider = Provider(factory)

        provider.get()
        assert provider.is_initialized

        provider.reset()
        assert not provider.is_initialized

        # Next get calls factory again
        provider.get()
        assert factory.call_count == 2


class TestContainerConfig:
    """Tests for ContainerConfig."""

    def test_defaults(self):
        """Test default values."""
        config = ContainerConfig()
        assert config.max_connections_per_host == 3
        assert config.requests_per_minute == 60

    def test_custom_values(self):
        """Test custom values."""
        config = ContainerConfig(
            max_connections_per_host=5,
            requests_per_minute=100,
        )
        assert config.max_connections_per_host == 5
        assert config.requests_per_minute == 100


class TestContainer:
    """Tests for Container."""

    @pytest.fixture
    def container(self):
        """Create container for testing."""
        config = ContainerConfig(enable_background_cleanup=False)
        container = Container(config=config)
        yield container
        container.shutdown()

    def test_init(self, container):
        """Test container initialization."""
        assert container.config is not None
        assert "_providers" in container.__dict__

    def test_pool_property(self, container):
        """Test pool property."""
        pool = container.pool
        assert isinstance(pool, SSHConnectionPool)

        # Same instance
        pool2 = container.pool
        assert pool is pool2

    def test_shell_manager_property(self, container):
        """Test shell_manager property."""
        manager = container.shell_manager
        assert isinstance(manager, ShellManager)

    def test_audit_logger_property(self, container):
        """Test audit_logger property."""
        logger = container.audit_logger
        assert isinstance(logger, AuditLogger)

    def test_rate_limiter_property(self, container):
        """Test rate_limiter property."""
        limiter = container.rate_limiter
        assert isinstance(limiter, RateLimiter)

    def test_register_custom(self, container):
        """Test registering custom provider."""
        container.register("custom", lambda: "custom_value")

        result = container.get("custom")
        assert result == "custom_value"

    def test_get_unknown(self, container):
        """Test getting unknown service."""
        with pytest.raises(KeyError, match="not registered"):
            container.get("nonexistent")

    def test_reset_single(self, container):
        """Test resetting single service."""
        # Initialize
        pool1 = container.pool
        assert container._providers["pool"].is_initialized

        # Reset
        container.reset("pool")
        assert not container._providers["pool"].is_initialized

        # New instance
        pool2 = container.pool
        assert pool2 is not pool1

    def test_reset_all(self, container):
        """Test resetting all services."""
        # Initialize all
        container.pool
        container.shell_manager
        container.audit_logger

        # Reset all
        container.reset()

        for provider in container._providers.values():
            assert not provider.is_initialized

    def test_set_machines_config(self, container):
        """Test setting machines config."""
        machine = MachineConfig(
            name="test",
            host="192.168.1.1",
            port=22,
            user="user",
            auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
            security=SecurityConfig(),
        )
        config = MachinesConfig(machines=[machine])

        container.set_machines_config(config)

        assert container._machines_config is config

    def test_context_manager(self):
        """Test context manager."""
        config = ContainerConfig(enable_background_cleanup=False)
        with Container(config=config) as container:
            pool = container.pool
            assert pool is not None


class TestGlobalContainer:
    """Tests for global container functions."""

    def setup_method(self):
        """Reset global container before each test."""
        reset_container()

    def teardown_method(self):
        """Reset global container after each test."""
        reset_container()

    def test_get_container(self):
        """Test getting global container."""
        container = get_container()
        assert isinstance(container, Container)

        # Same instance
        container2 = get_container()
        assert container is container2

    def test_init_container(self):
        """Test initializing global container."""
        config = ContainerConfig(
            max_connections_per_host=5,
            enable_background_cleanup=False,
        )

        container = init_container(config=config)

        assert container.config.max_connections_per_host == 5

    def test_init_container_with_machines(self):
        """Test init with machines config."""
        machine = MachineConfig(
            name="test",
            host="192.168.1.1",
            port=22,
            user="user",
            auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
            security=SecurityConfig(),
        )
        machines = MachinesConfig(machines=[machine])

        config = ContainerConfig(enable_background_cleanup=False)
        container = init_container(config=config, machines=machines)

        assert container._machines_config is machines

    def test_reinit_container(self):
        """Test reinitializing container."""
        config1 = ContainerConfig(
            max_connections_per_host=3,
            enable_background_cleanup=False,
        )
        container1 = init_container(config=config1)

        config2 = ContainerConfig(
            max_connections_per_host=10,
            enable_background_cleanup=False,
        )
        container2 = init_container(config=config2)

        assert container2 is not container1
        assert container2.config.max_connections_per_host == 10

    def test_reset_container(self):
        """Test resetting global container."""
        get_container()
        reset_container()

        # New instance created
        import sshmcp.core.container as module

        assert module._container is None
