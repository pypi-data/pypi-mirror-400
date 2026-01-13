"""
CHRONOS Configuration Manager
=============================

Handles configuration loading, validation, and management.
Supports YAML files, environment variables, and runtime updates.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union

import yaml
from pydantic import ValidationError

from chronos.core.schema import (
    ChronosConfig,
    DEFAULT_CONFIG,
    SecurityLevel,
    LogLevel,
    OutputFormat,
)

T = TypeVar("T")

# Environment variable prefix
ENV_PREFIX = "CHRONOS_"

# Default config file locations (in priority order)
CONFIG_LOCATIONS = [
    ".chronos/config.yaml",
    ".chronos/config.yml",
    "chronos.yaml",
    "chronos.yml",
    ".chronos.yaml",
    ".chronos.yml",
]

# Global config instance
_config_instance: Optional[ChronosConfig] = None


class ConfigurationError(Exception):
    """Configuration-related error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ConfigManager:
    """
    Configuration manager for CHRONOS.
    
    Handles loading configuration from multiple sources:
    1. Default values (lowest priority)
    2. YAML configuration file
    3. Environment variables (highest priority)
    
    Example:
        manager = ConfigManager()
        config = manager.load()
        
        # Access config values
        print(config.security_level)
        print(config.detection.enabled)
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        auto_create: bool = False,
    ):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Explicit path to config file.
            auto_create: Create default config if not found.
        """
        self.config_path = config_path
        self.auto_create = auto_create
        self._config: Optional[ChronosConfig] = None
    
    def load(self, reload: bool = False) -> ChronosConfig:
        """
        Load configuration from all sources.
        
        Args:
            reload: Force reload even if already loaded.
            
        Returns:
            Validated ChronosConfig instance.
        """
        if self._config is not None and not reload:
            return self._config
        
        # Start with defaults
        config_dict: Dict[str, Any] = DEFAULT_CONFIG.model_dump()
        
        # Load from YAML file
        yaml_config = self._load_yaml()
        if yaml_config:
            config_dict = self._deep_merge(config_dict, yaml_config)
        
        # Apply environment variables (highest priority)
        env_config = self._load_env_vars()
        if env_config:
            config_dict = self._deep_merge(config_dict, env_config)
        
        # Validate and create config instance
        try:
            self._config = ChronosConfig(**config_dict)
        except ValidationError as e:
            raise ConfigurationError(
                f"Configuration validation failed:\n{self._format_validation_errors(e)}"
            )
        
        return self._config
    
    def _load_yaml(self) -> Optional[Dict[str, Any]]:
        """Load configuration from YAML file."""
        config_file = self._find_config_file()
        
        if config_file is None:
            if self.auto_create:
                self._create_default_config()
                config_file = self._find_config_file()
            else:
                return None
        
        if config_file is None:
            return None
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content if isinstance(content, dict) else None
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_file}: {e}")
        except IOError as e:
            raise ConfigurationError(f"Cannot read config file {config_file}: {e}")
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in standard locations."""
        if self.config_path:
            if self.config_path.exists():
                return self.config_path
            return None
        
        for location in CONFIG_LOCATIONS:
            path = Path(location)
            if path.exists():
                return path
        
        return None
    
    def _load_env_vars(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Environment variables follow the pattern:
        CHRONOS_<SECTION>_<KEY> = value
        
        Examples:
            CHRONOS_SECURITY_LEVEL=maximum
            CHRONOS_DETECTION_ENABLED=true
            CHRONOS_API_PORT=9000
            CHRONOS_CRYPTO_QUANTUM_RESISTANT=false
        """
        config: Dict[str, Any] = {}
        
        for key, value in os.environ.items():
            if not key.startswith(ENV_PREFIX):
                continue
            
            # Remove prefix and split into parts
            key_parts = key[len(ENV_PREFIX):].lower().split("_")
            
            if len(key_parts) == 1:
                # Top-level setting (e.g., CHRONOS_VERSION)
                config[key_parts[0]] = self._parse_env_value(value)
            elif len(key_parts) == 2:
                # Section setting (e.g., CHRONOS_API_PORT)
                section, setting = key_parts
                if section not in config:
                    config[section] = {}
                config[section][setting] = self._parse_env_value(value)
            elif len(key_parts) >= 3:
                # Nested setting with underscores (e.g., CHRONOS_CRYPTO_QUANTUM_RESISTANT)
                section = key_parts[0]
                setting = "_".join(key_parts[1:])
                if section not in config:
                    config[section] = {}
                config[section][setting] = self._parse_env_value(value)
        
        return config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # List (comma-separated)
        if "," in value:
            return [v.strip() for v in value.split(",")]
        
        # String
        return value
    
    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_default_config(self) -> Path:
        """Create default configuration file."""
        config_dir = Path(".chronos")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "config.yaml"
        
        default_yaml = self.export_yaml(DEFAULT_CONFIG)
        config_file.write_text(default_yaml, encoding="utf-8")
        
        return config_file
    
    def _format_validation_errors(self, error: ValidationError) -> str:
        """Format Pydantic validation errors for display."""
        lines = []
        for err in error.errors():
            location = " -> ".join(str(loc) for loc in err["loc"])
            lines.append(f"  • {location}: {err['msg']}")
        return "\n".join(lines)
    
    @property
    def config(self) -> ChronosConfig:
        """Get current configuration (loads if needed)."""
        if self._config is None:
            self.load()
        return self._config  # type: ignore
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "detection.enabled")
            default: Default value if not found.
            
        Returns:
            Configuration value or default.
        """
        config = self.config
        parts = key.split(".")
        
        value: Any = config
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "detection.enabled")
            value: Value to set.
        """
        config = self.config
        parts = key.split(".")
        
        # Navigate to parent
        obj: Any = config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise ConfigurationError(f"Invalid config key: {key}")
        
        # Set value
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        else:
            raise ConfigurationError(f"Invalid config key: {key}")
    
    def save(self, path: Optional[Path] = None) -> Path:
        """
        Save current configuration to YAML file.
        
        Args:
            path: Output path (defaults to .chronos/config.yaml)
            
        Returns:
            Path to saved file.
        """
        output_path = path or self.config_path or Path(".chronos/config.yaml")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        yaml_content = self.export_yaml(self.config)
        output_path.write_text(yaml_content, encoding="utf-8")
        
        return output_path
    
    def export_yaml(self, config: Optional[ChronosConfig] = None) -> str:
        """
        Export configuration to YAML string.
        
        Args:
            config: Configuration to export (defaults to current).
            
        Returns:
            YAML string.
        """
        config = config or self.config
        config_dict = config.model_dump()
        
        # Add header comment
        header = """# CHRONOS Configuration File
# ===========================
# This file configures the CHRONOS Quantum Security Platform.
# 
# Environment variables can override these settings using the pattern:
#   CHRONOS_<SECTION>_<KEY>=value
#
# Examples:
#   CHRONOS_SECURITY_LEVEL=maximum
#   CHRONOS_DETECTION_ENABLED=false
#   CHRONOS_API_PORT=9000
#
# Documentation: https://chronos-security.io/docs/configuration

"""
        yaml_content = yaml.dump(
            config_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
        )
        
        return header + yaml_content
    
    def export_json(self, config: Optional[ChronosConfig] = None) -> str:
        """Export configuration to JSON string."""
        config = config or self.config
        return config.model_dump_json(indent=2)
    
    def export_env(self, config: Optional[ChronosConfig] = None) -> str:
        """
        Export configuration as environment variables.
        
        Returns:
            String of environment variable exports.
        """
        config = config or self.config
        config_dict = config.model_dump()
        
        lines = ["# CHRONOS Environment Variables", ""]
        
        def flatten(obj: Any, prefix: str = ENV_PREFIX) -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    flatten(value, f"{prefix}{key.upper()}_")
            elif isinstance(obj, list):
                lines.append(f'{prefix.rstrip("_")}="{",".join(str(v) for v in obj)}"')
            elif isinstance(obj, bool):
                lines.append(f'{prefix.rstrip("_")}={"true" if obj else "false"}')
            elif obj is not None:
                lines.append(f'{prefix.rstrip("_")}="{obj}"')
        
        flatten(config_dict)
        return "\n".join(lines)
    
    def validate(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if valid.
            
        Raises:
            ConfigurationError: If validation fails.
        """
        try:
            ChronosConfig(**self.config.model_dump())
            return True
        except ValidationError as e:
            raise ConfigurationError(
                f"Configuration validation failed:\n{self._format_validation_errors(e)}"
            )
    
    def reset(self) -> ChronosConfig:
        """Reset configuration to defaults."""
        self._config = ChronosConfig()
        return self._config


# Global functions for convenience
def get_config() -> ChronosConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        manager = ConfigManager()
        _config_instance = manager.load()
    return _config_instance


def load_config(
    config_path: Optional[Path] = None,
    reload: bool = False
) -> ChronosConfig:
    """
    Load configuration from file and environment.
    
    Args:
        config_path: Optional explicit config file path.
        reload: Force reload.
        
    Returns:
        Validated configuration instance.
    """
    global _config_instance
    
    if _config_instance is not None and not reload and config_path is None:
        return _config_instance
    
    manager = ConfigManager(config_path=config_path)
    _config_instance = manager.load()
    return _config_instance


def reset_config() -> None:
    """Reset global configuration instance."""
    global _config_instance
    _config_instance = None
