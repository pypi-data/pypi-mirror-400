"""Tests for file operation tools."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.models.file import FileContent, FileInfo, FileUploadResult
from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    SecurityConfig,
)


@pytest.fixture
def mock_machine():
    """Create a mock machine configuration."""
    return MachineConfig(
        name="test-server",
        host="192.168.1.1",
        port=22,
        user="testuser",
        auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
        security=SecurityConfig(
            allowed_commands=[".*"],
            forbidden_commands=[],
            timeout_seconds=30,
        ),
    )


@pytest.fixture
def mock_file_content():
    """Create a mock file content result."""
    result = MagicMock(spec=FileContent)
    result.content = "file content here"
    result.path = "/var/log/app.log"
    result.size = 17
    result.encoding = "utf-8"
    result.truncated = False
    result.to_dict.return_value = {
        "content": "file content here",
        "path": "/var/log/app.log",
        "size": 17,
        "encoding": "utf-8",
        "truncated": False,
    }
    return result


@pytest.fixture
def mock_write_result():
    """Create a mock write result."""
    result = MagicMock(spec=FileUploadResult)
    result.success = True
    result.path = "/opt/app/config.json"
    result.size = 20
    result.to_dict.return_value = {
        "success": True,
        "path": "/opt/app/config.json",
        "size": 20,
    }
    return result


@pytest.fixture
def mock_file_info():
    """Create a mock file info."""
    result = MagicMock(spec=FileInfo)
    result.name = "test.txt"
    result.path = "/var/www/test.txt"
    result.size = 100
    result.is_dir = False
    result.permissions = "-rw-r--r--"
    result.to_dict.return_value = {
        "name": "test.txt",
        "path": "/var/www/test.txt",
        "size": 100,
        "is_dir": False,
        "permissions": "-rw-r--r--",
    }
    return result


class TestReadFile:
    """Tests for read_file function."""

    def test_read_file_success(self, mock_machine, mock_file_content):
        """Test successful file read."""
        mock_client = MagicMock()
        mock_client.read_file.return_value = mock_file_content

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import read_file

                        # Use detailed format to get raw content
                        result = read_file(
                            "test-server",
                            "/var/log/app.log",
                            response_format="detailed",
                        )

        assert result["content"] == "file content here"
        assert result["size"] == 17
        mock_client.read_file.assert_called_once()
        mock_pool.release_client.assert_called_once_with(mock_client)

    def test_read_file_host_not_found(self):
        """Test read with non-existent host."""
        with patch(
            "sshmcp.tools.files.get_machine", side_effect=Exception("Host not found")
        ):
            from sshmcp.tools.files import read_file

            with pytest.raises(ValueError, match="Host not found"):
                read_file("nonexistent", "/var/log/app.log")

    def test_read_file_path_not_allowed(self, mock_machine):
        """Test read with disallowed path."""
        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.tools.files.validate_path",
                return_value=(False, "Path not allowed"),
            ):
                with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.files import read_file

                    with pytest.raises(ValueError, match="Path not allowed"):
                        read_file("test-server", "/etc/shadow")

    def test_read_file_ssh_error(self, mock_machine):
        """Test read with SSH error."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection failed")

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import read_file

                        # Now returns error dict instead of raising
                        result = read_file("test-server", "/var/log/app.log")
                        assert result["success"] is False
                        assert "error" in result

    def test_read_file_with_custom_encoding(self, mock_machine, mock_file_content):
        """Test read with custom encoding."""
        mock_client = MagicMock()
        mock_client.read_file.return_value = mock_file_content

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import read_file

                        read_file("test-server", "/var/log/app.log", encoding="latin-1")

        mock_client.read_file.assert_called_once_with(
            "/var/log/app.log", encoding="latin-1", max_size=1024 * 1024
        )

    def test_read_file_with_max_size(self, mock_machine, mock_file_content):
        """Test read with custom max size."""
        mock_client = MagicMock()
        mock_client.read_file.return_value = mock_file_content

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import read_file

                        read_file("test-server", "/var/log/app.log", max_size=512)

        mock_client.read_file.assert_called_once_with(
            "/var/log/app.log", encoding="utf-8", max_size=512
        )


class TestUploadFile:
    """Tests for upload_file function."""

    def test_upload_file_success(self, mock_machine, mock_write_result):
        """Test successful file upload."""
        mock_client = MagicMock()
        mock_client.write_file.return_value = mock_write_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import upload_file

                        result = upload_file(
                            "test-server", "/opt/app/config.json", '{"key": "value"}'
                        )

        assert result["success"] is True
        assert result["path"] == "/opt/app/config.json"
        mock_client.write_file.assert_called_once()
        mock_pool.release_client.assert_called_once_with(mock_client)

    def test_upload_file_with_mode(self, mock_machine, mock_write_result):
        """Test file upload with permissions mode."""
        mock_client = MagicMock()
        mock_client.write_file.return_value = mock_write_result

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import upload_file

                        upload_file(
                            "test-server",
                            "/opt/app/script.sh",
                            "#!/bin/bash\necho hello",
                            mode="0755",
                        )

        mock_client.write_file.assert_called_once_with(
            "/opt/app/script.sh", "#!/bin/bash\necho hello", mode="0755"
        )

    def test_upload_file_host_not_found(self):
        """Test upload with non-existent host."""
        with patch(
            "sshmcp.tools.files.get_machine", side_effect=Exception("Host not found")
        ):
            from sshmcp.tools.files import upload_file

            with pytest.raises(ValueError, match="Host not found"):
                upload_file("nonexistent", "/tmp/test.txt", "content")

    def test_upload_file_path_not_allowed(self, mock_machine):
        """Test upload with disallowed path."""
        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.tools.files.validate_path",
                return_value=(False, "Path forbidden"),
            ):
                with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.files import upload_file

                    with pytest.raises(ValueError, match="Path not allowed"):
                        upload_file("test-server", "/etc/passwd", "malicious")


class TestListFiles:
    """Tests for list_files function."""

    def test_list_files_success(self, mock_machine, mock_file_info):
        """Test successful directory listing."""
        mock_client = MagicMock()
        mock_client.list_files.return_value = [mock_file_info]

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import list_files

                        # Use detailed format to get full response
                        result = list_files(
                            "test-server", "/var/www", response_format="detailed"
                        )

        assert result["total_count"] == 1
        assert result["directory"] == "/var/www"
        assert result["host"] == "test-server"
        assert len(result["files"]) == 1
        mock_pool.release_client.assert_called_once_with(mock_client)

    def test_list_files_recursive(self, mock_machine, mock_file_info):
        """Test recursive directory listing."""
        mock_client = MagicMock()
        mock_client.list_files.return_value = [mock_file_info]

        mock_pool = MagicMock()
        mock_pool.get_client.return_value = mock_client

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import list_files

                        list_files("test-server", "/var/www", recursive=True)

        mock_client.list_files.assert_called_once_with("/var/www", recursive=True)

    def test_list_files_host_not_found(self):
        """Test listing with non-existent host."""
        with patch(
            "sshmcp.tools.files.get_machine", side_effect=Exception("Host not found")
        ):
            from sshmcp.tools.files import list_files

            with pytest.raises(ValueError, match="Host not found"):
                list_files("nonexistent", "/var/www")

    def test_list_files_path_not_allowed(self, mock_machine):
        """Test listing with disallowed path."""
        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch(
                "sshmcp.tools.files.validate_path",
                return_value=(False, "Path forbidden"),
            ):
                with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                    mock_audit.return_value = MagicMock()

                    from sshmcp.tools.files import list_files

                    with pytest.raises(ValueError, match="Path not allowed"):
                        list_files("test-server", "/root/.ssh")

    def test_list_files_ssh_error(self, mock_machine):
        """Test listing with SSH error."""
        mock_pool = MagicMock()
        mock_pool.get_client.side_effect = Exception("Connection failed")

        with patch("sshmcp.tools.files.get_machine", return_value=mock_machine):
            with patch("sshmcp.tools.files.validate_path", return_value=(True, None)):
                with patch("sshmcp.tools.files.get_pool", return_value=mock_pool):
                    with patch("sshmcp.tools.files.get_audit_logger") as mock_audit:
                        mock_audit.return_value = MagicMock()

                        from sshmcp.tools.files import list_files

                        # Now returns error dict instead of raising
                        result = list_files("test-server", "/var/www")
                        assert result["success"] is False
                        assert "error" in result
