# Tasks: Drive Sync Enhancements

**Input**: Design documents from `/specs/003-drive-sync-enhancements/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: pytest — test tasks included per constitution principles III (Test-First) and IV (real integration tests). Contract tests live in `tests/contract/`, integration tests in `tests/integration/`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**⚠️ Dependency note**: This feature extends the audiobook drive sync tool defined in `specs/002-audiobook-drive-sync`. The base sync tool (scan, upload, index) is a prerequisite of the Foundational phase below; if it is not yet implemented, complete feature `002` first or provide the base sync entrypoint (`sync_tool/sync.py` with scan/upload flow) as part of T004.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project (this project)**: `sync_tool/` at repository root (CLI package), `app/` for the Flask app
- Source code: `sync_tool/` (models, config, cli, services), tests: `tests/` at repository root
- Existing book metadata: `app/books/metadata/` (unchanged; generated index gains optional `validation_status`)
- Tests: `tests/contract/`, `tests/integration/`, fixtures in `tests/fixtures/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install Python dependencies: `pydub` (for MP3 compression) via `pip`; verify `ffmpeg` binary is on PATH; document both in `requirements.txt` (research.md decision)
- [X] T002 Create `sync_tool/` package structure: `__init__.py`, `models.py`, `config.py`, `cli.py`, `sync.py`, `services/__init__.py`
- [X] T003 [P] Configure shared test fixtures in `tests/conftest.py` — temp log dir, tiny valid MP3 fixture (generated via ffmpeg), and a mocked sync context (audiobook list + config)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Establish the base sync entrypoint: verify `sync_tool/sync.py` (scan → upload → index flow from feature 002) exposes a sync context (audiobook list, `SyncConfig`, error hook); add a minimal stub only if the base feature is unavailable (research.md Task 3)
- [X] T005 [P] Create `SyncConfig` in `sync_tool/models.py` — `log_path`, `log_level` (INFO/WARN/ERROR), `compression_enabled` (default False), `compression_level` (default `64k`), `metadata_api_endpoint` (default OpenLibrary `search.json`); validation per data-model.md
- [X] T006 [P] Create `LogEntry` in `sync_tool/models.py` — `timestamp`, `level`, `source`, `audiobook_id` (optional), `event_type`, `message`; plus JSON-lines serialization per contracts/cli.md
- [X] T007 [P] Create `CompressionSettings` in `sync_tool/models.py` — `enabled` (default False), `compression_level`
- [X] T008 [P] Create `DatabaseMatch` in `sync_tool/models.py` — `confidence`, `matched_title`, `matched_author`, `cover_url`
- [X] T009 Configure logging infrastructure in `sync_tool/services/logger.py` — file handler writing JSON-lines `LogEntry` records to `config.log_path`; on unwritable path, log to stderr and continue (spec edge case)
- [X] T010 Wire config loading (CLI args/env/file) into `sync_tool/config.py` — supports `--log-path`, `--log-level`, `--compress`, `--compression-level`, `--metadata-endpoint`, `--no-metadata-validation` per contracts/cli.md

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Library Creation Logging (Priority: P1) 🎯 MVP

**Goal**: Enable the sync tool to generate structured JSON-lines log entries for scan start/end, per-audiobook processing, file uploads, errors, and a summary — with configurable log level and file path (FR-001, FR-002, FR-003).

**Independent Test**: An administrator runs the sync tool, then checks the log file to verify entries exist for library scanning, folder creation, and file uploads.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Contract test for `LogEntry` serialization and level filtering in `tests/contract/test_logger.py` (validates contracts/cli.md log format)
- [X] T012 [P] [US1] Integration test for a sync run producing scan/upload/error/summary log entries in `tests/integration/test_sync_logging.py`

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement logging service in `sync_tool/services/logger.py` — `log_entry(level, source, audiobook_id, event_type, message)` appends JSON-lines `LogEntry` to the configured file; handles unwritable log file by logging to stderr and continuing
- [X] T014 [US1] Add scan start/end and per-audiobook processing log calls in `sync_tool/sync.py` (depends on T013, T004)
- [X] T015 [US1] Add `folder_created` and `file_uploaded` log calls in `sync_tool/sync.py` for each Drive folder and uploaded file
- [X] T016 [US1] Add error logging with timestamp and audiobook identifier in `sync_tool/sync.py` error hook (spec acceptance 2)
- [X] T017 [US1] Add summary log entry on successful sync completion with counts of processed audiobooks, uploaded files, and errors (spec acceptance 3)

**Checkpoint**: User Story 1 fully functional and testable independently — sync run produces complete structured logs

---

## Phase 4: User Story 2 — Optional MP3 Compression (Priority: P2)

**Goal**: Enable optional MP3 compression before upload, configurable level, off by default, preserving audio playability (FR-004, FR-005, FR-006).

**Independent Test**: An administrator enables compression before running the tool, then verifies that uploaded MP3 files are smaller while still being valid audio files.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US2] Contract test for compression service in `tests/contract/test_compression.py` — off by default, applies level, returns original when output is larger, output is valid playable MP3
- [X] T019 [P] [US2] Integration test for compressed file preserving playability and being smaller in `tests/integration/test_compression_flow.py` (real MP3 fixture; SC-002 coverage)
- [X] T020 [P] [US2] Aggregate compression test asserting ≥95% of a ≥10-file MP3 corpus reduces ≥20% and stays playable in `tests/integration/test_compression_aggregate.py` (SC-002 statistical verification; fixtures in `tests/fixtures/mp3_corpus/`)

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement compression service in `sync_tool/services/compression.py` — compress MP3 to target bitrate via `pydub` + `ffmpeg` (default `64k`); if compressed output is larger than original, keep original and log WARN (spec edge case)
- [X] T022 [US2] Integrate compression into upload flow in `sync_tool/sync.py` — skip by default, compress only when `CompressionSettings.enabled` (depends on T021, T005)
- [X] T023 [US2] Expose compression level configuration through `sync_tool/config.py` `--compression-level` (depends on T010)
- [X] T024 [US2] Log compression results (original vs compressed size) in `sync_tool/sync.py` via logger (depends on T013)

**Checkpoint**: User Story 2 fully functional — compression works when enabled, off by default, playability preserved

---

## Phase 5: User Story 3 — Metadata Validation Against Online Database (Priority: P3)

**Goal**: Enable optional validation of audiobook metadata (title, author) against the OpenLibrary Search API, populating missing fields (cover) and setting `validation_status`; log warnings on unreachable/no-match (FR-007, FR-008, FR-009, FR-010, FR-011).

**Independent Test**: An administrator enables metadata validation, then the tool cross-references one audiobook's title and author against an online database and fills in missing metadata (e.g., cover image).

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T025 [P] [US3] Contract test for OpenLibrary client in `tests/contract/test_metadata_validator.py` — query construction (`search.json?title=...&author=...&fields=title,author_name,cover_i,key`), response parsing into `DatabaseMatch`, no-match handling (recorded fixture)
- [X] T026 [P] [US3] Contract test for generated JSON index schema in `tests/contract/test_index_schema.py` — asserts `validation_status` is optional/additive and validates each of `pending`/`validated`/`validation_failed` (constitution Principle II)
- [X] T027 [P] [US3] Integration test for metadata validation flow populating cover and setting `validation_status` in `tests/integration/test_metadata_validation.py` (recorded OpenLibrary fixture + opt-in `@pytest.mark.live` for real API)
- [X] T028 [P] [US3] Integration test for unreachable database — sync continues for all other audiobooks, WARN logged, `validation_status=failed` in `tests/integration/test_metadata_unreachable.py` (SC-005)
- [X] T029 [P] [US3] Create fixture corpus of 20 well-known audiobooks with expected OpenLibrary matches in `tests/fixtures/well_known_audiobooks.json` (SC-003 corpus definition from spec)
- [X] T030 [P] [US3] Integration test asserting ≥80% match rate over the corpus in `tests/integration/test_metadata_match_rate.py` (SC-003; recorded fixtures)

### Implementation for User Story 3

- [X] T031 [P] [US3] Implement OpenLibrary client in `sync_tool/services/openlibrary.py` — `GET https://openlibrary.org/search.json` with title/author query and `fields=title,author_name,cover_i,key` via `requests` (already a dependency); parse top match into `DatabaseMatch`; cover URL from `https://covers.openlibrary.org/b/id/{cover_i}-L.jpg`; timeouts and HTTP error handling
- [X] T032 [US3] Implement metadata validator service in `sync_tool/services/metadata_validator.py` — query OpenLibrary per Audiobook, populate missing title/author/cover from best match, set `validation_status` to `validated`/`validation_failed` (depends on T031, T008)
- [X] T033 [US3] Handle unreachable/rate-limited API, no-match, and conflicting matches in `sync_tool/services/metadata_validator.py` — log WARN via logger and continue without modification (spec acceptance 3, SC-005; edge cases: invalid endpoint, conflicts)
- [X] T034 [US3] Integrate validation into sync flow in `sync_tool/sync.py` — run when enabled (`--no-metadata-validation` disables), before upload; sync continues for other audiobooks if API unreachable (depends on T032)
- [X] T035 [US3] Persist `validation_status` (optional additive field) on the generated JSON index at `app/books/metadata/{book_id}.json` in `sync_tool/sync.py` (depends on T034, base index generation)

**Checkpoint**: User Stories 1-3 all independently functional — logging, compression, and metadata validation all working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T036 [P] Add MP3 fixture helper (tiny valid MP3 generation via ffmpeg) in `tests/conftest.py`
- [X] T037 [P] Run full test suite: `pytest tests/` and verify all tests pass (deterministic — no live network)
- [X] T038 [P] Update `requirements.txt` to pin new dependencies (`pydub`); document `ffmpeg` prerequisite in README; keep dependencies minimal per constitution principle V
- [X] T039 [P] Run `quickstart.md` validation scenarios 1-5 and confirm expected outcomes (SC-001, SC-004, SC-005)
- [X] T040 [P] Code cleanup and refactoring: extract helpers, consolidate imports across `sync_tool/`
- [X] T041 [P] Add credentials-gated Google Drive upload integration test in `tests/integration/test_drive_upload.py` marked `@pytest.mark.drive` — requires real Google credentials, auto-skips when absent; asserts a real upload + public link is created (constitution IV; research.md Task 4)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (US1 → US2 → US3)
  - US1 and US2 can overlap on Foundational dependencies
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Depends on US1 for logging of compression results (T024)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — Depends on US1 for warning logging (T033)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints/integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All test tasks within a story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on sequentially (US1 → US2 → US3) or in parallel if team capacity allows

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all parallel foundational tasks together:
Task: "Create SyncConfig in sync_tool/models.py" [P]
Task: "Create LogEntry in sync_tool/models.py" [P]
Task: "Create CompressionSettings in sync_tool/models.py" [P]
Task: "Create DatabaseMatch in sync_tool/models.py" [P]
```

---

## Parallel Example: Phase 3 (US1 — Library Creation Logging)

```bash
# Launch all parallel US1 tasks together:
Task: "Contract test for LogEntry serialization in tests/contract/test_logger.py" [P]
Task: "Integration test for sync run producing log entries in tests/integration/test_sync_logging.py" [P]
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test logging independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Logging)
   - Developer B: User Story 2 (Compression)
   - Developer C: User Story 3 (Metadata Validation)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- File paths use `sync_tool/` prefix for the CLI package, `tests/` for tests
- Per constitution principle II, the `validation_status` JSON index field is optional/additive and covered by `tests/contract/test_index_schema.py` (T026)
- Per constitution principle III, contract tests (`tests/contract/`) validate interfaces (logging format, compression, OpenLibrary client, index schema) before implementation
- Per constitution principle IV, integration tests (`tests/integration/`) validate end-to-end user journeys (sync logging flow, compression flow, validation flow) with realistic fixtures; live OpenLibrary (T027) and Drive (T041) tests are opt-in via markers
- The OpenLibrary Search API (https://openlibrary.org/dev/docs/api/search) requires no authentication; no API key management needed (spec FR-011, research.md Task 2)