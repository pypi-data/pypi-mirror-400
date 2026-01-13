"""
CHRONOS Configuration Management
================================

Provides configuration management for the CHRONOS platform.
Supports YAML files, environment variables, and runtime configuration.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from chronos.core.schema import (
    ChronosConfig,
    DEFAULT_CONFIG,
    SecurityLevel,
    LogLevel,
    CryptoConfig,
    DetectionConfig,
    AnalysisConfig,
    DefenseConfig,
    APIConfig,
    LoggingConfig,
)


class Config:
    """
    Configuration manager for CHRONOS platform.
    
    This class provides a simplified interface for accessing configuration.
    For advanced configuration management, use ConfigManager from cli.utils.config.
    
    Example:
        config = Config()
        print(config.security_level)
        print(config.get("detection.enabled"))
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file.
        """
        self._config_path = config_path
        self._config: Optional[ChronosConfig] = None
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file and environment."""
        try:
            # Try to use the full ConfigManager if available
            from chronos.cli.utils.config import ConfigManager
            manager = ConfigManager(config_path=self._config_path)
            self._config = manager.load()
        except ImportError:
            # Fall back to default config
            self._config = DEFAULT_CONFIG
        except Exception:
            # On any error, use defaults
            self._config = DEFAULT_CONFIG
    
    def reload(self) -> None:
        """Reload configuration from sources."""
        self._load()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "detection.enabled").
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        if self._config is None:
            return default
        
        parts = key.split(".")
        value: Any = self._config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Dot-notation key.
            value: Value to set.
        """
        if self._config is None:
            self._config = DEFAULT_CONFIG
        
        parts = key.split(".")
        obj: Any = self._config
        
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise KeyError(f"Invalid config key: {key}")
        
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        else:
            raise KeyError(f"Invalid config key: {key}")
    
    # Convenience properties for common settings
    @property
    def security_level(self) -> SecurityLevel:
        """Get the global security level."""
        return self._config.security_level if self._config else SecurityLevel.HIGH
    
    @property
    def data_directory(self) -> Path:
        """Get the data directory path."""
        data_dir = self._config.data_directory if self._config else ".chronos"
        return Path(os.path.expanduser(data_dir))
    
    @property
    def quantum_resistant(self) -> bool:
        """Check if quantum-resistant mode is enabled."""
        return self._config.crypto.quantum_resistant if self._config else True
    
    @property
    def crypto(self) -> CryptoConfig:
        """Get cryptography configuration."""
        return self._config.crypto if self._config else CryptoConfig()
    
    @property
    def detection(self) -> DetectionConfig:
        """Get detection configuration."""
        return self._config.detection if self._config else DetectionConfig()
    
    @property
    def analysis(self) -> AnalysisConfig:
        """Get analysis configuration."""
        return self._config.analysis if self._config else AnalysisConfig()
    
    @property
    def defense(self) -> DefenseConfig:
        """Get defense configuration."""
        return self._config.defense if self._config else DefenseConfig()
    
    @property
    def api(self) -> APIConfig:
        """Get API configuration."""
        return self._config.api if self._config else APIConfig()
    
    @property
    def logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self._config.logging if self._config else LoggingConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        if self._config:
            return self._config.model_dump()
        return DEFAULT_CONFIG.model_dump()


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _global_config
    _global_config = None
