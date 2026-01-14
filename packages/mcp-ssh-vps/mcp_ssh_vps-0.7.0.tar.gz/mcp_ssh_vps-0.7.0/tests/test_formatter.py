"""Tests for response formatter."""

import pytest

from sshmcp.tools.formatter import (
    FormatterConfig,
    ResponseFormat,
    ResponseFormatter,
    get_formatter,
    init_formatter,
)


class TestResponseFormat:
    """Tests for ResponseFormat enum."""

    def test_values(self):
        """Test enum values."""
        assert ResponseFormat.CONCISE.value == "concise"
        assert ResponseFormat.DETAILED.value == "detailed"
        assert ResponseFormat.MARKDOWN.value == "markdown"

    def test_from_string(self):
        """Test creating from string."""
        assert ResponseFormat("concise") == ResponseFormat.CONCISE
        assert ResponseFormat("detailed") == ResponseFormat.DETAILED
        assert ResponseFormat("markdown") == ResponseFormat.MARKDOWN


class TestFormatterConfig:
    """Tests for FormatterConfig."""

    def test_defaults(self):
        """Test default values."""
        config = FormatterConfig()
        assert config.max_output_length == 10000
        assert config.max_lines == 200
        assert config.show_hints is True

    def test_custom_values(self):
        """Test custom values."""
        config = FormatterConfig(max_output_length=5000, max_lines=100)
        assert config.max_output_length == 5000
        assert config.max_lines == 100


class TestResponseFormatterCommandResult:
    """Tests for command result formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.fixture
    def success_result(self):
        return {
            "exit_code": 0,
            "stdout": "Hello World\n",
            "stderr": "",
            "duration_ms": 50,
            "host": "test-server",
            "command": "echo Hello World",
        }

    @pytest.fixture
    def error_result(self):
        return {
            "exit_code": 1,
            "stdout": "",
            "stderr": "Command not found\n",
            "duration_ms": 10,
            "host": "test-server",
            "command": "invalid_command",
        }

    def test_concise_success(self, formatter, success_result):
        """Test concise format for successful command."""
        result = formatter.format_command_result(success_result, ResponseFormat.CONCISE)

        assert result["success"] is True
        assert result["output"] == "Hello World\n"
        assert "exit_code" not in result  # Not included for success
        assert "stderr" not in result

    def test_concise_error(self, formatter, error_result):
        """Test concise format for failed command."""
        result = formatter.format_command_result(error_result, ResponseFormat.CONCISE)

        assert result["success"] is False
        assert result["exit_code"] == 1
        assert "error" in result or "output" in result

    def test_detailed_format(self, formatter, success_result):
        """Test detailed format."""
        result = formatter.format_command_result(
            success_result, ResponseFormat.DETAILED
        )

        assert "stdout" in result
        assert "stderr" in result
        assert "exit_code" in result
        assert "duration_ms" in result

    def test_markdown_success(self, formatter, success_result):
        """Test markdown format for success."""
        result = formatter.format_command_result(
            success_result, ResponseFormat.MARKDOWN
        )

        assert result["format"] == "markdown"
        assert "**Status:** ✓" in result["content"]
        assert "Hello World" in result["content"]

    def test_markdown_error(self, formatter, error_result):
        """Test markdown format for error."""
        result = formatter.format_command_result(error_result, ResponseFormat.MARKDOWN)

        assert result["format"] == "markdown"
        assert "✗" in result["content"]
        assert "exit: 1" in result["content"]


class TestResponseFormatterFileContent:
    """Tests for file content formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.fixture
    def file_result(self):
        return {
            "content": "line1\nline2\nline3",
            "path": "/etc/hosts",
            "size": 100,
            "encoding": "utf-8",
            "truncated": False,
            "host": "test-server",
        }

    def test_concise_format(self, formatter, file_result):
        """Test concise file format."""
        result = formatter.format_file_content(file_result, ResponseFormat.CONCISE)

        assert "content" in result
        assert "truncated" in result
        assert "path" not in result

    def test_detailed_format(self, formatter, file_result):
        """Test detailed file format."""
        result = formatter.format_file_content(file_result, ResponseFormat.DETAILED)

        assert "content" in result
        assert "path" in result
        assert "size" in result

    def test_markdown_format(self, formatter, file_result):
        """Test markdown file format."""
        result = formatter.format_file_content(file_result, ResponseFormat.MARKDOWN)

        assert result["format"] == "markdown"
        assert "**File:** `/etc/hosts`" in result["content"]
        assert "```" in result["content"]
        assert "line1" in result["content"]


class TestResponseFormatterFileList:
    """Tests for file list formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.fixture
    def files(self):
        return [
            {"name": "dir1", "type": "directory", "size": 0},
            {"name": "file1.txt", "type": "file", "size": 1024},
            {"name": "file2.py", "type": "file", "size": 2048},
        ]

    def test_concise_format(self, formatter, files):
        """Test concise file list."""
        result = formatter.format_file_list(files, ResponseFormat.CONCISE)

        assert "files" in result
        assert "total" in result
        assert result["total"] == 3
        # Directory should have trailing slash
        assert any("/" in f["name"] for f in result["files"])

    def test_markdown_format(self, formatter, files):
        """Test markdown file list."""
        result = formatter.format_file_list(files, ResponseFormat.MARKDOWN)

        assert result["format"] == "markdown"
        assert "**Directories:**" in result["content"]
        assert "**Files:**" in result["content"]
        assert "📁" in result["content"]
        assert "📄" in result["content"]

    def test_truncation_hint(self, formatter):
        """Test truncation hint for large lists."""
        config = FormatterConfig(max_lines=5)
        formatter = ResponseFormatter(config)

        files = [
            {"name": f"file{i}.txt", "type": "file", "size": i * 100} for i in range(20)
        ]

        result = formatter.format_file_list(files, ResponseFormat.CONCISE)

        assert result["truncated"] is True
        assert "hint" in result


class TestResponseFormatterError:
    """Tests for error formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    def test_basic_error(self, formatter):
        """Test basic error format."""
        result = formatter.format_error("Connection failed")

        assert result["success"] is False
        assert result["error"] == "Connection failed"

    def test_error_with_hint(self, formatter):
        """Test error with hint."""
        result = formatter.format_error(
            "File not found",
            hint="Check if the file path is correct.",
        )

        assert result["error"] == "File not found"
        assert result["hint"] == "Check if the file path is correct."

    def test_error_with_context(self, formatter):
        """Test error with context."""
        result = formatter.format_error(
            "Permission denied",
            context={"path": "/root/secret", "user": "test"},
        )

        assert result["error"] == "Permission denied"
        assert result["context"]["path"] == "/root/secret"

    def test_error_hints_disabled(self):
        """Test error when hints are disabled."""
        config = FormatterConfig(show_hints=False)
        formatter = ResponseFormatter(config)

        result = formatter.format_error("Error", hint="This should not appear")

        assert "hint" not in result


class TestResponseFormatterMultiHost:
    """Tests for multi-host result formatting."""

    @pytest.fixture
    def formatter(self):
        return ResponseFormatter()

    @pytest.fixture
    def multi_result(self):
        return {
            "success": False,
            "total": 3,
            "successful": 2,
            "failed": 1,
            "command": "uptime",
            "results": {
                "server1": {"success": True, "stdout": "up 5 days"},
                "server2": {"success": True, "stdout": "up 10 days"},
                "server3": {"success": False, "error": "Connection refused"},
            },
        }

    def test_concise_format(self, formatter, multi_result):
        """Test concise multi-host format."""
        result = formatter.format_multi_host_result(
            multi_result, ResponseFormat.CONCISE
        )

        assert result["success"] is False
        assert "2/3" in result["summary"]
        assert "failed_hosts" in result
        assert "server3" in result["failed_hosts"]

    def test_markdown_format(self, formatter, multi_result):
        """Test markdown multi-host format."""
        result = formatter.format_multi_host_result(
            multi_result, ResponseFormat.MARKDOWN
        )

        assert result["format"] == "markdown"
        assert "2/3" in result["content"]
        assert "❌" in result["content"]
        assert "server3" in result["content"]


class TestResponseFormatterTruncation:
    """Tests for text truncation."""

    def test_line_truncation(self):
        """Test truncation by line count."""
        config = FormatterConfig(max_lines=3)
        formatter = ResponseFormatter(config)

        text = "line1\nline2\nline3\nline4\nline5"
        result = formatter._truncate_text(text)

        assert "line1" in result
        assert "line3" in result
        assert "truncated" in result.lower()

    def test_length_truncation(self):
        """Test truncation by character count."""
        config = FormatterConfig(max_output_length=20)
        formatter = ResponseFormatter(config)

        text = "a" * 100
        result = formatter._truncate_text(text)

        assert len(result) < 100
        assert "truncated" in result.lower()

    def test_empty_text(self):
        """Test truncation of empty text."""
        formatter = ResponseFormatter()
        assert formatter._truncate_text("") == ""
        assert formatter._truncate_text(None) == ""  # type: ignore


class TestGlobalFormatter:
    """Tests for global formatter functions."""

    def test_get_formatter(self):
        """Test getting global formatter."""
        formatter = get_formatter()
        assert isinstance(formatter, ResponseFormatter)

    def test_init_formatter(self):
        """Test initializing global formatter."""
        config = FormatterConfig(max_lines=50)
        formatter = init_formatter(config)

        assert formatter.config.max_lines == 50

        # Global should be updated
        global_formatter = get_formatter()
        assert global_formatter.config.max_lines == 50
