"""MCP Tool for command execution."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import structlog

from sshmcp.config import get_config, get_machine, list_machines
from sshmcp.security.audit import get_audit_logger
from sshmcp.security.validator import check_command_safety, validate_command
from sshmcp.ssh.client import SSHExecutionError
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def execute_command(
    host: str,
    command: str,
    timeout: int | None = None,
) -> dict[str, Any]:
    """
    Execute a command on remote VPS server via SSH.

    This tool allows AI agents to execute commands on configured VPS servers
    with security validation and timeout protection.

    Args:
        host: Name of the host from machines.json configuration.
        command: Shell command to execute (must match whitelist patterns).
        timeout: Maximum execution time in seconds (default: from config).

    Returns:
        Dictionary with:
        - exit_code: Command exit code (0 = success)
        - stdout: Standard output text
        - stderr: Standard error text
        - duration_ms: Execution time in milliseconds
        - success: Boolean indicating success
        - host: Host where command was executed
        - command: The executed command

    Raises:
        ValueError: If host not found or command not allowed.
        RuntimeError: If SSH connection or execution fails.

    Example:
        >>> execute_command("production-server", "git pull origin main")
        {"exit_code": 0, "stdout": "Already up to date.", "stderr": "", ...}
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        audit.log(
            event="command_rejected",
            error=f"Host not found: {host}",
            metadata={"requested_host": host},
        )
        raise ValueError(f"Host not found: {host}") from e

    # Validate command against security rules
    is_valid, error_msg = validate_command(command, machine.security)
    if not is_valid:
        audit.log_command_rejected(host, command, error_msg or "Validation failed")
        raise ValueError(f"Command not allowed: {error_msg}")

    # Check for safety warnings
    warnings = check_command_safety(command)
    if warnings:
        logger.warning(
            "command_safety_warnings",
            host=host,
            command=command,
            warnings=warnings,
        )

    # Get timeout
    if timeout is None:
        timeout = machine.security.timeout_seconds

    # Execute command
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            result = client.execute(command, timeout=timeout)

            audit.log_command_executed(
                host=host,
                command=command,
                exit_code=result.exit_code,
                duration_ms=result.duration_ms,
            )

            return result.to_dict()

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        audit.log_command_failed(host, command, str(e))
        raise RuntimeError(f"Command execution failed: {e}") from e
    except Exception as e:
        audit.log_command_failed(host, command, str(e))
        raise RuntimeError(f"SSH error: {e}") from e


def execute_on_multiple(
    hosts: list[str],
    command: str,
    timeout: int | None = None,
    stop_on_error: bool = False,
    parallel: bool = True,
) -> dict[str, Any]:
    """
    Execute a command on multiple VPS servers.

    Runs the same command on multiple servers, optionally in parallel.
    Useful for checking status, deploying updates, or running maintenance
    across a fleet of servers.

    Args:
        hosts: List of host names to execute on. Use ["*"] for all servers,
               or ["tag:production"] to filter by tag.
        command: Shell command to execute.
        timeout: Maximum execution time per server in seconds.
        stop_on_error: If True, stop execution on first error.
        parallel: If True, execute on all hosts simultaneously.

    Returns:
        Dictionary with results from each server:
        - total: Number of servers
        - successful: Number of successful executions
        - failed: Number of failed executions
        - results: Per-server results

    Example:
        >>> execute_on_multiple(["web1", "web2"], "uptime")
        {"total": 2, "successful": 2, "results": {...}}

        >>> execute_on_multiple(["*"], "docker ps")  # All servers
        >>> execute_on_multiple(["tag:production"], "uptime")  # By tag
    """
    # Expand host list
    if hosts == ["*"] or hosts == "*":
        hosts = list_machines()
    elif len(hosts) == 1 and hosts[0].startswith("tag:"):
        tag = hosts[0][4:]
        config = get_config()
        hosts = [
            m.name
            for m in config.machines
            if hasattr(m, "tags") and tag in (m.tags or [])
        ]
        if not hosts:
            return {
                "success": False,
                "error": f"No servers found with tag: {tag}",
                "available_tags": _get_all_tags(),
            }

    if not hosts:
        return {
            "success": False,
            "error": "No hosts specified",
            "available_servers": list_machines(),
        }

    results = {}
    successful = 0
    failed = 0

    def run_on_host(host: str) -> tuple[str, dict]:
        try:
            result = execute_command(host, command, timeout)
            return host, {"success": True, **result}
        except Exception as e:
            return host, {"success": False, "error": str(e)}

    if parallel and len(hosts) > 1:
        with ThreadPoolExecutor(max_workers=min(len(hosts), 10)) as executor:
            futures = {executor.submit(run_on_host, host): host for host in hosts}
            for future in as_completed(futures):
                host, result = future.result()
                results[host] = result
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                    if stop_on_error:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
    else:
        for host in hosts:
            host, result = run_on_host(host)
            results[host] = result
            if result["success"]:
                successful += 1
            else:
                failed += 1
                if stop_on_error:
                    break

    return {
        "success": failed == 0,
        "total": len(hosts),
        "successful": successful,
        "failed": failed,
        "command": command,
        "results": results,
    }


def _get_all_tags() -> list[str]:
    """Get all unique tags from configured servers."""
    config = get_config()
    tags = set()
    for m in config.machines:
        if hasattr(m, "tags") and m.tags:
            tags.update(m.tags)
    return sorted(tags)
