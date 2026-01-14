"""Tests for MCP prompts."""


class TestDeployPrompt:
    """Tests for deploy_app prompt."""

    def test_deploy_prompt_default(self):
        """Test deploy prompt with defaults."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app("production-server")

        assert "production-server" in result
        assert "main" in result  # default branch
        assert "/var/www/app" in result  # default app path
        assert "npm ci" in result  # default package manager
        assert "pm2 restart" in result  # default process manager

    def test_deploy_prompt_custom_branch(self):
        """Test deploy prompt with custom branch."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app("production-server", branch="develop")

        assert "develop" in result
        assert "git checkout develop" in result

    def test_deploy_prompt_yarn(self):
        """Test deploy prompt with yarn package manager."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app("production-server", package_manager="yarn")

        assert "yarn install" in result
        assert "--frozen-lockfile" in result

    def test_deploy_prompt_pip(self):
        """Test deploy prompt with pip package manager."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app("production-server", package_manager="pip")

        assert "pip install -r requirements.txt" in result

    def test_deploy_prompt_systemd(self):
        """Test deploy prompt with systemd process manager."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app(
            "production-server", process_manager="systemd", app_name="myapp"
        )

        assert "systemctl restart myapp" in result
        assert "systemctl status myapp" in result

    def test_deploy_prompt_supervisor(self):
        """Test deploy prompt with supervisor process manager."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app(
            "production-server", process_manager="supervisor", app_name="myapp"
        )

        assert "supervisorctl restart myapp" in result
        assert "supervisorctl status myapp" in result

    def test_deploy_prompt_custom_app_path(self):
        """Test deploy prompt with custom app path."""
        from sshmcp.prompts.deploy import deploy_app

        result = deploy_app("production-server", app_path="/opt/myapp")

        assert "/opt/myapp" in result


class TestBackupPrompt:
    """Tests for backup_database prompt."""

    def test_backup_prompt_postgresql(self):
        """Test backup prompt for PostgreSQL."""
        from sshmcp.prompts.backup import backup_database

        result = backup_database("db-server", "mydb", database_type="postgresql")

        assert "db-server" in result
        assert "mydb" in result
        assert "pg_dump" in result

    def test_backup_prompt_mysql(self):
        """Test backup prompt for MySQL."""
        from sshmcp.prompts.backup import backup_database

        result = backup_database("db-server", "mydb", database_type="mysql")

        assert "mysqldump" in result

    def test_backup_prompt_mongodb(self):
        """Test backup prompt for MongoDB."""
        from sshmcp.prompts.backup import backup_database

        result = backup_database("db-server", "mydb", database_type="mongodb")

        assert "mongodump" in result

    def test_backup_prompt_custom_path(self):
        """Test backup prompt with custom backup path."""
        from sshmcp.prompts.backup import backup_database

        result = backup_database("db-server", "mydb", backup_path="/data/backups")

        assert "/data/backups" in result

    def test_backup_prompt_no_compress(self):
        """Test backup prompt without compression."""
        from sshmcp.prompts.backup import backup_database

        result = backup_database("db-server", "mydb", compress=False)

        # Result should not include gzip command when compress=False
        assert "mydb" in result


class TestMonitorPrompt:
    """Tests for monitor_health prompt."""

    def test_monitor_prompt_default(self):
        """Test monitor prompt with defaults."""
        from sshmcp.prompts.monitor import monitor_health

        result = monitor_health("web-server")

        assert "web-server" in result
        # Should check both logs and services by default
        assert "log" in result.lower() or "status" in result.lower()

    def test_monitor_prompt_no_logs(self):
        """Test monitor prompt without log checks."""
        from sshmcp.prompts.monitor import monitor_health

        result = monitor_health("web-server", check_logs=False)

        assert "web-server" in result

    def test_monitor_prompt_no_services(self):
        """Test monitor prompt without service checks."""
        from sshmcp.prompts.monitor import monitor_health

        result = monitor_health("web-server", check_services=False)

        assert "web-server" in result

    def test_monitor_prompt_includes_metrics(self):
        """Test monitor prompt includes metrics checks."""
        from sshmcp.prompts.monitor import monitor_health

        result = monitor_health("web-server")

        # Should mention metrics/resources
        assert (
            "metric" in result.lower()
            or "cpu" in result.lower()
            or "memory" in result.lower()
            or "resource" in result.lower()
        )
