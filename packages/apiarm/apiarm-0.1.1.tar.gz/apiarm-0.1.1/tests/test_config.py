"""
Tests for the ConfigManager class.
"""

import os
import json
import pytest
from pathlib import Path
from apiarm.core.config import ConfigManager


@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture for a temporary config file."""
    return tmp_path / "config.json"


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    def test_init_creates_empty_config(self, temp_config_file):
        config = ConfigManager(config_path=temp_config_file)
        assert config._config == {}
        
    def test_set_and_get(self, temp_config_file):
        config = ConfigManager(config_path=temp_config_file)
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        
    def test_persistence(self, temp_config_file):
        # Save value in first instance
        config1 = ConfigManager(config_path=temp_config_file)
        config1.github_token = "pypi-token-123"
        
        # Load value in second instance
        config2 = ConfigManager(config_path=temp_config_file)
        assert config2.github_token == "pypi-token-123"
        
    def test_delete(self, temp_config_file):
        config = ConfigManager(config_path=temp_config_file)
        config.set("to_delete", "value")
        assert config.get("to_delete") == "value"
        
        config.delete("to_delete")
        assert config.get("to_delete") is None
        
    def test_invalid_json_handling(self, temp_config_file):
        # Write invalid JSON
        temp_config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_file, "w") as f:
            f.write("{invalid: json}")
            
        config = ConfigManager(config_path=temp_config_file)
        assert config._config == {}
