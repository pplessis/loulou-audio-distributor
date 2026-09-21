# CLI Contract — Drive Sync Enhancements

**Contract version**: 1.0.0

## Command

```text
sync_tool [OPTIONS] <source_dir>
```

Runs the audiobook drive sync with optional compression and metadata validation.

## Options

| Flag | Type | Default | Description | Requirement |
|------|------|---------|-------------|-------------|
| `--log-path PATH` | string | `./sync.log` | File path for structured logs | FR-003 |
| `--log-level LEVEL` | enum | `INFO` | One of `INFO`, `WARN`, `ERROR` | FR-002 |
| `--compress` | flag | off | Enable MP3 compression before upload | FR-004, FR-006 |
| `--compression-level LEVEL` | string | `64k` | Bitrate/quality target (ffmpeg-compatible) | FR-005 |
| `--metadata-endpoint URL` | string | `https://openlibrary.org/search.json` | Metadata API endpoint | FR-007, FR-010 |
| `--no-metadata-validation` | flag | off | Disable metadata validation | FR-007 (opt-out) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Sync completed (with or without per-book errors) |
| 1 | Fatal error (config invalid, log file unwritable and stderr unavailable, interrupted) |

## Log Format (JSON Lines)

Each line is a `LogEntry` per [data-model.md](../data-model.md):

```json
{"timestamp": "ISO8601", "level": "INFO|WARN|ERROR", "source": "scan|upload|compress|validate", "audiobook_id": "string|null", "event_type": "scan_start|scan_end|folder_created|file_uploaded|error|summary", "message": "string"}
```

Required event types (FR-001):
- `scan_start`, `scan_end` — library scan lifecycle
- `folder_created` — per audiobook Drive folder
- `file_uploaded` — per uploaded file
- `error` — includes timestamp + audiobook identifier (if applicable)
- `summary` — on successful completion, with counts of processed audiobooks, uploaded files, and errors

## Generated JSON Index (validation extension)

The generated book index at `app/books/metadata/{book_id}.json` gains an **optional additive field**:

```json
{ "validation_status": "pending|validated|validation_failed" }
```

- Absent when validation never ran (backward-compatible, constitution Principle II)
- `validated`: title/author/cover populated from OpenLibrary match
- `validation_failed`: no match or API error (WARN logged, processing continues)

## Metadata API Contract (OpenLibrary)

- Endpoint: `GET https://openlibrary.org/search.json?title=<t>&author=<a>&fields=title,author_name,cover_i,key`
- Response: `{"numFound": N, "docs": [{"title", "author_name": [...], "cover_i": N, "key": "/works/..."}]}`
- Cover: `https://covers.openlibrary.org/b/id/{cover_i}-L.jpg`
- No authentication required
- Timeouts and HTTP errors → WARN log, `validation_status=failed`, sync continues (SC-005)