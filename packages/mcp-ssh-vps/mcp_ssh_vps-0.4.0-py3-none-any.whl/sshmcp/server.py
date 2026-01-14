"""SSH MCP Server - Main entry point."""

import argparse
import os
import sys
from typing import Any

import structlog
from mcp.server.fastmcp import FastMCP

from sshmcp.config import ConfigurationError, get_config, load_config
from sshmcp.prompts.backup import backup_database as _backup_database
from sshmcp.prompts.deploy import deploy_app as _deploy_app
from sshmcp.prompts.monitor import monitor_health as _monitor_health
from sshmcp.resources.logs import get_logs as _get_logs
from sshmcp.resources.metrics import get_metrics as _get_metrics
from sshmcp.resources.status import get_status as _get_status
from sshmcp.security.audit import init_audit_logger
from sshmcp.security.whitelist import init_whitelist
from sshmcp.ssh.pool import init_pool
from sshmcp.tools.commands import execute_command as _execute_command
from sshmcp.tools.commands import execute_on_multiple as _execute_on_multiple
from sshmcp.tools.files import list_files as _list_files
from sshmcp.tools.files import read_file as _read_file
from sshmcp.tools.files import upload_file as _upload_file
from sshmcp.tools.helpers import get_allowed_commands as _get_allowed_commands
from sshmcp.tools.helpers import get_help as _get_help
from sshmcp.tools.helpers import get_server_info as _get_server_info
from sshmcp.tools.processes import manage_process as _manage_process
from sshmcp.tools.servers import add_server as _add_server
from sshmcp.tools.servers import list_servers as _list_servers
from sshmcp.tools.servers import remove_server as _remove_server
from sshmcp.tools.servers import test_server_connection as _test_server_connection

# Configure structured logging
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
    logger_factory=structlog.PrintLoggerFactory(),
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
        choices=["stdio", "streamable-http"],
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
        else:
            # Note: streamable-http uses default host/port
            # Custom host/port require uvicorn configuration
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
