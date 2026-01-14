"""Pydantic models for file operations."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Information about a file on remote server."""

    name: str = Field(description="File name")
    path: str = Field(description="Full path to file")
    type: Literal["file", "directory", "link", "other"] = Field(description="File type")
    size: int = Field(ge=0, description="File size in bytes")
    modified: datetime = Field(description="Last modification time")
    permissions: str | None = Field(
        default=None, description="File permissions (e.g., '0644')"
    )
    owner: str | None = Field(default=None, description="File owner")
    group: str | None = Field(default=None, description="File group")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        result = {
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "size": self.size,
            "modified": self.modified.isoformat(),
        }
        if self.permissions:
            result["permissions"] = self.permissions
        if self.owner:
            result["owner"] = self.owner
        if self.group:
            result["group"] = self.group
        return result


class FileContent(BaseModel):
    """Content of a file from remote server."""

    content: str = Field(description="File content")
    path: str = Field(description="Full path to file")
    size: int = Field(ge=0, description="File size in bytes")
    encoding: str = Field(default="utf-8", description="File encoding")
    truncated: bool = Field(
        default=False, description="Whether content was truncated due to size limit"
    )
    host: str = Field(description="Host where file is located")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "content": self.content,
            "path": self.path,
            "size": self.size,
            "encoding": self.encoding,
            "truncated": self.truncated,
            "host": self.host,
        }


class FileUploadResult(BaseModel):
    """Result of file upload operation."""

    success: bool = Field(description="Whether upload was successful")
    path: str = Field(description="Path where file was uploaded")
    size: int = Field(ge=0, description="Uploaded file size in bytes")
    host: str = Field(description="Host where file was uploaded")
    message: str | None = Field(default=None, description="Additional message")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        result = {
            "success": self.success,
            "path": self.path,
            "size": self.size,
            "host": self.host,
        }
        if self.message:
            result["message"] = self.message
        return result


class FileListResult(BaseModel):
    """Result of listing files in directory."""

    files: list[FileInfo] = Field(description="List of files")
    directory: str = Field(description="Listed directory path")
    host: str = Field(description="Host where files are located")
    total_count: int = Field(ge=0, description="Total number of files")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "files": [f.to_dict() for f in self.files],
            "directory": self.directory,
            "host": self.host,
            "total_count": self.total_count,
        }
