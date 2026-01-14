"""Logging configuration and utilities.

This module provides a comprehensive logging system with:
- Configurable log levels and formats
- File and console handlers
- Structured logging support
- Log rotation
- Context-aware logging

Example:
    # Setup logging
    setup_logging(level="INFO")

    # Get logger
    logger = get_logger(__name__)
    logger.info("Application started")

    # Structured logging
    logger.info("Request processed", extra={"request_id": "abc123", "duration_ms": 50})
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any

from truthound_dashboard.config import get_settings


@dataclass
class LogConfig:
    """Configuration for logging.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Log format string.
        date_format: Date format string.
        log_to_file: Whether to log to file.
        log_dir: Directory for log files.
        max_file_size: Maximum size per log file in bytes.
        backup_count: Number of backup files to keep.
        json_format: Use JSON format for structured logging.
        include_thread: Include thread name in logs.
        include_process: Include process ID in logs.
    """

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    log_to_file: bool = True
    log_dir: Path | None = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    json_format: bool = False
    include_thread: bool = False
    include_process: bool = False


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging.

    Outputs logs in JSON format for easier parsing and analysis.
    """

    def __init__(
        self,
        include_thread: bool = False,
        include_process: bool = False,
    ) -> None:
        """Initialize JSON formatter.

        Args:
            include_thread: Include thread name in output.
            include_process: Include process ID in output.
        """
        super().__init__()
        self._include_thread = include_thread
        self._include_process = include_process

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON string.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add location info
        if record.pathname:
            log_data["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add thread/process info
        if self._include_thread:
            log_data["thread"] = record.threadName

        if self._include_process:
            log_data["process"] = record.process

        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        extra_keys = set(record.__dict__.keys()) - {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "message",
            "taskName",
        }

        for key in extra_keys:
            value = getattr(record, key)
            if value is not None:
                try:
                    # Ensure value is JSON serializable
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)

        return json.dumps(log_data)


class ColorFormatter(logging.Formatter):
    """Colored log formatter for console output.

    Uses ANSI escape codes to colorize log levels.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        use_colors: bool = True,
    ) -> None:
        """Initialize color formatter.

        Args:
            fmt: Log format string.
            datefmt: Date format string.
            use_colors: Whether to use colors.
        """
        super().__init__(fmt, datefmt)
        self._use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.

        Args:
            record: Log record to format.

        Returns:
            Formatted string with ANSI colors.
        """
        if self._use_colors:
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter with additional context.

    Allows adding persistent context to all log messages.
    """

    def __init__(
        self,
        logger: logging.Logger,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Initialize logger adapter.

        Args:
            logger: Base logger.
            extra: Extra context to add to all messages.
        """
        super().__init__(logger, extra or {})

    def process(
        self,
        msg: str,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Process log message with extra context.

        Args:
            msg: Log message.
            kwargs: Keyword arguments.

        Returns:
            Processed message and kwargs.
        """
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs

    def with_context(self, **context: Any) -> LoggerAdapter:
        """Create new adapter with additional context.

        Args:
            **context: Additional context to add.

        Returns:
            New LoggerAdapter with merged context.
        """
        merged = {**self.extra, **context}
        return LoggerAdapter(self.logger, merged)


def setup_logging(
    config: LogConfig | None = None,
    level: str | None = None,
) -> logging.Logger:
    """Configure application logging.

    Sets up logging with console and optional file handlers.

    Args:
        config: Logging configuration.
        level: Override log level.

    Returns:
        Root logger for the application.
    """
    settings = get_settings()
    config = config or LogConfig()

    # Override level if specified
    if level:
        config.level = level.upper()

    # Set log directory
    if config.log_dir is None:
        config.log_dir = settings.data_dir / "logs"

    # Create log directory
    config.log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger("truthound_dashboard")
    root_logger.setLevel(getattr(logging, config.level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.level))

    if config.json_format:
        console_formatter = JsonFormatter(
            include_thread=config.include_thread,
            include_process=config.include_process,
        )
    else:
        console_formatter = ColorFormatter(
            fmt=config.format,
            datefmt=config.date_format,
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if config.log_to_file:
        log_file = config.log_dir / "dashboard.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
        )
        file_handler.setLevel(getattr(logging, config.level))

        if config.json_format:
            file_formatter = JsonFormatter(
                include_thread=config.include_thread,
                include_process=config.include_process,
            )
        else:
            file_formatter = logging.Formatter(
                fmt=config.format,
                datefmt=config.date_format,
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure third-party loggers
    configure_library_loggers(config.level)

    root_logger.info(f"Logging configured at {config.level} level")
    return root_logger


def configure_library_loggers(level: str) -> None:
    """Configure logging levels for third-party libraries.

    Args:
        level: Application log level.
    """
    # Quiet down noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Enable SQLAlchemy logging in debug mode
    if level == "DEBUG":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str, **context: Any) -> LoggerAdapter:
    """Get a logger with optional context.

    Args:
        name: Logger name (typically __name__).
        **context: Additional context to add to all messages.

    Returns:
        LoggerAdapter instance.
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, context)


class AuditLogger:
    """Specialized logger for audit events.

    Logs security and compliance-relevant events in a structured format.
    """

    def __init__(self) -> None:
        """Initialize audit logger."""
        self._logger = logging.getLogger("truthound_dashboard.audit")

    def log_event(
        self,
        event_type: str,
        user: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        status: str = "success",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an audit event.

        Args:
            event_type: Type of event (auth, access, modification, etc.).
            user: User who performed the action.
            resource: Resource affected.
            action: Action performed.
            status: Result status (success, failure).
            details: Additional event details.
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": user or "system",
            "resource": resource,
            "action": action,
            "status": status,
        }

        if details:
            event["details"] = details

        self._logger.info(
            f"AUDIT: {event_type} - {action} on {resource}",
            extra=event,
        )

    def log_auth_success(self, user: str, method: str) -> None:
        """Log successful authentication."""
        self.log_event(
            event_type="auth",
            user=user,
            action="login",
            status="success",
            details={"method": method},
        )

    def log_auth_failure(self, user: str, reason: str) -> None:
        """Log failed authentication."""
        self.log_event(
            event_type="auth",
            user=user,
            action="login",
            status="failure",
            details={"reason": reason},
        )

    def log_resource_access(
        self,
        user: str,
        resource: str,
        action: str,
        granted: bool,
    ) -> None:
        """Log resource access attempt."""
        self.log_event(
            event_type="access",
            user=user,
            resource=resource,
            action=action,
            status="granted" if granted else "denied",
        )

    def log_data_modification(
        self,
        user: str,
        resource: str,
        action: str,
        changes: dict[str, Any] | None = None,
    ) -> None:
        """Log data modification."""
        self.log_event(
            event_type="modification",
            user=user,
            resource=resource,
            action=action,
            details={"changes": changes} if changes else None,
        )


# Singleton audit logger
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get audit logger singleton.

    Returns:
        AuditLogger instance.
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
