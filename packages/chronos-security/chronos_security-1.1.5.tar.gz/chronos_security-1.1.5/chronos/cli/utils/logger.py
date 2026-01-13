"""
CHRONOS Logging System
======================

Structured logging with JSON format, file rotation, and rich console output.
Supports correlation IDs for request tracing across the platform.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from rich.theme import Theme

# Context variable for correlation ID (thread-safe)
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

# Default configuration
DEFAULT_LOG_DIR = Path(".chronos/logs")
DEFAULT_LOG_FILE = "chronos.log"
DEFAULT_JSON_LOG_FILE = "chronos.json.log"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Custom theme for console output
CHRONOS_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "critical": "red bold reverse",
    "debug": "dim",
    "success": "green",
    "timestamp": "dim cyan",
    "correlation": "magenta",
    "module": "blue",
})

# Global logger registry
_loggers: Dict[str, logging.Logger] = {}
_initialized: bool = False


class CorrelationIdFilter(logging.Filter):
    """Filter that adds correlation ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to the log record."""
        record.correlation_id = get_correlation_id() or "no-correlation"
        return True


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs log records as JSON.
    
    Provides structured logging for easy parsing and analysis.
    """
    
    def __init__(
        self,
        include_extra: bool = True,
        include_stack: bool = True,
    ):
        """
        Initialize JSON formatter.
        
        Args:
            include_extra: Include extra fields from log record.
            include_stack: Include stack trace for exceptions.
        """
        super().__init__()
        self.include_extra = include_extra
        self.include_stack = include_stack
        
        # Standard LogRecord attributes to exclude from extra
        self._standard_attrs = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "exc_info", "exc_text", "thread", "threadName",
            "message", "correlation_id", "taskName",
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        # Build base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "correlation_id": getattr(record, "correlation_id", None),
            "process": record.process,
            "thread": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info and self.include_stack:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add extra fields
        if self.include_extra:
            extra = {}
            for key, value in record.__dict__.items():
                if key not in self._standard_attrs:
                    try:
                        # Ensure value is JSON serializable
                        json.dumps(value)
                        extra[key] = value
                    except (TypeError, ValueError):
                        extra[key] = str(value)
            
            if extra:
                log_entry["extra"] = extra
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RichConsoleHandler(RichHandler):
    """
    Enhanced Rich handler with CHRONOS styling.
    
    Provides beautiful console output with color coding and formatting.
    """
    
    def __init__(
        self,
        console: Optional[Console] = None,
        show_time: bool = True,
        show_path: bool = False,
        show_level: bool = True,
        show_correlation: bool = True,
        **kwargs,
    ):
        """
        Initialize Rich console handler.
        
        Args:
            console: Rich Console instance.
            show_time: Show timestamp.
            show_path: Show file path.
            show_level: Show log level.
            show_correlation: Show correlation ID.
        """
        self.show_correlation = show_correlation
        
        if console is None:
            console = Console(theme=CHRONOS_THEME, stderr=True)
        
        super().__init__(
            console=console,
            show_time=show_time,
            show_path=show_path,
            show_level=show_level,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            markup=True,
            **kwargs,
        )
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with correlation ID."""
        # Add correlation ID to message if enabled
        if self.show_correlation:
            correlation_id = getattr(record, "correlation_id", None)
            if correlation_id and correlation_id != "no-correlation":
                # Prepend correlation ID to message
                original_msg = record.msg
                record.msg = f"[correlation]{correlation_id[:8]}[/correlation] {original_msg}"
        
        super().emit(record)


class ChronosLogger:
    """
    Main logging class for CHRONOS.
    
    Provides a unified interface for logging with:
    - Multiple output handlers (console, file, JSON)
    - Correlation ID tracking
    - Structured logging support
    - Rich formatting
    
    Example:
        logger = ChronosLogger("my_module")
        logger.info("Processing started", extra={"items": 42})
        
        with logger.correlation_context():
            logger.info("Request processing")
            do_work()
            logger.info("Request complete")
    """
    
    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.INFO,
        log_dir: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = True,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ):
        """
        Initialize CHRONOS logger.
        
        Args:
            name: Logger name (usually module name).
            level: Logging level.
            log_dir: Directory for log files.
            enable_console: Enable console output.
            enable_file: Enable file logging.
            enable_json: Enable JSON file logging.
            max_bytes: Max size per log file.
            backup_count: Number of backup files to keep.
        """
        self.name = f"chronos.{name}" if not name.startswith("chronos") else name
        self.log_dir = log_dir or DEFAULT_LOG_DIR
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Get or create logger
        self._logger = logging.getLogger(self.name)
        
        # Set level
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Add correlation ID filter
        self._logger.addFilter(CorrelationIdFilter())
        
        # Configure handlers if not already done
        if not self._logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up logging handlers."""
        # Ensure log directory exists
        if self.enable_file or self.enable_json:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Console handler with Rich formatting
        if self.enable_console:
            console_handler = RichConsoleHandler(
                show_time=True,
                show_path=False,
                show_level=True,
                show_correlation=True,
            )
            console_handler.setLevel(self._logger.level)
            self._logger.addHandler(console_handler)
        
        # File handler with rotation (human-readable)
        if self.enable_file:
            file_path = self.log_dir / DEFAULT_LOG_FILE
            file_handler = RotatingFileHandler(
                filename=str(file_path),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(self._logger.level)
            file_handler.setFormatter(logging.Formatter(
                fmt=DEFAULT_LOG_FORMAT,
                datefmt=DEFAULT_DATE_FORMAT,
            ))
            file_handler.addFilter(CorrelationIdFilter())
            self._logger.addHandler(file_handler)
        
        # JSON file handler with rotation (structured)
        if self.enable_json:
            json_path = self.log_dir / DEFAULT_JSON_LOG_FILE
            json_handler = RotatingFileHandler(
                filename=str(json_path),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            json_handler.setLevel(self._logger.level)
            json_handler.setFormatter(JSONFormatter())
            json_handler.addFilter(CorrelationIdFilter())
            self._logger.addHandler(json_handler)
    
    def _log(
        self,
        level: int,
        msg: str,
        *args,
        exc_info: Any = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Internal logging method."""
        extra = extra or {}
        self._logger.log(level, msg, *args, exc_info=exc_info, extra=extra, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def success(self, msg: str, *args, **kwargs) -> None:
        """Log success message (INFO level with success styling)."""
        # Add success marker for Rich handler
        msg = f"[success]✓[/success] {msg}"
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def security(self, msg: str, *args, **kwargs) -> None:
        """Log security-related message (WARNING level)."""
        extra = kwargs.pop("extra", {})
        extra["security_event"] = True
        msg = f"🔒 {msg}"
        self._log(logging.WARNING, msg, *args, extra=extra, **kwargs)
    
    def audit(self, msg: str, *args, **kwargs) -> None:
        """Log audit message (INFO level with audit marker)."""
        extra = kwargs.pop("extra", {})
        extra["audit_event"] = True
        msg = f"📋 {msg}"
        self._log(logging.INFO, msg, *args, extra=extra, **kwargs)
    
    def set_level(self, level: Union[str, int]) -> None:
        """Set logging level."""
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)
    
    @property
    def level(self) -> int:
        """Get current logging level."""
        return self._logger.level
    
    def correlation_context(self, correlation_id: Optional[str] = None):
        """
        Context manager for correlation ID scope.
        
        Args:
            correlation_id: Optional correlation ID (auto-generated if None).
            
        Returns:
            Context manager.
            
        Example:
            with logger.correlation_context() as cid:
                logger.info("Processing request")
                process_request()
        """
        return CorrelationContext(correlation_id)


class CorrelationContext:
    """Context manager for correlation ID tracking."""
    
    def __init__(self, correlation_id: Optional[str] = None):
        """
        Initialize correlation context.
        
        Args:
            correlation_id: Optional correlation ID (auto-generated if None).
        """
        self.correlation_id = correlation_id or generate_correlation_id()
        self._token: Optional[Any] = None
    
    def __enter__(self) -> str:
        """Enter context and set correlation ID."""
        self._token = _correlation_id.set(self.correlation_id)
        return self.correlation_id
    
    def __exit__(self, *args) -> None:
        """Exit context and reset correlation ID."""
        if self._token is not None:
            _correlation_id.reset(self._token)


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID.
    
    Returns:
        Unique correlation ID string.
    """
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.
    
    Returns:
        Current correlation ID or None.
    """
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.
    
    Args:
        correlation_id: Correlation ID to set.
    """
    _correlation_id.set(correlation_id)


def get_logger(
    name: str,
    level: Union[str, int] = logging.INFO,
    **kwargs,
) -> ChronosLogger:
    """
    Get or create a CHRONOS logger.
    
    Args:
        name: Logger name.
        level: Logging level.
        **kwargs: Additional arguments for ChronosLogger.
        
    Returns:
        ChronosLogger instance.
    """
    full_name = f"chronos.{name}" if not name.startswith("chronos") else name
    
    if full_name not in _loggers:
        _loggers[full_name] = ChronosLogger(name, level=level, **kwargs)
    
    return _loggers[full_name]


def setup_logging(
    level: Union[str, int] = logging.INFO,
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> ChronosLogger:
    """
    Set up the root CHRONOS logger.
    
    Args:
        level: Logging level.
        log_dir: Directory for log files.
        enable_console: Enable console output.
        enable_file: Enable file logging.
        enable_json: Enable JSON file logging.
        max_bytes: Max size per log file.
        backup_count: Number of backup files to keep.
        
    Returns:
        Root ChronosLogger instance.
    """
    global _initialized
    
    # Configure root logger to not propagate
    root = logging.getLogger()
    root.setLevel(logging.WARNING)  # Only show warnings from third-party
    
    # Create and configure main CHRONOS logger
    logger = get_logger(
        "root",
        level=level,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_json=enable_json,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    
    _initialized = True
    return logger


def log_event(
    event_type: str,
    message: str,
    level: str = "INFO",
    **data,
) -> None:
    """
    Log a structured event.
    
    Convenience function for logging structured events with metadata.
    
    Args:
        event_type: Type of event (e.g., "scan_started", "threat_detected").
        message: Human-readable message.
        level: Log level.
        **data: Additional event data.
        
    Example:
        log_event(
            "threat_detected",
            "Malware signature found",
            severity="high",
            file="/path/to/file",
            signature_id="MAL-001",
        )
    """
    logger = get_logger("events")
    
    extra = {
        "event_type": event_type,
        "event_data": data,
    }
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger._log(log_level, message, extra=extra)


# Convenience aliases
debug = lambda msg, **kw: get_logger("root").debug(msg, **kw)
info = lambda msg, **kw: get_logger("root").info(msg, **kw)
warning = lambda msg, **kw: get_logger("root").warning(msg, **kw)
error = lambda msg, **kw: get_logger("root").error(msg, **kw)
critical = lambda msg, **kw: get_logger("root").critical(msg, **kw)
