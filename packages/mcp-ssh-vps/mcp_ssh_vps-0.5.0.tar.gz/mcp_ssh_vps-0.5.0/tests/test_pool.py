"""Tests for SSH connection pool."""

import pytest

from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
from sshmcp.ssh.pool import SSHConnectionPool, get_pool


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


class TestSSHConnectionPool:
    """Tests for SSHConnectionPool."""

    def test_pool_initialization(self):
        """Test pool initializes with default settings."""
        pool = SSHConnectionPool()
        assert pool.max_connections_per_host == 3
        assert pool.idle_timeout == 300

    def test_pool_custom_settings(self):
        """Test pool with custom settings."""
        pool = SSHConnectionPool(max_connections_per_host=10, idle_timeout=600)
        assert pool.max_connections_per_host == 10
        assert pool.idle_timeout == 600

    def test_register_machine(self, machine_config):
        """Test registering a machine."""
        pool = SSHConnectionPool()
        pool.register_machine(machine_config)
        assert "test-server" in pool._machines

    def test_register_duplicate_machine(self, machine_config):
        """Test registering same machine twice updates it."""
        pool = SSHConnectionPool()
        pool.register_machine(machine_config)
        pool.register_machine(machine_config)
        assert "test-server" in pool._machines


class TestPoolGlobalFunctions:
    """Tests for global pool functions."""

    def test_get_pool_singleton(self):
        """Test get_pool returns singleton."""
        # Reset global pool
        import sshmcp.ssh.pool as pool_module

        pool_module._pool = None

        pool1 = get_pool()
        pool2 = get_pool()
        assert pool1 is pool2
