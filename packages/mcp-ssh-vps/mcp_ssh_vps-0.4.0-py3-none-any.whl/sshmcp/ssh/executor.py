"""Command executor with security validation."""

import structlog

from sshmcp.models.command import CommandResult
from sshmcp.models.machine import MachineConfig
from sshmcp.ssh.client import SSHClient
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


class CommandExecutor:
    """
    Execute commands on remote servers with validation and pooling.
    """

    def __init__(self) -> None:
        """Initialize executor."""
        self._pool = get_pool()

    def execute(
        self,
        machine: MachineConfig,
        command: str,
        timeout: int | None = None,
    ) -> CommandResult:
        """
        Execute command on remote server.

        Args:
            machine: Machine configuration.
            command: Command to execute.
            timeout: Optional timeout override.

        Returns:
            CommandResult with execution details.

        Raises:
            SSHExecutionError: If execution fails.
        """
        client = self._pool.get_client(machine.name)

        try:
            result = client.execute(command, timeout=timeout)
            return result
        finally:
            self._pool.release_client(client)

    def execute_with_client(
        self,
        client: SSHClient,
        command: str,
        timeout: int | None = None,
    ) -> CommandResult:
        """
        Execute command using provided client.

        Args:
            client: SSHClient to use.
            command: Command to execute.
            timeout: Optional timeout override.

        Returns:
            CommandResult with execution details.
        """
        return client.execute(command, timeout=timeout)


# Global executor instance
_executor: CommandExecutor | None = None


def get_executor() -> CommandExecutor:
    """Get or create the global command executor."""
    global _executor
    if _executor is None:
        _executor = CommandExecutor()
    return _executor
