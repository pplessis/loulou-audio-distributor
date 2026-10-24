# tasks.md - Drive Sync Enhancements

## Implementation Plan: Drive Sync Enhancements
**Branch**: `003-drive-sync-enhancements` | **Date**: 2026-09-19 | **Spec**: specs/003-drive-sync-enhancements/spec.md

## Task Organization
Tasks organized by user story to enable independent implementation and testing.
- Tests are OPTIONAL: Only generated where explicitly requested or TDD approach needed.
- Each user story gets its own phase for independent implementation.
- Dependencies: User stories should be mostly independent; P1 (logging) before P2/P3.
- Checklist format: `- [ ] T### [P] [USX] Description with file path`

## Phase Structure
- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests `arr` Models `arr` Services `arr` Endpoints `arr` Integration
- Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

---
## Phase 1: Setup
- [X] T001 Initialize sync_tool package structure per implementation plan
- [X] T002 Create __init__.py for sync_tool package
- [X] T003 Set up Python 3.11+ project dependencies in requirements.txt
- [X] T004 Configure Python standard library logging with file handler
- [X] T005 Create bash entry point per quickstart.md setup instructions

## Phase 2: Foundational (blocking prerequisites)
- [X] T010 Implement base sync orchestration in sync_tool/sync.py
- [X] T011 Create CLI entry point with argparse (--log-path, --log-level, --compress, --metadata-endpoint, --no-metadata-validation)
- [X] T012 Set up Google Drive upload service (google-api-python-client)
- [X] T013 Configure ffmpeg availability check for MP3 compression
- [X] T014 Write contract tests for CLI exit codes and JSON Lines log format

## Phase 3: User Story 1 - Library Creation Logging (Priority: P1)
En tant qu'administrateur de la biblioth que audio, je veux suivre la cr ation de la biblioth que audio dans un journal, afin de pouvoir auditer et diagnostiquer le processus de synchronisation.
- [X] T020 [US1] [P] Implement library scan start/end logging in sync_tool/logger.py (FR-001)
- [X] T021 [US1] [P] Implement configurable logging levels INFO/WARN/ERROR (FR-002)
- [X] T022 [US1] [P] Allow users to specify log file path via CLI arg (FR-003)
- [X] T023 [US1] [P] Generate summary log entry with counts of processed audiobooks, uploaded files, errors (FR-001 acceptance)
- [X] T024 [US1] Write contract test for logger (tests/contract/test_logger.py)
- [X] T025 [US1] Write integration test for sync logging flow (end-to-end)

## Phase 4: User Story 2 - Optional MP3 Compression (Priority: P2)
En tant qu'administrateur, je veux pouvoir compresser les fichiers MP3 audio avant l'upload, afin de r duire l'espace de stockage utilis sur Google Drive et accelerer les transferts.
- [X] T030 [US2] [P] Implement MP3 compression service with pydub in sync_tool/services/compression.py (FR-004)
- [X] T031 [US2] [P] Configure compression level via CLI --compression-level 64k (FR-005)
- [X] T032 [US2] [P] Skip compression by default, only compress when explicitly enabled --compress (FR-006)
- [X] T033 [US2] [P] Handle edge case: compressed file larger than original (keep original, log WARN)
- [X] T034 [US2] Write contract test for compression service (tests/contract/test_compression.py)
- [X] T035 [US2] Write integration test for compression flow (real MP3 fixture, size + playability assertion)

## Phase 5: User Story 3 - Metadata Validation Against Online Database (Priority: P3)
En tant qu'administrateur, je veux valider les mdonn es de mes audiobooks contre une base de donn es en ligne, afin de m'assurer que les informations (titre, auteur, couverte) sont correctes et compl tes.
- [X] T040 [US3] [P] Implement OpenLibrary Search API client in sync_tool/services/openlibrary.py (FR-007, FR-011)
- [X] T041 [US3] [P] Implement metadata validation service (query OpenLibrary, parse results) (FR-007)
- [X] T042 [US3] [P] Populate missing metadata fields (cover_url, title, author) when database match found (FR-008)
- [X] T043 [US3] [P] Set validation_status field on Audiobook: pending/validated/validation_failed (FR-011)
- [X] T044 [US3] [P] Log warnings when online database unreachable or rate-limited (FR-009, SC-005)
- [X] T045 [US3] Write contract test for metadata validator (tests/contract/test_metadata_validator.py)
- [X] T046 [US3] Write integration test for metadata validation (recorded OpenLibrary response fixture)

## Final Phase: Polish & Cross-Cutting Concerns
- [X] T050 Polish: Review all task independence and testability per constitution principles
- [X] T051 Polish: Update quickstart.md with all validation scenarios and expected outcomes
- [X] T052 Polish: Verify cross-story dependency graph is correct (P1 before P2/P3)
- [X] T053 Polish: Check checklist format on ALL tasks (checkbox, ID, [P]/[US] label, file path)
- [X] T054 Polish: Add integration test for full sync flow (logging + compression + validation together)
- [X] T055 Polish: Update requirements.txt with all new dependencies (pydub, etc.)

## Dependency Graph
**Completion Order**: T001 T002 T003 T003 T004 T005 T010 T011 T012 T013 T014 T020 T021 T022 T023 T024 T025 T030 T031 T032 T033 T034 T035 T040 T041 T042 T043 T044 T045 T046 T050 T051 T052 T053 T054 T055
**Parallel Opportunities**: T010 and T011 (both in sync_tool/ but different files, no dependency). T020 and T030 (different stories, different files, independent). T040 and T011 (different stories, can run in parallel).
**MVP Scope**: Typical MVP: Just User Story 1 (P1 - Library Creation Logging). T001-T005 (setup), T010-T014 (foundational), T020-T025 (P1 logging). Can ship after T025 with basic logging functionality.
**Independent Test Criteria per Story**: **US1 (P1)**: Contract test passes (test_logger.py), integration test passes (sync logging flow), 100% of sync operations generate log entries (SC-001). **US2 (P2)**: Contract test passes (test_compression.py), integration test passes (compression flow with real MP3 fixture), 95% of MP3 files reduced 20% while playable (SC-002). **US3 (P3)**: Contract test passes (test_metadata_validator.py), integration test passes (metadata validation with recorded OpenLibrary fixture), 80% of well-known audiobooks matched (SC-003).