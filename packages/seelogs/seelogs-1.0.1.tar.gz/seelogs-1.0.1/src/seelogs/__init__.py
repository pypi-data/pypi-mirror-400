"""
SeeLogs Python Client
"""

from .client import SeeLogs
from .types import LogLevel, LogEvent, SeeLogsConfig

__version__ = "1.0.1"
__all__ = ["SeeLogs", "LogLevel", "LogEvent", "SeeLogsConfig"]