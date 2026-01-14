"""MCP Resource for server status."""

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def get_status(host: str) -> dict:
    """
    Get status of VPS server.

    Returns server availability, hostname, and service statuses.

    Args:
        host: Name of the host from machines.json configuration.

    Returns:
        Dictionary with:
        - hostname: Server hostname
        - status: Server status (online/offline)
        - services: List of service statuses
        - system_info: Basic system information

    Raises:
        ValueError: If host not found.
        RuntimeError: If status cannot be retrieved.

    Example:
        Resource URI: vps://production-server/status
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    pool = get_pool()
    pool.register_machine(machine)

    status_info = {
        "hostname": "",
        "status": "unknown",
        "host": host,
        "services": [],
        "system_info": {},
    }

    try:
        client = pool.get_client(host)
        try:
            # Server is online if we can connect
            status_info["status"] = "online"

            # Get hostname
            hostname_result = client.execute("hostname")
            status_info["hostname"] = hostname_result.stdout.strip()

            # Get basic system info
            uname_result = client.execute("uname -a")
            status_info["system_info"]["uname"] = uname_result.stdout.strip()

            # Get OS info
            os_result = client.execute(
                "cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'"
            )
            if os_result.exit_code == 0 and os_result.stdout.strip():
                status_info["system_info"]["os"] = os_result.stdout.strip()

            # Get running services (try systemd first)
            services_result = client.execute(
                "systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | head -20"
            )

            if services_result.exit_code == 0 and services_result.stdout.strip():
                status_info["services"] = _parse_systemd_services(
                    services_result.stdout
                )
            else:
                # Try pm2
                pm2_result = client.execute("pm2 jlist 2>/dev/null")
                if pm2_result.exit_code == 0 and pm2_result.stdout.strip():
                    status_info["services"] = _parse_pm2_services(pm2_result.stdout)

            audit.log(
                event="status_read",
                host=host,
            )

            return status_info

        finally:
            pool.release_client(client)

    except Exception as e:
        # If we can't connect, server is offline
        status_info["status"] = "offline"
        status_info["error"] = str(e)

        audit.log(
            event="status_read_failed",
            host=host,
            error=str(e),
        )

        return status_info


def _parse_systemd_services(output: str) -> list[dict]:
    """Parse systemd services from systemctl output."""
    services = []

    for line in output.strip().split("\n"):
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) >= 1:
            service_name = parts[0]
            # Remove .service suffix
            if service_name.endswith(".service"):
                service_name = service_name[:-8]

            services.append(
                {
                    "name": service_name,
                    "status": "running",
                    "manager": "systemd",
                }
            )

    return services


def _parse_pm2_services(output: str) -> list[dict]:
    """Parse pm2 services from pm2 jlist output."""
    import json

    services = []

    try:
        data = json.loads(output)
        for app in data:
            services.append(
                {
                    "name": app.get("name", "unknown"),
                    "status": app.get("pm2_env", {}).get("status", "unknown"),
                    "manager": "pm2",
                    "pid": app.get("pid"),
                }
            )
    except json.JSONDecodeError:
        pass

    return services
