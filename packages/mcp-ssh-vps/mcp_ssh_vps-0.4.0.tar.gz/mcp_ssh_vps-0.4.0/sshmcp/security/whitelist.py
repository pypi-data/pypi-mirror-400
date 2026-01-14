"""Command whitelist management."""

import re
from typing import TYPE_CHECKING, Dict, List, Pattern

import structlog

if TYPE_CHECKING:
    from sshmcp.models.machine import MachinesConfig

logger = structlog.get_logger()


class CommandWhitelist:
    """
    Manages command whitelist patterns with compiled regex caching.
    """

    def __init__(self) -> None:
        """Initialize whitelist manager."""
        self._patterns: Dict[str, List[Pattern[str]]] = {}
        self._forbidden: Dict[str, List[Pattern[str]]] = {}

    def load_patterns(
        self,
        machine_name: str,
        allowed: List[str],
        forbidden: List[str],
    ) -> None:
        """
        Load and compile patterns for a machine.

        Args:
            machine_name: Name of the machine.
            allowed: List of allowed command patterns.
            forbidden: List of forbidden command patterns.
        """
        self._patterns[machine_name] = []
        self._forbidden[machine_name] = []

        for pattern in allowed:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._patterns[machine_name].append(compiled)
            except re.error as e:
                logger.error(
                    "invalid_allowed_pattern",
                    machine=machine_name,
                    pattern=pattern,
                    error=str(e),
                )

        for pattern in forbidden:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._forbidden[machine_name].append(compiled)
            except re.error as e:
                logger.error(
                    "invalid_forbidden_pattern",
                    machine=machine_name,
                    pattern=pattern,
                    error=str(e),
                )

        logger.info(
            "whitelist_loaded",
            machine=machine_name,
            allowed_count=len(self._patterns[machine_name]),
            forbidden_count=len(self._forbidden[machine_name]),
        )

    def is_allowed(self, machine_name: str, command: str) -> bool:
        """
        Check if command is allowed for machine.

        Args:
            machine_name: Name of the machine.
            command: Command to check.

        Returns:
            True if command is allowed.
        """
        command = command.strip()

        # Check forbidden first
        if machine_name in self._forbidden:
            for pattern in self._forbidden[machine_name]:
                if pattern.match(command):
                    return False

        # If no allowed patterns, allow all (except forbidden)
        if machine_name not in self._patterns or not self._patterns[machine_name]:
            return True

        # Check allowed patterns
        for pattern in self._patterns[machine_name]:
            if pattern.match(command):
                return True

        return False

    def is_forbidden(self, machine_name: str, command: str) -> bool:
        """
        Check if command is explicitly forbidden.

        Args:
            machine_name: Name of the machine.
            command: Command to check.

        Returns:
            True if command is forbidden.
        """
        if machine_name not in self._forbidden:
            return False

        command = command.strip()
        for pattern in self._forbidden[machine_name]:
            if pattern.match(command):
                return True

        return False

    def get_patterns(self, machine_name: str) -> Dict[str, int]:
        """
        Get pattern counts for a machine.

        Args:
            machine_name: Name of the machine.

        Returns:
            Dictionary with allowed and forbidden pattern counts.
        """
        return {
            "allowed": len(self._patterns.get(machine_name, [])),
            "forbidden": len(self._forbidden.get(machine_name, [])),
        }


# Global whitelist instance
_whitelist: CommandWhitelist | None = None


def get_whitelist() -> CommandWhitelist:
    """Get or create the global whitelist."""
    global _whitelist
    if _whitelist is None:
        _whitelist = CommandWhitelist()
    return _whitelist


def init_whitelist(config: "MachinesConfig") -> CommandWhitelist:  # type: ignore
    """
    Initialize whitelist from configuration.

    Args:
        config: MachinesConfig with machine definitions.

    Returns:
        Initialized CommandWhitelist.
    """

    whitelist = get_whitelist()
    for machine in config.machines:
        whitelist.load_patterns(
            machine.name,
            machine.security.allowed_commands,
            machine.security.forbidden_commands,
        )
    return whitelist
