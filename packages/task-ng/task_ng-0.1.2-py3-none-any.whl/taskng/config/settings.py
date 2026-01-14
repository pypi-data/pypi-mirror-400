"""Configuration system with layered loading."""

import os
import tomllib
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "taskng"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "taskng"

# Singleton instance
_config_instance: "Config | None" = None
_custom_config_path: Path | None = None
_custom_data_dir: Path | None = None


def set_config_path(path: Path | None) -> None:
    """Set custom config file path.

    Args:
        path: Custom config file path, or None for default.
    """
    global _custom_config_path, _config_instance
    _custom_config_path = path
    _config_instance = None  # Reset singleton


def set_data_dir(path: Path | None) -> None:
    """Set custom data directory.

    Args:
        path: Custom data directory, or None for default.
    """
    global _custom_data_dir
    _custom_data_dir = path


def get_data_dir() -> Path:
    """Get the current data directory.

    Resolution order:
    1. Custom data dir set via set_data_dir() (--data-dir CLI option)
    2. TASKNG_DATA_DIR environment variable
    3. data.location from config file
    4. Default ~/.local/share/taskng

    Returns:
        Path to data directory.
    """
    if _custom_data_dir is not None:
        return _custom_data_dir

    env_data_dir = os.environ.get("TASKNG_DATA_DIR")
    if env_data_dir:
        return Path(env_data_dir)

    config = get_config()
    config_data_dir = config.get("data.location")
    if config_data_dir:
        return Path(config_data_dir)

    return DEFAULT_DATA_DIR


def get_config_dir() -> Path:
    """Get the config directory based on current config file.

    Returns:
        Path to config directory.
    """
    if _custom_config_path is not None:
        return _custom_config_path.parent
    return DEFAULT_CONFIG_DIR


class Config:
    """Layered configuration system."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration.

        Args:
            config_path: Path to config file, or None for default.
        """
        self.config_path = config_path or DEFAULT_CONFIG_FILE
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from all layers."""
        # Layer 1: Defaults
        from .defaults import DEFAULTS

        self._config = self._deep_copy(DEFAULTS)

        # Layer 2: Config file
        if self.config_path.exists():
            with open(self.config_path, "rb") as f:
                file_config = tomllib.load(f)
                self._merge(file_config)

        # Layer 3: Environment variables
        self._load_env()

    def _deep_copy(self, d: dict[str, Any]) -> dict[str, Any]:
        """Deep copy a dictionary."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deep_copy(v)
            else:
                result[k] = v
        return result

    def _merge(self, override: dict[str, Any]) -> None:
        """Merge override into config."""
        for key, value in override.items():
            if isinstance(value, dict) and key in self._config:
                if isinstance(self._config[key], dict):
                    self._merge_dict(self._config[key], value)
                else:
                    self._config[key] = value
            else:
                self._config[key] = value

    def _merge_dict(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Recursively merge override into base."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value

    def _load_env(self) -> None:
        """Load TASKNG_* environment variables."""
        prefix = "TASKNG_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower().replace("__", ".")
                # Convert string values to appropriate types
                converted = self._convert_value(value)
                self.set(config_key, converted)

    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        lower = value.lower()
        if lower in ("true", "yes", "1"):
            return True
        if lower in ("false", "no", "0"):
            return False
        if value.isdigit():
            return int(value)
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "data.location").
            default: Default value if key not found.

        Returns:
            Configuration value.
        """
        parts = key.split(".")
        value: Any = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "data.location").
            value: Value to set.
        """
        parts = key.split(".")
        config = self._config

        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        config[parts[-1]] = value

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Build TOML string manually (avoiding tomli-w dependency)
        lines = self._to_toml_lines(self._config)
        with open(self.config_path, "w") as f:
            f.write("\n".join(lines))

    def _to_toml_lines(self, d: dict[str, Any], prefix: str = "") -> list[str]:
        """Convert dict to TOML lines."""
        lines = []

        # First pass: simple values
        for key, value in d.items():
            if not isinstance(value, dict):
                lines.append(f"{key} = {self._to_toml_value(value)}")

        # Second pass: tables
        for key, value in d.items():
            if isinstance(value, dict):
                section = f"{prefix}.{key}" if prefix else key
                lines.append("")
                lines.append(f"[{section}]")
                lines.extend(self._to_toml_lines(value, section))

        return lines

    def _to_toml_value(self, value: Any) -> str:
        """Convert value to TOML string."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, int | float):
            return str(value)
        if isinstance(value, list):
            items = ", ".join(self._to_toml_value(v) for v in value)
            return f"[{items}]"
        if isinstance(value, dict):
            # TOML inline table syntax: {key = value, key2 = value2}
            pairs = ", ".join(
                f"{k} = {self._to_toml_value(v)}" for k, v in value.items()
            )
            return f"{{{pairs}}}"
        if value is None:
            return '""'
        return str(value)

    @property
    def data_location(self) -> Path:
        """Get data directory path."""
        return Path(self.get("data.location", ""))

    @property
    def color_enabled(self) -> bool:
        """Check if color output is enabled."""
        return bool(self.get("ui.color", True))


def get_config(config_path: Path | None = None) -> Config:
    """Get or create singleton config instance.

    Args:
        config_path: Optional custom config path.

    Returns:
        Config instance.
    """
    global _config_instance
    if _config_instance is None:
        # Resolution order:
        # 1. Explicit parameter
        # 2. Custom path set via set_config_path()
        # 3. Environment variable
        # 4. Default
        if config_path is None:
            if _custom_config_path is not None:
                config_path = _custom_config_path
            else:
                env_path = os.environ.get("TASKNG_CONFIG_FILE")
                if env_path:
                    config_path = Path(env_path)
        _config_instance = Config(config_path)
    return _config_instance


def reset_config() -> None:
    """Reset singleton config instance (for testing)."""
    global _config_instance, _custom_config_path, _custom_data_dir
    _config_instance = None
    _custom_config_path = None
    _custom_data_dir = None
