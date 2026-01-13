"""
CHRONOS Configuration Schema
============================

Pydantic models for configuration validation and type safety.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class SecurityLevel(str, Enum):
    """Security level settings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class LogLevel(str, Enum):
    """Logging level settings."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OutputFormat(str, Enum):
    """Output format options."""
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


class CryptoConfig(BaseModel):
    """Cryptography configuration settings."""
    
    quantum_resistant: bool = Field(
        default=True,
        description="Enable quantum-resistant cryptographic algorithms"
    )
    default_algorithm: str = Field(
        default="AES-256-GCM",
        description="Default encryption algorithm"
    )
    key_derivation: str = Field(
        default="PBKDF2",
        description="Key derivation function"
    )
    min_key_size: int = Field(
        default=256,
        ge=128,
        le=4096,
        description="Minimum key size in bits"
    )
    post_quantum_algorithms: List[str] = Field(
        default=["CRYSTALS-Kyber", "CRYSTALS-Dilithium", "SPHINCS+"],
        description="Enabled post-quantum algorithms"
    )
    
    @field_validator("default_algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        allowed = [
            "AES-256-GCM", "AES-128-GCM", "ChaCha20-Poly1305",
            "CRYSTALS-Kyber", "CRYSTALS-Dilithium"
        ]
        if v not in allowed:
            raise ValueError(f"Algorithm must be one of: {', '.join(allowed)}")
        return v


class DetectionConfig(BaseModel):
    """Threat detection configuration."""
    
    enabled: bool = Field(default=True, description="Enable threat detection")
    scan_depth: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Directory scan depth"
    )
    file_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs"],
        description="File extensions to scan"
    )
    exclude_patterns: List[str] = Field(
        default=["node_modules", "__pycache__", ".git", "venv", ".venv"],
        description="Patterns to exclude from scanning"
    )
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum file size to scan in MB"
    )
    signature_update_interval: int = Field(
        default=86400,
        description="Signature update interval in seconds"
    )
    real_time_monitoring: bool = Field(
        default=False,
        description="Enable real-time file monitoring"
    )


class AnalysisConfig(BaseModel):
    """Security analysis configuration."""
    
    enabled: bool = Field(default=True, description="Enable security analysis")
    crypto_audit: bool = Field(
        default=True,
        description="Enable cryptographic audit"
    )
    vulnerability_scan: bool = Field(
        default=True,
        description="Enable vulnerability scanning"
    )
    quantum_assessment: bool = Field(
        default=True,
        description="Enable quantum readiness assessment"
    )
    cve_database: str = Field(
        default="https://cve.mitre.org",
        description="CVE database URL"
    )
    report_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="Default report format"
    )


class DefenseConfig(BaseModel):
    """Defense system configuration."""
    
    enabled: bool = Field(default=True, description="Enable defense systems")
    auto_quarantine: bool = Field(
        default=False,
        description="Automatically quarantine threats"
    )
    auto_remediate: bool = Field(
        default=False,
        description="Automatically apply remediations"
    )
    shield_level: SecurityLevel = Field(
        default=SecurityLevel.HIGH,
        description="Default shield protection level"
    )
    quarantine_path: str = Field(
        default=".chronos/quarantine",
        description="Quarantine directory path"
    )
    notification_enabled: bool = Field(
        default=True,
        description="Enable threat notifications"
    )


class APIConfig(BaseModel):
    """API server configuration."""
    
    enabled: bool = Field(default=False, description="Enable API server")
    host: str = Field(default="127.0.0.1", description="API server host")
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port"
    )
    api_key_required: bool = Field(
        default=True,
        description="Require API key for requests"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    rate_limit: int = Field(
        default=100,
        ge=1,
        description="Rate limit per minute"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    file_enabled: bool = Field(
        default=True,
        description="Enable file logging"
    )
    file_path: str = Field(
        default=".chronos/logs/chronos.log",
        description="Log file path"
    )
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum log file size in MB"
    )
    backup_count: int = Field(
        default=5,
        ge=0,
        le=20,
        description="Number of backup log files"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    rich_console: bool = Field(
        default=True,
        description="Use rich formatting for console output"
    )


class IntegrationConfig(BaseModel):
    """External integrations configuration."""
    
    github_enabled: bool = Field(
        default=False,
        description="Enable GitHub integration"
    )
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub API token"
    )
    slack_enabled: bool = Field(
        default=False,
        description="Enable Slack notifications"
    )
    slack_webhook: Optional[str] = Field(
        default=None,
        description="Slack webhook URL"
    )
    custom_webhooks: List[str] = Field(
        default=[],
        description="Custom webhook URLs for notifications"
    )


class ChronosConfig(BaseModel):
    """
    Root CHRONOS Configuration Schema.
    
    This is the main configuration model that contains all settings
    for the CHRONOS quantum security platform.
    """
    
    # Metadata
    version: str = Field(
        default="0.1.0",
        description="Configuration version"
    )
    project_name: str = Field(
        default="CHRONOS",
        description="Project name"
    )
    
    # Global settings
    security_level: SecurityLevel = Field(
        default=SecurityLevel.HIGH,
        description="Global security level"
    )
    data_directory: str = Field(
        default=".chronos",
        description="CHRONOS data directory"
    )
    
    # Module configurations
    crypto: CryptoConfig = Field(
        default_factory=CryptoConfig,
        description="Cryptography settings"
    )
    detection: DetectionConfig = Field(
        default_factory=DetectionConfig,
        description="Threat detection settings"
    )
    analysis: AnalysisConfig = Field(
        default_factory=AnalysisConfig,
        description="Security analysis settings"
    )
    defense: DefenseConfig = Field(
        default_factory=DefenseConfig,
        description="Defense system settings"
    )
    api: APIConfig = Field(
        default_factory=APIConfig,
        description="API server settings"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging settings"
    )
    integrations: IntegrationConfig = Field(
        default_factory=IntegrationConfig,
        description="External integrations"
    )
    
    # Custom settings
    custom: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom user-defined settings"
    )
    
    model_config = {
        "extra": "allow",
        "validate_assignment": True,
        "use_enum_values": True,
    }
    
    @model_validator(mode="after")
    def validate_config(self) -> "ChronosConfig":
        """Validate overall configuration consistency."""
        # Ensure quarantine path is under data directory
        if not self.defense.quarantine_path.startswith(self.data_directory):
            self.defense.quarantine_path = f"{self.data_directory}/quarantine"
        
        # Ensure log path is under data directory
        if not self.logging.file_path.startswith(self.data_directory):
            self.logging.file_path = f"{self.data_directory}/logs/chronos.log"
        
        return self


# Default configuration instance
DEFAULT_CONFIG = ChronosConfig()
