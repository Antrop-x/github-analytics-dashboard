"""
Centralized logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Setup centralized logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        log_file: Optional log file path

    Returns:
        Root logger instance
    """
    # Use settings defaults if not provided
    level = level or settings.LOG_LEVEL
    format_string = format_string or settings.LOG_FORMAT

    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on import
root_logger = setup_logging()