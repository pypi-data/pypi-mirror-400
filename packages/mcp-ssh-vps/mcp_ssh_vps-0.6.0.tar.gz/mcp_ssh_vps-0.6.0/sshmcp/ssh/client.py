"""SSH client for remote server connections."""

import time
from pathlib import Path
from typing import Any

import paramiko
import structlog

from sshmcp.models.command import CommandResult
from sshmcp.models.file import FileContent, FileInfo, FileUploadResult
from sshmcp.models.machine import MachineConfig

logger = structlog.get_logger()


class SSHConnectionError(Exception):
    """Error connecting to SSH server."""

    pass


class SSHExecutionError(Exception):
    """Error executing command on SSH server."""

    pass


class SSHClient:
    """SSH client wrapper around paramiko."""

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    RETRY_BACKOFF = 2.0  # exponential backoff multiplier

    def __init__(self, machine: MachineConfig) -> None:
        """
        Initialize SSH client for a machine.

        Args:
            machine: Machine configuration.
        """
        self.machine = machine
        self._client: paramiko.SSHClient | None = None
        self._sftp: paramiko.SFTPClient | None = None
        self._retry_count = 0

    @property
    def is_connected(self) -> bool:
        """Check if SSH connection is active."""
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()

    def connect(self, retry: bool = True) -> None:
        """
        Establish SSH connection to the server with retry logic.

        Args:
            retry: Whether to retry on failure (default: True).

        Raises:
            SSHConnectionError: If connection fails after all retries.
        """
        if self.is_connected:
            return

        last_error: Exception | None = None
        max_attempts = self.MAX_RETRIES if retry else 1

        for attempt in range(max_attempts):
            try:
                self._connect_once()
                self._retry_count = 0  # Reset on success
                return
            except SSHConnectionError as e:
                last_error = e
                if attempt < max_attempts - 1:
                    delay = self.RETRY_DELAY * (self.RETRY_BACKOFF**attempt)
                    logger.warning(
                        "ssh_connection_retry",
                        host=self.machine.host,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e),
                    )
                    time.sleep(delay)

        self._retry_count += 1
        raise SSHConnectionError(
            f"Failed to connect after {max_attempts} attempts: {last_error}"
        )

    def _connect_once(self) -> None:
        """Single connection attempt without retry."""
        logger.info(
            "ssh_connecting",
            host=self.machine.host,
            port=self.machine.port,
            user=self.machine.user,
        )

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            connect_kwargs: dict[str, Any] = {
                "hostname": self.machine.host,
                "port": self.machine.port,
                "username": self.machine.user,
                "timeout": 30,
            }

            auth = self.machine.auth
            if auth.type == "key":
                key_path = Path(auth.key_path).expanduser()  # type: ignore
                if not key_path.exists():
                    raise SSHConnectionError(f"SSH key not found: {key_path}")

                # Try to load the key
                try:
                    if auth.passphrase:
                        pkey = paramiko.RSAKey.from_private_key_file(
                            str(key_path), password=auth.passphrase
                        )
                    else:
                        # Try RSA first, then Ed25519, then ECDSA
                        pkey = self._load_private_key(key_path, auth.passphrase)
                    connect_kwargs["pkey"] = pkey
                except Exception as e:
                    raise SSHConnectionError(f"Failed to load SSH key: {e}")

            elif auth.type == "password":
                connect_kwargs["password"] = auth.password

            elif auth.type == "agent":
                # Use SSH agent for authentication
                connect_kwargs["allow_agent"] = True
                connect_kwargs["look_for_keys"] = False

            # Enable agent forwarding if requested
            if auth.agent_forwarding:
                connect_kwargs["allow_agent"] = True

            self._client.connect(**connect_kwargs)
            logger.info("ssh_connected", host=self.machine.host)

        except paramiko.AuthenticationException as e:
            raise SSHConnectionError(f"Authentication failed: {e}")
        except paramiko.SSHException as e:
            raise SSHConnectionError(f"SSH error: {e}")
        except Exception as e:
            raise SSHConnectionError(f"Connection failed: {e}")

    def _load_private_key(
        self, key_path: Path, passphrase: str | None
    ) -> paramiko.PKey:
        """Try to load private key with different algorithms."""
        key_types = [
            paramiko.RSAKey,
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
        ]

        last_error = None
        for key_type in key_types:
            try:
                return key_type.from_private_key_file(
                    str(key_path), password=passphrase
                )
            except Exception as e:
                last_error = e
                continue

        raise SSHConnectionError(
            f"Could not load SSH key with any supported algorithm: {last_error}"
        )

    def disconnect(self) -> None:
        """Close SSH connection."""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None

        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

        logger.info("ssh_disconnected", host=self.machine.host)

    def execute(self, command: str, timeout: int | None = None) -> CommandResult:
        """
        Execute command on remote server.

        Args:
            command: Command to execute.
            timeout: Optional timeout in seconds. Uses machine config if not provided.

        Returns:
            CommandResult with execution details.

        Raises:
            SSHExecutionError: If execution fails.
        """
        if not self.is_connected:
            self.connect()

        if timeout is None:
            timeout = self.machine.security.timeout_seconds

        logger.info(
            "ssh_executing",
            host=self.machine.host,
            command=command,
            timeout=timeout,
        )

        start_time = time.time()

        try:
            stdin, stdout, stderr = self._client.exec_command(  # type: ignore
                command, timeout=timeout
            )

            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode("utf-8", errors="replace")
            stderr_text = stderr.read().decode("utf-8", errors="replace")

            duration_ms = int((time.time() - start_time) * 1000)

            result = CommandResult(
                exit_code=exit_code,
                stdout=stdout_text,
                stderr=stderr_text,
                duration_ms=duration_ms,
                host=self.machine.name,
                command=command,
            )

            logger.info(
                "ssh_executed",
                host=self.machine.host,
                exit_code=exit_code,
                duration_ms=duration_ms,
            )

            return result

        except paramiko.SSHException as e:
            raise SSHExecutionError(f"SSH execution error: {e}")
        except Exception as e:
            raise SSHExecutionError(f"Command execution failed: {e}")

    def _get_sftp(self) -> paramiko.SFTPClient:
        """Get or create SFTP client."""
        if not self.is_connected:
            self.connect()

        if self._sftp is None:
            self._sftp = self._client.open_sftp()  # type: ignore

        return self._sftp

    def read_file(
        self,
        path: str,
        encoding: str = "utf-8",
        max_size: int = 1024 * 1024,  # 1MB default
    ) -> FileContent:
        """
        Read file content from remote server.

        Args:
            path: Path to file on remote server.
            encoding: File encoding.
            max_size: Maximum file size to read in bytes.

        Returns:
            FileContent with file data.

        Raises:
            SSHExecutionError: If file cannot be read.
        """
        sftp = self._get_sftp()

        try:
            stat = sftp.stat(path)
            file_size = stat.st_size or 0

            truncated = file_size > max_size
            read_size = min(file_size, max_size)

            with sftp.open(path, "r") as f:
                content = f.read(read_size)
                if isinstance(content, bytes):
                    content = content.decode(encoding, errors="replace")

            logger.info(
                "ssh_file_read",
                host=self.machine.host,
                path=path,
                size=file_size,
                truncated=truncated,
            )

            return FileContent(
                content=content,
                path=path,
                size=file_size,
                encoding=encoding,
                truncated=truncated,
                host=self.machine.name,
            )

        except FileNotFoundError:
            raise SSHExecutionError(f"File not found: {path}")
        except PermissionError:
            raise SSHExecutionError(f"Permission denied: {path}")
        except Exception as e:
            raise SSHExecutionError(f"Error reading file: {e}")

    def write_file(
        self,
        path: str,
        content: str,
        mode: str | None = None,
    ) -> FileUploadResult:
        """
        Write file to remote server.

        Args:
            path: Destination path on remote server.
            content: File content to write.
            mode: Optional file permissions (e.g., "0644").

        Returns:
            FileUploadResult with upload details.

        Raises:
            SSHExecutionError: If file cannot be written.
        """
        sftp = self._get_sftp()

        try:
            content_bytes = content.encode("utf-8")
            size = len(content_bytes)

            with sftp.open(path, "w") as f:
                f.write(content_bytes)

            if mode:
                mode_int = int(mode, 8)
                sftp.chmod(path, mode_int)

            logger.info(
                "ssh_file_written",
                host=self.machine.host,
                path=path,
                size=size,
            )

            return FileUploadResult(
                success=True,
                path=path,
                size=size,
                host=self.machine.name,
            )

        except PermissionError:
            raise SSHExecutionError(f"Permission denied: {path}")
        except Exception as e:
            raise SSHExecutionError(f"Error writing file: {e}")

    def list_files(
        self,
        directory: str,
        recursive: bool = False,
    ) -> list[FileInfo]:
        """
        List files in remote directory.

        Args:
            directory: Directory path on remote server.
            recursive: Whether to list files recursively.

        Returns:
            List of FileInfo objects.

        Raises:
            SSHExecutionError: If directory cannot be listed.
        """
        sftp = self._get_sftp()
        files: list[FileInfo] = []

        try:
            self._list_directory(sftp, directory, files, recursive)
            return files

        except FileNotFoundError:
            raise SSHExecutionError(f"Directory not found: {directory}")
        except PermissionError:
            raise SSHExecutionError(f"Permission denied: {directory}")
        except Exception as e:
            raise SSHExecutionError(f"Error listing directory: {e}")

    def _list_directory(
        self,
        sftp: paramiko.SFTPClient,
        directory: str,
        files: list[FileInfo],
        recursive: bool,
    ) -> None:
        """Recursively list directory contents."""
        import stat
        from datetime import datetime

        for entry in sftp.listdir_attr(directory):
            full_path = f"{directory.rstrip('/')}/{entry.filename}"

            # Determine file type
            if stat.S_ISDIR(entry.st_mode or 0):
                file_type = "directory"
            elif stat.S_ISLNK(entry.st_mode or 0):
                file_type = "link"
            elif stat.S_ISREG(entry.st_mode or 0):
                file_type = "file"
            else:
                file_type = "other"

            file_info = FileInfo(
                name=entry.filename,
                path=full_path,
                type=file_type,  # type: ignore
                size=entry.st_size or 0,
                modified=datetime.fromtimestamp(entry.st_mtime or 0),
                permissions=oct(entry.st_mode or 0)[-4:] if entry.st_mode else None,
                owner=str(entry.st_uid) if entry.st_uid else None,
                group=str(entry.st_gid) if entry.st_gid else None,
            )
            files.append(file_info)

            if recursive and file_type == "directory":
                try:
                    self._list_directory(sftp, full_path, files, recursive)
                except PermissionError:
                    pass  # Skip directories we can't access

    def __enter__(self) -> "SSHClient":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
