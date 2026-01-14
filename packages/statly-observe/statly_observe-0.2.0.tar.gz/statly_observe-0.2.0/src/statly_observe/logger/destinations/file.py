"""
File Destination
Writes log entries to files with rotation support
"""

import gzip
import json
import os
import shutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, TextIO

from ..types import LogEntry, LogLevel, FileDestinationConfig, LEVEL_NAMES


def parse_size(size: str) -> int:
    """Parse size string to bytes"""
    size = size.strip().upper()
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
    }

    for suffix, mult in multipliers.items():
        if size.endswith(suffix):
            try:
                return int(float(size[:-len(suffix)].strip()) * mult)
            except ValueError:
                break

    # Default 10MB
    return 10 * 1024 * 1024


class FileDestination:
    """File log destination with rotation support"""

    name = "file"

    def __init__(self, config: FileDestinationConfig):
        self.config = config
        self.min_level = LogLevel.TRACE
        self._file: Optional[TextIO] = None
        self._current_size = 0
        self._last_rotation = datetime.now()
        self._lock = threading.Lock()
        self._max_size = parse_size(config.max_size)

        # Ensure directory exists
        Path(config.path).parent.mkdir(parents=True, exist_ok=True)

        # Open file
        self._open_file()

    def _open_file(self) -> None:
        """Open the log file"""
        try:
            self._file = open(self.config.path, "a", encoding="utf-8")
            self._current_size = os.path.getsize(self.config.path) if os.path.exists(self.config.path) else 0
        except OSError as e:
            print(f"[Statly Logger] Failed to open log file: {e}")
            self._file = None

    def write(self, entry: LogEntry) -> None:
        """Write a log entry to the file"""
        if not self.config.enabled or not self._file:
            return

        # Check level filter
        if self.config.levels and entry.level not in self.config.levels:
            return

        if entry.level < self.min_level:
            return

        # Format the entry
        if self.config.format == "json":
            line = json.dumps(entry.to_dict())
        else:
            # Text format
            ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            level = LEVEL_NAMES[entry.level].upper()
            logger = f"[{entry.logger_name}] " if entry.logger_name else ""
            line = f"{ts} [{level}] {logger}{entry.message}"
            if entry.context:
                line += f" {json.dumps(entry.context)}"

        line += "\n"

        with self._lock:
            try:
                self._file.write(line)
                self._current_size += len(line.encode("utf-8"))

                # Check rotation
                self._check_rotation()
            except OSError as e:
                print(f"[Statly Logger] Failed to write to log file: {e}")

    def _check_rotation(self) -> None:
        """Check if rotation is needed"""
        should_rotate = False

        if self.config.rotation_type == "size":
            should_rotate = self._current_size >= self._max_size
        elif self.config.rotation_type == "time":
            interval = self._get_rotation_interval()
            should_rotate = datetime.now() - self._last_rotation >= interval

        if should_rotate:
            self._rotate()

    def _get_rotation_interval(self) -> timedelta:
        """Get rotation interval as timedelta"""
        intervals = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }
        return intervals.get(self.config.rotation_interval, timedelta(days=1))

    def _rotate(self) -> None:
        """Rotate the log file"""
        if not self._file:
            return

        try:
            self._file.close()

            # Generate rotated filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            rotated_path = f"{self.config.path}.{timestamp}"

            # Rename current file
            if os.path.exists(self.config.path):
                os.rename(self.config.path, rotated_path)

                # Compress if configured
                if self.config.compress:
                    with open(rotated_path, "rb") as f_in:
                        with gzip.open(f"{rotated_path}.gz", "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(rotated_path)

            # Cleanup old files
            self._cleanup_old_files()

            # Reopen file
            self._open_file()
            self._last_rotation = datetime.now()

        except OSError as e:
            print(f"[Statly Logger] Failed to rotate log file: {e}")
            self._open_file()

    def _cleanup_old_files(self) -> None:
        """Clean up old rotated files"""
        try:
            log_dir = Path(self.config.path).parent
            base_name = Path(self.config.path).name

            # Find rotated files
            rotated_files = sorted(
                [f for f in log_dir.iterdir()
                 if f.name.startswith(base_name + ".") and f != Path(self.config.path)],
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            # Remove files exceeding max_files
            for old_file in rotated_files[self.config.max_files:]:
                old_file.unlink()

            # Remove files exceeding retention_days
            if self.config.retention_days:
                cutoff = datetime.now() - timedelta(days=self.config.retention_days)
                for f in rotated_files:
                    if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                        f.unlink()

        except OSError as e:
            print(f"[Statly Logger] Failed to cleanup old files: {e}")

    def set_min_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        self.min_level = level

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the destination"""
        self.config.enabled = enabled

    def flush(self) -> None:
        """Flush the file"""
        if self._file:
            with self._lock:
                self._file.flush()

    def close(self) -> None:
        """Close the destination"""
        if self._file:
            with self._lock:
                self._file.close()
                self._file = None
