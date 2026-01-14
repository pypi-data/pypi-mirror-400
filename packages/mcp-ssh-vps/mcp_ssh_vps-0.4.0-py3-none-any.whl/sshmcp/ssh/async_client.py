"""Async SSH client wrapper for parallel execution."""

import asyncio
from typing import Any

import structlog

from sshmcp.models.command import CommandResult
from sshmcp.models.file import FileContent, FileInfo, FileUploadResult
from sshmcp.models.machine import MachineConfig
from sshmcp.ssh.client import SSHClient, SSHConnectionError, SSHExecutionError

logger = structlog.get_logger()


class AsyncSSHClient:
    """
    Async wrapper around SSHClient for non-blocking operations.

    Uses asyncio.to_thread() to run blocking paramiko operations
    in a thread pool without blocking the event loop.
    """

    def __init__(self, machine: MachineConfig) -> None:
        """
        Initialize async SSH client.

        Args:
            machine: Machine configuration.
        """
        self.machine = machine
        self._sync_client: SSHClient | None = None

    @property
    def is_connected(self) -> bool:
        """Check if SSH connection is active."""
        return self._sync_client is not None and self._sync_client.is_connected

    async def connect(self, retry: bool = True) -> None:
        """
        Establish SSH connection asynchronously.

        Args:
            retry: Whether to retry on failure.

        Raises:
            SSHConnectionError: If connection fails.
        """
        if self.is_connected:
            return

        self._sync_client = SSHClient(self.machine)
        await asyncio.to_thread(self._sync_client.connect, retry)
        logger.info("async_ssh_connected", host=self.machine.host)

    async def disconnect(self) -> None:
        """Close SSH connection asynchronously."""
        if self._sync_client:
            await asyncio.to_thread(self._sync_client.disconnect)
            self._sync_client = None
            logger.info("async_ssh_disconnected", host=self.machine.host)

    async def execute(self, command: str, timeout: int | None = None) -> CommandResult:
        """
        Execute command asynchronously.

        Args:
            command: Command to execute.
            timeout: Optional timeout in seconds.

        Returns:
            CommandResult with execution details.

        Raises:
            SSHExecutionError: If execution fails.
        """
        if not self.is_connected:
            await self.connect()

        return await asyncio.to_thread(
            self._sync_client.execute,
            command,
            timeout,  # type: ignore
        )

    async def read_file(
        self,
        path: str,
        encoding: str = "utf-8",
        max_size: int = 1024 * 1024,
    ) -> FileContent:
        """
        Read file asynchronously.

        Args:
            path: Path to file.
            encoding: File encoding.
            max_size: Maximum file size to read.

        Returns:
            FileContent with file data.
        """
        if not self.is_connected:
            await self.connect()

        return await asyncio.to_thread(
            self._sync_client.read_file,
            path,
            encoding,
            max_size,  # type: ignore
        )

    async def write_file(
        self,
        path: str,
        content: str,
        mode: str | None = None,
    ) -> FileUploadResult:
        """
        Write file asynchronously.

        Args:
            path: Destination path.
            content: File content.
            mode: Optional file permissions.

        Returns:
            FileUploadResult with upload details.
        """
        if not self.is_connected:
            await self.connect()

        return await asyncio.to_thread(
            self._sync_client.write_file,
            path,
            content,
            mode,  # type: ignore
        )

    async def list_files(
        self,
        directory: str,
        recursive: bool = False,
    ) -> list[FileInfo]:
        """
        List files asynchronously.

        Args:
            directory: Directory path.
            recursive: Whether to list recursively.

        Returns:
            List of FileInfo objects.
        """
        if not self.is_connected:
            await self.connect()

        return await asyncio.to_thread(
            self._sync_client.list_files,
            directory,
            recursive,  # type: ignore
        )

    async def __aenter__(self) -> "AsyncSSHClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()


async def execute_on_hosts_async(
    machines: list[MachineConfig],
    command: str,
    timeout: int | None = None,
    max_concurrency: int = 10,
) -> dict[str, dict[str, Any]]:
    """
    Execute command on multiple hosts concurrently.

    Args:
        machines: List of machine configurations.
        command: Command to execute.
        timeout: Optional timeout per host.
        max_concurrency: Maximum concurrent connections.

    Returns:
        Dictionary mapping host names to results.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    results: dict[str, dict[str, Any]] = {}

    async def run_on_host(machine: MachineConfig) -> tuple[str, dict[str, Any]]:
        async with semaphore:
            try:
                async with AsyncSSHClient(machine) as client:
                    result = await client.execute(command, timeout)
                    return machine.name, {
                        "success": True,
                        **result.to_dict(),
                    }
            except (SSHConnectionError, SSHExecutionError) as e:
                return machine.name, {
                    "success": False,
                    "error": str(e),
                }
            except Exception as e:
                return machine.name, {
                    "success": False,
                    "error": f"Unexpected error: {e}",
                }

    tasks = [run_on_host(machine) for machine in machines]
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in task_results:
        if isinstance(result, Exception):
            logger.error("async_execution_error", error=str(result))
        else:
            host, data = result
            results[host] = data

    return results


async def health_check_hosts_async(
    machines: list[MachineConfig],
    max_concurrency: int = 20,
) -> dict[str, dict[str, Any]]:
    """
    Check health of multiple hosts concurrently.

    Args:
        machines: List of machine configurations.
        max_concurrency: Maximum concurrent checks.

    Returns:
        Dictionary mapping host names to health status.
    """
    return await execute_on_hosts_async(
        machines,
        "echo ok",
        timeout=5,
        max_concurrency=max_concurrency,
    )
