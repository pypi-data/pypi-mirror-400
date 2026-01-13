"""
Logging Configuration
=====================

Centralized logging setup for the simulation framework.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Create module-level logger
logger = logging.getLogger("sim")


class SimFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        # Format: [TIME] LEVEL module: message
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        if self.use_colors and record.levelname in self.COLORS:
            level = f"{self.COLORS[record.levelname]}{record.levelname:8s}{self.RESET}"
        else:
            level = f"{record.levelname:8s}"

        module = record.name.replace("sim.", "")
        message = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return f"[{timestamp}] {level} {module}: {message}"


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True,
    verbose: bool = False,
) -> logging.Logger:
    """
    Configure logging for the simulation framework.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs
        use_colors: Use colored output in terminal
        verbose: Enable verbose (DEBUG) logging

    Returns:
        Configured logger instance
    """
    if verbose:
        level = logging.DEBUG

    # Clear existing handlers
    logger.handlers.clear()
    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(SimFormatter(use_colors=use_colors))
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(SimFormatter(use_colors=False))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (will be prefixed with 'sim.')

    Returns:
        Logger instance
    """
    if not name.startswith("sim."):
        name = f"sim.{name}"
    return logging.getLogger(name)


# Convenience functions
def debug(msg: str, *args, **kwargs):
    """Log debug message."""
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message."""
    logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message."""
    logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message."""
    logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log critical message."""
    logger.critical(msg, *args, **kwargs)


class LogContext:
    """Context manager for temporary log level changes."""

    def __init__(self, level: int):
        self.level = level
        self.previous_level = None

    def __enter__(self):
        self.previous_level = logger.level
        logger.setLevel(self.level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.setLevel(self.previous_level)
        return False


def silence():
    """Context manager to silence all logging."""
    return LogContext(logging.CRITICAL + 1)


def verbose():
    """Context manager for verbose (DEBUG) logging."""
    return LogContext(logging.DEBUG)


# Initialize with default settings
setup_logging()
