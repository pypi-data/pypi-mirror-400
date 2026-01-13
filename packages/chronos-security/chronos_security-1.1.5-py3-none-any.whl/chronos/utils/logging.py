"""
CHRONOS Logging Utilities
=========================

Re-exports logging utilities from cli.utils.logger for backwards compatibility.
For new code, prefer importing directly from chronos.cli.utils.logger.
"""

import logging
import sys
from typing import Optional

from rich.logging import RichHandler

# Re-export from main logger module
try:
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
except ImportError:
    # Fallback for standalone usage
    pass


def setup_logging_legacy(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rich_output: bool = True
) -> None:
    """
    Configure logging for CHRONOS (legacy interface).
    
    For new code, use setup_logging() instead.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional file path for log output.
        rich_output: Use rich formatting for console output.
    """
    handlers = []
    
    # Console handler
    if rich_output:
        console_handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_path=False,
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
    )


# Backwards compatibility aliases
setup_logging_simple = setup_logging_legacy


__all__ = [
    # Main exports
    "ChronosLogger",
    "CorrelationContext", 
    "JSONFormatter",
    "get_logger",
    "setup_logging",
    "log_event",
    "generate_correlation_id",
    "get_correlation_id",
    "set_correlation_id",
    # Legacy
    "setup_logging_legacy",
    "setup_logging_simple",
]
