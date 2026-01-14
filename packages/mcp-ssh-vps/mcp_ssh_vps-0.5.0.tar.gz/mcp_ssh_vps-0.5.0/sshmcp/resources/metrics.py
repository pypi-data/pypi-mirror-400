"""MCP Resource for system metrics."""

import re

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def get_metrics(host: str) -> dict:
    """
    Get system metrics from VPS server.

    Returns CPU, memory, disk usage, and uptime information.

    Args:
        host: Name of the host from machines.json configuration.

    Returns:
        Dictionary with metrics:
        - cpu: CPU usage information
        - memory: Memory usage information
        - disk: Disk usage information
        - uptime_seconds: System uptime

    Raises:
        ValueError: If host not found.
        RuntimeError: If metrics cannot be retrieved.

    Example:
        Resource URI: vps://production-server/metrics
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        raise ValueError(f"Host not found: {host}") from e

    pool = get_pool()
    pool.register_machine(machine)

    metrics = {
        "cpu": {},
        "memory": {},
        "disk": {},
        "uptime_seconds": 0,
        "host": host,
    }

    try:
        client = pool.get_client(host)
        try:
            # Get CPU usage
            cpu_result = client.execute(
                "top -bn1 | head -5 | grep 'Cpu' || cat /proc/stat | head -1"
            )
            metrics["cpu"] = _parse_cpu(cpu_result.stdout)

            # Get memory usage
            mem_result = client.execute("free -m")
            metrics["memory"] = _parse_memory(mem_result.stdout)

            # Get disk usage
            disk_result = client.execute("df -h / | tail -1")
            metrics["disk"] = _parse_disk(disk_result.stdout)

            # Get uptime
            uptime_result = client.execute("cat /proc/uptime")
            metrics["uptime_seconds"] = _parse_uptime(uptime_result.stdout)

            # Get load average
            load_result = client.execute("cat /proc/loadavg")
            metrics["load_average"] = _parse_load(load_result.stdout)

            audit.log(
                event="metrics_read",
                host=host,
            )

            return metrics

        finally:
            pool.release_client(client)

    except Exception as e:
        raise RuntimeError(f"Failed to get metrics: {e}") from e


def _parse_cpu(output: str) -> dict:
    """Parse CPU usage from top or /proc/stat output."""
    cpu_info = {"usage_percent": 0.0, "cores": 1}

    try:
        # Try parsing top output
        if "Cpu" in output:
            # Format: %Cpu(s):  1.2 us,  0.3 sy,  0.0 ni, 98.5 id, ...
            match = re.search(r"(\d+\.?\d*)\s*id", output)
            if match:
                idle = float(match.group(1))
                cpu_info["usage_percent"] = round(100.0 - idle, 1)

        # Get CPU cores
        import os

        cpu_info["cores"] = os.cpu_count() or 1

    except Exception:
        pass

    return cpu_info


def _parse_memory(output: str) -> dict:
    """Parse memory usage from free -m output."""
    mem_info = {"used_mb": 0, "total_mb": 0, "usage_percent": 0.0, "available_mb": 0}

    try:
        lines = output.strip().split("\n")
        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()
                if len(parts) >= 4:
                    mem_info["total_mb"] = int(parts[1])
                    mem_info["used_mb"] = int(parts[2])
                    if len(parts) >= 7:
                        mem_info["available_mb"] = int(parts[6])
                    else:
                        mem_info["available_mb"] = (
                            mem_info["total_mb"] - mem_info["used_mb"]
                        )

                    if mem_info["total_mb"] > 0:
                        mem_info["usage_percent"] = round(
                            mem_info["used_mb"] / mem_info["total_mb"] * 100, 1
                        )
    except Exception:
        pass

    return mem_info


def _parse_disk(output: str) -> dict:
    """Parse disk usage from df -h output."""
    disk_info = {
        "used_gb": 0.0,
        "total_gb": 0.0,
        "usage_percent": 0.0,
        "available_gb": 0.0,
    }

    try:
        parts = output.split()
        if len(parts) >= 5:
            # Parse size with units (e.g., "50G", "1.2T")
            def parse_size(s: str) -> float:
                s = s.upper()
                multipliers = {"K": 1 / 1024 / 1024, "M": 1 / 1024, "G": 1, "T": 1024}
                for unit, mult in multipliers.items():
                    if unit in s:
                        return float(s.replace(unit, "")) * mult
                return float(s)

            disk_info["total_gb"] = round(parse_size(parts[1]), 1)
            disk_info["used_gb"] = round(parse_size(parts[2]), 1)
            disk_info["available_gb"] = round(parse_size(parts[3]), 1)
            disk_info["usage_percent"] = float(parts[4].replace("%", ""))

    except Exception:
        pass

    return disk_info


def _parse_uptime(output: str) -> int:
    """Parse uptime from /proc/uptime."""
    try:
        parts = output.strip().split()
        if parts:
            return int(float(parts[0]))
    except Exception:
        pass
    return 0


def _parse_load(output: str) -> dict:
    """Parse load average from /proc/loadavg."""
    load = {"1min": 0.0, "5min": 0.0, "15min": 0.0}

    try:
        parts = output.strip().split()
        if len(parts) >= 3:
            load["1min"] = float(parts[0])
            load["5min"] = float(parts[1])
            load["15min"] = float(parts[2])
    except Exception:
        pass

    return load
