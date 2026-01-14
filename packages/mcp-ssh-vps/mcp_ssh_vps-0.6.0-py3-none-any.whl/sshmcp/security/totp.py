"""TOTP-based two-factor authentication for critical operations."""

import io
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import structlog

logger = structlog.get_logger()

# Optional imports for TOTP
try:
    import pyotp

    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None  # type: ignore

try:
    import qrcode

    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None  # type: ignore


class TOTPError(Exception):
    """Error in TOTP operations."""

    pass


class TOTPNotConfigured(TOTPError):
    """TOTP is not configured for this host."""

    pass


class TOTPVerificationFailed(TOTPError):
    """TOTP verification failed."""

    pass


class TOTPManager:
    """
    TOTP-based two-factor authentication manager.

    Provides TOTP setup, verification, and management for critical SSH operations.
    """

    def __init__(
        self,
        secrets_file: str | None = None,
        issuer: str = "SSH-MCP",
        digits: int = 6,
        interval: int = 30,
    ) -> None:
        """
        Initialize TOTP manager.

        Args:
            secrets_file: Path to encrypted secrets file.
            issuer: Issuer name for TOTP (shown in authenticator apps).
            digits: Number of digits in TOTP code.
            interval: Time interval in seconds.
        """
        if not PYOTP_AVAILABLE:
            raise TOTPError(
                "pyotp package is required for TOTP. Install with: pip install pyotp"
            )

        self.secrets_file = secrets_file or str(
            Path.home() / ".sshmcp" / "totp_secrets.json"
        )
        self.issuer = issuer
        self.digits = digits
        self.interval = interval

        self._secrets: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._critical_commands: list[str] = [
            r".*rm\s+-rf.*",
            r".*shutdown.*",
            r".*reboot.*",
            r".*systemctl\s+(stop|disable).*",
            r".*docker\s+(rm|stop|kill).*",
            r".*DROP\s+DATABASE.*",
            r".*DROP\s+TABLE.*",
        ]
        self._verification_callbacks: list[Callable[[str, bool], None]] = []

        self._load_secrets()

    def setup_totp(self, host: str, account_name: str | None = None) -> dict:
        """
        Set up TOTP for a host.

        Args:
            host: Host name to set up TOTP for.
            account_name: Account name (default: host name).

        Returns:
            Dictionary with secret, provisioning URI, and optional QR code.
        """
        account = account_name or host
        secret = pyotp.random_base32()

        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.interval)
        uri = totp.provisioning_uri(name=account, issuer_name=self.issuer)

        result = {
            "host": host,
            "secret": secret,
            "uri": uri,
            "account": account,
            "issuer": self.issuer,
        }

        # Generate QR code if available
        if QRCODE_AVAILABLE:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)

            # Generate ASCII QR code
            buffer = io.StringIO()
            qr.print_ascii(out=buffer)
            result["qr_ascii"] = buffer.getvalue()

        # Save secret
        with self._lock:
            self._secrets[host] = {
                "secret": secret,
                "account": account,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "enabled": True,
            }
            self._save_secrets()

        logger.info("totp_setup", host=host)
        return result

    def verify_totp(self, host: str, code: str) -> bool:
        """
        Verify a TOTP code for a host.

        Args:
            host: Host name.
            code: TOTP code to verify.

        Returns:
            True if verification successful.

        Raises:
            TOTPNotConfigured: If TOTP not set up for host.
            TOTPVerificationFailed: If code is invalid.
        """
        with self._lock:
            if host not in self._secrets:
                raise TOTPNotConfigured(f"TOTP not configured for host: {host}")

            host_config = self._secrets[host]
            if not host_config.get("enabled", True):
                return True  # TOTP disabled for this host

            secret = host_config["secret"]

        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.interval)

        # Verify with 1-step window for clock drift
        is_valid = totp.verify(code, valid_window=1)

        # Notify callbacks
        for callback in self._verification_callbacks:
            try:
                callback(host, is_valid)
            except Exception:
                pass

        if not is_valid:
            logger.warning("totp_verification_failed", host=host)
            raise TOTPVerificationFailed("Invalid TOTP code")

        logger.info("totp_verified", host=host)
        return True

    def is_totp_required(self, host: str) -> bool:
        """
        Check if TOTP is required for a host.

        Args:
            host: Host name.

        Returns:
            True if TOTP is configured and enabled.
        """
        with self._lock:
            if host not in self._secrets:
                return False
            return self._secrets[host].get("enabled", True)

    def is_critical_command(self, command: str) -> bool:
        """
        Check if a command is considered critical (requires TOTP).

        Args:
            command: Command to check.

        Returns:
            True if command is critical.
        """
        import re

        command_lower = command.lower()
        for pattern in self._critical_commands:
            if re.match(pattern, command_lower, re.IGNORECASE):
                return True
        return False

    def add_critical_pattern(self, pattern: str) -> None:
        """
        Add a pattern for critical commands.

        Args:
            pattern: Regex pattern to add.
        """
        self._critical_commands.append(pattern)

    def remove_totp(self, host: str) -> bool:
        """
        Remove TOTP configuration for a host.

        Args:
            host: Host name.

        Returns:
            True if removed, False if not configured.
        """
        with self._lock:
            if host not in self._secrets:
                return False

            del self._secrets[host]
            self._save_secrets()

        logger.info("totp_removed", host=host)
        return True

    def disable_totp(self, host: str) -> bool:
        """
        Temporarily disable TOTP for a host.

        Args:
            host: Host name.

        Returns:
            True if disabled.
        """
        with self._lock:
            if host not in self._secrets:
                return False

            self._secrets[host]["enabled"] = False
            self._save_secrets()

        logger.info("totp_disabled", host=host)
        return True

    def enable_totp(self, host: str) -> bool:
        """
        Enable TOTP for a host.

        Args:
            host: Host name.

        Returns:
            True if enabled.
        """
        with self._lock:
            if host not in self._secrets:
                return False

            self._secrets[host]["enabled"] = True
            self._save_secrets()

        logger.info("totp_enabled", host=host)
        return True

    def get_configured_hosts(self) -> list[str]:
        """Get list of hosts with TOTP configured."""
        with self._lock:
            return list(self._secrets.keys())

    def register_verification_callback(
        self, callback: Callable[[str, bool], None]
    ) -> None:
        """
        Register a callback for verification events.

        Args:
            callback: Function called with (host, success).
        """
        self._verification_callbacks.append(callback)

    def _load_secrets(self) -> None:
        """Load secrets from file."""
        path = Path(self.secrets_file)
        if not path.exists():
            return

        try:
            with open(path) as f:
                self._secrets = json.load(f)
            logger.info("totp_secrets_loaded", count=len(self._secrets))
        except Exception as e:
            logger.error("totp_secrets_load_error", error=str(e))

    def _save_secrets(self) -> None:
        """Save secrets to file."""
        path = Path(self.secrets_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w") as f:
                json.dump(self._secrets, f, indent=2)
            # Set restrictive permissions
            os.chmod(path, 0o600)
        except Exception as e:
            logger.error("totp_secrets_save_error", error=str(e))


# Global TOTP manager instance
_totp_manager: TOTPManager | None = None


def get_totp_manager() -> TOTPManager:
    """Get or create the global TOTP manager."""
    global _totp_manager
    if _totp_manager is None:
        _totp_manager = TOTPManager()
    return _totp_manager


def init_totp_manager(
    secrets_file: str | None = None,
    issuer: str = "SSH-MCP",
) -> TOTPManager:
    """
    Initialize the global TOTP manager.

    Args:
        secrets_file: Path to secrets file.
        issuer: Issuer name for TOTP.

    Returns:
        Initialized TOTPManager.
    """
    global _totp_manager
    _totp_manager = TOTPManager(secrets_file=secrets_file, issuer=issuer)
    return _totp_manager


def require_totp(host: str, code: str | None = None) -> bool:
    """
    Check if TOTP is required and verify if code provided.

    Args:
        host: Host name.
        code: Optional TOTP code.

    Returns:
        True if verified or not required.

    Raises:
        TOTPVerificationFailed: If code required but invalid/missing.
    """
    manager = get_totp_manager()

    if not manager.is_totp_required(host):
        return True

    if code is None:
        raise TOTPVerificationFailed(f"TOTP code required for host: {host}")

    return manager.verify_totp(host, code)
