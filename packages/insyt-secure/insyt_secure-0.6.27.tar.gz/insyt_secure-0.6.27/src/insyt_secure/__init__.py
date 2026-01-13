"""Insyt Secure package."""

__version__ = "0.6.27"

from .utils.logging_config import configure_logging, LoggingFormat

__all__ = ['configure_logging', 'LoggingFormat']