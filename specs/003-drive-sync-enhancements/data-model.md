# Data Model — Drive Sync Enhancements

**Feature**: [003-drive-sync-enhancements](spec.md)
**Date**: 2026-09-19

---

## Entities

### SyncConfig

**Description**: Runtime configuration for the sync tool, loaded from CLI args / env / file.

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| log_path | string | Yes | File path for structured log output |
| log_level | enum (INFO/WARN/ERROR) | Yes | Minimum log level to record |
| compression_enabled | boolean | Yes | Whether MP3 compression runs (default False) |
| compression_level | string/int | Yes | Bitrate/quality target (default 64kbps) |
| metadata_api_endpoint | string | Yes | Metadata API URL (default OpenLibrary search.json) |

**Validation Rules**:
- `log_level` must be one of INFO, WARN, ERROR (FR-002)
- `compression_enabled` defaults to False (FR-006)
- Metadata endpoint must be a valid HTTP(S) URL (edge case: invalid API key/endpoint)

---

### LogEntry

**Description**: A record of an event during the sync process (FR-001).

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | datetime (ISO8601) | Yes | When the event occurred |
| level | enum (INFO/WARN/ERROR) | Yes | Severity level |
| source | string | Yes | Component emitting the log (scan/upload/compress/validate) |
| audiobook_id | string | No | Audiobook identifier (if applicable) |
| event_type | string | Yes | Event type (scan_start, scan_end, folder_created, file_uploaded, error, summary) |
| message | string | Yes | Human-readable message |

**Validation Rules**:
- `level` matches FR-002 levels
- `timestamp` auto-generated
- Unwritable log file → entry logged to stderr, sync continues (spec edge case)

**Storage**: Appended to the file at `config.log_path`.

---

### CompressionSettings

**Description**: Configuration controlling optional MP3 compression (FR-004, FR-005, FR-006).

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| enabled | boolean | Yes | Master switch (default False) |
| compression_level | string/int | Yes | Bitrate/quality target (default 64kbps VBR-equivalent) |

**Validation Rules**:
- Compression is skipped by default (FR-006)
- If compressed output is larger than original, keep the original and log a WARN (spec edge case)
- Only MP3 files are compressed (base FR-022)

---

### DatabaseMatch

**Description**: A candidate match returned by the online metadata database (FR-007, FR-008).

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| confidence | float (0-1) | Yes | Match confidence score |
| matched_title | string | Yes | Title from the database |
| matched_author | string | No | Author from the database |
| cover_url | string | No | Cover image URL (e.g., OpenLibrary covers endpoint) |

**Validation Rules**:
- Matches with low confidence or conflicting results trigger a WARN log and no modification (spec edge cases)

---

### Audiobook (extended from base feature 002)

**Description**: A detected audiobook; extended with a metadata validation status.

**Fields (addition)**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| validation_status | enum (pending/validated/validation_failed) | No (additive, backward-compatible) | Metadata validation state |

**Validation Rules (addition)**:
- `validation_status` is an **optional, additive field** — absent value implies `pending` (constitution Principle II: backward-compatible JSON contract change)
- Set to `validated` when metadata matched the online database; `validation_failed` on no-match or error; `pending` when not yet checked
- When the database is unreachable, the sync continues for all other audiobooks (SC-005)

---

## Entity Relationship Summary

```
SyncConfig (1) ──── (1) LogEntry (N)  (each log entry references sync context)
SyncConfig (1) ──── (1) CompressionSettings (1)
Audiobook (N) ──── (N) DatabaseMatch (queried per audiobook when validation enabled)
Audiobook (1) ──── (N) LogEntry (audiobook_id references Audiobook)
```

- LogEntry optionally references an Audiobook by id
- DatabaseMatch is a transient query result, not persisted
- CompressionSettings derives from SyncConfig

---

## Data Flow

1. **Configuration**: CLI/env/file → `SyncConfig` (log path, level, compression, metadata endpoint)
2. **Sync run**: `sync_tool/sync.py` walks the source directory, identifies audiobooks (base 002)
3. **Logging**: each scan start/end, folder creation, file upload, and error produces a `LogEntry` → log file
4. **Compression**: if `CompressionSettings.enabled`, each MP3 is compressed before upload; result logged
5. **Validation**: if enabled, each Audiobook is queried against OpenLibrary; missing fields populated, `validation_status` set
6. **Index generation**: JSON index written to `app/books/metadata/{book_id}.json` including optional `validation_status`

---

## Storage Architecture

```
sync_tool/                      # CLI package (new)
tests/                          # contract + integration tests (existing convention)
app/books/metadata/{book_id}.json   # Generated JSON index (+ optional validation_status)
<log_path>                      # Configurable structured log file
```

Log file format (JSON Lines):
```json
{"timestamp": "2026-09-19T14:30:00Z", "level": "INFO", "source": "scan", "audiobook_id": null, "event_type": "scan_start", "message": "Scanning /books"}
{"timestamp": "2026-09-19T14:31:05Z", "level": "INFO", "source": "upload", "audiobook_id": "le-petit-prince", "event_type": "file_uploaded", "message": "chapter-01.mp3"}
```