"""Pydantic models for command execution results."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    """Result of command execution on remote server."""

    exit_code: int = Field(description="Command exit code (0 = success)")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error output")
    duration_ms: int = Field(ge=0, description="Execution duration in milliseconds")
    host: str = Field(description="Host where command was executed")
    command: str = Field(description="Executed command")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Execution timestamp"
    )

    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.exit_code == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "host": self.host,
            "command": self.command,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }


class CommandError(BaseModel):
    """Error details for failed command execution."""

    error_type: str = Field(description="Type of error")
    message: str = Field(description="Error message")
    host: str | None = Field(default=None, description="Host where error occurred")
    command: str | None = Field(default=None, description="Command that caused error")
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        result = {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.host:
            result["host"] = self.host
        if self.command:
            result["command"] = self.command
        if self.details:
            result["details"] = self.details
        return result
