"""Response formatter for AI agents.

Provides optimized response formatting to minimize token usage
while maintaining useful context for AI agents.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResponseFormat(str, Enum):
    """Response format options for tool outputs."""

    CONCISE = "concise"  # Minimal tokens, essential data only
    DETAILED = "detailed"  # Full data with IDs for chaining
    MARKDOWN = "markdown"  # Human-readable markdown format


@dataclass
class FormatterConfig:
    """Configuration for response formatting."""

    max_output_length: int = 10000
    max_lines: int = 200
    truncate_message: str = (
        "\n\n[Output truncated. Use filters or pagination for more specific results.]"
    )
    show_hints: bool = True


class ResponseFormatter:
    """Format tool responses for optimal AI agent consumption."""

    def __init__(self, config: FormatterConfig | None = None) -> None:
        self.config = config or FormatterConfig()

    def format_command_result(
        self,
        result: dict[str, Any],
        format: ResponseFormat = ResponseFormat.CONCISE,
    ) -> dict[str, Any]:
        """
        Format command execution result.

        Args:
            result: Raw command result dict.
            format: Output format.

        Returns:
            Formatted result dict.
        """
        if format == ResponseFormat.MARKDOWN:
            return self._command_to_markdown(result)
        elif format == ResponseFormat.CONCISE:
            return self._command_to_concise(result)
        else:  # DETAILED
            return self._truncate_dict(result)

    def _command_to_concise(self, result: dict[str, Any]) -> dict[str, Any]:
        """Minimal command result."""
        stdout = self._truncate_text(result.get("stdout", ""))
        stderr = self._truncate_text(result.get("stderr", ""))

        concise = {
            "success": result.get("exit_code", 1) == 0,
            "output": stdout if stdout else stderr,
        }

        # Add exit_code only if non-zero
        if result.get("exit_code", 0) != 0:
            concise["exit_code"] = result["exit_code"]

        # Add stderr only if different from output and non-empty
        if stderr and stderr != concise.get("output"):
            concise["error"] = stderr

        return concise

    def _command_to_markdown(self, result: dict[str, Any]) -> dict[str, Any]:
        """Markdown formatted command result."""
        exit_code = result.get("exit_code", 0)
        status = "✓" if exit_code == 0 else f"✗ (exit: {exit_code})"

        md_parts = [f"**Status:** {status}"]

        stdout = result.get("stdout", "").strip()
        if stdout:
            stdout = self._truncate_text(stdout)
            md_parts.append(f"\n**Output:**\n```\n{stdout}\n```")

        stderr = result.get("stderr", "").strip()
        if stderr:
            stderr = self._truncate_text(stderr)
            md_parts.append(f"\n**Errors:**\n```\n{stderr}\n```")

        if result.get("duration_ms"):
            md_parts.append(f"\n*Duration: {result['duration_ms']}ms*")

        return {"content": "\n".join(md_parts), "format": "markdown"}

    def format_file_content(
        self,
        result: dict[str, Any],
        format: ResponseFormat = ResponseFormat.CONCISE,
    ) -> dict[str, Any]:
        """Format file read result."""
        if format == ResponseFormat.MARKDOWN:
            return self._file_to_markdown(result)
        elif format == ResponseFormat.CONCISE:
            return self._file_to_concise(result)
        else:
            return self._truncate_dict(result)

    def _file_to_concise(self, result: dict[str, Any]) -> dict[str, Any]:
        """Minimal file content."""
        content = self._truncate_text(result.get("content", ""))
        return {
            "content": content,
            "truncated": result.get("truncated", False)
            or len(content) < len(result.get("content", "")),
        }

    def _file_to_markdown(self, result: dict[str, Any]) -> dict[str, Any]:
        """Markdown formatted file content."""
        path = result.get("path", "unknown")
        content = self._truncate_text(result.get("content", ""))
        ext = path.rsplit(".", 1)[-1] if "." in path else ""

        md = f"**File:** `{path}`"
        if result.get("size"):
            md += f" ({result['size']} bytes)"
        md += f"\n```{ext}\n{content}\n```"

        if result.get("truncated"):
            md += "\n\n*[Content truncated]*"

        return {"content": md, "format": "markdown"}

    def format_file_list(
        self,
        files: list[dict[str, Any]],
        format: ResponseFormat = ResponseFormat.CONCISE,
    ) -> dict[str, Any]:
        """Format directory listing."""
        if format == ResponseFormat.MARKDOWN:
            return self._files_to_markdown(files)
        elif format == ResponseFormat.CONCISE:
            return self._files_to_concise(files)
        else:
            return {"files": files, "total": len(files)}

    def _files_to_concise(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Minimal file listing."""
        concise_files = []
        for f in files[: self.config.max_lines]:
            entry = {"name": f.get("name", "")}
            if f.get("type") == "directory":
                entry["name"] += "/"
            elif f.get("size"):
                entry["size"] = f["size"]
            concise_files.append(entry)

        result = {"files": concise_files, "total": len(files)}
        if len(files) > self.config.max_lines:
            result["truncated"] = True
            result["hint"] = (
                f"Showing {self.config.max_lines} of {len(files)} files. Use filters for specific files."
            )

        return result

    def _files_to_markdown(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Markdown file listing."""
        lines = []
        dirs = [f for f in files if f.get("type") == "directory"]
        regular = [f for f in files if f.get("type") != "directory"]

        if dirs:
            lines.append("**Directories:**")
            for d in dirs[: self.config.max_lines // 2]:
                lines.append(f"- 📁 {d.get('name', '')}/")

        if regular:
            lines.append("\n**Files:**")
            for f in regular[: self.config.max_lines // 2]:
                size = f.get("size", 0)
                size_str = self._human_size(size) if size else ""
                lines.append(f"- 📄 {f.get('name', '')} {size_str}")

        if len(files) > self.config.max_lines:
            lines.append(
                f"\n*[Showing {self.config.max_lines} of {len(files)} entries]*"
            )

        return {"content": "\n".join(lines), "format": "markdown"}

    def format_error(
        self,
        error: str,
        hint: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Format error response with helpful hints.

        Instead of raw tracebacks, provide actionable guidance.
        """
        result: dict[str, Any] = {"success": False, "error": error}

        if hint and self.config.show_hints:
            result["hint"] = hint

        if context:
            result["context"] = context

        return result

    def format_multi_host_result(
        self,
        result: dict[str, Any],
        format: ResponseFormat = ResponseFormat.CONCISE,
    ) -> dict[str, Any]:
        """Format multi-host execution result."""
        if format == ResponseFormat.CONCISE:
            return self._multi_to_concise(result)
        elif format == ResponseFormat.MARKDOWN:
            return self._multi_to_markdown(result)
        return result

    def _multi_to_concise(self, result: dict[str, Any]) -> dict[str, Any]:
        """Minimal multi-host result."""
        summary = {
            "success": result.get("success", False),
            "summary": f"{result.get('successful', 0)}/{result.get('total', 0)} succeeded",
        }

        # Only include failed hosts details
        if result.get("failed", 0) > 0:
            failed_hosts = {
                host: data.get("error", "Unknown error")
                for host, data in result.get("results", {}).items()
                if not data.get("success")
            }
            if failed_hosts:
                summary["failed_hosts"] = failed_hosts

        return summary

    def _multi_to_markdown(self, result: dict[str, Any]) -> dict[str, Any]:
        """Markdown multi-host result."""
        total = result.get("total", 0)
        ok = result.get("successful", 0)
        failed = result.get("failed", 0)

        lines = [f"**Results:** {ok}/{total} succeeded"]

        if failed > 0:
            lines.append("\n**Failed hosts:**")
            for host, data in result.get("results", {}).items():
                if not data.get("success"):
                    lines.append(f"- ❌ {host}: {data.get('error', 'Unknown')}")

        if ok > 0 and ok <= 5:
            lines.append("\n**Successful hosts:**")
            for host, data in result.get("results", {}).items():
                if data.get("success"):
                    output = data.get("stdout", "")[:100]
                    lines.append(f"- ✅ {host}: {output}...")

        return {"content": "\n".join(lines), "format": "markdown"}

    def _truncate_text(self, text: str) -> str:
        """Truncate text to configured limits."""
        if not text:
            return ""

        lines = text.split("\n")
        if len(lines) > self.config.max_lines:
            text = "\n".join(lines[: self.config.max_lines])
            text += self.config.truncate_message

        if len(text) > self.config.max_output_length:
            text = text[: self.config.max_output_length]
            text += self.config.truncate_message

        return text

    def _truncate_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        """Truncate string values in dict."""
        result = {}
        for k, v in d.items():
            if isinstance(v, str):
                result[k] = self._truncate_text(v)
            elif isinstance(v, dict):
                result[k] = self._truncate_dict(v)
            else:
                result[k] = v
        return result

    def _human_size(self, size: int) -> str:
        """Convert bytes to human readable."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"({size:.0f}{unit})"
            size /= 1024
        return f"({size:.0f}TB)"


# Global formatter instance
_formatter: ResponseFormatter | None = None


def get_formatter() -> ResponseFormatter:
    """Get global formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = ResponseFormatter()
    return _formatter


def init_formatter(config: FormatterConfig | None = None) -> ResponseFormatter:
    """Initialize global formatter with config."""
    global _formatter
    _formatter = ResponseFormatter(config)
    return _formatter
