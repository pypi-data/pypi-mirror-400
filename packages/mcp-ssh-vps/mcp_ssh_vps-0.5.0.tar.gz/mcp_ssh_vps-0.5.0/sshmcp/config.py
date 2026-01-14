"""Configuration loading and validation."""

import json
import os
from pathlib import Path

import structlog

from sshmcp.models.machine import MachineConfig, MachinesConfig

logger = structlog.get_logger()

DEFAULT_CONFIG_PATH = "config/machines.json"
CONFIG_ENV_VAR = "SSHMCP_CONFIG_PATH"

_config_cache: MachinesConfig | None = None


class ConfigurationError(Exception):
    """Error loading or validating configuration."""

    pass


def get_config_path() -> Path:
    """Get configuration file path from environment or default."""
    env_path = os.environ.get(CONFIG_ENV_VAR)
    if env_path:
        return Path(env_path).expanduser().resolve()

    # Try relative path from current directory
    cwd_config = Path.cwd() / DEFAULT_CONFIG_PATH
    if cwd_config.exists():
        return cwd_config

    # Try relative to package
    package_dir = Path(__file__).parent.parent
    package_config = package_dir / DEFAULT_CONFIG_PATH
    if package_config.exists():
        return package_config

    # Return default path (will raise error if not exists)
    return cwd_config


def load_config(config_path: str | Path | None = None) -> MachinesConfig:
    """
    Load and validate configuration from JSON file.

    Args:
        config_path: Optional path to configuration file.
                    If not provided, uses SSHMCP_CONFIG_PATH env var or default.

    Returns:
        MachinesConfig object with validated configuration.

    Raises:
        ConfigurationError: If file not found, invalid JSON, or validation fails.
    """
    global _config_cache

    if config_path is None:
        path = get_config_path()
    else:
        path = Path(config_path).expanduser().resolve()

    logger.info("loading_config", path=str(path))

    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
    except PermissionError:
        raise ConfigurationError(f"Permission denied reading configuration: {path}")
    except Exception as e:
        raise ConfigurationError(f"Error reading configuration file: {e}")

    try:
        config = MachinesConfig.model_validate(data)
    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed: {e}")

    logger.info(
        "config_loaded",
        machines_count=len(config.machines),
        machine_names=config.get_machine_names(),
    )

    _config_cache = config
    return config


def get_config() -> MachinesConfig:
    """
    Get cached configuration or load it.

    Returns:
        MachinesConfig object.

    Raises:
        ConfigurationError: If configuration cannot be loaded.
    """
    global _config_cache
    if _config_cache is None:
        return load_config()
    return _config_cache


def reload_config() -> MachinesConfig:
    """
    Force reload configuration from file.

    Returns:
        MachinesConfig object with fresh configuration.
    """
    global _config_cache
    _config_cache = None
    return load_config()


def get_machine(name: str) -> MachineConfig:
    """
    Get machine configuration by name.

    Args:
        name: Machine name.

    Returns:
        MachineConfig for the specified machine.

    Raises:
        ConfigurationError: If machine not found.
    """
    config = get_config()
    machine = config.get_machine(name)
    if machine is None:
        available = config.get_machine_names()
        raise ConfigurationError(
            f"Machine '{name}' not found. Available machines: {available}"
        )
    return machine


def list_machines() -> list[str]:
    """
    Get list of configured machine names.

    Returns:
        List of machine names.
    """
    return get_config().get_machine_names()
