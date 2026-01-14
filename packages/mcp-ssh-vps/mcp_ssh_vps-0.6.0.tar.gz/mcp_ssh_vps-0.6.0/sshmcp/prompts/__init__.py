"""MCP Prompts for common VPS tasks."""

from sshmcp.prompts.backup import backup_database
from sshmcp.prompts.deploy import deploy_app
from sshmcp.prompts.monitor import monitor_health

__all__ = ["deploy_app", "backup_database", "monitor_health"]
