"""Data entities for the Drive Sync Enhancements feature."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    VALIDATION_FAILED = "validation_failed"


@dataclass
class SyncConfig:
    """Runtime configuration for the sync tool (FR-002, FR-003, FR-004, FR-005, FR-007)."""

    log_path: str = "sync.log"
    log_level: LogLevel = LogLevel.INFO
    compression_enabled: bool = False
    compression_level: str = "64k"
    metadata_api_endpoint: str = "https://openlibrary.org/search.json"
    metadata_validation_enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.log_level, LogLevel):
            try:
                self.log_level = LogLevel(str(self.log_level).upper())
            except ValueError:
                raise ValueError(
                    f"Invalid log_level {self.log_level!r}: must be one of INFO, WARN, ERROR"
                )
        if not self.metadata_api_endpoint.startswith(("http://", "https://")):
            raise ValueError(f"Invalid metadata endpoint URL: {self.metadata_api_endpoint!r}")


@dataclass
class LogEntry:
    """A structured record of an event during the sync process (FR-001)."""

    timestamp: datetime
    level: LogLevel
    source: str
    event_type: str
    message: str
    audiobook_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat(),
            "level": self.level.value,
            "source": self.source,
            "audiobook_id": self.audiobook_id,
            "event_type": self.event_type,
            "message": self.message,
        }


@dataclass
class CompressionSettings:
    """Configuration controlling optional MP3 compression (FR-004, FR-005, FR-006)."""

    enabled: bool = False
    compression_level: str = "64k"


@dataclass
class DatabaseMatch:
    """A candidate match returned by the online metadata database (FR-007, FR-008)."""

    confidence: float
    matched_title: str
    matched_author: Optional[str] = None
    cover_url: Optional[str] = None


@dataclass
class Audiobook:
    """An audiobook detected by the base sync tool, extended with validation status."""

    book_id: str
    title: str
    author: Optional[str] = None
    cover: Optional[str] = None
    chapters: list = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    folder_name: Optional[str] = None
