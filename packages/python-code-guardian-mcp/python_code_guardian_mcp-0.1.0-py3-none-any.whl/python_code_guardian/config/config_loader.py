"""Configuration loader for Code Guardian."""

import os
import yaml
from typing import Any, Dict, Optional


class ConfigLoader:
    """Loads and manages configuration for code checks."""

    def __init__(self):
        """Initialize the config loader with default configuration."""
        self.current_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "rules": {
                "pylint": {
                    "enabled": True,
                    "max_line_length": 100,
                    "disable": []
                },
                "complexity": {
                    "enabled": True,
                    "max_complexity": 10,
                    "max_function_length": 50
                },
                "typo": {
                    "enabled": True,
                    "check_variables": True,
                    "check_comments": True,
                    "custom_dictionary": []
                },
                "structure": {
                    "enabled": True,
                    "require_docstrings": True,
                    "naming_convention": "snake_case"
                },
                "coverage": {
                    "enabled": True,
                    "test_coverage_threshold": 75
                },
                "duplicates": {
                    "enabled": True,
                    "min_lines": 6,
                    "ignore_patterns": ["tests/*", "test_*"]
                }
            },
            "custom_checkers": []
        }

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or use default.
        
        Args:
            config_path: Path to configuration file (.code-guardian.yaml)
            
        Returns:
            Configuration dictionary
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Merge with defaults
                    self.current_config = self._merge_configs(self._get_default_config(), user_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")
        else:
            # Try to find .code-guardian.yaml in current directory
            default_config_path = ".code-guardian.yaml"
            if os.path.exists(default_config_path):
                try:
                    with open(default_config_path, 'r') as f:
                        user_config = yaml.safe_load(f)
                        self.current_config = self._merge_configs(self._get_default_config(), user_config)
                except Exception:
                    pass  # Use defaults
        
        return self.current_config

    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config."""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result

    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.current_config

    def update_config(self, new_config: Dict[str, Any]):
        """Update current configuration."""
        self.current_config = self._merge_configs(self.current_config, new_config)

    def config_to_yaml(self, config: Dict[str, Any]) -> str:
        """Convert config dict to YAML string."""
        return yaml.dump(config, default_flow_style=False)

    def save_config(self, file_path: str):
        """Save current configuration to file."""
        try:
            with open(file_path, 'w') as f:
                yaml.dump(self.current_config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

