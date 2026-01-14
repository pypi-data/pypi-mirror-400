"""Security validation for commands and paths."""

import os
import re
from typing import List, Tuple

import structlog

from sshmcp.models.machine import SecurityConfig

logger = structlog.get_logger()


class ValidationError(Exception):
    """Command or path validation failed."""

    pass


def validate_command(
    command: str,
    security: SecurityConfig,
) -> Tuple[bool, str | None]:
    """
    Validate command against security rules.

    Args:
        command: Command to validate.
        security: Security configuration with allowed/forbidden patterns.

    Returns:
        Tuple of (is_valid, error_message).
    """
    command = command.strip()

    if not command:
        return False, "Empty command"

    # Check forbidden commands first (blacklist)
    for pattern in security.forbidden_commands:
        try:
            if re.match(pattern, command, re.IGNORECASE):
                logger.warning(
                    "command_forbidden",
                    command=command,
                    pattern=pattern,
                )
                return False, f"Command matches forbidden pattern: {pattern}"
        except re.error as e:
            logger.error("invalid_regex_pattern", pattern=pattern, error=str(e))
            continue

    # If no allowed commands specified, allow all (except forbidden)
    if not security.allowed_commands:
        return True, None

    # Check allowed commands (whitelist)
    for pattern in security.allowed_commands:
        try:
            if re.match(pattern, command, re.IGNORECASE):
                logger.debug(
                    "command_allowed",
                    command=command,
                    pattern=pattern,
                )
                return True, None
        except re.error as e:
            logger.error("invalid_regex_pattern", pattern=pattern, error=str(e))
            continue

    logger.warning(
        "command_not_allowed",
        command=command,
    )
    return False, "Command not in allowed list"


def validate_path(
    path: str,
    security: SecurityConfig,
    check_type: str = "read",
) -> Tuple[bool, str | None]:
    """
    Validate file path against security rules.

    Args:
        path: Path to validate.
        security: Security configuration with allowed/forbidden paths.
        check_type: Type of operation ('read' or 'write').

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not path:
        return False, "Empty path"

    # Normalize path
    normalized = normalize_path(path)

    # Check for path traversal attacks
    if ".." in normalized or normalized.startswith("../"):
        logger.warning(
            "path_traversal_attempt",
            path=path,
            normalized=normalized,
        )
        return False, "Path traversal not allowed"

    # Check forbidden paths
    for forbidden in security.forbidden_paths:
        forbidden_normalized = normalize_path(forbidden)
        if (
            normalized.startswith(forbidden_normalized)
            or normalized == forbidden_normalized
        ):
            logger.warning(
                "path_forbidden",
                path=path,
                forbidden=forbidden,
            )
            return False, f"Path is forbidden: {forbidden}"

    # If no allowed paths specified, allow all (except forbidden)
    if not security.allowed_paths:
        return True, None

    # Check allowed paths
    for allowed in security.allowed_paths:
        allowed_normalized = normalize_path(allowed)
        if (
            normalized.startswith(allowed_normalized)
            or normalized == allowed_normalized
        ):
            logger.debug(
                "path_allowed",
                path=path,
                allowed=allowed,
            )
            return True, None

    logger.warning(
        "path_not_allowed",
        path=path,
    )
    return False, "Path not in allowed list"


def normalize_path(path: str) -> str:
    """
    Normalize a file path.

    Args:
        path: Path to normalize.

    Returns:
        Normalized path.
    """
    # Expand user home directory
    if path.startswith("~"):
        path = os.path.expanduser(path)

    # Remove trailing slashes
    path = path.rstrip("/")

    # Collapse multiple slashes
    while "//" in path:
        path = path.replace("//", "/")

    return path


def check_command_safety(command: str) -> List[str]:
    """
    Check command for potential safety issues.

    Returns list of warnings (empty if no issues found).

    Args:
        command: Command to check.

    Returns:
        List of warning messages.
    """
    warnings = []

    # Dangerous patterns to warn about
    dangerous_patterns = [
        (r"rm\s+-rf", "Recursive force delete detected"),
        (r"rm\s+.*\*", "Wildcard delete detected"),
        (r">\s*/dev/", "Writing to /dev/ detected"),
        (r"chmod\s+777", "World-writable permissions detected"),
        (r"\|\s*sh", "Piping to shell detected"),
        (r"\|\s*bash", "Piping to bash detected"),
        (r"curl.*\|\s*", "Curl piped to command detected"),
        (r"wget.*\|\s*", "Wget piped to command detected"),
        (r"eval\s+", "Eval command detected"),
        (r";\s*rm\s+", "Command chaining with rm detected"),
        (r"&&\s*rm\s+", "Command chaining with rm detected"),
        (r"\$\(.*\)", "Command substitution detected"),
        (r"`.*`", "Backtick command substitution detected"),
    ]

    for pattern, warning in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(warning)

    return warnings


def sanitize_command_for_log(command: str) -> str:
    """
    Sanitize command for logging (hide potential secrets).

    Args:
        command: Command to sanitize.

    Returns:
        Sanitized command safe for logging.
    """
    # Patterns that might contain secrets
    secret_patterns = [
        (r"password[=:\s]+\S+", "password=***"),
        (r"passwd[=:\s]+\S+", "passwd=***"),
        (r"secret[=:\s]+\S+", "secret=***"),
        (r"token[=:\s]+\S+", "token=***"),
        (r"api[_-]?key[=:\s]+\S+", "api_key=***"),
        (r"AWS_SECRET[=:\s]+\S+", "AWS_SECRET=***"),
    ]

    sanitized = command
    for pattern, replacement in secret_patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized
