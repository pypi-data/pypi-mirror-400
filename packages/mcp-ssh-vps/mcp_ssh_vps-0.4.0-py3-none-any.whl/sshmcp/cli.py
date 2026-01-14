"""CLI interface for SSH MCP server management."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
import structlog

from sshmcp.models.machine import (
    AuthConfig,
    MachineConfig,
    MachinesConfig,
    SecurityConfig,
)

logger = structlog.get_logger()

DEFAULT_CONFIG_PATH = Path.home() / ".sshmcp" / "machines.json"


def get_config_path() -> Path:
    """Get configuration file path."""
    env_path = os.environ.get("SSHMCP_CONFIG_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_CONFIG_PATH


def load_machines_config() -> MachinesConfig:
    """Load machines configuration."""
    config_path = get_config_path()
    if not config_path.exists():
        return MachinesConfig(machines=[])

    with open(config_path, "r") as f:
        data = json.load(f)
    return MachinesConfig.model_validate(data)


def save_machines_config(config: MachinesConfig) -> None:
    """Save machines configuration."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)

    click.echo(f"Configuration saved to {config_path}")


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """SSH MCP Server - Manage VPS servers for AI agents."""
    pass


@cli.group()
def server() -> None:
    """Manage VPS servers."""
    pass


@server.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_servers(verbose: bool) -> None:
    """List all configured servers."""
    config = load_machines_config()

    if not config.machines:
        click.echo("No servers configured yet.")
        click.echo("\nAdd a server with: sshmcp server add")
        return

    click.echo(f"\n{'Name':<20} {'Host':<25} {'User':<15} {'Auth':<10}")
    click.echo("-" * 70)

    for machine in config.machines:
        auth_type = machine.auth.type
        click.echo(
            f"{machine.name:<20} {machine.host:<25} {machine.user:<15} {auth_type:<10}"
        )

        if verbose:
            click.echo(f"  Port: {machine.port}")
            if machine.description:
                click.echo(f"  Description: {machine.description}")
            click.echo(f"  Timeout: {machine.security.timeout_seconds}s")
            click.echo(f"  Allowed commands: {len(machine.security.allowed_commands)}")
            click.echo()

    click.echo(f"\nTotal: {len(config.machines)} server(s)")


@server.command("add")
@click.option("--name", "-n", prompt="Server name", help="Unique name for the server")
@click.option(
    "--host", "-h", prompt="Host (IP or domain)", help="Server hostname or IP"
)
@click.option(
    "--port", "-p", default=22, prompt="SSH port", help="SSH port (default: 22)"
)
@click.option("--user", "-u", prompt="SSH user", help="SSH username")
@click.option(
    "--auth-type",
    "-a",
    type=click.Choice(["key", "password"]),
    prompt="Authentication type",
    help="Authentication method",
)
@click.option(
    "--key-path", "-k", default="~/.ssh/id_rsa", help="Path to SSH private key"
)
@click.option("--password", help="SSH password (will prompt if auth-type is password)")
@click.option("--description", "-d", default="", help="Server description")
@click.option(
    "--security-profile",
    "-s",
    type=click.Choice(["strict", "moderate", "full"]),
    default="moderate",
    help="Security profile",
)
def add_server(
    name: str,
    host: str,
    port: int,
    user: str,
    auth_type: str,
    key_path: str,
    password: Optional[str],
    description: str,
    security_profile: str,
) -> None:
    """Add a new VPS server."""
    config = load_machines_config()

    # Check if server already exists
    if config.has_machine(name):
        click.echo(f"Error: Server '{name}' already exists.", err=True)
        sys.exit(1)

    # Handle authentication
    if auth_type == "key":
        key_path_expanded = str(Path(key_path).expanduser())
        if not Path(key_path_expanded).exists():
            click.echo(f"Warning: Key file not found: {key_path_expanded}")
            if not click.confirm("Continue anyway?"):
                sys.exit(1)
        auth = AuthConfig(type="key", key_path=key_path)
    else:
        if not password:
            password = click.prompt("SSH password", hide_input=True)
        auth = AuthConfig(type="password", password=password)

    # Security profiles
    security_profiles = {
        "strict": SecurityConfig(
            allowed_commands=[
                r"^git (pull|status|log|diff).*",
                r"^ls .*",
                r"^cat .*",
                r"^tail .*",
                r"^head .*",
                r"^pwd$",
                r"^whoami$",
                r"^df -h$",
                r"^free -m$",
                r"^uptime$",
            ],
            forbidden_commands=[
                r".*rm\s+-rf.*",
                r".*sudo.*",
                r".*su\s+-.*",
                r".*dd\s+if=.*",
                r".*mkfs\..*",
                r".*chmod\s+777.*",
            ],
            timeout_seconds=30,
        ),
        "moderate": SecurityConfig(
            allowed_commands=[
                r"^git .*",
                r"^npm .*",
                r"^yarn .*",
                r"^pip .*",
                r"^pm2 .*",
                r"^systemctl (status|restart).*",
                r"^docker (ps|logs|stats).*",
                r"^ls .*",
                r"^cat .*",
                r"^tail .*",
                r"^head .*",
                r"^pwd$",
                r"^whoami$",
                r"^df -h$",
                r"^free -m$",
                r"^uptime$",
                r"^ps aux$",
                r"^top -bn1$",
            ],
            forbidden_commands=[
                r".*rm\s+-rf\s+/.*",
                r".*sudo\s+rm.*",
                r".*dd\s+if=.*",
            ],
            timeout_seconds=60,
        ),
        "full": SecurityConfig(
            allowed_commands=[r".*"],
            forbidden_commands=[r".*rm\s+-rf\s+/$"],
            timeout_seconds=120,
        ),
    }

    security = security_profiles[security_profile]

    # Create machine config
    machine = MachineConfig(
        name=name,
        host=host,
        port=port,
        user=user,
        auth=auth,
        security=security,
        description=description or None,
    )

    config.machines.append(machine)
    save_machines_config(config)

    click.echo(f"\n✓ Server '{name}' added successfully!")
    click.echo(f"  Host: {host}:{port}")
    click.echo(f"  User: {user}")
    click.echo(f"  Auth: {auth_type}")
    click.echo(f"  Security: {security_profile}")

    if click.confirm("\nTest connection now?"):
        _test_connection(machine)


@server.command("remove")
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def remove_server(name: str, force: bool) -> None:
    """Remove a VPS server."""
    config = load_machines_config()

    if not config.has_machine(name):
        click.echo(f"Error: Server '{name}' not found.", err=True)
        sys.exit(1)

    if not force:
        if not click.confirm(f"Remove server '{name}'?"):
            click.echo("Cancelled.")
            return

    config.machines = [m for m in config.machines if m.name != name]
    save_machines_config(config)

    click.echo(f"✓ Server '{name}' removed.")


@server.command("test")
@click.argument("name")
def test_server(name: str) -> None:
    """Test connection to a server."""
    config = load_machines_config()

    machine = config.get_machine(name)
    if not machine:
        click.echo(f"Error: Server '{name}' not found.", err=True)
        sys.exit(1)

    _test_connection(machine)


@server.command("edit")
@click.argument("name")
def edit_server(name: str) -> None:
    """Edit server configuration (opens in editor)."""
    config_path = get_config_path()

    if not config_path.exists():
        click.echo("No configuration file found.")
        return

    editor = os.environ.get("EDITOR", "nano")
    os.system(f"{editor} {config_path}")


@server.command("import-ssh")
@click.option("--ssh-config", default="~/.ssh/config", help="Path to SSH config")
def import_from_ssh(ssh_config: str) -> None:
    """Import servers from ~/.ssh/config."""
    ssh_config_path = Path(ssh_config).expanduser()

    if not ssh_config_path.exists():
        click.echo(f"SSH config not found: {ssh_config_path}", err=True)
        sys.exit(1)

    # Parse SSH config
    hosts = _parse_ssh_config(ssh_config_path)

    if not hosts:
        click.echo("No hosts found in SSH config.")
        return

    click.echo(f"Found {len(hosts)} host(s) in SSH config:\n")
    for host in hosts:
        click.echo(f"  - {host['name']}: {host.get('hostname', 'N/A')}")

    if not click.confirm("\nImport these hosts?"):
        return

    config = load_machines_config()
    imported = 0

    for host in hosts:
        if config.has_machine(host["name"]):
            click.echo(f"  Skipping '{host['name']}' (already exists)")
            continue

        try:
            machine = MachineConfig(
                name=host["name"],
                host=host.get("hostname", host["name"]),
                port=int(host.get("port", 22)),
                user=host.get("user", os.environ.get("USER", "root")),
                auth=AuthConfig(
                    type="key", key_path=host.get("identityfile", "~/.ssh/id_rsa")
                ),
                security=SecurityConfig(
                    allowed_commands=[r".*"],
                    forbidden_commands=[r".*rm\s+-rf\s+/$"],
                ),
                description="Imported from SSH config",
            )
            config.machines.append(machine)
            imported += 1
            click.echo(f"  ✓ Imported '{host['name']}'")
        except Exception as e:
            click.echo(f"  ✗ Failed to import '{host['name']}': {e}")

    if imported > 0:
        save_machines_config(config)
        click.echo(f"\n✓ Imported {imported} server(s)")


def _parse_ssh_config(path: Path) -> list[dict]:
    """Parse SSH config file."""
    hosts = []
    current_host = None

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(None, 1)
            if len(parts) != 2:
                continue

            key, value = parts[0].lower(), parts[1]

            if key == "host":
                if current_host and current_host["name"] != "*":
                    hosts.append(current_host)
                current_host = {"name": value}
            elif current_host:
                if key == "hostname":
                    current_host["hostname"] = value
                elif key == "port":
                    current_host["port"] = value
                elif key == "user":
                    current_host["user"] = value
                elif key == "identityfile":
                    current_host["identityfile"] = value

    if current_host and current_host["name"] != "*":
        hosts.append(current_host)

    return hosts


def _test_connection(machine: MachineConfig) -> bool:
    """Test SSH connection to a machine."""
    click.echo(f"\nTesting connection to {machine.name}...")

    try:
        from sshmcp.ssh.client import SSHClient

        client = SSHClient(machine)
        client.connect()

        result = client.execute("echo 'Connection successful!' && hostname && uptime")
        client.disconnect()

        if result.exit_code == 0:
            click.echo("✓ Connection successful!")
            click.echo(f"\n{result.stdout}")
            return True
        else:
            click.echo(f"✗ Command failed: {result.stderr}", err=True)
            return False

    except Exception as e:
        click.echo(f"✗ Connection failed: {e}", err=True)
        return False


@cli.command("run")
@click.option(
    "--transport",
    "-t",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport type",
)
@click.option("--port", "-p", default=8000, help="HTTP port")
def run_server(transport: str, port: int) -> None:
    """Start the MCP server."""
    from sshmcp.server import main as server_main

    # Set config path
    os.environ["SSHMCP_CONFIG_PATH"] = str(get_config_path())

    if transport == "http":
        sys.argv = ["sshmcp", "--transport", "streamable-http", "--port", str(port)]
    else:
        sys.argv = ["sshmcp"]

    server_main()


@cli.command("init")
def init_config() -> None:
    """Initialize configuration with interactive wizard."""
    config_path = get_config_path()

    click.echo("SSH MCP Server Setup Wizard")
    click.echo("=" * 40)

    if config_path.exists():
        if not click.confirm(f"\nConfig already exists at {config_path}. Overwrite?"):
            click.echo("Cancelled.")
            return

    click.echo("\nLet's add your first VPS server.\n")

    # Invoke add command
    ctx = click.Context(add_server)
    ctx.invoke(add_server)

    click.echo("\n" + "=" * 40)
    click.echo("Setup complete!")
    click.echo(f"\nConfig file: {config_path}")
    click.echo("\nNext steps:")
    click.echo("  1. Add more servers: sshmcp server add")
    click.echo("  2. Start MCP server: sshmcp run")
    click.echo("  3. Configure your AI agent (see docs/integration.md)")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
