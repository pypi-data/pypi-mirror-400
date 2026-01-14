"""
Console Destination
Outputs log entries to the console with formatting and colors
"""

import json
import sys
from datetime import datetime
from typing import Optional, TextIO

from ..types import LogEntry, LogLevel, ConsoleDestinationConfig, LEVEL_NAMES


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    # Background
    BG_RED = "\033[41m"
    WHITE = "\033[37m"


# Level colors
LEVEL_COLORS = {
    LogLevel.TRACE: Colors.GRAY,
    LogLevel.DEBUG: Colors.CYAN,
    LogLevel.INFO: Colors.GREEN,
    LogLevel.WARN: Colors.YELLOW,
    LogLevel.ERROR: Colors.RED,
    LogLevel.FATAL: f"{Colors.BG_RED}{Colors.WHITE}",
    LogLevel.AUDIT: Colors.MAGENTA,
}

# Level labels (padded)
LEVEL_LABELS = {
    LogLevel.TRACE: "TRACE",
    LogLevel.DEBUG: "DEBUG",
    LogLevel.INFO: "INFO ",
    LogLevel.WARN: "WARN ",
    LogLevel.ERROR: "ERROR",
    LogLevel.FATAL: "FATAL",
    LogLevel.AUDIT: "AUDIT",
}


class ConsoleDestination:
    """Console log destination with color support"""

    name = "console"

    def __init__(
        self,
        config: Optional[ConsoleDestinationConfig] = None,
        stream: Optional[TextIO] = None,
    ):
        self.config = config or ConsoleDestinationConfig()
        self.stream = stream or sys.stderr
        self.min_level = LogLevel.TRACE
        self._supports_colors = self._check_color_support()

    def _check_color_support(self) -> bool:
        """Check if the terminal supports colors"""
        if not self.config.colors:
            return False

        # Check if stream is a TTY
        if hasattr(self.stream, "isatty") and not self.stream.isatty():
            return False

        # Check environment variables
        import os
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("FORCE_COLOR"):
            return True
        if os.environ.get("TERM") == "dumb":
            return False

        return True

    def write(self, entry: LogEntry) -> None:
        """Write a log entry to the console"""
        if not self.config.enabled:
            return

        # Check level filter
        if self.config.levels and entry.level not in self.config.levels:
            return

        if entry.level < self.min_level:
            return

        # Format and output
        if self.config.format == "json":
            output = json.dumps(entry.to_dict())
        else:
            output = self._format_pretty(entry)

        print(output, file=self.stream)

    def _format_pretty(self, entry: LogEntry) -> str:
        """Format an entry for pretty output"""
        parts = []
        use_colors = self._supports_colors

        # Timestamp
        if self.config.timestamps:
            ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            if use_colors:
                parts.append(f"{Colors.DIM}{ts}{Colors.RESET}")
            else:
                parts.append(ts)

        # Level
        level_label = LEVEL_LABELS[entry.level]
        if use_colors:
            color = LEVEL_COLORS[entry.level]
            parts.append(f"{color}{level_label}{Colors.RESET}")
        else:
            parts.append(level_label)

        # Logger name
        if entry.logger_name:
            if use_colors:
                parts.append(f"{Colors.BLUE}[{entry.logger_name}]{Colors.RESET}")
            else:
                parts.append(f"[{entry.logger_name}]")

        # Message
        parts.append(entry.message)

        result = " ".join(parts)

        # Context
        if entry.context:
            context_str = json.dumps(entry.context, indent=2)
            if use_colors:
                result += f"\n{Colors.DIM}{context_str}{Colors.RESET}"
            else:
                result += f"\n{context_str}"

        return result

    def set_min_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        self.min_level = level

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the destination"""
        self.config.enabled = enabled

    def flush(self) -> None:
        """Flush the stream"""
        self.stream.flush()

    def close(self) -> None:
        """Close the destination"""
        self.flush()
