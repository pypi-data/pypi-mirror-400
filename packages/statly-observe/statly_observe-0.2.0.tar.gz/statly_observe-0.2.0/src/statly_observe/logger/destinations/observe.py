"""
Observe Destination
Sends log entries to Statly Observe backend with batching and sampling
"""

import json
import random
import threading
import time
from queue import Queue, Empty
from typing import Optional
from urllib.parse import urlparse

import requests

from ..types import LogEntry, LogLevel, ObserveDestinationConfig


DEFAULT_SAMPLING = {
    LogLevel.TRACE: 0.01,   # 1%
    LogLevel.DEBUG: 0.1,    # 10%
    LogLevel.INFO: 0.5,     # 50%
    LogLevel.WARN: 1.0,     # 100%
    LogLevel.ERROR: 1.0,    # 100%
    LogLevel.FATAL: 1.0,    # 100%
    LogLevel.AUDIT: 1.0,    # 100% - never sampled
}


class ObserveDestination:
    """Remote log destination with batching and sampling"""

    name = "observe"

    def __init__(
        self,
        dsn: str,
        config: Optional[ObserveDestinationConfig] = None,
    ):
        self.dsn = dsn
        self.config = config or ObserveDestinationConfig()
        self.endpoint = self._parse_endpoint(dsn)
        self.min_level = LogLevel.TRACE

        # Sampling rates
        self.sampling = {**DEFAULT_SAMPLING}
        if self.config.sampling:
            self.sampling.update(self.config.sampling)

        # Queue and worker
        self._queue: Queue[LogEntry] = Queue()
        self._shutdown = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Start worker
        self._start_worker()

    def _parse_endpoint(self, dsn: str) -> str:
        """Parse DSN to construct endpoint"""
        try:
            parsed = urlparse(dsn)
            return f"{parsed.scheme}://{parsed.hostname}/api/v1/logs/ingest"
        except Exception:
            return "https://statly.live/api/v1/logs/ingest"

    def _start_worker(self) -> None:
        """Start the background worker"""
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def _worker_loop(self) -> None:
        """Background worker for batched sending"""
        batch: list[LogEntry] = []
        last_flush = time.time()

        while not self._shutdown.is_set():
            try:
                # Get entries from queue
                try:
                    entry = self._queue.get(timeout=0.5)
                    batch.append(entry)
                    self._queue.task_done()
                except Empty:
                    pass

                # Check if we should flush
                should_flush = (
                    len(batch) >= self.config.batch_size
                    or (batch and time.time() - last_flush >= self.config.flush_interval)
                )

                if should_flush and batch:
                    self._send_batch(batch)
                    batch = []
                    last_flush = time.time()

            except Exception as e:
                print(f"[Statly Logger] Worker error: {e}")

        # Flush remaining on shutdown
        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: list[LogEntry]) -> bool:
        """Send a batch of entries"""
        if not batch:
            return True

        try:
            payload = {"logs": [entry.to_dict() for entry in batch]}

            response = requests.post(
                self.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Statly-DSN": self.dsn,
                    "User-Agent": "statly-observe-python/0.2.0",
                },
                timeout=30,
            )

            if response.status_code in (200, 202):
                return True

            print(f"[Statly Logger] API error: {response.status_code}")
            return False

        except requests.RequestException as e:
            print(f"[Statly Logger] Request failed: {e}")
            return False

    def write(self, entry: LogEntry) -> None:
        """Write a log entry (queues for batching)"""
        if not self.config.enabled:
            return

        # Check level filter
        if self.config.levels and entry.level not in self.config.levels:
            return

        if entry.level < self.min_level:
            return

        # Apply sampling (audit logs never sampled)
        if entry.level != LogLevel.AUDIT:
            sample_rate = self.sampling.get(entry.level, 1.0)
            if random.random() > sample_rate:
                return

        # Add to queue
        self._queue.put(entry)

    def set_min_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        self.min_level = level

    def set_sampling_rate(self, level: LogLevel, rate: float) -> None:
        """Set sampling rate for a level"""
        self.sampling[level] = max(0.0, min(1.0, rate))

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the destination"""
        self.config.enabled = enabled

    def flush(self) -> None:
        """Force flush queued entries"""
        # Wait for queue to empty
        self._queue.join()

    def close(self) -> None:
        """Close the destination"""
        self._shutdown.set()
        if self._worker:
            self._worker.join(timeout=5.0)

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self._queue.qsize()
