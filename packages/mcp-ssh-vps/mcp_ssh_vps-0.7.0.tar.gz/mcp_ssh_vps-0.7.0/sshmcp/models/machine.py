"""Pydantic models for machine configuration."""

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AuthConfig(BaseModel):
    """Authentication configuration for SSH connection."""

    type: Literal["key", "password", "agent"] = Field(
        description="Authentication type: 'key' for SSH key, 'password' for password, 'agent' for SSH agent"
    )
    key_path: str | None = Field(
        default=None, description="Path to SSH private key file"
    )
    passphrase: str | None = Field(
        default=None, description="Passphrase for encrypted SSH key"
    )
    password: str | None = Field(
        default=None, description="Password for password authentication"
    )
    agent_forwarding: bool = Field(
        default=False, description="Enable SSH agent forwarding"
    )

    @field_validator("key_path")
    @classmethod
    def expand_key_path(cls, v: str | None) -> str | None:
        """Expand ~ in key path."""
        if v:
            return os.path.expanduser(v)
        return v

    def model_post_init(self, __context: object) -> None:
        """Validate that required fields are present based on auth type."""
        if self.type == "key" and not self.key_path:
            raise ValueError("key_path is required when auth type is 'key'")
        if self.type == "password" and not self.password:
            raise ValueError("password is required when auth type is 'password'")
        # 'agent' type doesn't require additional fields


class SecurityConfig(BaseModel):
    """Security configuration for command execution."""

    allowed_commands: list[str] = Field(
        default_factory=list,
        description="List of regex patterns for allowed commands",
    )
    forbidden_commands: list[str] = Field(
        default_factory=lambda: [
            r".*rm\s+-rf\s+/.*",
            r".*sudo\s+.*",
            r".*su\s+-.*",
            r".*dd\s+if=.*",
            r".*mkfs\..*",
            r".*:\(\)\{.*",  # Fork bomb
        ],
        description="List of regex patterns for forbidden commands",
    )
    timeout_seconds: int = Field(
        default=30, ge=1, le=3600, description="Command timeout in seconds"
    )
    max_concurrent_commands: int = Field(
        default=3, ge=1, le=10, description="Maximum concurrent commands per machine"
    )
    allowed_paths: list[str] = Field(
        default_factory=list,
        description="List of allowed file paths for read/write operations",
    )
    forbidden_paths: list[str] = Field(
        default_factory=lambda: [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/root",
            "~/.ssh",
        ],
        description="List of forbidden file paths",
    )


class MachineConfig(BaseModel):
    """Configuration for a VPS machine."""

    name: str = Field(
        min_length=1, max_length=64, description="Unique name for the machine"
    )
    host: str = Field(min_length=1, description="Hostname or IP address")
    port: int = Field(default=22, ge=1, le=65535, description="SSH port")
    user: str = Field(min_length=1, description="SSH username")
    auth: AuthConfig = Field(description="Authentication configuration")
    security: SecurityConfig = Field(
        default_factory=SecurityConfig, description="Security configuration"
    )
    description: str | None = Field(
        default=None, description="Optional description of the machine"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for grouping and filtering servers (e.g., ['production', 'web'])",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate machine name contains only safe characters."""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Machine name must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v


class MachinesConfig(BaseModel):
    """Root configuration containing all machines."""

    machines: list[MachineConfig] = Field(
        default_factory=list, description="List of configured machines"
    )

    def get_machine(self, name: str) -> MachineConfig | None:
        """Get machine by name."""
        for machine in self.machines:
            if machine.name == name:
                return machine
        return None

    def has_machine(self, name: str) -> bool:
        """Check if machine exists."""
        return self.get_machine(name) is not None

    def get_machine_names(self) -> list[str]:
        """Get list of all machine names."""
        return [m.name for m in self.machines]
