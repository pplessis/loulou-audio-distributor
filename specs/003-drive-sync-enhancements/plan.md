# Implementation Plan: Drive Sync Enhancements

**Branch**: `003-drive-sync-enhancements` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-drive-sync-enhancements/spec.md`

## Summary

Extend the audiobook drive sync tool with three enhancements: structured library-creation logging (P1), optional MP3 compression before upload (P2), and metadata validation against the OpenLibrary Search API (P3). Implemented as a Python CLI (`sync_tool/`) that extends the base sync flow from feature 002. Logging uses the Python standard library; compression uses `pydub` with an `ffmpeg` backend; metadata validation uses the `requests` library against `https://openlibrary.org/search.json` (no API key required).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `requests` (present), `pydub` (+ `ffmpeg` binary) for MP3 compression, `google-api-python-client` (inherited from base feature 002 for Drive upload)

**Storage**: Local log file (configurable path); Google Drive (base feature); generated book JSON index files at `app/books/metadata/{book_id}.json`

**Testing**: pytest — contract tests in `tests/contract/`, integration tests in `tests/integration/`

**Target Platform**: CLI tool run on an administrator workstation (macOS/Linux); the Flask web app remains Vercel-deployable

**Project Type**: cli

**Performance Goals**: SC-001 (100% sync ops generate log entries); SC-002 (95% of MP3 files reduced ≥20% while playable); SC-003 (≥80% match rate for well-known audiobooks)

**Constraints**: MP3-only compression (per base FR-022); compression off by default; `validation_status` JSON schema change must be backward-compatible and contract-tested; dependencies kept minimal and documented in `requirements.txt`

**Scale/Scope**: Small-to-medium audiobook library (up to 50 books, 30 chapters each, per base SC-001); single admin operator

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (familial simplicity)**: No child-facing complexity added — this is admin tooling. No violation.
- **Principle II (stable JSON contracts)**: Adding `validation_status` to the generated book JSON index changes the metadata contract. MUST be a backward-compatible additive optional field, documented in this spec, and covered by a contract test in `tests/contract/` before implementation. **Compliance path**: additive field; contract test added in T026.
- **Principle III (Test-First, NON-NÉGOCIABLE)**: All three stories follow TDD — contract tests first (fail → implement → pass) per tasks.md.
- **Principle IV (real integration tests)**: Compression and metadata validation get realistic integration tests (real MP3 fixtures, recorded/real OpenLibrary responses). Drive upload integration uses realistic fixtures with a credentials-gated test; documented as an assumption in research.md.
- **Principle V (Vercel-first, minimal deps)**: The CLI runs locally and does not affect the Vercel-deployed Flask app. New deps (`pydub`, `ffmpeg`) are justified and documented. No violation.

**Gate result: PASS** — no constitution violations to justify in Complexity Tracking.

**Post-Design Re-check**: All design artifacts (data-model.md, contracts/, quickstart.md) remain compliant. `validation_status` documented as optional/additive (Principle II satisfied).

## Project Structure

### Documentation (this feature)

```text
specs/003-drive-sync-enhancements/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── README.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
sync_tool/
├── __init__.py
├── models.py            # SyncConfig, LogEntry, CompressionSettings, DatabaseMatch, Audiobook
├── config.py            # CLI arg/env/file config loading
├── cli.py               # CLI entry point
├── sync.py              # Base sync orchestration (extends feature 002)
└── services/
    ├── __init__.py
    ├── logger.py        # Structured logging service
    ├── compression.py   # MP3 compression service
    ├── openlibrary.py   # OpenLibrary Search API client
    └── metadata_validator.py  # Metadata validation service

tests/
├── conftest.py          # Shared fixtures (MP3 fixture, temp log dir, mocked sync context)
├── contract/
│   ├── test_logger.py
│   ├── test_compression.py
│   └── test_metadata_validator.py
└── integration/
    ├── test_sync_logging.py
    ├── test_compression_flow.py
    └── test_metadata_validation.py
```

**Structure Decision**: Single Python CLI package `sync_tool/` at the repository root, mirroring the existing `tests/` layout used by feature 001. No new services or servers. The Flask app (`app/`) is untouched.

## Complexity Tracking

No constitution violations to justify. The implementation stays within the existing project conventions with minimal new dependencies.