# Quickstart — Drive Sync Enhancements

**Feature**: [003-drive-sync-enhancements](spec.md)
**Date**: 2026-09-19

---

## Prerequisites

- Python 3.11+ with pip
- `ffmpeg` installed and on PATH (for MP3 compression)
- Base drive sync dependencies: `requests`, `google-api-python-client`
- Internet connectivity for metadata validation

## Setup

```bash
# Install dependencies
pip install pydub

# Verify ffmpeg is available
ffmpeg -version

# (Optional) Existing book metadata
ls app/books/metadata/*.json
```

## Running Validation

### 1. Logging Flow

```bash
cd <repo root>
python -m sync_tool /path/to/audiobooks --log-path /tmp/sync.log
# Verify: /tmp/sync.log contains scan_start, folder_created, file_uploaded, summary entries
```

### 2. Compression Flow

```bash
# Compression off (default) — files uploaded at original size
python -m sync_tool /path/to/audiobooks

# Compression on at 64k
python -m sync_tool /path/to/audiobooks --compress --compression-level 64k
# Verify: uploaded MP3 files are smaller and still playable
```

### 3. Metadata Validation Flow

```bash
python -m sync_tool /path/to/audiobooks --metadata-endpoint https://openlibrary.org/search.json
# Verify: generated JSON index files include validation_status;
# missing cover fields are populated from OpenLibrary where a match is found
```

### 4. Edge Case: Unreachable Database

```bash
python -m sync_tool /path/to/audiobooks --metadata-endpoint https://invalid.invalid/search.json
# Verify: WARN entries logged, sync continues for all audiobooks, validation_status=failed
```

### 5. Edge Case: Log File Unwritable

```bash
python -m sync_tool /path/to/audiobooks --log-path /nonexistent/dir/sync.log
# Verify: errors logged to stderr, sync continues
```

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run full suite (deterministic: fixtures used, no live network)
cd <repo root> && python -m pytest tests/

# Optional live metadata test (requires network)
python -m pytest tests/integration/test_metadata_validation.py -m live
```

## Expected Outcomes

| Scenario | Expected Result |
|----------|-----------------|
| Sync with default logging | Structured log entries for scan/upload/summary (SC-001) |
| Compression enabled | 95% of MP3 files reduced ≥20%, still playable (SC-002) |
| Metadata validation enabled | ≥80% of well-known audiobooks matched (SC-003); missing cover populated |
| Configuration before run | log path, log level, compression, API endpoint configurable (SC-004) |
| Database unreachable | Sync continues for all other audiobooks, WARN logged (SC-005) |
| Compressed file larger than original | Original kept, WARN logged |

## References

- [Data Model](../data-model.md)
- [CLI Contract](contracts/cli.md)