"""MCP Prompt for system monitoring."""


def monitor_health(
    host: str,
    check_logs: bool = True,
    check_services: bool = True,
    log_paths: list[str] | None = None,
    services: list[str] | None = None,
) -> str:
    """
    Generate health monitoring prompt.

    Creates a comprehensive health check plan for a server.

    Args:
        host: Target host name.
        check_logs: Whether to check log files for errors.
        check_services: Whether to check service statuses.
        log_paths: List of log file paths to check.
        services: List of services to check.

    Returns:
        Monitoring instructions as multi-line string.
    """
    default_logs = [
        "/var/log/syslog",
        "/var/log/nginx/error.log",
        "/var/log/app/error.log",
    ]
    default_services = ["nginx", "postgresql", "redis"]

    log_paths = log_paths or default_logs
    services = services or default_services

    logs_section = ""
    if check_logs:
        logs_section = """
## Log Analysis

Check for errors in application logs:
"""
        for log_path in log_paths:
            logs_section += f"""
### {log_path}
- Use get_logs resource for {host} with path "{log_path.lstrip("/")}" and filter_level="error"
- Or execute directly:
```
execute_command(host="{host}", command="tail -n 100 {log_path} | grep -iE 'error|fatal|critical' | tail -20")
```
"""

    services_section = ""
    if check_services:
        services_section = """
## Service Health

Check status of critical services:
"""
        for service in services:
            services_section += f"""
### {service}
```
manage_process(host="{host}", action="status", process_name="{service}")
```
"""

    return f"""Monitor health of {host}:

## System Metrics

1. Get current system metrics:
   - Use get_metrics resource for {host}
   - This provides CPU, memory, disk usage, and load average

2. Check for high resource usage:
   ```
   execute_command(host="{host}", command="top -bn1 | head -20")
   ```

3. Check disk space on all mounts:
   ```
   execute_command(host="{host}", command="df -h")
   ```

4. Check memory details:
   ```
   execute_command(host="{host}", command="free -m")
   ```

5. Check system load:
   ```
   execute_command(host="{host}", command="uptime")
   ```
{logs_section}{services_section}
## Network Health

Check network connectivity:
```
execute_command(host="{host}", command="netstat -tuln | head -20")
```

Check established connections:
```
execute_command(host="{host}", command="netstat -an | grep ESTABLISHED | wc -l")
```

## Recent System Events

Check dmesg for hardware/kernel issues:
```
execute_command(host="{host}", command="dmesg | tail -20")
```

Check authentication logs:
```
execute_command(host="{host}", command="tail -20 /var/log/auth.log")
```

## Health Report Summary

After running the above checks, summarize:

1. **System Resources**:
   - CPU usage: [X]%
   - Memory usage: [X]%
   - Disk usage: [X]%
   - Load average: [X]

2. **Services Status**:
   - List all checked services and their status

3. **Issues Found**:
   - List any errors from logs
   - List any services that are not running
   - List any resource usage concerns

4. **Recommendations**:
   - Based on findings, provide action items

## Thresholds to Watch
- CPU > 80%: High usage warning
- Memory > 85%: Memory pressure warning
- Disk > 90%: Disk space critical
- Load average > number of cores: System overloaded
"""
