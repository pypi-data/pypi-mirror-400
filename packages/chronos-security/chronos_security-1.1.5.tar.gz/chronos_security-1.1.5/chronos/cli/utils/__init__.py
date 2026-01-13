"""
CHRONOS CLI Utils Package
=========================

Utility functions for the CLI module.
"""

from chronos.cli.utils.helpers import (
    ChronosCLIError,
    ConfigurationError,
    ScanError,
    AnalysisError,
    DefenseError,
    error_handler,
    create_progress,
    print_success,
    print_warning,
    print_error,
    confirm_action,
)
from chronos.cli.utils.config import ConfigManager, get_config, load_config
from chronos.cli.utils.logger import (
    ChronosLogger,
    CorrelationContext,
    JSONFormatter,
    get_logger,
    setup_logging,
    log_event,
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)

__all__ = [
    # Exceptions
    "ChronosCLIError",
    "ConfigurationError",
    "ScanError",
    "AnalysisError",
    "DefenseError",
    # Utilities
    "error_handler",
    "create_progress",
    "print_success",
    "print_warning",
    "print_error",
    "confirm_action",
    # Config
    "ConfigManager",
    "get_config",
    "load_config",
    # Logging
    "ChronosLogger",
    "CorrelationContext",
    "JSONFormatter",
    "get_logger",
    "setup_logging",
    "log_event",
    "generate_correlation_id",
    "get_correlation_id",
    "set_correlation_id",
]
