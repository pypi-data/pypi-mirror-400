"""
Log Destinations
Multi-destination logging support
"""

from .console import ConsoleDestination
from .observe import ObserveDestination
from .file import FileDestination

__all__ = ["ConsoleDestination", "ObserveDestination", "FileDestination"]
