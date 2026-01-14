"""MCP Tools for help and information."""

from typing import Any

from sshmcp.config import get_machine, list_machines


def get_help(topic: str | None = None) -> dict[str, Any]:
    """
    Get help information about available commands and features.

    Provides documentation about tools, security profiles, and usage examples.

    Args:
        topic: Specific topic to get help for. Options:
               - "tools" - list all available MCP tools
               - "security" - security profiles and allowed commands
               - "servers" - server management commands
               - "examples" - usage examples
               - None - general overview

    Returns:
        Dictionary with help information.

    Example:
        >>> get_help("tools")
        {"topic": "tools", "content": "Available tools: ..."}
    """
    help_topics = {
        "tools": {
            "topic": "Available MCP Tools",
            "tools": [
                {
                    "name": "execute_command",
                    "description": "Execute shell command on remote server",
                    "args": "host (str), command (str), timeout (int, optional)",
                    "example": 'execute_command("prod", "docker ps -a")',
                },
                {
                    "name": "execute_on_multiple",
                    "description": "Execute command on multiple servers",
                    "args": "hosts (list[str]), command (str)",
                    "example": 'execute_on_multiple(["prod", "staging"], "uptime")',
                },
                {
                    "name": "list_servers",
                    "description": "List all configured servers",
                    "args": "tag (str, optional) - filter by tag",
                    "example": "list_servers() or list_servers(tag='production')",
                },
                {
                    "name": "add_server",
                    "description": "Add new VPS server",
                    "args": "name, host, user, port, auth_type, key_path/password, tags",
                    "example": 'add_server("web1", "1.2.3.4", "root", tags=["production"])',
                },
                {
                    "name": "remove_server",
                    "description": "Remove server from configuration",
                    "args": "name (str)",
                    "example": 'remove_server("old-server")',
                },
                {
                    "name": "test_connection",
                    "description": "Test SSH connection to server",
                    "args": "name (str)",
                    "example": 'test_connection("prod")',
                },
                {
                    "name": "get_allowed_commands",
                    "description": "Get list of allowed commands for a server",
                    "args": "host (str)",
                    "example": 'get_allowed_commands("prod")',
                },
                {
                    "name": "read_file",
                    "description": "Read file content from remote server",
                    "args": "host (str), path (str), max_size (int, optional)",
                    "example": 'read_file("prod", "/var/log/app.log")',
                },
                {
                    "name": "upload_file",
                    "description": "Upload file to remote server",
                    "args": "host (str), remote_path (str), content (str)",
                    "example": 'upload_file("prod", "/tmp/script.sh", "#!/bin/bash\\necho hi")',
                },
                {
                    "name": "list_files",
                    "description": "List files in directory on remote server",
                    "args": "host (str), directory (str), recursive (bool)",
                    "example": 'list_files("prod", "/var/log")',
                },
                {
                    "name": "manage_process",
                    "description": "Manage processes (systemd/pm2/supervisor)",
                    "args": "host (str), action (start/stop/restart/status), process_name",
                    "example": 'manage_process("prod", "restart", "nginx")',
                },
            ],
        },
        "security": {
            "topic": "Security Profiles",
            "profiles": [
                {
                    "name": "strict",
                    "description": "Only safe read-only commands",
                    "allowed": [
                        "git pull/status",
                        "ls",
                        "cat",
                        "tail",
                        "df",
                        "free",
                        "uptime",
                    ],
                    "forbidden": ["rm -rf", "sudo", "su -"],
                    "timeout": 30,
                },
                {
                    "name": "moderate",
                    "description": "Standard DevOps commands",
                    "allowed": [
                        "git",
                        "npm",
                        "yarn",
                        "pip",
                        "pm2",
                        "systemctl",
                        "docker",
                        "ls",
                        "cat",
                        "ps",
                        "top",
                    ],
                    "forbidden": ["rm -rf /", "sudo rm"],
                    "timeout": 60,
                },
                {
                    "name": "full",
                    "description": "All commands allowed",
                    "allowed": ["ALL commands"],
                    "forbidden": ["rm -rf /"],
                    "timeout": 120,
                },
            ],
            "note": "Use security_level parameter when adding servers: add_server(..., security_level='full')",
        },
        "servers": {
            "topic": "Server Management",
            "commands": [
                "list_servers() - List all servers",
                "list_servers(tag='prod') - Filter by tag",
                "add_server(name, host, user, ...) - Add new server",
                "remove_server(name) - Remove server",
                "update_server(name, ...) - Update server settings",
                "test_connection(name) - Test SSH connection",
            ],
            "tips": [
                "Use tags to organize servers: tags=['production', 'web']",
                "Test connection after adding: test_connection('server-name')",
                "Use security_level='full' for unrestricted access",
            ],
        },
        "examples": {
            "topic": "Usage Examples",
            "examples": [
                {
                    "task": "Check server status",
                    "commands": [
                        'execute_command("prod", "uptime")',
                        'execute_command("prod", "df -h")',
                        'execute_command("prod", "free -m")',
                    ],
                },
                {
                    "task": "Docker management",
                    "commands": [
                        'execute_command("prod", "docker ps -a")',
                        'execute_command("prod", "docker logs nginx --tail 100")',
                        'execute_command("prod", "docker restart nginx")',
                    ],
                },
                {
                    "task": "Deploy application",
                    "commands": [
                        'execute_command("prod", "cd /app && git pull")',
                        'execute_command("prod", "cd /app && npm install")',
                        'execute_command("prod", "pm2 restart all")',
                    ],
                },
                {
                    "task": "Check logs",
                    "commands": [
                        'execute_command("prod", "tail -100 /var/log/nginx/error.log")',
                        'execute_command("prod", "journalctl -u nginx --since \'1 hour ago\'")',
                    ],
                },
                {
                    "task": "Run on multiple servers",
                    "commands": [
                        'execute_on_multiple(["web1", "web2", "web3"], "uptime")',
                        'execute_on_multiple(["prod", "staging"], "docker ps")',
                    ],
                },
            ],
        },
    }

    if topic is None:
        return {
            "topic": "SSH MCP Server Help",
            "description": "MCP server for managing VPS via SSH",
            "available_topics": list(help_topics.keys()),
            "usage": "Call get_help(topic) for detailed information",
            "quick_start": [
                "1. list_servers() - See available servers",
                "2. test_connection('server-name') - Test connection",
                "3. execute_command('server-name', 'uptime') - Run command",
            ],
        }

    if topic not in help_topics:
        return {
            "error": f"Unknown topic: {topic}",
            "available_topics": list(help_topics.keys()),
        }

    return help_topics[topic]


def get_allowed_commands(host: str) -> dict[str, Any]:
    """
    Get the list of allowed and forbidden commands for a server.

    Shows the security configuration including command patterns,
    timeout settings, and path restrictions.

    Args:
        host: Name of the server to check.

    Returns:
        Dictionary with security configuration details.

    Example:
        >>> get_allowed_commands("production")
        {"host": "production", "allowed": [".*"], "forbidden": ["rm -rf /"]}
    """
    try:
        machine = get_machine(host)
    except Exception:
        available = list_machines()
        return {
            "success": False,
            "error": f"Server '{host}' not found",
            "available_servers": available,
        }

    security = machine.security

    # Determine security level based on patterns
    if security.allowed_commands == [r".*"] or ".*" in security.allowed_commands:
        security_level = "full"
    elif len(security.allowed_commands) > 10:
        security_level = "moderate"
    else:
        security_level = "strict"

    return {
        "success": True,
        "host": host,
        "security_level": security_level,
        "allowed_commands": security.allowed_commands,
        "forbidden_commands": security.forbidden_commands,
        "timeout_seconds": security.timeout_seconds,
        "max_concurrent_commands": security.max_concurrent_commands,
        "allowed_paths": security.allowed_paths or ["all paths allowed"],
        "forbidden_paths": security.forbidden_paths or [],
        "tip": "Use update_server(name, security_level='full') to allow all commands",
    }


def get_server_info(host: str) -> dict[str, Any]:
    """
    Get detailed information about a server.

    Returns configuration details, security settings, and connection info.

    Args:
        host: Name of the server.

    Returns:
        Dictionary with server details.

    Example:
        >>> get_server_info("production")
        {"name": "production", "host": "1.2.3.4", "user": "deploy", ...}
    """
    try:
        machine = get_machine(host)
    except Exception:
        available = list_machines()
        return {
            "success": False,
            "error": f"Server '{host}' not found",
            "available_servers": available,
        }

    return {
        "success": True,
        "name": machine.name,
        "host": machine.host,
        "port": machine.port,
        "user": machine.user,
        "description": machine.description,
        "tags": getattr(machine, "tags", []),
        "auth_type": machine.auth.type,
        "security_level": "full"
        if ".*" in machine.security.allowed_commands
        else "restricted",
        "timeout_seconds": machine.security.timeout_seconds,
    }
