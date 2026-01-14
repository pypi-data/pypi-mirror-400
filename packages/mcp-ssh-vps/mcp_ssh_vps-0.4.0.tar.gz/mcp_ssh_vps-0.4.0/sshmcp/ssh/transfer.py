"""File and directory transfer operations via SFTP."""

import os
import stat
from pathlib import Path
from typing import Callable

import paramiko
import structlog

from sshmcp.models.machine import MachineConfig
from sshmcp.ssh.client import SSHClient

logger = structlog.get_logger()


class TransferError(Exception):
    """Error during file transfer."""

    pass


class TransferProgress:
    """Progress tracking for file transfers."""

    def __init__(self, total_files: int = 0, total_bytes: int = 0):
        self.total_files = total_files
        self.total_bytes = total_bytes
        self.transferred_files = 0
        self.transferred_bytes = 0
        self.current_file = ""
        self.errors: list[str] = []

    @property
    def file_progress(self) -> float:
        """Get file transfer progress percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.transferred_files / self.total_files) * 100

    @property
    def byte_progress(self) -> float:
        """Get byte transfer progress percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.transferred_bytes / self.total_bytes) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "total_bytes": self.total_bytes,
            "transferred_files": self.transferred_files,
            "transferred_bytes": self.transferred_bytes,
            "current_file": self.current_file,
            "file_progress": round(self.file_progress, 1),
            "byte_progress": round(self.byte_progress, 1),
            "errors": self.errors,
        }


class DirectoryTransfer:
    """
    Transfer directories between local and remote systems via SFTP.

    Provides rsync-like functionality for syncing directories.
    """

    def __init__(self, ssh_client: SSHClient) -> None:
        """
        Initialize directory transfer.

        Args:
            ssh_client: Connected SSH client.
        """
        self.ssh_client = ssh_client
        self._sftp: paramiko.SFTPClient | None = None
        self._progress_callback: Callable[[TransferProgress], None] | None = None

    def set_progress_callback(
        self, callback: Callable[[TransferProgress], None]
    ) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback

    def _get_sftp(self) -> paramiko.SFTPClient:
        """Get or create SFTP client."""
        if self._sftp is None:
            if not self.ssh_client.is_connected:
                self.ssh_client.connect()
            self._sftp = self.ssh_client._client.open_sftp()  # type: ignore
        return self._sftp

    def upload_directory(
        self,
        local_path: str,
        remote_path: str,
        exclude_patterns: list[str] | None = None,
        delete_extra: bool = False,
    ) -> TransferProgress:
        """
        Upload a local directory to remote server.

        Args:
            local_path: Local directory path.
            remote_path: Remote destination path.
            exclude_patterns: Patterns to exclude (glob-style).
            delete_extra: Delete files on remote not in local.

        Returns:
            TransferProgress with results.
        """
        local = Path(local_path)
        if not local.exists():
            raise TransferError(f"Local path does not exist: {local_path}")
        if not local.is_dir():
            raise TransferError(f"Local path is not a directory: {local_path}")

        sftp = self._get_sftp()
        progress = TransferProgress()
        exclude = exclude_patterns or []

        # Count files first
        for root, dirs, files in os.walk(local):
            for f in files:
                file_path = Path(root) / f
                if not self._should_exclude(str(file_path), exclude):
                    progress.total_files += 1
                    progress.total_bytes += file_path.stat().st_size

        # Create remote base directory
        self._ensure_remote_dir(sftp, remote_path)

        # Track remote files for deletion
        remote_files: set[str] = set()
        if delete_extra:
            remote_files = self._list_remote_files(sftp, remote_path)

        uploaded_files: set[str] = set()

        # Upload files
        for root, dirs, files in os.walk(local):
            rel_root = Path(root).relative_to(local)
            remote_dir = f"{remote_path}/{rel_root}".rstrip("/.")

            # Create subdirectories
            if str(rel_root) != ".":
                self._ensure_remote_dir(sftp, remote_dir)

            for f in files:
                local_file = Path(root) / f
                rel_file = str(rel_root / f).lstrip("./")
                remote_file = f"{remote_path}/{rel_file}"

                if self._should_exclude(str(local_file), exclude):
                    continue

                progress.current_file = str(local_file)

                try:
                    sftp.put(str(local_file), remote_file)
                    progress.transferred_files += 1
                    progress.transferred_bytes += local_file.stat().st_size
                    uploaded_files.add(rel_file)

                    if self._progress_callback:
                        self._progress_callback(progress)

                except Exception as e:
                    progress.errors.append(f"{local_file}: {e}")
                    logger.error(
                        "upload_file_error", file=str(local_file), error=str(e)
                    )

        # Delete extra files on remote
        if delete_extra:
            extra_files = remote_files - uploaded_files
            for rel_file in extra_files:
                try:
                    remote_file = f"{remote_path}/{rel_file}"
                    sftp.remove(remote_file)
                    logger.info("deleted_extra_file", file=remote_file)
                except Exception as e:
                    progress.errors.append(f"delete {rel_file}: {e}")

        logger.info(
            "directory_uploaded",
            local=local_path,
            remote=remote_path,
            files=progress.transferred_files,
        )

        return progress

    def download_directory(
        self,
        remote_path: str,
        local_path: str,
        exclude_patterns: list[str] | None = None,
        delete_extra: bool = False,
    ) -> TransferProgress:
        """
        Download a remote directory to local system.

        Args:
            remote_path: Remote directory path.
            local_path: Local destination path.
            exclude_patterns: Patterns to exclude.
            delete_extra: Delete files in local not in remote.

        Returns:
            TransferProgress with results.
        """
        sftp = self._get_sftp()
        local = Path(local_path)
        progress = TransferProgress()
        exclude = exclude_patterns or []

        # Count remote files first
        remote_files_info = self._list_remote_files_with_info(sftp, remote_path)
        for rel_path, size in remote_files_info.items():
            if not self._should_exclude(rel_path, exclude):
                progress.total_files += 1
                progress.total_bytes += size

        # Create local base directory
        local.mkdir(parents=True, exist_ok=True)

        # Track local files for deletion
        local_files: set[str] = set()
        if delete_extra:
            for root, dirs, files in os.walk(local):
                for f in files:
                    rel = str((Path(root) / f).relative_to(local))
                    local_files.add(rel)

        downloaded_files: set[str] = set()

        # Download files
        self._download_recursive(
            sftp, remote_path, local, "", progress, exclude, downloaded_files
        )

        # Delete extra local files
        if delete_extra:
            extra_files = local_files - downloaded_files
            for rel_file in extra_files:
                try:
                    (local / rel_file).unlink()
                    logger.info("deleted_extra_local_file", file=rel_file)
                except Exception as e:
                    progress.errors.append(f"delete {rel_file}: {e}")

        logger.info(
            "directory_downloaded",
            remote=remote_path,
            local=local_path,
            files=progress.transferred_files,
        )

        return progress

    def sync_directory(
        self,
        local_path: str,
        remote_path: str,
        direction: str = "upload",
        exclude_patterns: list[str] | None = None,
        delete_extra: bool = False,
    ) -> TransferProgress:
        """
        Sync a directory (rsync-like behavior).

        Args:
            local_path: Local directory path.
            remote_path: Remote directory path.
            direction: "upload" or "download".
            exclude_patterns: Patterns to exclude.
            delete_extra: Delete files not in source.

        Returns:
            TransferProgress with results.
        """
        if direction == "upload":
            return self.upload_directory(
                local_path, remote_path, exclude_patterns, delete_extra
            )
        elif direction == "download":
            return self.download_directory(
                remote_path, local_path, exclude_patterns, delete_extra
            )
        else:
            raise TransferError(f"Invalid direction: {direction}")

    def _ensure_remote_dir(self, sftp: paramiko.SFTPClient, path: str) -> None:
        """Ensure remote directory exists."""
        try:
            sftp.stat(path)
        except FileNotFoundError:
            # Create parent directories recursively
            parts = path.split("/")
            current = ""
            for part in parts:
                if not part:
                    continue
                current = f"{current}/{part}"
                try:
                    sftp.stat(current)
                except FileNotFoundError:
                    sftp.mkdir(current)

    def _list_remote_files(
        self, sftp: paramiko.SFTPClient, path: str, prefix: str = ""
    ) -> set[str]:
        """List all files in remote directory recursively."""
        files: set[str] = set()

        try:
            for entry in sftp.listdir_attr(path):
                full_path = f"{path}/{entry.filename}"
                rel_path = f"{prefix}/{entry.filename}".lstrip("/")

                if stat.S_ISDIR(entry.st_mode or 0):
                    files.update(self._list_remote_files(sftp, full_path, rel_path))
                else:
                    files.add(rel_path)
        except Exception:
            pass

        return files

    def _list_remote_files_with_info(
        self, sftp: paramiko.SFTPClient, path: str, prefix: str = ""
    ) -> dict[str, int]:
        """List all files with sizes in remote directory."""
        files: dict[str, int] = {}

        try:
            for entry in sftp.listdir_attr(path):
                full_path = f"{path}/{entry.filename}"
                rel_path = f"{prefix}/{entry.filename}".lstrip("/")

                if stat.S_ISDIR(entry.st_mode or 0):
                    files.update(
                        self._list_remote_files_with_info(sftp, full_path, rel_path)
                    )
                else:
                    files[rel_path] = entry.st_size or 0
        except Exception:
            pass

        return files

    def _download_recursive(
        self,
        sftp: paramiko.SFTPClient,
        remote_path: str,
        local_base: Path,
        prefix: str,
        progress: TransferProgress,
        exclude: list[str],
        downloaded: set[str],
    ) -> None:
        """Recursively download directory contents."""
        try:
            for entry in sftp.listdir_attr(remote_path):
                remote_file = f"{remote_path}/{entry.filename}"
                rel_path = f"{prefix}/{entry.filename}".lstrip("/")
                local_file = local_base / rel_path

                if self._should_exclude(rel_path, exclude):
                    continue

                if stat.S_ISDIR(entry.st_mode or 0):
                    local_file.mkdir(parents=True, exist_ok=True)
                    self._download_recursive(
                        sftp,
                        remote_file,
                        local_base,
                        rel_path,
                        progress,
                        exclude,
                        downloaded,
                    )
                else:
                    progress.current_file = remote_file

                    try:
                        local_file.parent.mkdir(parents=True, exist_ok=True)
                        sftp.get(remote_file, str(local_file))
                        progress.transferred_files += 1
                        progress.transferred_bytes += entry.st_size or 0
                        downloaded.add(rel_path)

                        if self._progress_callback:
                            self._progress_callback(progress)

                    except Exception as e:
                        progress.errors.append(f"{remote_file}: {e}")

        except Exception as e:
            progress.errors.append(f"{remote_path}: {e}")

    def _should_exclude(self, path: str, patterns: list[str]) -> bool:
        """Check if path matches any exclude pattern."""
        import fnmatch

        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        return False

    def close(self) -> None:
        """Close SFTP connection."""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None


def sync_directory(
    machine: MachineConfig,
    local_path: str,
    remote_path: str,
    direction: str = "upload",
    exclude: list[str] | None = None,
    delete_extra: bool = False,
    progress_callback: Callable[[TransferProgress], None] | None = None,
) -> TransferProgress:
    """
    Convenience function to sync a directory.

    Args:
        machine: Machine configuration.
        local_path: Local directory path.
        remote_path: Remote directory path.
        direction: "upload" or "download".
        exclude: Patterns to exclude.
        delete_extra: Delete files not in source.
        progress_callback: Optional progress callback.

    Returns:
        TransferProgress with results.
    """
    client = SSHClient(machine)
    client.connect()

    try:
        transfer = DirectoryTransfer(client)
        if progress_callback:
            transfer.set_progress_callback(progress_callback)

        return transfer.sync_directory(
            local_path, remote_path, direction, exclude, delete_extra
        )
    finally:
        client.disconnect()
