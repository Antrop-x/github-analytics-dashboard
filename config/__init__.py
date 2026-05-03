"""
Configuration package for GitHub Analytics Dashboard.
"""

from .settings import Settings, settings
from .logging_config import setup_logging, get_logger

__all__ = ["Settings", "settings", "setup_logging", "get_logger"]