"""Configuration management for Prompt Cheater."""

import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".cheater"
CONFIG_FILE = CONFIG_DIR / "config"


class ConfigManager:
    """Manage configuration stored in ~/.cheater/config."""

    def __init__(self) -> None:
        """Initialize the config manager."""
        self._config = configparser.ConfigParser()
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            self._config.read(CONFIG_FILE)

    def _save(self) -> None:
        """Save configuration to file with secure permissions."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with CONFIG_FILE.open("w") as f:
            self._config.write(f)

        # Set secure permissions (owner read/write only)
        CONFIG_FILE.chmod(0o600)

    def set(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key name.
            value: Configuration value.
        """
        if "DEFAULT" not in self._config:
            self._config["DEFAULT"] = {}
        self._config["DEFAULT"][key] = value
        self._save()

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a configuration value.

        Args:
            key: Configuration key name.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._config.get("DEFAULT", key, fallback=default)

    def show(self) -> dict[str, str]:
        """Get all configuration values.

        Returns:
            Dictionary of all configuration key-value pairs.
        """
        if "DEFAULT" in self._config:
            return dict(self._config["DEFAULT"])
        return {}

    def delete(self, key: str) -> bool:
        """Delete a configuration value.

        Args:
            key: Configuration key name.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        if "DEFAULT" in self._config and key in self._config["DEFAULT"]:
            del self._config["DEFAULT"][key]
            self._save()
            return True
        return False
