"""Tests for Pydantic models."""

from datetime import datetime

import pytest

from sshmcp.models.command import CommandResult
from sshmcp.models.file import FileContent, FileInfo
from sshmcp.models.machine import AuthConfig, SecurityConfig


class TestAuthConfig:
    """Tests for AuthConfig model."""

    def test_key_auth(self):
        """Test key-based authentication config."""
        auth = AuthConfig(type="key", key_path="~/.ssh/id_rsa")
        assert auth.type == "key"
        assert "/.ssh/id_rsa" in auth.key_path  # expanded path

    def test_password_auth(self):
        """Test password-based authentication config."""
        auth = AuthConfig(type="password", password="secret")
        assert auth.type == "password"
        assert auth.password == "secret"

    def test_key_auth_missing_path(self):
        """Test that key auth requires key_path."""
        with pytest.raises(ValueError):
            AuthConfig(type="key")

    def test_password_auth_missing_password(self):
        """Test that password auth requires password."""
        with pytest.raises(ValueError):
            AuthConfig(type="password")


class TestSecurityConfig:
    """Tests for SecurityConfig model."""

    def test_default_values(self):
        """Test default security config values."""
        security = SecurityConfig()
        assert security.timeout_seconds == 30
        assert security.max_concurrent_commands == 3
        assert len(security.forbidden_commands) > 0  # Has default forbidden

    def test_custom_values(self):
        """Test custom security config values."""
        security = SecurityConfig(
            allowed_commands=[".*"],
            timeout_seconds=60,
            max_concurrent_commands=5,
        )
        assert security.timeout_seconds == 60
        assert security.max_concurrent_commands == 5


class TestCommandResult:
    """Tests for CommandResult model."""

    def test_successful_command(self):
        """Test successful command result."""
        result = CommandResult(
            exit_code=0,
            stdout="output",
            stderr="",
            duration_ms=100,
            host="test-server",
            command="echo hello",
        )
        assert result.success
        assert result.exit_code == 0

    def test_failed_command(self):
        """Test failed command result."""
        result = CommandResult(
            exit_code=1,
            stdout="",
            stderr="error",
            duration_ms=50,
            host="test-server",
            command="false",
        )
        assert not result.success
        assert result.exit_code == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = CommandResult(
            exit_code=0,
            stdout="output",
            stderr="",
            duration_ms=100,
            host="test-server",
            command="echo hello",
        )
        data = result.to_dict()
        assert "exit_code" in data
        assert "stdout" in data
        assert "success" in data
        assert data["success"] is True


class TestFileInfo:
    """Tests for FileInfo model."""

    def test_file_info(self):
        """Test file info creation."""
        info = FileInfo(
            name="test.txt",
            path="/var/www/test.txt",
            type="file",
            size=1024,
            modified=datetime.now(),
        )
        assert info.name == "test.txt"
        assert info.type == "file"

    def test_directory_info(self):
        """Test directory info creation."""
        info = FileInfo(
            name="logs",
            path="/var/log/app",
            type="directory",
            size=4096,
            modified=datetime.now(),
        )
        assert info.type == "directory"


class TestFileContent:
    """Tests for FileContent model."""

    def test_file_content(self):
        """Test file content model."""
        content = FileContent(
            content="Hello, World!",
            path="/var/www/test.txt",
            size=13,
            encoding="utf-8",
            truncated=False,
            host="test-server",
        )
        assert content.content == "Hello, World!"
        assert not content.truncated

    def test_truncated_content(self):
        """Test truncated file content."""
        content = FileContent(
            content="truncated...",
            path="/var/log/huge.log",
            size=10000000,
            encoding="utf-8",
            truncated=True,
            host="test-server",
        )
        assert content.truncated
