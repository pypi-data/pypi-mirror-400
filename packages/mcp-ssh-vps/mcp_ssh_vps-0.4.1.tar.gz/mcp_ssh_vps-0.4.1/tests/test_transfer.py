"""Tests for directory transfer operations."""

from unittest.mock import MagicMock, patch

import pytest

from sshmcp.ssh.transfer import (
    DirectoryTransfer,
    TransferError,
    TransferProgress,
)


class TestTransferProgress:
    """Tests for TransferProgress."""

    def test_initial_state(self):
        """Test initial progress state."""
        progress = TransferProgress()

        assert progress.total_files == 0
        assert progress.transferred_files == 0
        assert progress.file_progress == 0.0
        assert progress.byte_progress == 0.0

    def test_progress_calculation(self):
        """Test progress percentage calculation."""
        progress = TransferProgress(total_files=10, total_bytes=1000)
        progress.transferred_files = 5
        progress.transferred_bytes = 500

        assert progress.file_progress == 50.0
        assert progress.byte_progress == 50.0

    def test_to_dict(self):
        """Test converting to dictionary."""
        progress = TransferProgress(total_files=10, total_bytes=1000)
        progress.transferred_files = 5
        progress.current_file = "/path/to/file"

        data = progress.to_dict()

        assert data["total_files"] == 10
        assert data["transferred_files"] == 5
        assert data["current_file"] == "/path/to/file"
        assert "file_progress" in data
        assert "byte_progress" in data


class TestDirectoryTransfer:
    """Tests for DirectoryTransfer."""

    @pytest.fixture
    def mock_ssh_client(self):
        """Create mock SSH client."""
        client = MagicMock()
        client.is_connected = True
        client._client = MagicMock()
        return client

    @pytest.fixture
    def mock_sftp(self):
        """Create mock SFTP client."""
        sftp = MagicMock()
        return sftp

    def test_init(self, mock_ssh_client):
        """Test transfer initialization."""
        transfer = DirectoryTransfer(mock_ssh_client)
        assert transfer.ssh_client == mock_ssh_client

    def test_set_progress_callback(self, mock_ssh_client):
        """Test setting progress callback."""
        transfer = DirectoryTransfer(mock_ssh_client)

        callback = MagicMock()
        transfer.set_progress_callback(callback)

        assert transfer._progress_callback == callback

    def test_upload_directory_not_exists(self, mock_ssh_client):
        """Test upload with non-existent local path."""
        transfer = DirectoryTransfer(mock_ssh_client)

        with pytest.raises(TransferError, match="does not exist"):
            transfer.upload_directory("/nonexistent/path", "/remote/path")

    def test_upload_directory_not_dir(self, mock_ssh_client, tmp_path):
        """Test upload with file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        transfer = DirectoryTransfer(mock_ssh_client)

        with pytest.raises(TransferError, match="not a directory"):
            transfer.upload_directory(str(test_file), "/remote/path")

    def test_upload_directory_success(self, mock_ssh_client, tmp_path):
        """Test successful directory upload."""
        # Create local directory structure
        local_dir = tmp_path / "source"
        local_dir.mkdir()
        (local_dir / "file1.txt").write_text("content1")
        (local_dir / "file2.txt").write_text("content2")

        # Mock SFTP
        mock_sftp = MagicMock()
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_ssh_client._client.open_sftp.return_value = mock_sftp

        transfer = DirectoryTransfer(mock_ssh_client)
        progress = transfer.upload_directory(str(local_dir), "/remote/dest")

        assert progress.total_files == 2
        assert mock_sftp.put.call_count == 2

    def test_download_directory_success(self, mock_ssh_client, tmp_path):
        """Test successful directory download."""
        local_dir = tmp_path / "dest"

        # Mock SFTP with file listings
        mock_sftp = MagicMock()

        mock_entry = MagicMock()
        mock_entry.filename = "test.txt"
        mock_entry.st_mode = 0o100644  # Regular file
        mock_entry.st_size = 100

        mock_sftp.listdir_attr.return_value = [mock_entry]
        mock_ssh_client._client.open_sftp.return_value = mock_sftp

        transfer = DirectoryTransfer(mock_ssh_client)
        transfer.download_directory("/remote/source", str(local_dir))

        assert mock_sftp.get.call_count == 1

    def test_sync_upload(self, mock_ssh_client, tmp_path):
        """Test sync in upload direction."""
        local_dir = tmp_path / "source"
        local_dir.mkdir()
        (local_dir / "file.txt").write_text("content")

        mock_sftp = MagicMock()
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_ssh_client._client.open_sftp.return_value = mock_sftp

        transfer = DirectoryTransfer(mock_ssh_client)
        progress = transfer.sync_directory(
            str(local_dir), "/remote/dest", direction="upload"
        )

        assert progress.total_files == 1

    def test_sync_invalid_direction(self, mock_ssh_client, tmp_path):
        """Test sync with invalid direction."""
        transfer = DirectoryTransfer(mock_ssh_client)

        with pytest.raises(TransferError, match="Invalid direction"):
            transfer.sync_directory("/local", "/remote", direction="invalid")

    def test_exclude_patterns(self, mock_ssh_client, tmp_path):
        """Test file exclusion patterns."""
        local_dir = tmp_path / "source"
        local_dir.mkdir()
        (local_dir / "include.txt").write_text("include")
        (local_dir / "exclude.log").write_text("exclude")
        (local_dir / ".hidden").write_text("hidden")

        mock_sftp = MagicMock()
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_ssh_client._client.open_sftp.return_value = mock_sftp

        transfer = DirectoryTransfer(mock_ssh_client)
        progress = transfer.upload_directory(
            str(local_dir),
            "/remote/dest",
            exclude_patterns=["*.log", ".*"],
        )

        # Should only upload include.txt
        assert progress.total_files == 1

    def test_close(self, mock_ssh_client):
        """Test closing SFTP connection."""
        mock_sftp = MagicMock()
        mock_ssh_client._client.open_sftp.return_value = mock_sftp

        transfer = DirectoryTransfer(mock_ssh_client)
        transfer._get_sftp()  # Initialize SFTP
        transfer.close()

        mock_sftp.close.assert_called_once()


class TestSyncDirectory:
    """Tests for sync_directory convenience function."""

    def test_sync_directory_function(self, tmp_path):
        """Test sync_directory function."""
        from sshmcp.models.machine import AuthConfig, MachineConfig, SecurityConfig
        from sshmcp.ssh.transfer import sync_directory

        local_dir = tmp_path / "source"
        local_dir.mkdir()
        (local_dir / "file.txt").write_text("content")

        machine = MachineConfig(
            name="test",
            host="192.168.1.1",
            port=22,
            user="user",
            auth=AuthConfig(type="key", key_path="~/.ssh/id_rsa"),
            security=SecurityConfig(),
        )

        with patch("sshmcp.ssh.transfer.SSHClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_connected = True
            mock_sftp = MagicMock()
            mock_sftp.stat.side_effect = FileNotFoundError()
            mock_client._client.open_sftp.return_value = mock_sftp
            mock_client_class.return_value = mock_client

            progress = sync_directory(
                machine,
                str(local_dir),
                "/remote/dest",
                direction="upload",
            )

            assert progress.total_files == 1
            mock_client.connect.assert_called_once()
            mock_client.disconnect.assert_called_once()
