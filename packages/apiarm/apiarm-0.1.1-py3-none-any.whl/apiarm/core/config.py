"""
Configuration manager for API-ARM.
Handles local storage of API tokens and user settings.
"""

import os
import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """
    Manages API-ARM local configuration.
    Stores settings in ~/.apiarm/config.json
    """
    
    DEFAULT_CONFIG_DIR = Path.home() / ".apiarm"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.config_dir = self.config_path.parent
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from disk."""
        if not self.config_path.exists():
            self._config = {}
            return
            
        try:
            with open(self.config_path, "r") as f:
                self._config = json.load(f)
        except Exception:
            self._config = {}

    def save(self) -> None:
        """Save current configuration to disk."""
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
        self.save()

    def delete(self, key: str) -> None:
        """Delete a configuration value."""
        if key in self._config:
            del self._config[key]
            self.save()

    @property
    def github_token(self) -> Optional[str]:
        """Convenience property for GitHub token."""
        return self.get("github_token")

    @github_token.setter
    def github_token(self, value: str) -> None:
        self.set("github_token", value)
