"""MCP Tools for file operations."""

from typing import Any

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.security.validator import validate_path
from sshmcp.ssh.client import SSHExecutionError
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def read_file(
    host: str,
    path: str,
    encoding: str = "utf-8",
    max_size: int = 1024 * 1024,
) -> dict[str, Any]:
    """
    Read file content from remote VPS server.

    Args:
        host: Name of the host from machines.json configuration.
        path: Path to the file on remote server.
        encoding: File encoding (default: utf-8).
        max_size: Maximum file size to read in bytes (default: 1MB).

    Returns:
        Dictionary with:
        - content: File content as string
        - path: Full path to file
        - size: File size in bytes
        - encoding: File encoding used
        - truncated: Whether content was truncated
        - host: Host where file is located

    Raises:
        ValueError: If host not found or path not allowed.
        RuntimeError: If file cannot be read.

    Example:
        >>> read_file("production-server", "/var/log/app.log")
        {"content": "log content...", "size": 1024, ...}
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    # Validate path
    is_valid, error_msg = validate_path(path, machine.security, "read")
    if not is_valid:
        audit.log_path_rejected(host, path, error_msg or "Path not allowed")
        raise ValueError(f"Path not allowed: {error_msg}")

    # Read file
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            result = client.read_file(path, encoding=encoding, max_size=max_size)

            audit.log_file_read(host, path, result.size)

            return result.to_dict()

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        raise RuntimeError(f"Failed to read file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"SSH error: {e}") from e


def upload_file(
    host: str,
    path: str,
    content: str,
    mode: str | None = None,
) -> dict[str, Any]:
    """
    Upload file to remote VPS server.

    Args:
        host: Name of the host from machines.json configuration.
        path: Destination path on remote server.
        content: File content to write.
        mode: Optional file permissions (e.g., "0644").

    Returns:
        Dictionary with:
        - success: Whether upload was successful
        - path: Path where file was uploaded
        - size: Uploaded file size in bytes
        - host: Host where file was uploaded

    Raises:
        ValueError: If host not found or path not allowed.
        RuntimeError: If file cannot be written.

    Example:
        >>> upload_file("production-server", "/opt/app/config.json", '{"key": "value"}')
        {"success": true, "path": "/opt/app/config.json", "size": 16, ...}
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    # Validate path
    is_valid, error_msg = validate_path(path, machine.security, "write")
    if not is_valid:
        audit.log_path_rejected(host, path, error_msg or "Path not allowed")
        raise ValueError(f"Path not allowed: {error_msg}")

    # Write file
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            result = client.write_file(path, content, mode=mode)

            audit.log_file_write(host, path, result.size)

            return result.to_dict()

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        raise RuntimeError(f"Failed to write file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"SSH error: {e}") from e


def list_files(
    host: str,
    directory: str,
    recursive: bool = False,
) -> dict[str, Any]:
    """
    List files in directory on remote VPS server.

    Args:
        host: Name of the host from machines.json configuration.
        directory: Path to directory on remote server.
        recursive: Whether to list files recursively (default: false).

    Returns:
        Dictionary with:
        - files: List of file information objects
        - directory: Listed directory path
        - host: Host where files are located
        - total_count: Total number of files

    Raises:
        ValueError: If host not found or path not allowed.
        RuntimeError: If directory cannot be listed.

    Example:
        >>> list_files("production-server", "/var/www")
        {"files": [...], "directory": "/var/www", "total_count": 10, ...}
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    # Validate path
    is_valid, error_msg = validate_path(directory, machine.security, "read")
    if not is_valid:
        audit.log_path_rejected(host, directory, error_msg or "Path not allowed")
        raise ValueError(f"Path not allowed: {error_msg}")

    # List files
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            files = client.list_files(directory, recursive=recursive)

            audit.log(
                event="directory_listed",
                host=host,
                result={"path": directory, "count": len(files)},
            )

            return {
                "files": [f.to_dict() for f in files],
                "directory": directory,
                "host": host,
                "total_count": len(files),
            }

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        raise RuntimeError(f"Failed to list directory: {e}") from e
    except Exception as e:
        raise RuntimeError(f"SSH error: {e}") from e
