"""Tests for command whitelist."""

from sshmcp.security.whitelist import CommandWhitelist, get_whitelist


class TestCommandWhitelist:
    """Tests for CommandWhitelist."""

    def test_whitelist_initialization(self):
        """Test whitelist initializes empty."""
        whitelist = CommandWhitelist()
        assert whitelist._patterns == {}
        assert whitelist._forbidden == {}

    def test_load_patterns(self):
        """Test loading allowed and forbidden patterns."""
        whitelist = CommandWhitelist()
        whitelist.load_patterns(
            "test-server",
            allowed=[r"^ls.*", r"^cat.*"],
            forbidden=[r".*rm -rf.*"],
        )
        assert "test-server" in whitelist._patterns
        assert len(whitelist._patterns["test-server"]) == 2
        assert len(whitelist._forbidden["test-server"]) == 1

    def test_is_allowed_command(self):
        """Test checking if command is allowed."""
        whitelist = CommandWhitelist()
        whitelist.load_patterns(
            "test-server",
            allowed=[r"^ls.*", r"^cat.*"],
            forbidden=[],
        )

        assert whitelist.is_allowed("test-server", "ls -la") is True
        assert whitelist.is_allowed("test-server", "cat /etc/passwd") is True
        assert whitelist.is_allowed("test-server", "rm -rf /") is False

    def test_forbidden_overrides_allowed(self):
        """Test forbidden patterns override allowed."""
        whitelist = CommandWhitelist()
        whitelist.load_patterns(
            "test-server",
            allowed=[r".*"],  # Allow all
            forbidden=[r".*rm -rf.*"],
        )

        assert whitelist.is_allowed("test-server", "ls -la") is True
        assert whitelist.is_allowed("test-server", "rm -rf /") is False

    def test_empty_command(self):
        """Test empty command."""
        whitelist = CommandWhitelist()
        whitelist.load_patterns("test-server", allowed=[r".*"], forbidden=[])
        # Empty command should still match .*
        assert whitelist.is_allowed("test-server", "") is True


class TestGetWhitelist:
    """Tests for get_whitelist function."""

    def test_get_whitelist_singleton(self):
        """Test get_whitelist returns singleton."""
        import sshmcp.security.whitelist as whitelist_module

        whitelist_module._whitelist = None

        wl1 = get_whitelist()
        wl2 = get_whitelist()
        assert wl1 is wl2
