"""MCP Resource for reading logs."""

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.security.validator import validate_path
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def get_logs(
    host: str,
    log_path: str,
    lines: int = 100,
    filter_level: str | None = None,
) -> str:
    """
    Get logs from VPS server.

    Reads the last N lines from a log file, optionally filtering by log level.

    Args:
        host: Name of the host from machines.json configuration.
        log_path: Path to log file (e.g., "var/log/app.log").
        lines: Number of lines to retrieve (default: 100).
        filter_level: Optional log level filter (error, warn, info).

    Returns:
        Log content as string.

    Raises:
        ValueError: If host not found or path not allowed.
        RuntimeError: If logs cannot be read.

    Example:
        Resource URI: vps://production-server/logs/var/log/app.log
    """
    audit = get_audit_logger()

    # Normalize path (add leading slash if needed)
    if not log_path.startswith("/"):
        log_path = "/" + log_path

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    # Validate path
    is_valid, error_msg = validate_path(log_path, machine.security, "read")
    if not is_valid:
        audit.log_path_rejected(host, log_path, error_msg or "Path not allowed")
        raise ValueError(f"Path not allowed: {error_msg}")

    # Build command
    if filter_level:
        level_patterns = {
            "error": "ERROR|FATAL|CRITICAL",
            "warn": "WARN|WARNING|ERROR|FATAL|CRITICAL",
            "info": "INFO|WARN|WARNING|ERROR|FATAL|CRITICAL",
        }
        pattern = level_patterns.get(filter_level.lower(), "")
        if pattern:
            command = f"tail -n {lines * 2} {log_path} | grep -iE '{pattern}' | tail -n {lines}"
        else:
            command = f"tail -n {lines} {log_path}"
    else:
        command = f"tail -n {lines} {log_path}"

    # Execute command
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            result = client.execute(command)

            if result.exit_code != 0:
                if "No such file" in result.stderr:
                    raise RuntimeError(f"Log file not found: {log_path}")
                raise RuntimeError(f"Failed to read logs: {result.stderr}")

            audit.log(
                event="logs_read",
                host=host,
                result={"path": log_path, "lines": lines},
            )

            return result.stdout

        finally:
            pool.release_client(client)

    except Exception as e:
        raise RuntimeError(f"Failed to read logs: {e}") from e
