"""MCP Resources for VPS data access."""

from sshmcp.resources.logs import get_logs
from sshmcp.resources.metrics import get_metrics
from sshmcp.resources.status import get_status

__all__ = ["get_logs", "get_metrics", "get_status"]
