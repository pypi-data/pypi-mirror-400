<p align="center">
  <img src="https://img.shields.io/pypi/v/mcp-ssh-vps?color=blue&label=PyPI" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/mcp-ssh-vps" alt="Python">
  <img src="https://img.shields.io/github/license/LuxVTZ/sshmcp" alt="License">
  <img src="https://img.shields.io/pypi/dm/mcp-ssh-vps?color=green" alt="Downloads">
</p>

<h1 align="center">🔐 SSH MCP Server</h1>

<p align="center">
  <b>Give AI agents secure access to your VPS servers via SSH</b><br>
  Execute commands, transfer files, manage processes — all through Model Context Protocol
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-ide-integration">IDE Integration</a> •
  <a href="#-tools-reference">Tools</a> •
  <a href="#-security">Security</a>
</p>

---

## 🚀 Quick Start

### Install

```bash
# Via pip
pip install mcp-ssh-vps

# Via uvx (recommended for MCP)
uvx mcp-ssh-vps
```

### Add Your First Server

```bash
# Interactive setup
uvx mcp-ssh-vps --help

# Or use the CLI
sshmcp-cli server add --name prod --host 192.168.1.100 --user deploy
sshmcp-cli server test prod
```

### Connect to Your AI Agent

Add to your AI IDE config and start managing servers with natural language!

```
"Deploy my app to the production server"
"Check disk space on all servers"
"Restart nginx on web1 and web2"
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Execute Commands** | Run any shell command on remote servers |
| 📁 **File Operations** | Read, write, and list files via SFTP |
| ⚙️ **Process Management** | Control systemd, pm2, supervisor services |
| 🏷️ **Server Tags** | Group servers with tags for batch operations |
| 🔄 **Batch Execution** | Run commands on multiple servers in parallel |
| 🔒 **Security Profiles** | Strict, moderate, or full access levels |
| 📝 **Audit Logging** | Track all operations for compliance |
| 🔑 **SSH Keys & Passwords** | Support for both authentication methods |

---

## 🔌 IDE Integration

> **Note:** Config is auto-loaded from `~/.sshmcp/machines.json` by default. No env variables required!

### Claude Code

```bash
claude mcp add ssh-vps -- uvx mcp-ssh-vps
```

Or add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### Factory Droid

```bash
droid mcp add ssh-vps "uvx mcp-ssh-vps"
```

Or add to `~/.factory/mcp.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### Qwen Code

```bash
qwen mcp add ssh-vps uvx mcp-ssh-vps
```

Or add to `~/.qwen/settings.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### VS Code + Continue

Add to `.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uvx",
          "args": ["mcp-ssh-vps"]
        }
      }
    ]
  }
}
```

---

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "ssh-vps": {
      "command": "uvx",
      "args": ["mcp-ssh-vps"]
    }
  }
}
```

---

### OpenAI Codex CLI

```bash
codex --mcp-config '{"ssh-vps": {"command": "uvx", "args": ["mcp-ssh-vps"]}}'
```

---

### Any MCP-Compatible Client

Generic stdio configuration:

```json
{
  "command": "uvx",
  "args": ["mcp-ssh-vps"]
}
```

> **Custom config path?** Add `"env": {"SSHMCP_CONFIG_PATH": "/custom/path.json"}`

---

## 🛠️ Tools Reference

### Command Execution

| Tool | Description | Example |
|------|-------------|---------|
| `execute_command` | Run command on server | `execute_command("prod", "docker ps")` |
| `execute_on_multiple` | Run on multiple servers | `execute_on_multiple(["*"], "uptime")` |

### Server Management

| Tool | Description | Example |
|------|-------------|---------|
| `list_servers` | List all servers | `list_servers()` or `list_servers(tag="web")` |
| `add_server` | Add new server | `add_server("web1", "1.2.3.4", "root")` |
| `remove_server` | Remove server | `remove_server("old-server")` |
| `test_connection` | Test SSH connection | `test_connection("prod")` |

### File Operations

| Tool | Description | Example |
|------|-------------|---------|
| `read_file` | Read remote file | `read_file("prod", "/var/log/app.log")` |
| `upload_file` | Upload file | `upload_file("prod", "/tmp/script.sh", "#!/bin/bash\n...")` |
| `list_files` | List directory | `list_files("prod", "/var/log")` |

### Process Management

| Tool | Description | Example |
|------|-------------|---------|
| `manage_process` | Control services | `manage_process("prod", "restart", "nginx")` |

### Help & Info

| Tool | Description | Example |
|------|-------------|---------|
| `get_help` | Get documentation | `get_help("examples")` |
| `get_allowed_commands` | View security config | `get_allowed_commands("prod")` |
| `get_server_info` | Server details | `get_server_info("prod")` |

---

## 🏷️ Server Tags & Batch Operations

### Add servers with tags

```python
add_server("web1", "192.168.1.10", "deploy", tags=["production", "web"])
add_server("web2", "192.168.1.11", "deploy", tags=["production", "web"])
add_server("db1", "192.168.1.20", "deploy", tags=["production", "database"])
```

### Filter by tag

```python
list_servers(tag="web")           # Only web servers
list_servers(tag="production")    # All production servers
```

### Execute on tagged servers

```python
execute_on_multiple(["tag:web"], "nginx -t")           # All web servers
execute_on_multiple(["tag:production"], "uptime")      # All production
execute_on_multiple(["*"], "df -h")                    # ALL servers
```

---

## 🔒 Security

### Security Profiles

| Profile | Allowed Commands | Use Case |
|---------|-----------------|----------|
| `strict` | `git`, `ls`, `cat`, `df`, `uptime` | Read-only monitoring |
| `moderate` | + `docker`, `npm`, `systemctl`, `pm2` | Standard DevOps |
| `full` | All commands (except `rm -rf /`) | Full access |

### Set security level

```python
add_server("prod", "1.2.3.4", "root", security_level="full")
```

### Audit Logging

All commands are logged with timestamps, user, and results:

```
2024-01-15T10:30:00Z | prod | root | docker ps | exit_code=0 | 150ms
```

---

## 📁 Configuration

### Config Location

```
~/.sshmcp/machines.json
```

### Example Config

```json
{
  "machines": [
    {
      "name": "production",
      "host": "192.168.1.100",
      "port": 22,
      "user": "deploy",
      "auth": {
        "type": "key",
        "key_path": "~/.ssh/id_rsa"
      },
      "security": {
        "allowed_commands": [".*"],
        "forbidden_commands": [".*rm\\s+-rf\\s+/$"],
        "timeout_seconds": 120
      },
      "tags": ["production", "web"],
      "description": "Main production server"
    }
  ]
}
```

### Environment Variable

```bash
export SSHMCP_CONFIG_PATH=/custom/path/machines.json
```

---

## 📖 Usage Examples

### Check status of all servers

```
User: Check the status of all my servers
AI: I'll run uptime on all configured servers...

execute_on_multiple(["*"], "uptime && df -h | head -5")
```

### Deploy application

```
User: Deploy the latest code to production
AI: I'll pull the latest changes and restart the service...

execute_command("prod", "cd /app && git pull origin main")
execute_command("prod", "npm install --production")
execute_command("prod", "pm2 restart all")
```

### Debug server issues

```
User: Why is the web server slow?
AI: Let me check system resources and logs...

execute_command("web1", "top -bn1 | head -20")
execute_command("web1", "tail -50 /var/log/nginx/error.log")
execute_command("web1", "free -m && df -h")
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```bash
git clone https://github.com/LuxVTZ/sshmcp.git
cd sshmcp
pip install -e ".[dev]"
pytest
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for the AI agent ecosystem<br>
  <a href="https://pypi.org/project/mcp-ssh-vps/">PyPI</a> •
  <a href="https://github.com/LuxVTZ/sshmcp">GitHub</a> •
  <a href="https://github.com/LuxVTZ/sshmcp/issues">Issues</a>
</p>
