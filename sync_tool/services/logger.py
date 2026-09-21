"""Structured JSON-lines logging service (FR-001, FR-002, FR-003)."""

import sys
from datetime import datetime, timezone
from typing import List, Optional

from ..models import LogEntry, LogLevel


class SyncLogger:
    """Appends JSON-lines LogEntry records to a configured file.

    If the log file cannot be written (permissions, disk full), entries are
    written to stderr and sync continues (spec edge case).
    """

    def __init__(self, log_path: str, level: LogLevel = LogLevel.INFO):
        self.log_path = log_path
        self.level = level
        self._file = None
        self._open()

    def _open(self) -> None:
        try:
            self._file = open(self.log_path, "a", encoding="utf-8")
        except OSError:
            self._file = None

    def log_entry(
        self,
        level: LogLevel,
        source: str,
        event_type: str,
        message: str,
        audiobook_id: Optional[str] = None,
    ) -> None:
        if self._level_allowed(level):
            entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=level,
                source=source,
                event_type=event_type,
                message=message,
                audiobook_id=audiobook_id,
            )
            self._write(entry)

    def _level_allowed(self, level: LogLevel) -> bool:
        order = {LogLevel.INFO: 0, LogLevel.WARN: 1, LogLevel.ERROR: 2}
        return order[level] >= order[self.level]

    def _write(self, entry: LogEntry) -> None:
        line = __import__("json").dumps(entry.to_dict()) + "\n"
        if self._file is not None:
            try:
                self._file.write(line)
                self._file.flush()
                return
            except OSError:
                self._file = None
        # Fallback: log file unwritable — write to stderr and continue
        sys.stderr.write(line)

    def close(self) -> None:
        if self._file is not None:
            try:
                self._file.close()
            except OSError:
                pass
            self._file = None

    def __enter__(self) -> "SyncLogger":
        return self

    def __exit__(self, *exc) -> None:
        self.close()