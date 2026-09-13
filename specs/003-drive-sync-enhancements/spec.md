# Feature Specification: Drive Sync Enhancements

**Feature Branch**: `003-drive-sync-enhancements`

**Created**: 2026-09-13

**Status**: Draft

**Input**: "Extend the audiobook drive sync feature to add logging for library creation tracking, an optional MP3 compression feature, and metadata validation against an online audiobook database (with free/public API suggestions)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Library Creation Logging (Priority: P1)

En tant qu'administrateur de la bibliothèque audio, je veux suivre la création de la bibliothèque audio dans un journal, afin de pouvoir auditer et diagnostiquer le processus de synchronisation.

**Why this priority**: Logging is essential for operational visibility and troubleshooting when the sync process encounters issues or when auditing library changes over time.

**Independent Test**: An administrator runs the sync tool, then checks the log file to verify entries exist for library scanning, folder creation, and file uploads.

**Acceptance Scenarios**:

1. **Given** an administrator runs the sync tool on a directory with audiobooks, **When** the tool processes each audiobook, **Then** a log entry is generated for library scan start, each audiobook folder created on Drive, and each file uploaded.
2. **Given** the sync tool encounters an error during processing, **When** the error occurs, **Then** the log records the error with timestamp and audiobook identifier for diagnostic purposes.
3. **Given** logging is configured, **When** a successful sync completes, **Then** a summary log entry is generated with counts of processed audiobooks, uploaded files, and any errors encountered.

---

### User Story 2 - Optional MP3 Compression (Priority: P2)

En tant qu'administrateur, je veux pouvoir compresser les fichiers MP3 audio avant l'upload, afin de réduire l'espace de stockage utilisé sur Google Drive et accélérer les transferts.

**Why this priority**: Compression is a valuable enhancement for storage optimization but should be optional to respect user preference and audio quality requirements.

**Independent Test**: An administrator enables compression before running the tool, then verifies that uploaded MP3 files are smaller while still being valid audio files.

**Acceptance Scenarios**:

1. **Given** compression is enabled, **When** the tool processes MP3 files, **Then** each file is compressed before upload while preserving audio playability.
2. **Given** compression is disabled, **When** the tool processes MP3 files, **Then** files are uploaded at their original size without modification.
3. **Given** a user selects compression level, **When** compression is applied, **Then** the compressed file maintains acceptable audio quality suitable for audiobook playback.

---

### User Story 3 - Metadata Validation Against Online Database (Priority: P3)

En tant qu'administrateur, je veux valider les métadonnées de mes audiobooks contre une base de données en ligne, afin de m'assurer que les informations (titre, auteur, couverture) sont correctes et complètes.

**Why this priority**: Metadata quality improves the user experience for listeners browsing the library, but validation is an enhancement rather than core functionality.

**Independent Test**: An administrator enables metadata validation, then the tool cross-references one audiobook's title and author against an online database and fills in missing metadata (e.g., cover image).

**Acceptance Scenarios**:

1. **Given** an audiobook with missing or partial metadata, **When** metadata validation is enabled, **Then** the system queries the online database and populates missing fields (title, author, cover) where matches are found.
2. **Given** an audiobook with existing metadata, **When** validation is performed, **Then** the system indicates whether the metadata matches the database or highlights discrepancies.
3. **Given** the metadata database has no match for a particular audiobook, **When** validation is attempted, **Then** a warning is logged and processing continues without modification.

---

### Edge Cases

- What happens when the log file cannot be written (permissions, disk full)?
- What happens when MP3 compression produces a file that is larger than the original?
- What happens when the online metadata database is unreachable or rate-limited?
- What happens when the online database returns conflicting metadata (multiple matches)?
- What happens when the user provides an invalid API key or endpoint for the metadata database?
- **Concurrent sync**: If two sync operations attempt to create the same audiobook folder simultaneously, the last-write-wins approach is used based on timestamp ordering; the newer sync overwrites earlier state for that folder.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate log entries for library scan start/end, audiobook processing, file uploads, and errors during sync operations.
- **FR-002**: The system MUST support configurable logging levels (INFO, WARN, ERROR).
- **FR-003**: The system MUST allow users to specify a log file path for writing logs.
- **FR-004**: The system MUST support an optional MP3 compression mode that reduces audio file sizes before upload.
- **FR-005**: The system MUST allow users to configure the compression level when compression is enabled.
- **FR-006**: The system MUST skip compression by default and only compress when explicitly enabled by the user.
- **FR-007**: The system MUST validate audiobook metadata (title, author) against an online database.
- **FR-008**: The system MUST populate missing metadata fields (cover, potentially title/author) when a database match is found.
- **FR-009**: The system MUST log warnings when the online database is unreachable or returns no matches.
- **FR-010**: The system MUST support at least one free and publicly available audiobook metadata API.
- **FR-011**: The system MUST query the OpenLibrary Search API (https://openlibrary.org/dev/docs/api/search) as the primary metadata source for audiobook validation.

### Key Entities *(include if feature involves data)*

- **LogEntry**: A record entry capturing a timestamp, log level, source component, audiobook ID (if applicable), event type, and a message describing an event during the sync process.
- **CompressionSettings**: Configuration values including whether compression is enabled and the compression level/quality target.
- **DatabaseMatch**: Results from an online metadata query, including confidence score, matched title, author, and cover URL.
- **Audiobook**: (Extended from base feature) Includes a `validation_status` field with three states: `pending` (not yet checked), `validated` (metadata matched online database), `validation_failed` (no match or error during validation).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of sync operations generate log entries for each processed audiobook and file upload.
- **SC-002**: When compression is enabled, 95% of MP3 files are reduced in size by at least 20% while remaining playable.
- **SC-003**: Metadata validation successfully matches at least 80% of well-known audiobooks against the online database.
- **SC-004**: Users can configure logging path, log level, compression, and metadata API endpoint before running the tool.
- **SC-005**: When the online database is unreachable, the sync continues for all other audiobooks without interruption, with appropriate warnings logged.

## Assumptions

- Logging output can be written to a file on the local filesystem with standard permissions.
- MP3 compression is performed using standard audio processing libraries preserving MP3 format.
- The chosen online metadata database provides a REST API with at least title and author search capabilities.
- Users have internet connectivity when metadata validation is enabled.
- Audio quality after compression remains acceptable for audiobook consumption (at least 64kbps VBR or equivalent).

## Dependencies

- Relies on the existing audiobook drive sync feature (specs/002-audiobook-drive-sync) for the core upload functionality.
- Requires an internet connection to query online metadata databases.
- Depends on audio processing libraries for MP3 compression.

## Out of Scope

- Building or hosting a custom audiobook metadata database.
- Supporting non-MP3 audio formats in the compression step (MP3 only, as per FR-022 in base spec).
- Real-time streaming of compressed files.
- Cross-referencing against multiple databases simultaneously.

## Notes

**Selected Metadata API**: OpenLibrary Search API (https://openlibrary.org/dev/docs/api/search) — Free, no authentication required, supports title and author search with cover image results. Well-suited for audiobook metadata validation without requiring API key management.
