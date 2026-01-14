"""Tests for TOTP authentication."""

import pytest

# Skip all tests if pyotp not available
pytest.importorskip("pyotp")

from sshmcp.security.totp import (
    TOTPManager,
    TOTPNotConfigured,
    TOTPVerificationFailed,
    get_totp_manager,
    init_totp_manager,
    require_totp,
)


class TestTOTPManager:
    """Tests for TOTPManager."""

    def test_setup_totp(self, tmp_path):
        """Test setting up TOTP for a host."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        result = manager.setup_totp("test-host")

        assert result["host"] == "test-host"
        assert "secret" in result
        assert "uri" in result
        assert len(result["secret"]) == 32  # Base32 encoded
        assert manager.is_totp_required("test-host")

    def test_setup_totp_with_account_name(self, tmp_path):
        """Test setup with custom account name."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        result = manager.setup_totp("test-host", account_name="admin@test")

        assert result["account"] == "admin@test"

    def test_verify_totp_success(self, tmp_path):
        """Test successful TOTP verification."""
        import pyotp

        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        result = manager.setup_totp("test-host")
        secret = result["secret"]

        # Generate valid code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        assert manager.verify_totp("test-host", code) is True

    def test_verify_totp_invalid_code(self, tmp_path):
        """Test TOTP verification with invalid code."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        manager.setup_totp("test-host")

        with pytest.raises(TOTPVerificationFailed):
            manager.verify_totp("test-host", "000000")

    def test_verify_totp_not_configured(self, tmp_path):
        """Test verification for unconfigured host."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        with pytest.raises(TOTPNotConfigured):
            manager.verify_totp("unknown-host", "123456")

    def test_remove_totp(self, tmp_path):
        """Test removing TOTP configuration."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        manager.setup_totp("test-host")
        assert manager.is_totp_required("test-host")

        result = manager.remove_totp("test-host")
        assert result is True
        assert not manager.is_totp_required("test-host")

    def test_remove_totp_not_configured(self, tmp_path):
        """Test removing non-existent configuration."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        result = manager.remove_totp("unknown-host")
        assert result is False

    def test_disable_enable_totp(self, tmp_path):
        """Test disabling and enabling TOTP."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        manager.setup_totp("test-host")
        assert manager.is_totp_required("test-host")

        manager.disable_totp("test-host")
        assert not manager.is_totp_required("test-host")

        manager.enable_totp("test-host")
        assert manager.is_totp_required("test-host")

    def test_get_configured_hosts(self, tmp_path):
        """Test getting list of configured hosts."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        manager.setup_totp("host1")
        manager.setup_totp("host2")

        hosts = manager.get_configured_hosts()
        assert "host1" in hosts
        assert "host2" in hosts

    def test_is_critical_command(self, tmp_path):
        """Test critical command detection."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        assert manager.is_critical_command("rm -rf /var/data")
        assert manager.is_critical_command("shutdown -h now")
        assert manager.is_critical_command("reboot")
        assert manager.is_critical_command("DROP DATABASE test")
        assert not manager.is_critical_command("ls -la")
        assert not manager.is_critical_command("git pull")

    def test_add_critical_pattern(self, tmp_path):
        """Test adding custom critical pattern."""
        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        assert not manager.is_critical_command("custom-dangerous-cmd")

        manager.add_critical_pattern(r".*custom-dangerous.*")
        assert manager.is_critical_command("custom-dangerous-cmd")

    def test_persistence(self, tmp_path):
        """Test that secrets persist across instances."""
        secrets_file = tmp_path / "secrets.json"

        # Create and setup
        manager1 = TOTPManager(secrets_file=str(secrets_file))
        result = manager1.setup_totp("test-host")
        secret = result["secret"]

        # New instance should load secrets
        manager2 = TOTPManager(secrets_file=str(secrets_file))
        assert manager2.is_totp_required("test-host")

        # Should be able to verify with same secret
        import pyotp

        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert manager2.verify_totp("test-host", code)

    def test_verification_callback(self, tmp_path):
        """Test verification callback."""
        import pyotp

        secrets_file = tmp_path / "secrets.json"
        manager = TOTPManager(secrets_file=str(secrets_file))

        callback_data = []

        def callback(host: str, success: bool) -> None:
            callback_data.append((host, success))

        manager.register_verification_callback(callback)
        result = manager.setup_totp("test-host")

        # Successful verification
        totp = pyotp.TOTP(result["secret"])
        manager.verify_totp("test-host", totp.now())

        assert len(callback_data) == 1
        assert callback_data[0] == ("test-host", True)


class TestGlobalTOTPManager:
    """Tests for global TOTP manager functions."""

    def test_get_totp_manager(self):
        """Test getting global manager."""
        manager = get_totp_manager()
        assert isinstance(manager, TOTPManager)

    def test_init_totp_manager(self, tmp_path):
        """Test initializing global manager."""
        secrets_file = tmp_path / "secrets.json"
        manager = init_totp_manager(secrets_file=str(secrets_file))
        assert manager.secrets_file == str(secrets_file)


class TestRequireTOTP:
    """Tests for require_totp function."""

    def test_require_totp_not_configured(self, tmp_path):
        """Test require_totp when not configured."""
        secrets_file = tmp_path / "secrets.json"
        init_totp_manager(secrets_file=str(secrets_file))

        # Should return True when TOTP not required
        assert require_totp("unknown-host") is True

    def test_require_totp_missing_code(self, tmp_path):
        """Test require_totp with missing code."""
        secrets_file = tmp_path / "secrets.json"
        manager = init_totp_manager(secrets_file=str(secrets_file))
        manager.setup_totp("test-host")

        with pytest.raises(TOTPVerificationFailed, match="code required"):
            require_totp("test-host")

    def test_require_totp_valid_code(self, tmp_path):
        """Test require_totp with valid code."""
        import pyotp

        secrets_file = tmp_path / "secrets.json"
        manager = init_totp_manager(secrets_file=str(secrets_file))
        result = manager.setup_totp("test-host")

        totp = pyotp.TOTP(result["secret"])
        code = totp.now()

        assert require_totp("test-host", code) is True
