"""
CHRONOS Configuration System
============================

Pydantic-settings based configuration with config.toml and environment variables.
Supports API keys, feature flags, and operational settings.
"""

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Literal, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11 fallback

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from chronos.utils.logging import get_logger

logger = get_logger(__name__)


class APIKeysConfig(BaseModel):
    """API key configuration."""
    
    model_config = {"populate_by_name": True}
    
    # Threat Intelligence APIs
    nvd_api_key: Optional[SecretStr] = Field(
        default=None,
        description="NVD CVE API key for higher rate limits",
    )
    virustotal_api_key: Optional[SecretStr] = Field(
        default=None,
        alias="vt_api_key",
        description="VirusTotal API key for URL/file reputation",
    )
    urlhaus_auth_key: Optional[SecretStr] = Field(
        default=None,
        description="URLhaus authentication key (optional)",
    )
    shodan_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Shodan API key for network reconnaissance",
    )
    
    # LLM Backend (optional, for AI-powered analysis)
    llm_backend: Literal["openai", "anthropic", "local", "none"] = Field(
        default="none",
        description="LLM backend for AI-powered analysis",
    )
    llm_url: Optional[str] = Field(
        default=None,
        description="Custom LLM endpoint URL",
    )
    llm_api_key: Optional[SecretStr] = Field(
        default=None,
        description="LLM API key",
    )


class IntelConfig(BaseModel):
    """Threat intelligence configuration."""
    
    # EPSS (Exploit Prediction Scoring System)
    epss_enabled: bool = Field(default=True, description="Enable EPSS scoring")
    epss_cache_hours: int = Field(default=24, description="EPSS data cache duration")
    
    # NVD (National Vulnerability Database)
    nvd_enabled: bool = Field(default=True, description="Enable NVD CVE lookups")
    nvd_rate_limit: float = Field(
        default=0.6, 
        description="Seconds between NVD requests (without API key)",
    )
    nvd_rate_limit_with_key: float = Field(
        default=0.15,
        description="Seconds between NVD requests (with API key)",
    )
    
    # CISA KEV (Known Exploited Vulnerabilities)
    kev_enabled: bool = Field(default=True, description="Enable CISA KEV checks")
    kev_url: str = Field(
        default="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        description="CISA KEV catalog URL",
    )
    kev_cache_hours: int = Field(default=6, description="KEV data cache duration")
    
    # URLhaus
    urlhaus_enabled: bool = Field(default=True, description="Enable URLhaus lookups")
    urlhaus_api_url: str = Field(
        default="https://urlhaus-api.abuse.ch/v1/",
        description="URLhaus API base URL",
    )
    
    # VirusTotal
    virustotal_enabled: bool = Field(default=True, description="Enable VirusTotal lookups")
    virustotal_api_url: str = Field(
        default="https://www.virustotal.com/api/v3/",
        description="VirusTotal API base URL",
    )


class ScanConfig(BaseModel):
    """Scanning configuration."""
    
    max_file_size_mb: int = Field(
        default=50, 
        description="Maximum file size to scan in MB",
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "*.pyc", "__pycache__", ".git", ".svn", "node_modules",
            "*.min.js", "*.map", "venv", ".venv", "*.egg-info",
        ],
        description="Glob patterns to exclude from scanning",
    )
    python_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".pyw", ".pyx"],
        description="Python file extensions",
    )
    code_extensions: list[str] = Field(
        default_factory=lambda: [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
            ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php",
        ],
        description="All code file extensions to analyze",
    )
    config_extensions: list[str] = Field(
        default_factory=lambda: [
            ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
            ".env", ".properties", ".xml",
        ],
        description="Configuration file extensions",
    )


class PhishingConfig(BaseModel):
    """Phishing detection configuration."""
    
    suspicious_tlds: list[str] = Field(
        default_factory=lambda: [
            ".xyz", ".top", ".club", ".work", ".click", ".link",
            ".info", ".online", ".site", ".website", ".space",
        ],
        description="Suspicious top-level domains",
    )
    suspicious_keywords: list[str] = Field(
        default_factory=lambda: [
            "verify", "confirm", "suspend", "urgent", "immediately",
            "account", "security", "update", "password", "login",
            "click here", "act now", "limited time", "winner",
        ],
        description="Suspicious keywords in emails",
    )
    url_shorteners: list[str] = Field(
        default_factory=lambda: [
            "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
            "is.gd", "buff.ly", "rebrand.ly", "cutt.ly",
        ],
        description="Known URL shortener domains",
    )


class LogsConfig(BaseModel):
    """Log analysis configuration."""
    
    baseline_window_hours: int = Field(
        default=168,  # 7 days
        description="Hours of logs for baseline calculation",
    )
    anomaly_threshold: float = Field(
        default=0.1,
        description="Anomaly detection threshold (lower = more sensitive)",
    )
    max_log_lines: int = Field(
        default=1_000_000,
        description="Maximum log lines to process",
    )
    syslog_patterns: list[str] = Field(
        default_factory=lambda: [
            "/var/log/syslog",
            "/var/log/messages", 
            "/var/log/auth.log",
            "/var/log/secure",
        ],
        description="Default syslog file patterns (Unix)",
    )
    windows_event_logs: list[str] = Field(
        default_factory=lambda: [
            "Security",
            "System",
            "Application",
        ],
        description="Windows Event Log names to analyze",
    )


class ReportConfig(BaseModel):
    """Report generation configuration."""
    
    company_name: str = Field(
        default="Organization",
        description="Company name for reports",
    )
    analyst_name: str = Field(
        default="CHRONOS",
        description="Analyst name for reports",
    )
    output_dir: str = Field(
        default="~/.chronos/reports",
        description="Default report output directory",
    )
    include_recommendations: bool = Field(
        default=True,
        description="Include remediation recommendations",
    )
    include_charts: bool = Field(
        default=True,
        description="Include charts in reports",
    )


class IRConfig(BaseModel):
    """Incident response configuration."""
    
    dry_run_default: bool = Field(
        default=True,
        description="Default to dry-run mode for IR actions",
    )
    playbooks_dir: str = Field(
        default="~/.chronos/playbooks",
        description="Custom playbooks directory",
    )
    require_confirmation: bool = Field(
        default=True,
        description="Require confirmation for destructive actions",
    )
    max_parallel_actions: int = Field(
        default=5,
        description="Maximum parallel IR actions",
    )


class ChronosSettings(BaseSettings):
    """
    Main CHRONOS configuration.
    
    Configuration sources (in priority order):
    1. Environment variables (CHRONOS_*)
    2. config.toml file
    3. Default values
    """
    
    model_config = SettingsConfigDict(
        env_prefix="CHRONOS_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Paths
    data_dir: str = Field(
        default="~/.chronos",
        description="CHRONOS data directory",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    
    # Sub-configurations
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)
    intel: IntelConfig = Field(default_factory=IntelConfig)
    scan: ScanConfig = Field(default_factory=ScanConfig)
    phishing: PhishingConfig = Field(default_factory=PhishingConfig)
    logs: LogsConfig = Field(default_factory=LogsConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)
    ir: IRConfig = Field(default_factory=IRConfig)
    
    @property
    def data_path(self) -> Path:
        """Get expanded data directory path."""
        return Path(self.data_dir).expanduser()
    
    @property
    def config_path(self) -> Path:
        """Get config file path."""
        return self.data_path / "config.toml"
    
    @property
    def db_path(self) -> Path:
        """Get database path."""
        return self.data_path / "chronos.db"
    
    @property
    def quarantine_path(self) -> Path:
        """Get quarantine directory path."""
        return self.data_path / "quarantine"
    
    @property
    def playbooks_path(self) -> Path:
        """Get playbooks directory path."""
        return Path(self.ir.playbooks_dir).expanduser()
    
    @property
    def reports_path(self) -> Path:
        """Get reports directory path."""
        return Path(self.report.output_dir).expanduser()


def load_toml_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from TOML file.
    
    Args:
        config_path: Path to config.toml. Defaults to ~/.chronos/config.toml
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path.home() / ".chronos" / "config.toml"
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        logger.debug(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}")
        return {}


def create_default_config(config_path: Optional[Path] = None) -> Path:
    """
    Create default configuration file.
    
    Args:
        config_path: Path for config.toml. Defaults to ~/.chronos/config.toml
    
    Returns:
        Path to created config file
    """
    if config_path is None:
        config_path = Path.home() / ".chronos" / "config.toml"
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = '''# CHRONOS Configuration
# =====================
# Environment variables take precedence over these settings.
# Use CHRONOS_<SECTION>__<KEY> format for env vars.

# Data storage location
data_dir = "~/.chronos"
log_level = "INFO"

[api_keys]
# Threat Intelligence API Keys
# Get these from:
# - NVD: https://nvd.nist.gov/developers/request-an-api-key
# - VirusTotal: https://www.virustotal.com/gui/join-us
# - URLhaus: Optional, no key needed for basic use
# - Shodan: https://account.shodan.io/

# nvd_api_key = "your-nvd-api-key"
# vt_api_key = "your-virustotal-api-key"
# shodan_api_key = "your-shodan-api-key"

# LLM Backend (for AI-powered analysis)
llm_backend = "none"  # Options: openai, anthropic, local, none
# llm_url = "http://localhost:11434/api"  # For local LLM
# llm_api_key = "your-llm-api-key"

[intel]
# Threat Intelligence Settings
epss_enabled = true
epss_cache_hours = 24
nvd_enabled = true
kev_enabled = true
urlhaus_enabled = true
virustotal_enabled = true

[scan]
# Scanning Settings
max_file_size_mb = 50
exclude_patterns = [
    "*.pyc", "__pycache__", ".git", ".svn", 
    "node_modules", "*.min.js", "venv", ".venv"
]

[phishing]
# Phishing Detection Settings
suspicious_tlds = [".xyz", ".top", ".club", ".work", ".click"]

[logs]
# Log Analysis Settings
baseline_window_hours = 168  # 7 days
anomaly_threshold = 0.1
max_log_lines = 1000000

[report]
# Report Generation Settings
company_name = "Organization"
analyst_name = "CHRONOS"
output_dir = "~/.chronos/reports"
include_recommendations = true
include_charts = true

[ir]
# Incident Response Settings
dry_run_default = true
playbooks_dir = "~/.chronos/playbooks"
require_confirmation = true
max_parallel_actions = 5
'''
    
    config_path.write_text(default_config)
    logger.info(f"Created default config at {config_path}")
    return config_path


@lru_cache(maxsize=1)
def get_settings() -> ChronosSettings:
    """
    Get or create the global settings instance.
    
    Uses caching to ensure single instance.
    """
    # Load TOML config if exists
    toml_config = load_toml_config()
    
    # Handle nested configs properly - pydantic needs nested dicts to be passed correctly
    if 'api_keys' in toml_config:
        toml_config['api_keys'] = APIKeysConfig(**toml_config['api_keys'])
    if 'intel' in toml_config:
        toml_config['intel'] = IntelConfig(**toml_config['intel'])
    if 'scan' in toml_config:
        toml_config['scan'] = ScanConfig(**toml_config['scan'])
    if 'phishing' in toml_config:
        toml_config['phishing'] = PhishingConfig(**toml_config['phishing'])
    if 'logs' in toml_config:
        toml_config['logs'] = LogsConfig(**toml_config['logs'])
    if 'report' in toml_config:
        toml_config['report'] = ReportConfig(**toml_config['report'])
    if 'ir' in toml_config:
        toml_config['ir'] = IRConfig(**toml_config['ir'])
    
    # Merge with environment variables (pydantic-settings handles this)
    settings = ChronosSettings(**toml_config)
    
    # Ensure directories exist
    settings.data_path.mkdir(parents=True, exist_ok=True)
    settings.quarantine_path.mkdir(parents=True, exist_ok=True)
    settings.playbooks_path.mkdir(parents=True, exist_ok=True)
    settings.reports_path.mkdir(parents=True, exist_ok=True)
    
    return settings


def reload_settings() -> ChronosSettings:
    """Force reload settings (clears cache)."""
    get_settings.cache_clear()
    return get_settings()


def get_api_key(key_name: str) -> Optional[str]:
    """
    Get an API key from settings.
    
    Args:
        key_name: Name of the API key (e.g., 'nvd_api_key', 'vt_api_key')
    
    Returns:
        API key string or None
    """
    settings = get_settings()
    key = getattr(settings.api_keys, key_name, None)
    if key is None:
        return None
    if isinstance(key, SecretStr):
        return key.get_secret_value()
    return str(key)


def check_api_keys() -> Dict[str, bool]:
    """
    Check which API keys are configured.
    
    Returns:
        Dictionary of key_name -> is_configured
    """
    settings = get_settings()
    return {
        "nvd_api_key": settings.api_keys.nvd_api_key is not None,
        "virustotal_api_key": settings.api_keys.virustotal_api_key is not None,
        "urlhaus_auth_key": settings.api_keys.urlhaus_auth_key is not None,
        "shodan_api_key": settings.api_keys.shodan_api_key is not None,
        "llm_api_key": settings.api_keys.llm_api_key is not None,
    }


def save_api_key(key_name: str, key_value: str) -> Path:
    """
    Save an API key to the config file.
    
    Args:
        key_name: Name of the key (e.g., 'virustotal_api_key', 'nvd_api_key')
        key_value: The API key value
    
    Returns:
        Path to the config file
    """
    config_path = Path.home() / ".chronos" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
        except Exception:
            config = {}
    else:
        config = {}
    
    # Ensure api_keys section exists
    if "api_keys" not in config:
        config["api_keys"] = {}
    
    # Map friendly names to actual field names
    key_mapping = {
        "virustotal": "virustotal_api_key",
        "vt": "virustotal_api_key",
        "virustotal_api_key": "virustotal_api_key",
        "vt_api_key": "virustotal_api_key",
        "nvd": "nvd_api_key",
        "nvd_api_key": "nvd_api_key",
        "shodan": "shodan_api_key",
        "shodan_api_key": "shodan_api_key",
        "urlhaus": "urlhaus_auth_key",
        "urlhaus_auth_key": "urlhaus_auth_key",
    }
    
    actual_key_name = key_mapping.get(key_name.lower(), key_name)
    config["api_keys"][actual_key_name] = key_value
    
    # Write back as TOML
    toml_content = _dict_to_toml(config)
    config_path.write_text(toml_content, encoding="utf-8")
    
    # Clear settings cache to reload
    reload_settings()
    
    logger.info(f"Saved {actual_key_name} to {config_path}")
    return config_path


def _dict_to_toml(d: Dict[str, Any], parent_key: str = "") -> str:
    """
    Convert a dictionary to TOML format string.
    
    Args:
        d: Dictionary to convert
        parent_key: Parent key for nested sections
    
    Returns:
        TOML formatted string
    """
    lines = []
    
    # First, write simple key-value pairs
    for key, value in d.items():
        if not isinstance(value, dict):
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, list):
                items = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                lines.append(f"{key} = [{items}]")
            else:
                lines.append(f"{key} = {value}")
    
    # Then, write sections (nested dicts)
    for key, value in d.items():
        if isinstance(value, dict):
            section_name = f"{parent_key}.{key}" if parent_key else key
            lines.append(f"\n[{section_name}]")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    lines.append(f'{sub_key} = "{sub_value}"')
                elif isinstance(sub_value, bool):
                    lines.append(f"{sub_key} = {str(sub_value).lower()}")
                elif isinstance(sub_value, list):
                    items = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in sub_value)
                    lines.append(f"{sub_key} = [{items}]")
                elif sub_value is not None:
                    lines.append(f"{sub_key} = {sub_value}")
    
    return "\n".join(lines) + "\n"
