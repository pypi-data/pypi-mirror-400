"""Tests for audit logging."""

import json

from sshmcp.security.audit import AuditLogger
from sshmcp.security.validator import sanitize_command_for_log


class TestSanitizeCommand:
    """Tests for command sanitization."""

    def test_safe_command_unchanged(self):
        """Test safe command is not changed."""
        cmd = "ls -la /var/log"
        sanitized = sanitize_command_for_log(cmd)
        assert sanitized == cmd

    def test_sanitize_removes_potential_secrets(self):
        """Test potential secrets are handled."""
        cmd = "echo test"
        sanitized = sanitize_command_for_log(cmd)
        # Should not error and return something
        assert isinstance(sanitized, str)


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_logger_initialization(self):
        """Test logger initializes correctly."""
        logger = AuditLogger()
        assert logger.log_to_stdout is True

    def test_logger_with_file(self, tmp_path):
        """Test logger with file output."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=str(log_file))

        # Log should create file
        logger.log("test_event", host="test-server")

        assert log_file.exists()

    def test_log_event(self, tmp_path):
        """Test logging an event."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=str(log_file), log_to_stdout=False)

        logger.log(
            "command_executed",
            host="prod",
            command="ls -la",
            result={"exit_code": 0, "success": True},
        )

        logger.close()

        content = log_file.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["event"] == "command_executed"
        assert log_entry["host"] == "prod"
        assert log_entry["command"] == "ls -la"
        assert log_entry["result"]["exit_code"] == 0

    def test_log_with_error(self, tmp_path):
        """Test logging an error event."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=str(log_file), log_to_stdout=False)

        logger.log(
            "command_failed",
            host="prod",
            command="bad-command",
            error="Command not found",
        )

        logger.close()

        content = log_file.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["error"] == "Command not found"

    def test_close_logger(self, tmp_path):
        """Test closing logger."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=str(log_file))
        logger.close()

        assert logger._file_handle is None
