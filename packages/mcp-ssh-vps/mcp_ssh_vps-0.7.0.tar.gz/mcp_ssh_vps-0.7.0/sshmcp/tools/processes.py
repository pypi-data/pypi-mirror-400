"""MCP Tool for process management."""

from typing import Any, Literal

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.ssh.client import SSHExecutionError
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


ServiceManager = Literal["systemd", "pm2", "supervisor", "auto"]
ProcessAction = Literal["start", "stop", "restart", "status"]


def manage_process(
    host: str,
    action: ProcessAction,
    process_name: str,
    service_manager: ServiceManager = "auto",
) -> dict[str, Any]:
    """
    Manage processes on remote VPS server.

    Supports systemd, pm2, and supervisor service managers.

    Args:
        host: Name of the host from machines.json configuration.
        action: Action to perform (start, stop, restart, status).
        process_name: Name of the process or service.
        service_manager: Service manager to use (systemd, pm2, supervisor, auto).

    Returns:
        Dictionary with:
        - success: Whether action was successful
        - action: Action that was performed
        - process: Process name
        - status: Current process status (if available)
        - output: Command output
        - host: Host where action was performed

    Raises:
        ValueError: If host not found or invalid parameters.
        RuntimeError: If action fails.

    Example:
        >>> manage_process("production-server", "restart", "nginx")
        {"success": true, "action": "restart", "process": "nginx", ...}
    """
    audit = get_audit_logger()

    # Validate action
    valid_actions = ("start", "stop", "restart", "status")
    if action not in valid_actions:
        raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    # Get pool and client
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            # Detect service manager if auto
            if service_manager == "auto":
                service_manager = _detect_service_manager(client, process_name)

            # Build and execute command
            command = _build_process_command(service_manager, action, process_name)

            result = client.execute(command)

            # Parse status if requested
            status = None
            if action == "status":
                status = _parse_status(service_manager, result.stdout, result.exit_code)

            audit.log(
                event="process_managed",
                host=host,
                metadata={
                    "action": action,
                    "process": process_name,
                    "service_manager": service_manager,
                    "exit_code": result.exit_code,
                },
            )

            return {
                "success": result.exit_code == 0 or (action == "status"),
                "action": action,
                "process": process_name,
                "service_manager": service_manager,
                "status": status,
                "output": result.stdout or result.stderr,
                "exit_code": result.exit_code,
                "host": host,
            }

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        raise RuntimeError(f"Process management failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"SSH error: {e}") from e


def _detect_service_manager(client: Any, process_name: str) -> str:
    """Detect which service manager to use."""
    # Try systemd first
    try:
        result = client.execute(f"systemctl is-enabled {process_name} 2>/dev/null")
        if (
            result.exit_code == 0
            or "enabled" in result.stdout
            or "disabled" in result.stdout
        ):
            return "systemd"
    except Exception:
        pass

    # Try pm2
    try:
        result = client.execute("which pm2 2>/dev/null")
        if result.exit_code == 0:
            result = client.execute(f"pm2 describe {process_name} 2>/dev/null")
            if result.exit_code == 0:
                return "pm2"
    except Exception:
        pass

    # Try supervisor
    try:
        result = client.execute("which supervisorctl 2>/dev/null")
        if result.exit_code == 0:
            return "supervisor"
    except Exception:
        pass

    # Default to systemd
    return "systemd"


def _build_process_command(
    service_manager: str,
    action: str,
    process_name: str,
) -> str:
    """Build command for the service manager."""
    if service_manager == "systemd":
        return f"systemctl {action} {process_name}"
    elif service_manager == "pm2":
        if action == "status":
            return f"pm2 describe {process_name}"
        return f"pm2 {action} {process_name}"
    elif service_manager == "supervisor":
        if action == "status":
            return f"supervisorctl status {process_name}"
        return f"supervisorctl {action} {process_name}"
    else:
        raise ValueError(f"Unknown service manager: {service_manager}")


def _parse_status(
    service_manager: str,
    output: str,
    exit_code: int,
) -> str:
    """Parse status from command output."""
    output_lower = output.lower()

    if service_manager == "systemd":
        if "active (running)" in output_lower:
            return "running"
        elif "inactive" in output_lower:
            return "stopped"
        elif "failed" in output_lower:
            return "failed"
        elif "activating" in output_lower:
            return "starting"
        else:
            return "unknown"

    elif service_manager == "pm2":
        if "online" in output_lower:
            return "running"
        elif "stopped" in output_lower:
            return "stopped"
        elif "errored" in output_lower:
            return "failed"
        else:
            return "unknown"

    elif service_manager == "supervisor":
        if "running" in output_lower:
            return "running"
        elif "stopped" in output_lower:
            return "stopped"
        elif "fatal" in output_lower or "error" in output_lower:
            return "failed"
        else:
            return "unknown"

    return "unknown"
