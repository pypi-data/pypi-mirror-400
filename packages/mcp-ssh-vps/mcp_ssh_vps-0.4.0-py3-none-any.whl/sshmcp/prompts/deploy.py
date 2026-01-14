"""MCP Prompt for application deployment."""


def deploy_app(
    host: str,
    branch: str = "main",
    app_path: str = "/var/www/app",
    package_manager: str = "npm",
    process_manager: str = "pm2",
    app_name: str = "app",
) -> str:
    """
    Generate deployment prompt for application.

    Creates a step-by-step deployment plan for a web application.

    Args:
        host: Target host name.
        branch: Git branch to deploy (default: main).
        app_path: Application directory path.
        package_manager: Package manager (npm, yarn, pip).
        process_manager: Process manager (pm2, systemd, supervisor).
        app_name: Application name for process manager.

    Returns:
        Deployment instructions as multi-line string.
    """
    # Build install command based on package manager
    install_commands = {
        "npm": "npm ci --production",
        "yarn": "yarn install --frozen-lockfile --production",
        "pip": "pip install -r requirements.txt",
        "poetry": "poetry install --no-dev",
    }
    install_cmd = install_commands.get(package_manager, "npm install")

    # Build restart command based on process manager
    restart_commands = {
        "pm2": f"pm2 restart {app_name}",
        "systemd": f"systemctl restart {app_name}",
        "supervisor": f"supervisorctl restart {app_name}",
    }
    restart_cmd = restart_commands.get(process_manager, f"pm2 restart {app_name}")

    # Build status command
    status_commands = {
        "pm2": f"pm2 status {app_name}",
        "systemd": f"systemctl status {app_name}",
        "supervisor": f"supervisorctl status {app_name}",
    }
    status_cmd = status_commands.get(process_manager, f"pm2 status {app_name}")

    return f"""Deploy application to {host}:

## Pre-deployment Checks
1. Check server status:
   - Use get_status resource for {host} to verify server is online
   - Use get_metrics resource for {host} to check available resources

2. Check current application state:
   ```
   execute_command(host="{host}", command="cd {app_path} && git status")
   ```

## Deployment Steps

3. Pull latest code from branch {branch}:
   ```
   execute_command(host="{host}", command="cd {app_path} && git fetch origin && git checkout {branch} && git pull origin {branch}")
   ```

4. Install dependencies:
   ```
   execute_command(host="{host}", command="cd {app_path} && {install_cmd}")
   ```

5. Build application (if needed):
   ```
   execute_command(host="{host}", command="cd {app_path} && npm run build")
   ```

6. Restart application:
   ```
   execute_command(host="{host}", command="{restart_cmd}")
   ```

## Post-deployment Verification

7. Check application status:
   ```
   execute_command(host="{host}", command="{status_cmd}")
   ```

8. Check application logs:
   - Use get_logs resource for {host} with path "var/log/{app_name}.log" or appropriate log path

9. Verify health endpoint (if available):
   ```
   execute_command(host="{host}", command="curl -s http://localhost:3000/health")
   ```

## Rollback Plan
If deployment fails:
1. Checkout previous commit:
   ```
   execute_command(host="{host}", command="cd {app_path} && git checkout HEAD~1")
   ```
2. Reinstall dependencies and restart application

## Notes
- Branch: {branch}
- Application path: {app_path}
- Package manager: {package_manager}
- Process manager: {process_manager}
"""
