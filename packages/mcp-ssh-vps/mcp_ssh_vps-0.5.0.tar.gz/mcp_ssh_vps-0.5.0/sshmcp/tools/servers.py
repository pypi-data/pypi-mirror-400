"""MCP Tools for server management."""

import json
import os
from pathlib import Path
from typing import Any

import structlog

from sshmcp.config import reload_config as reload_global_config
from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    MachinesConfig,
    SecurityConfig,
)
from sshmcp.security.whitelist import init_whitelist
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()

DEFAULT_CONFIG_PATH = Path.home() / ".sshmcp" / "machines.json"


def _get_config_path() -> Path:
    """Get configuration file path."""
    env_path = os.environ.get("SSHMCP_CONFIG_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_CONFIG_PATH


def _load_config() -> MachinesConfig:
    """Load machines configuration."""
    config_path = _get_config_path()
    if not config_path.exists():
        return MachinesConfig(machines=[])

    with open(config_path, "r") as f:
        data = json.load(f)
    return MachinesConfig.model_validate(data)


def _save_config(config: MachinesConfig) -> None:
    """Save machines configuration."""
    config_path = _get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def list_servers(tag: str | None = None) -> dict[str, Any]:
    """
    List all configured VPS servers.

    Returns a list of all servers with their basic information.
    Use this to see what servers are available for commands.

    Args:
        tag: Optional tag to filter servers. Only servers with this tag will be returned.

    Returns:
        Dictionary with:
        - servers: List of server info (name, host, user, description, tags)
        - count: Total number of servers (after filtering)
        - all_tags: List of all available tags
        - config_path: Path to configuration file

    Example:
        >>> list_servers()
        {"servers": [{"name": "prod", "host": "1.2.3.4", ...}], "count": 1}

        >>> list_servers(tag="production")
        {"servers": [...], "count": 2, "filter": "production"}
    """
    config = _load_config()

    # Collect all tags
    all_tags = set()
    for machine in config.machines:
        if machine.tags:
            all_tags.update(machine.tags)

    servers = []
    for machine in config.machines:
        # Filter by tag if specified
        if tag and tag not in (machine.tags or []):
            continue

        servers.append(
            {
                "name": machine.name,
                "host": machine.host,
                "port": machine.port,
                "user": machine.user,
                "description": machine.description,
                "auth_type": machine.auth.type,
                "tags": machine.tags or [],
                "security_level": "full"
                if ".*" in machine.security.allowed_commands
                else "restricted",
            }
        )

    result = {
        "servers": servers,
        "count": len(servers),
        "all_tags": sorted(all_tags),
        "config_path": str(_get_config_path()),
    }

    if tag:
        result["filter"] = f"tag:{tag}"

    return result


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

    Adds a new server that can be used with execute_command and other tools.

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
        tags: List of tags for grouping servers (e.g., ["production", "web"]).

    Returns:
        Dictionary with success status and server details.

    Example:
        >>> add_server("prod", "192.168.1.100", "deploy", tags=["production"])
        {"success": true, "name": "prod", "message": "Server added"}
    """
    config = _load_config()

    # Check if already exists
    if config.has_machine(name):
        return {
            "success": False,
            "error": f"Server '{name}' already exists",
            "hint": "Use a different name or remove the existing server first",
        }

    # Validate auth
    if auth_type == "key":
        auth = AuthConfig(type="key", key_path=key_path)
    elif auth_type == "password":
        if not password:
            return {
                "success": False,
                "error": "Password required for password authentication",
            }
        auth = AuthConfig(type="password", password=password)
    else:
        return {
            "success": False,
            "error": f"Invalid auth_type: {auth_type}. Use 'key' or 'password'",
        }

    # Security profiles
    security_profiles = {
        "strict": SecurityConfig(
            allowed_commands=[
                r"^git (pull|status|log|diff).*",
                r"^ls .*",
                r"^cat .*",
                r"^tail .*",
                r"^head .*",
                r"^pwd$",
                r"^whoami$",
                r"^df -h$",
                r"^free -m$",
                r"^uptime$",
            ],
            forbidden_commands=[
                r".*rm\s+-rf.*",
                r".*sudo.*",
                r".*su\s+-.*",
            ],
            timeout_seconds=30,
        ),
        "moderate": SecurityConfig(
            allowed_commands=[
                r"^git .*",
                r"^npm .*",
                r"^yarn .*",
                r"^pip .*",
                r"^pm2 .*",
                r"^systemctl .*",
                r"^docker .*",
                r"^ls .*",
                r"^cat .*",
                r"^tail .*",
                r"^head .*",
                r"^pwd$",
                r"^whoami$",
                r"^df -h$",
                r"^free -m$",
                r"^uptime$",
                r"^ps aux$",
                r"^top -bn1$",
            ],
            forbidden_commands=[
                r".*rm\s+-rf\s+/.*",
                r".*sudo\s+rm.*",
            ],
            timeout_seconds=60,
        ),
        "full": SecurityConfig(
            allowed_commands=[r".*"],
            forbidden_commands=[r".*rm\s+-rf\s+/$"],
            timeout_seconds=120,
        ),
    }

    if security_level not in security_profiles:
        return {
            "success": False,
            "error": f"Invalid security_level: {security_level}",
            "valid_options": list(security_profiles.keys()),
        }

    security = security_profiles[security_level]

    try:
        machine = MachineConfig(
            name=name,
            host=host,
            port=port,
            user=user,
            auth=auth,
            security=security,
            description=description,
            tags=tags or [],
        )

        config.machines.append(machine)
        _save_config(config)

        # Reload global config cache so get_machine() finds the new server
        reload_global_config()

        # Register in connection pool immediately
        pool = get_pool()
        pool.register_machine(machine)
        init_whitelist(MachinesConfig(machines=[machine]))

        logger.info("server_added", name=name, host=host)

        return {
            "success": True,
            "name": name,
            "host": host,
            "user": user,
            "port": port,
            "auth_type": auth_type,
            "security_level": security_level,
            "tags": tags or [],
            "message": f"Server '{name}' added successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def remove_server(name: str) -> dict[str, Any]:
    """
    Remove a VPS server from the configuration.

    Args:
        name: Name of the server to remove.

    Returns:
        Dictionary with success status.

    Example:
        >>> remove_server("old-server")
        {"success": true, "message": "Server removed"}
    """
    config = _load_config()

    if not config.has_machine(name):
        return {
            "success": False,
            "error": f"Server '{name}' not found",
            "available_servers": config.get_machine_names(),
        }

    config.machines = [m for m in config.machines if m.name != name]
    _save_config(config)
    reload_global_config()

    logger.info("server_removed", name=name)

    return {
        "success": True,
        "name": name,
        "message": f"Server '{name}' removed successfully",
        "remaining_servers": config.get_machine_names(),
    }


def test_server_connection(name: str) -> dict[str, Any]:
    """
    Test SSH connection to a server.

    Attempts to connect and run a simple command to verify the server is accessible.

    Args:
        name: Name of the server to test.

    Returns:
        Dictionary with connection status and details.

    Example:
        >>> test_server_connection("prod")
        {"success": true, "hostname": "server1", "message": "Connection OK"}
    """
    config = _load_config()

    machine = config.get_machine(name)
    if not machine:
        return {
            "success": False,
            "error": f"Server '{name}' not found",
            "available_servers": config.get_machine_names(),
        }

    try:
        from sshmcp.ssh.client import SSHClient

        client = SSHClient(machine)
        client.connect()

        # Run test commands
        result = client.execute("hostname && uptime")
        client.disconnect()

        if result.exit_code == 0:
            lines = result.stdout.strip().split("\n")
            hostname = lines[0] if lines else "unknown"

            return {
                "success": True,
                "name": name,
                "hostname": hostname,
                "host": machine.host,
                "output": result.stdout,
                "message": "Connection successful",
            }
        else:
            return {
                "success": False,
                "name": name,
                "error": "Command failed",
                "stderr": result.stderr,
            }

    except Exception as e:
        return {
            "success": False,
            "name": name,
            "error": str(e),
            "message": "Connection failed",
        }


def update_server(
    name: str,
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    description: str | None = None,
    security_level: str | None = None,
) -> dict[str, Any]:
    """
    Update an existing server's configuration.

    Only specified fields will be updated.

    Args:
        name: Name of the server to update.
        host: New hostname or IP (optional).
        user: New SSH username (optional).
        port: New SSH port (optional).
        description: New description (optional).
        security_level: New security level (optional).

    Returns:
        Dictionary with update status.

    Example:
        >>> update_server("prod", host="10.0.0.1")
        {"success": true, "message": "Server updated"}
    """
    config = _load_config()

    machine = config.get_machine(name)
    if not machine:
        return {
            "success": False,
            "error": f"Server '{name}' not found",
        }

    # Find and update
    for i, m in enumerate(config.machines):
        if m.name == name:
            if host:
                config.machines[i].host = host
            if user:
                config.machines[i].user = user
            if port:
                config.machines[i].port = port
            if description is not None:
                config.machines[i].description = description

            if security_level:
                security_profiles = {
                    "strict": SecurityConfig(
                        allowed_commands=[r"^git.*", r"^ls.*", r"^cat.*"],
                        forbidden_commands=[r".*rm\s+-rf.*", r".*sudo.*"],
                        timeout_seconds=30,
                    ),
                    "moderate": SecurityConfig(
                        allowed_commands=[
                            r"^git.*",
                            r"^npm.*",
                            r"^pm2.*",
                            r"^docker.*",
                        ],
                        forbidden_commands=[r".*rm\s+-rf\s+/.*"],
                        timeout_seconds=60,
                    ),
                    "full": SecurityConfig(
                        allowed_commands=[r".*"],
                        forbidden_commands=[r".*rm\s+-rf\s+/$"],
                        timeout_seconds=120,
                    ),
                }
                if security_level in security_profiles:
                    config.machines[i].security = security_profiles[security_level]

            break

    _save_config(config)
    reload_global_config()

    # Re-register in pool with updated config
    pool = get_pool()
    for m in config.machines:
        if m.name == name:
            pool.register_machine(m)
            init_whitelist(MachinesConfig(machines=[m]))
            break

    return {
        "success": True,
        "name": name,
        "message": f"Server '{name}' updated",
    }
