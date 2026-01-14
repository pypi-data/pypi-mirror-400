"""Audit logging for SSH MCP operations."""

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import structlog

from sshmcp.security.validator import sanitize_command_for_log

logger = structlog.get_logger()


def get_client_info() -> dict[str, str | None]:
    """
    Get information about the client making the request.

    Returns:
        Dictionary with client IP, hostname, and user.
    """
    info: dict[str, str | None] = {
        "client_ip": None,
        "client_hostname": None,
        "client_user": None,
    }

    # Get current user
    try:
        info["client_user"] = os.getenv("USER") or os.getenv("USERNAME")
    except Exception:
        pass

    # Get local hostname
    try:
        info["client_hostname"] = socket.gethostname()
    except Exception:
        pass

    # Get SSH client IP if available (from SSH_CLIENT or SSH_CONNECTION env vars)
    try:
        ssh_client = os.getenv("SSH_CLIENT")
        if ssh_client:
            info["client_ip"] = ssh_client.split()[0]
        else:
            ssh_connection = os.getenv("SSH_CONNECTION")
            if ssh_connection:
                info["client_ip"] = ssh_connection.split()[0]
    except Exception:
        pass

    return info


class AuditLogger:
    """
    Audit logger for tracking all SSH MCP operations.
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        log_to_stdout: bool = True,
    ) -> None:
        """
        Initialize audit logger.

        Args:
            log_file: Optional path to audit log file.
            log_to_stdout: Whether to also log to stdout via structlog.
        """
        self.log_file = log_file
        self.log_to_stdout = log_to_stdout
        self._file_handle = None

        if log_file:
            path = Path(log_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(path, "a", encoding="utf-8")

    def log(
        self,
        event: str,
        host: Optional[str] = None,
        command: Optional[str] = None,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        include_client_info: bool = True,
    ) -> None:
        """
        Log an audit event.

        Args:
            event: Event type (e.g., 'command_executed', 'file_read').
            host: Target host name.
            command: Command that was executed (will be sanitized).
            result: Result of the operation.
            error: Error message if operation failed.
            metadata: Additional metadata to log.
            include_client_info: Whether to include client IP/user info.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        audit_record: dict[str, Any] = {
            "timestamp": timestamp,
            "event": event,
        }

        # Include client information
        if include_client_info:
            client_info = get_client_info()
            audit_record["client"] = {
                k: v for k, v in client_info.items() if v is not None
            }

        # Build log kwargs (without event, as it's passed separately to structlog)
        log_kwargs: dict[str, Any] = {"timestamp": timestamp}

        if host:
            audit_record["host"] = host
            log_kwargs["host"] = host

        if command:
            # Sanitize command to hide potential secrets
            sanitized = sanitize_command_for_log(command)
            audit_record["command"] = sanitized
            log_kwargs["command"] = sanitized

        if result:
            # Only include safe result fields
            safe_result = {
                k: v
                for k, v in result.items()
                if k in ("exit_code", "success", "duration_ms", "size", "path")
            }
            audit_record["result"] = safe_result
            log_kwargs["result"] = safe_result

        if error:
            audit_record["error"] = error
            log_kwargs["error"] = error

        if metadata:
            audit_record["metadata"] = metadata
            log_kwargs["metadata"] = metadata

        # Log to structlog
        if self.log_to_stdout:
            if error:
                logger.error(event, **log_kwargs)
            else:
                logger.info(event, **log_kwargs)

        # Write to file
        if self._file_handle:
            self._file_handle.write(json.dumps(audit_record) + "\n")
            self._file_handle.flush()

    def log_command_executed(
        self,
        host: str,
        command: str,
        exit_code: int,
        duration_ms: int,
    ) -> None:
        """Log command execution."""
        self.log(
            event="command_executed",
            host=host,
            command=command,
            result={
                "exit_code": exit_code,
                "duration_ms": duration_ms,
                "success": exit_code == 0,
            },
        )

    def log_command_failed(
        self,
        host: str,
        command: str,
        error: str,
    ) -> None:
        """Log failed command execution."""
        self.log(
            event="command_failed",
            host=host,
            command=command,
            error=error,
        )

    def log_command_rejected(
        self,
        host: str,
        command: str,
        reason: str,
    ) -> None:
        """Log rejected command (security validation failed)."""
        self.log(
            event="command_rejected",
            host=host,
            command=command,
            error=reason,
            metadata={"security_violation": True},
        )

    def log_file_read(
        self,
        host: str,
        path: str,
        size: int,
    ) -> None:
        """Log file read operation."""
        self.log(
            event="file_read",
            host=host,
            result={"path": path, "size": size},
        )

    def log_file_write(
        self,
        host: str,
        path: str,
        size: int,
    ) -> None:
        """Log file write operation."""
        self.log(
            event="file_write",
            host=host,
            result={"path": path, "size": size},
        )

    def log_path_rejected(
        self,
        host: str,
        path: str,
        reason: str,
    ) -> None:
        """Log rejected path access."""
        self.log(
            event="path_rejected",
            host=host,
            error=reason,
            metadata={"path": path, "security_violation": True},
        )

    def close(self) -> None:
        """Close audit log file."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def init_audit_logger(
    log_file: Optional[str] = None,
    log_to_stdout: bool = True,
) -> AuditLogger:
    """
    Initialize the global audit logger.

    Args:
        log_file: Optional path to audit log file.
        log_to_stdout: Whether to also log to stdout.

    Returns:
        Initialized AuditLogger.
    """
    global _audit_logger
    _audit_logger = AuditLogger(log_file=log_file, log_to_stdout=log_to_stdout)
    return _audit_logger


def audit_log(
    event: str,
    host: Optional[str] = None,
    command: Optional[str] = None,
    result: Optional[dict[str, Any]] = None,
    error: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """
    Convenience function to log an audit event.

    Args:
        event: Event type.
        host: Target host name.
        command: Command that was executed.
        result: Result of the operation.
        error: Error message if operation failed.
        metadata: Additional metadata.
    """
    get_audit_logger().log(
        event=event,
        host=host,
        command=command,
        result=result,
        error=error,
        metadata=metadata,
    )
