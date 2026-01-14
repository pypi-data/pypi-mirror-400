"""SSH MCP Server - Main entry point."""

import argparse
import os
import sys
from typing import Any

import structlog
from mcp.server.fastmcp import FastMCP

from sshmcp.config import ConfigurationError, get_config, load_config
from sshmcp.monitoring.alerts import get_alert_manager
from sshmcp.prompts.backup import backup_database as _backup_database
from sshmcp.prompts.deploy import deploy_app as _deploy_app
from sshmcp.prompts.monitor import monitor_health as _monitor_health
from sshmcp.resources.logs import get_logs as _get_logs
from sshmcp.resources.metrics import get_metrics as _get_metrics
from sshmcp.resources.status import get_status as _get_status
from sshmcp.security.audit import init_audit_logger
from sshmcp.security.whitelist import init_whitelist
from sshmcp.ssh.pool import init_pool
from sshmcp.ssh.shell import get_shell_manager
from sshmcp.tools.commands import execute_command as _execute_command
from sshmcp.tools.commands import execute_on_multiple as _execute_on_multiple
from sshmcp.tools.files import list_files as _list_files
from sshmcp.tools.files import read_file as _read_file
from sshmcp.tools.files import upload_file as _upload_file
from sshmcp.tools.helpers import get_allowed_commands as _get_allowed_commands
from sshmcp.tools.helpers import get_help as _get_help
from sshmcp.tools.helpers import get_server_info as _get_server_info

# New tool imports
from sshmcp.tools.history import get_history
from sshmcp.tools.processes import manage_process as _manage_process
from sshmcp.tools.servers import add_server as _add_server
from sshmcp.tools.servers import list_servers as _list_servers
from sshmcp.tools.servers import remove_server as _remove_server
from sshmcp.tools.servers import test_server_connection as _test_server_connection

# Configure structured logging to stderr (stdout is used for MCP JSON protocol)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create MCP server instance
mcp = FastMCP(
    "SSH VPS Manager",
    json_response=True,
)

# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
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
        Dictionary with exit_code, stdout, stderr, duration_ms, success.
    """
    return _execute_command(host, command, timeout)


@mcp.tool()
async def execute_command_streaming(
    host: str,
    command: str,
    timeout: int | None = None,
    ctx: Any = None,
) -> dict[str, Any]:
    """
    Execute a command with streaming progress updates.

    Similar to execute_command but reports progress for long-running commands.
    Uses MCP progress reporting to stream output chunks.

    Args:
        host: Name of the host.
        command: Shell command to execute.
        timeout: Maximum execution time in seconds.
        ctx: MCP Context for progress reporting (injected automatically).

    Returns:
        Dictionary with full output after completion.
    """
    from mcp.server.fastmcp import Context

    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    try:
        # Execute with streaming
        transport = client._client.get_transport()
        if not transport:
            return {"success": False, "error": "No transport"}

        channel = transport.open_session()
        channel.settimeout(timeout or 60)
        channel.exec_command(command)

        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        chunk_count = 0

        # Stream output
        while True:
            if channel.recv_ready():
                chunk = channel.recv(4096).decode("utf-8", errors="replace")
                if chunk:
                    stdout_chunks.append(chunk)
                    chunk_count += 1
                    # Report progress if context available
                    if ctx and isinstance(ctx, Context):
                        await ctx.report_progress(
                            chunk_count,
                            None,
                            f"Received {len(''.join(stdout_chunks))} bytes",
                        )

            if channel.recv_stderr_ready():
                chunk = channel.recv_stderr(4096).decode("utf-8", errors="replace")
                if chunk:
                    stderr_chunks.append(chunk)

            if channel.exit_status_ready():
                # Drain remaining output
                while channel.recv_ready():
                    stdout_chunks.append(
                        channel.recv(4096).decode("utf-8", errors="replace")
                    )
                while channel.recv_stderr_ready():
                    stderr_chunks.append(
                        channel.recv_stderr(4096).decode("utf-8", errors="replace")
                    )
                break

        exit_code = channel.recv_exit_status()
        channel.close()

        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": "".join(stdout_chunks),
            "stderr": "".join(stderr_chunks),
            "chunks_received": chunk_count,
            "host": host,
            "command": command,
        }
    finally:
        client.disconnect()


@mcp.tool()
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
        Dictionary with content, path, size, encoding, truncated.
    """
    return _read_file(host, path, encoding, max_size)


@mcp.tool()
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
        Dictionary with success, path, size.
    """
    return _upload_file(host, path, content, mode)


@mcp.tool()
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
        Dictionary with files list, directory, total_count.
    """
    return _list_files(host, directory, recursive)


@mcp.tool()
def manage_process(
    host: str,
    action: str,
    process_name: str,
    service_manager: str = "auto",
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
        Dictionary with success, action, process, status.
    """
    return _manage_process(host, action, process_name, service_manager)  # type: ignore


@mcp.tool()
def get_available_machines() -> dict[str, Any]:
    """
    Get list of available configured machines.

    Returns:
        Dictionary with list of machine names and their descriptions.
    """
    try:
        config = get_config()
        machines = []
        for machine in config.machines:
            machines.append(
                {
                    "name": machine.name,
                    "host": machine.host,
                    "description": machine.description,
                }
            )
        return {
            "machines": machines,
            "count": len(machines),
        }
    except ConfigurationError as e:
        return {
            "error": str(e),
            "machines": [],
            "count": 0,
        }


# ============================================================================
# Server Management Tools
# ============================================================================


@mcp.tool()
def list_servers(tag: str | None = None) -> dict[str, Any]:
    """
    List all configured VPS servers.

    Returns a list of all servers with their connection details.
    Use this to see what servers are available.

    Args:
        tag: Optional tag to filter servers (e.g., "production", "web").

    Returns:
        Dictionary with servers list, count, and available tags.
    """
    return _list_servers(tag)


@mcp.tool()
def add_server(
    name: str,
    host: str,
    user: str,
    port: int = 22,
    auth_type: str = "key",
    key_path: str = "~/.ssh/id_rsa",
    password: str | None = None,
    description: str | None = None,
    security_level: str = "full",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Add a new VPS server to the configuration.

    After adding, the server can be used with execute_command and other tools.

    Args:
        name: Unique name for the server (e.g., "production", "staging").
        host: Server hostname or IP address.
        user: SSH username.
        port: SSH port (default: 22).
        auth_type: Authentication type - "key" or "password".
        key_path: Path to SSH private key (for key auth).
        password: SSH password (for password auth).
        description: Optional description of the server.
        security_level: Security profile - "strict", "moderate", or "full" (default: full).
        tags: Tags for grouping servers (e.g., ["production", "web"]).

    Returns:
        Dictionary with success status and server details.
    """
    return _add_server(
        name=name,
        host=host,
        user=user,
        port=port,
        auth_type=auth_type,
        key_path=key_path,
        password=password,
        description=description,
        security_level=security_level,
        tags=tags,
    )


@mcp.tool()
def remove_server(name: str) -> dict[str, Any]:
    """
    Remove a VPS server from the configuration.

    Args:
        name: Name of the server to remove.

    Returns:
        Dictionary with success status.
    """
    return _remove_server(name)


@mcp.tool()
def test_connection(name: str) -> dict[str, Any]:
    """
    Test SSH connection to a server.

    Attempts to connect and verify the server is accessible.

    Args:
        name: Name of the server to test.

    Returns:
        Dictionary with connection status and server info.
    """
    return _test_server_connection(name)


@mcp.tool()
def execute_on_multiple(
    hosts: list[str],
    command: str,
    timeout: int | None = None,
    stop_on_error: bool = False,
) -> dict[str, Any]:
    """
    Execute a command on multiple VPS servers.

    Run the same command on multiple servers simultaneously.
    Useful for fleet management, deployments, and status checks.

    Args:
        hosts: List of server names. Use ["*"] for all servers,
               or ["tag:production"] to filter by tag.
        command: Shell command to execute.
        timeout: Timeout per server in seconds.
        stop_on_error: Stop on first error if True.

    Returns:
        Dictionary with results from each server.

    Examples:
        execute_on_multiple(["web1", "web2"], "uptime")
        execute_on_multiple(["*"], "docker ps")
        execute_on_multiple(["tag:production"], "systemctl status nginx")
    """
    return _execute_on_multiple(hosts, command, timeout, stop_on_error)


@mcp.tool()
def get_help(topic: str | None = None) -> dict[str, Any]:
    """
    Get help information about SSH MCP tools.

    Provides documentation, examples, and usage information.

    Args:
        topic: Help topic - "tools", "security", "servers", "examples", or None for overview.

    Returns:
        Dictionary with help information.
    """
    return _get_help(topic)


@mcp.tool()
def get_allowed_commands(host: str) -> dict[str, Any]:
    """
    Get the list of allowed commands for a server.

    Shows security configuration including allowed/forbidden patterns.

    Args:
        host: Name of the server.

    Returns:
        Dictionary with allowed commands, forbidden patterns, and timeouts.
    """
    return _get_allowed_commands(host)


@mcp.tool()
def get_server_info(host: str) -> dict[str, Any]:
    """
    Get detailed information about a server.

    Shows configuration, security settings, and connection details.

    Args:
        host: Name of the server.

    Returns:
        Dictionary with server details.
    """
    return _get_server_info(host)


# ============================================================================
# Command History Tools
# ============================================================================


@mcp.tool()
def get_command_history(
    host: str | None = None,
    limit: int = 50,
    success_only: bool = False,
) -> dict[str, Any]:
    """
    Get command execution history.

    View previously executed commands with their results.
    Useful for auditing, debugging, and understanding past operations.

    Args:
        host: Filter by host name (optional, all hosts if not specified).
        limit: Maximum number of entries to return (default: 50).
        success_only: Only show successful commands (default: false).

    Returns:
        Dictionary with:
        - entries: List of history entries with command, exit_code, timestamp
        - total: Total matching entries
        - hosts: List of hosts in results
    """
    history = get_history()
    entries = list(history.get_history(host=host, limit=limit))

    if success_only:
        entries = [e for e in entries if e.exit_code == 0]

    return {
        "entries": [
            {
                "host": e.host,
                "command": e.command,
                "exit_code": e.exit_code,
                "timestamp": e.timestamp.isoformat(),
                "duration_ms": e.duration_ms,
            }
            for e in entries
        ],
        "total": len(entries),
        "hosts": list(set(e.host for e in entries)),
    }


@mcp.tool()
def search_command_history(
    pattern: str,
    host: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Search command history by pattern.

    Find commands matching a search pattern in history.

    Args:
        pattern: Search pattern (substring match in command).
        host: Filter by host name (optional).
        limit: Maximum results (default: 20).

    Returns:
        Dictionary with matching history entries.
    """
    history = get_history()
    entries = list(history.search(pattern, host=host, limit=limit))

    return {
        "pattern": pattern,
        "matches": [
            {
                "host": e.host,
                "command": e.command,
                "exit_code": e.exit_code,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in entries
        ],
        "total": len(entries),
    }


@mcp.tool()
def get_command_stats(host: str | None = None) -> dict[str, Any]:
    """
    Get command execution statistics.

    Summary of command history with success/failure rates.

    Args:
        host: Filter by host name (optional).

    Returns:
        Dictionary with statistics:
        - total_commands: Total executed commands
        - successful: Number of successful (exit_code=0)
        - failed: Number of failed commands
        - success_rate: Percentage of successful commands
        - by_host: Breakdown by host
    """
    history = get_history()
    return history.get_stats(host)


# ============================================================================
# Interactive Shell Tools
# ============================================================================


@mcp.tool()
def shell_start(
    host: str,
    term: str = "xterm",
    width: int = 80,
    height: int = 24,
) -> dict[str, Any]:
    """
    Start an interactive shell session.

    Opens a PTY-based shell for interactive commands.
    Use shell_send to send commands and shell_recv to get output.

    Args:
        host: Name of the host to connect to.
        term: Terminal type (default: xterm).
        width: Terminal width in characters (default: 80).
        height: Terminal height in characters (default: 24).

    Returns:
        Dictionary with session_id and session details.
    """
    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    manager = get_shell_manager()
    session = manager.create_session(
        ssh_client=client,
        term=term,
        width=width,
        height=height,
    )

    return {
        "success": True,
        "session_id": session.session_id,
        "host": session.host,
        "terminal": session.terminal,
        "hint": "Use shell_send to send commands, shell_recv to get output, shell_close to end session.",
    }


@mcp.tool()
def shell_send(session_id: str, data: str, newline: bool = True) -> dict[str, Any]:
    """
    Send data to an interactive shell session.

    Args:
        session_id: Session ID from shell_start.
        data: Text to send to shell.
        newline: Add newline after data (default: true).

    Returns:
        Dictionary with success status.
    """
    manager = get_shell_manager()
    shell = manager.get_session(session_id)

    if not shell:
        return {"success": False, "error": f"Session not found: {session_id}"}

    if newline:
        shell.send_line(data)
    else:
        shell.send(data)

    return {"success": True, "sent": data}


@mcp.tool()
def shell_recv(session_id: str, timeout: float = 2.0) -> dict[str, Any]:
    """
    Receive output from an interactive shell session.

    Args:
        session_id: Session ID from shell_start.
        timeout: Maximum time to wait for output (default: 2 seconds).

    Returns:
        Dictionary with output data.
    """
    manager = get_shell_manager()
    shell = manager.get_session(session_id)

    if not shell:
        return {"success": False, "error": f"Session not found: {session_id}"}

    outputs = shell.recv(timeout=timeout)

    return {
        "success": True,
        "output": "".join(o.data for o in outputs),
        "chunks": len(outputs),
    }


@mcp.tool()
def shell_close(session_id: str) -> dict[str, Any]:
    """
    Close an interactive shell session.

    Args:
        session_id: Session ID to close.

    Returns:
        Dictionary with success status.
    """
    manager = get_shell_manager()
    closed = manager.close_session(session_id)

    return {
        "success": closed,
        "message": "Session closed" if closed else "Session not found",
    }


@mcp.tool()
def shell_list() -> dict[str, Any]:
    """
    List active shell sessions.

    Returns:
        Dictionary with list of active sessions.
    """
    manager = get_shell_manager()
    sessions = manager.list_sessions()

    return {
        "sessions": [s.to_dict() for s in sessions],
        "total": len(sessions),
    }


# ============================================================================
# Monitoring & Alerts Tools
# ============================================================================


@mcp.tool()
def get_alerts(
    host: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get monitoring alerts.

    View active and historical alerts for CPU, memory, disk usage.

    Args:
        host: Filter by host name (optional).
        severity: Filter by severity: "warning" or "critical" (optional).
        limit: Maximum alerts to return (default: 50).

    Returns:
        Dictionary with alerts list.
    """
    from sshmcp.monitoring.alerts import AlertSeverity

    manager = get_alert_manager()

    sev = None
    if severity:
        sev = AlertSeverity(severity.lower())

    alerts = manager.get_alerts(host=host, severity=sev, limit=limit)

    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": len(alerts),
        "active_count": len(manager.get_active_alerts()),
    }


@mcp.tool()
def get_active_alerts() -> dict[str, Any]:
    """
    Get currently active alerts.

    Shows alerts that haven't been cleared yet.

    Returns:
        Dictionary with active alerts.
    """
    manager = get_alert_manager()
    active = manager.get_active_alerts()

    return {
        "alerts": [a.to_dict() for a in active],
        "total": len(active),
    }


@mcp.tool()
def clear_alert(host: str, metric: str) -> dict[str, Any]:
    """
    Clear an active alert.

    Args:
        host: Host name.
        metric: Metric type: "cpu", "memory", "disk", or "load".

    Returns:
        Dictionary with success status.
    """
    from sshmcp.monitoring.alerts import MetricType

    manager = get_alert_manager()
    metric_type = MetricType(metric.lower())
    cleared = manager.clear_alert(host, metric_type)

    return {
        "success": cleared,
        "message": f"Alert cleared for {host}:{metric}"
        if cleared
        else "Alert not found",
    }


# ============================================================================
# Directory Transfer Tools
# ============================================================================

# Store active transfers for progress tracking
_active_transfers: dict[str, dict] = {}


@mcp.tool()
def upload_directory(
    host: str,
    local_path: str,
    remote_path: str,
    exclude_patterns: list[str] | None = None,
    delete_extra: bool = False,
) -> dict[str, Any]:
    """
    Upload a local directory to remote server via SFTP.

    Recursively uploads all files from local directory to remote.
    Similar to rsync for uploading.

    Args:
        host: Name of the host.
        local_path: Local directory path to upload.
        remote_path: Remote destination path.
        exclude_patterns: Glob patterns to exclude (e.g., ["*.pyc", "__pycache__"]).
        delete_extra: Delete files on remote that don't exist locally (sync mode).

    Returns:
        Dictionary with transfer results including files transferred and errors.
    """
    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient
    from sshmcp.ssh.transfer import DirectoryTransfer

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    try:
        transfer = DirectoryTransfer(client)
        progress = transfer.upload_directory(
            local_path=local_path,
            remote_path=remote_path,
            exclude_patterns=exclude_patterns,
            delete_extra=delete_extra,
        )

        return {
            "success": len(progress.errors) == 0,
            "host": host,
            "local_path": local_path,
            "remote_path": remote_path,
            "files_transferred": progress.transferred_files,
            "bytes_transferred": progress.transferred_bytes,
            "errors": progress.errors,
        }
    finally:
        client.disconnect()


@mcp.tool()
def download_directory(
    host: str,
    remote_path: str,
    local_path: str,
    exclude_patterns: list[str] | None = None,
    delete_extra: bool = False,
) -> dict[str, Any]:
    """
    Download a remote directory to local system via SFTP.

    Recursively downloads all files from remote directory to local.
    Similar to rsync for downloading.

    Args:
        host: Name of the host.
        remote_path: Remote directory path to download.
        local_path: Local destination path.
        exclude_patterns: Glob patterns to exclude.
        delete_extra: Delete local files that don't exist on remote (sync mode).

    Returns:
        Dictionary with transfer results.
    """
    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient
    from sshmcp.ssh.transfer import DirectoryTransfer

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    try:
        transfer = DirectoryTransfer(client)
        progress = transfer.download_directory(
            remote_path=remote_path,
            local_path=local_path,
            exclude_patterns=exclude_patterns,
            delete_extra=delete_extra,
        )

        return {
            "success": len(progress.errors) == 0,
            "host": host,
            "remote_path": remote_path,
            "local_path": local_path,
            "files_transferred": progress.transferred_files,
            "bytes_transferred": progress.transferred_bytes,
            "errors": progress.errors,
        }
    finally:
        client.disconnect()


@mcp.tool()
def sync_directory(
    host: str,
    source_path: str,
    dest_path: str,
    direction: str = "upload",
    exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """
    Synchronize directories between local and remote (rsync-like).

    Syncs files and removes extra files on destination.

    Args:
        host: Name of the host.
        source_path: Source directory path.
        dest_path: Destination directory path.
        direction: "upload" (local->remote) or "download" (remote->local).
        exclude_patterns: Glob patterns to exclude from sync.

    Returns:
        Dictionary with sync results.
    """
    if direction == "upload":
        return upload_directory(
            host=host,
            local_path=source_path,
            remote_path=dest_path,
            exclude_patterns=exclude_patterns,
            delete_extra=True,
        )
    elif direction == "download":
        return download_directory(
            host=host,
            remote_path=source_path,
            local_path=dest_path,
            exclude_patterns=exclude_patterns,
            delete_extra=True,
        )
    else:
        return {
            "success": False,
            "error": f"Invalid direction: {direction}. Use 'upload' or 'download'.",
        }


# ============================================================================
# Port Forwarding Tools
# ============================================================================

# Store active port forwards
_active_forwards: dict[str, Any] = {}
_forward_counter = 0


@mcp.tool()
def forward_local(
    host: str,
    local_port: int,
    remote_host: str,
    remote_port: int,
    local_bind: str = "127.0.0.1",
) -> dict[str, Any]:
    """
    Create a local port forward (SSH tunnel).

    Forwards connections from local_port to remote_host:remote_port via SSH.
    Use case: Access a database on remote server through SSH tunnel.

    Example: forward_local("prod", 5433, "localhost", 5432)
    Then connect to localhost:5433 to reach remote PostgreSQL.

    Args:
        host: SSH host to tunnel through.
        local_port: Local port to listen on.
        remote_host: Target host (from SSH server's perspective).
        remote_port: Target port on remote_host.
        local_bind: Local address to bind (default: 127.0.0.1).

    Returns:
        Dictionary with forward_id and connection details.
    """
    global _forward_counter
    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient
    from sshmcp.ssh.forwarding import LocalForwarder

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    forwarder = LocalForwarder(
        ssh_client=client,
        local_port=local_port,
        remote_host=remote_host,
        remote_port=remote_port,
        local_bind=local_bind,
    )
    forwarder.start()

    _forward_counter += 1
    forward_id = f"local-{_forward_counter}"

    _active_forwards[forward_id] = {
        "type": "local",
        "forwarder": forwarder,
        "client": client,
        "host": host,
        "local_bind": local_bind,
        "local_port": local_port,
        "remote_host": remote_host,
        "remote_port": remote_port,
    }

    return {
        "success": True,
        "forward_id": forward_id,
        "type": "local",
        "local": f"{local_bind}:{local_port}",
        "remote": f"{remote_host}:{remote_port}",
        "via": host,
        "hint": f"Connect to {local_bind}:{local_port} to reach {remote_host}:{remote_port}",
    }


@mcp.tool()
def forward_remote(
    host: str,
    remote_port: int,
    local_host: str = "127.0.0.1",
    local_port: int = 0,
    remote_bind: str = "127.0.0.1",
) -> dict[str, Any]:
    """
    Create a remote port forward (reverse SSH tunnel).

    Forwards connections from remote_port on SSH server to local_host:local_port.
    Use case: Expose a local service to the remote server.

    Example: forward_remote("prod", 8080, "localhost", 3000)
    Then access localhost:8080 on prod server to reach your local port 3000.

    Args:
        host: SSH host to create reverse tunnel on.
        remote_port: Remote port to listen on.
        local_host: Local host to forward to (default: 127.0.0.1).
        local_port: Local port to forward to (default: same as remote_port).
        remote_bind: Remote address to bind (default: 127.0.0.1).

    Returns:
        Dictionary with forward_id and connection details.
    """
    global _forward_counter
    from sshmcp.config import get_machine
    from sshmcp.ssh.client import SSHClient
    from sshmcp.ssh.forwarding import RemoteForwarder

    machine = get_machine(host)
    client = SSHClient(machine)
    client.connect()

    forwarder = RemoteForwarder(
        ssh_client=client,
        remote_port=remote_port,
        local_host=local_host,
        local_port=local_port or remote_port,
        remote_bind=remote_bind,
    )
    forwarder.start()

    _forward_counter += 1
    forward_id = f"remote-{_forward_counter}"

    _active_forwards[forward_id] = {
        "type": "remote",
        "forwarder": forwarder,
        "client": client,
        "host": host,
        "remote_bind": remote_bind,
        "remote_port": remote_port,
        "local_host": local_host,
        "local_port": local_port or remote_port,
    }

    return {
        "success": True,
        "forward_id": forward_id,
        "type": "remote",
        "remote": f"{remote_bind}:{remote_port}",
        "local": f"{local_host}:{local_port or remote_port}",
        "on": host,
        "hint": f"Access {remote_bind}:{remote_port} on {host} to reach local {local_host}:{local_port or remote_port}",
    }


@mcp.tool()
def list_forwards() -> dict[str, Any]:
    """
    List all active port forwards.

    Returns:
        Dictionary with list of active forwards.
    """
    forwards = []
    for fwd_id, info in _active_forwards.items():
        if info["type"] == "local":
            forwards.append(
                {
                    "forward_id": fwd_id,
                    "type": "local",
                    "local": f"{info['local_bind']}:{info['local_port']}",
                    "remote": f"{info['remote_host']}:{info['remote_port']}",
                    "via": info["host"],
                }
            )
        else:
            forwards.append(
                {
                    "forward_id": fwd_id,
                    "type": "remote",
                    "remote": f"{info['remote_bind']}:{info['remote_port']}",
                    "local": f"{info['local_host']}:{info['local_port']}",
                    "on": info["host"],
                }
            )

    return {
        "forwards": forwards,
        "total": len(forwards),
    }


@mcp.tool()
def close_forward(forward_id: str) -> dict[str, Any]:
    """
    Close an active port forward.

    Args:
        forward_id: ID of the forward to close (from forward_local/forward_remote).

    Returns:
        Dictionary with success status.
    """
    if forward_id not in _active_forwards:
        return {
            "success": False,
            "error": f"Forward not found: {forward_id}",
        }

    info = _active_forwards.pop(forward_id)
    info["forwarder"].stop()
    info["client"].disconnect()

    return {
        "success": True,
        "message": f"Forward {forward_id} closed",
    }


# ============================================================================
# MCP Resources
# ============================================================================


@mcp.resource("vps://{host}/logs/{log_path}")
def resource_logs(host: str, log_path: str) -> str:
    """
    Get logs from VPS server.

    URI pattern: vps://{host}/logs/{log_path}
    Example: vps://production-server/logs/var/log/app.log

    Args:
        host: Name of the host.
        log_path: Path to log file (without leading slash).

    Returns:
        Log content as string.
    """
    return _get_logs(host, log_path)


@mcp.resource("vps://{host}/metrics")
def resource_metrics(host: str) -> str:
    """
    Get system metrics from VPS server.

    URI pattern: vps://{host}/metrics
    Example: vps://production-server/metrics

    Args:
        host: Name of the host.

    Returns:
        JSON string with CPU, memory, disk, uptime metrics.
    """
    import json

    metrics = _get_metrics(host)
    return json.dumps(metrics, indent=2)


@mcp.resource("vps://{host}/status")
def resource_status(host: str) -> str:
    """
    Get status of VPS server.

    URI pattern: vps://{host}/status
    Example: vps://production-server/status

    Args:
        host: Name of the host.

    Returns:
        JSON string with server status information.
    """
    import json

    status = _get_status(host)
    return json.dumps(status, indent=2)


# ============================================================================
# MCP Prompts
# ============================================================================


@mcp.prompt()
def deploy_app(
    host: str,
    branch: str = "main",
    app_path: str = "/var/www/app",
    package_manager: str = "npm",
    process_manager: str = "pm2",
    app_name: str = "app",
) -> str:
    """
    Generate deployment prompt for application.

    Creates a step-by-step deployment plan.

    Args:
        host: Target host name.
        branch: Git branch to deploy (default: main).
        app_path: Application directory path.
        package_manager: Package manager (npm, yarn, pip).
        process_manager: Process manager (pm2, systemd, supervisor).
        app_name: Application name for process manager.

    Returns:
        Deployment instructions.
    """
    return _deploy_app(
        host, branch, app_path, package_manager, process_manager, app_name
    )


@mcp.prompt()
def backup_database(
    host: str,
    database_name: str,
    database_type: str = "postgresql",
    backup_path: str = "/var/backups",
    compress: bool = True,
) -> str:
    """
    Generate database backup prompt.

    Creates a step-by-step backup plan.

    Args:
        host: Target host name.
        database_name: Name of the database to backup.
        database_type: Database type (postgresql, mysql, mongodb).
        backup_path: Directory for backup files.
        compress: Whether to compress the backup.

    Returns:
        Backup instructions.
    """
    return _backup_database(host, database_name, database_type, backup_path, compress)


@mcp.prompt()
def monitor_health(
    host: str,
    check_logs: bool = True,
    check_services: bool = True,
) -> str:
    """
    Generate health monitoring prompt.

    Creates a comprehensive health check plan.

    Args:
        host: Target host name.
        check_logs: Whether to check log files for errors.
        check_services: Whether to check service statuses.

    Returns:
        Monitoring instructions.
    """
    return _monitor_health(host, check_logs, check_services)


# ============================================================================
# Server Initialization
# ============================================================================


def initialize_server(config_path: str | None = None) -> None:
    """
    Initialize the MCP server with configuration.

    Args:
        config_path: Optional path to configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_path)

        # Initialize connection pool
        init_pool(config)

        # Initialize whitelist
        init_whitelist(config)

        # Initialize audit logger
        audit_log_path = os.environ.get("SSHMCP_AUDIT_LOG")
        init_audit_logger(log_file=audit_log_path)

        logger.info(
            "server_initialized",
            machines=config.get_machine_names(),
        )

    except ConfigurationError as e:
        logger.error("server_init_failed", error=str(e))
        raise


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="SSH MCP Server - Manage VPS servers via MCP protocol"
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to machines.json configuration file",
        default=None,
    )
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)",
    )

    args = parser.parse_args()

    # Set config path from argument or environment
    if args.config:
        os.environ["SSHMCP_CONFIG_PATH"] = args.config

    try:
        # Initialize server
        initialize_server(args.config)

        # Run MCP server
        logger.info(
            "server_starting",
            transport=args.transport,
        )

        if args.transport == "stdio":
            mcp.run(transport="stdio")
        elif args.transport == "sse":
            # SSE transport for web integration
            mcp.run(transport="sse")
        else:
            # Streamable HTTP for production
            mcp.run(transport="streamable-http")

    except ConfigurationError as e:
        logger.error("configuration_error", error=str(e))
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("server_stopped", reason="keyboard_interrupt")
    except Exception as e:
        logger.error("server_error", error=str(e))
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
