"""Tests for MCP tools."""

from unittest.mock import MagicMock, patch


class TestListServers:
    """Tests for list_servers tool."""

    def test_list_servers_empty(self, tmp_path):
        """Test listing servers when no servers configured."""
        config_file = tmp_path / "machines.json"
        config_file.write_text('{"machines": []}')

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            from sshmcp.tools.servers import list_servers

            result = list_servers()

        assert result["count"] == 0
        assert result["servers"] == []

    def test_list_servers_with_machines(self, tmp_path):
        """Test listing servers with configured machines."""
        config_file = tmp_path / "machines.json"
        config_file.write_text(
            """{
            "machines": [{
                "name": "test-server",
                "host": "192.168.1.1",
                "port": 22,
                "user": "testuser",
                "auth": {"type": "key", "key_path": "~/.ssh/id_rsa"},
                "security": {"allowed_commands": [".*"], "forbidden_commands": [], "timeout_seconds": 30}
            }]
        }"""
        )

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            from sshmcp.tools.servers import list_servers

            result = list_servers()

        assert result["count"] == 1
        assert len(result["servers"]) == 1
        assert result["servers"][0]["name"] == "test-server"


class TestHelpers:
    """Tests for helper tools."""

    def test_get_help_all(self):
        """Test get_help returns documentation."""
        from sshmcp.tools.helpers import get_help

        result = get_help()
        # Result should be a dict with documentation
        assert isinstance(result, dict)


class TestServerManagement:
    """Tests for server management tools."""

    def test_add_server_creates_config(self, tmp_path):
        """Test add_server creates machine config."""
        config_file = tmp_path / "machines.json"
        config_file.write_text('{"machines": []}')

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            with patch("sshmcp.tools.servers.get_pool") as mock_pool:
                with patch("sshmcp.tools.servers.init_whitelist"):
                    with patch("sshmcp.tools.servers.reload_global_config"):
                        mock_pool.return_value.register_machine = MagicMock()

                        from sshmcp.tools.servers import add_server

                        result = add_server(
                            name="new-server",
                            host="192.168.1.100",
                            user="deploy",
                            port=22,
                            auth_type="key",
                            key_path="~/.ssh/id_rsa",
                        )

        assert result["success"] is True
        assert result["name"] == "new-server"
        assert result["host"] == "192.168.1.100"

    def test_add_server_duplicate_fails(self, tmp_path):
        """Test add_server fails for duplicate name."""
        config_file = tmp_path / "machines.json"
        config_file.write_text(
            """{
            "machines": [{
                "name": "existing",
                "host": "192.168.1.1",
                "port": 22,
                "user": "testuser",
                "auth": {"type": "key", "key_path": "~/.ssh/id_rsa"},
                "security": {"allowed_commands": [".*"], "forbidden_commands": [], "timeout_seconds": 30}
            }]
        }"""
        )

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            from sshmcp.tools.servers import add_server

            result = add_server(
                name="existing",
                host="192.168.1.100",
                user="deploy",
            )

        assert result["success"] is False
        assert "already exists" in result["error"]

    def test_remove_server(self, tmp_path):
        """Test remove_server removes machine."""
        config_file = tmp_path / "machines.json"
        config_file.write_text(
            """{
            "machines": [{
                "name": "to-remove",
                "host": "192.168.1.1",
                "port": 22,
                "user": "testuser",
                "auth": {"type": "key", "key_path": "~/.ssh/id_rsa"},
                "security": {"allowed_commands": [".*"], "forbidden_commands": [], "timeout_seconds": 30}
            }]
        }"""
        )

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            with patch("sshmcp.tools.servers.reload_global_config"):
                from sshmcp.tools.servers import remove_server

                result = remove_server(name="to-remove")

        assert result["success"] is True

    def test_remove_server_not_found(self, tmp_path):
        """Test remove_server fails for non-existent server."""
        config_file = tmp_path / "machines.json"
        config_file.write_text('{"machines": []}')

        with patch("sshmcp.tools.servers._get_config_path", return_value=config_file):
            from sshmcp.tools.servers import remove_server

            result = remove_server(name="non-existent")

        assert result["success"] is False
        assert "not found" in result["error"]
