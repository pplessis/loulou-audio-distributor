# Feature Specification: Audiobook Drive Sync & Index Generator

**Feature Branch**: `002-audiobook-drive-sync`

**Created**: 2026-09-13

**Status**: Draft

**Input**: User description: "Lire une arborescence de répertoires, identifier les audiobooks avec leurs chapitres MP3, les uploader sur Google Drive avec la même structure, créer un lien public par chapitre, et générer un JSON d'index par livre."

## User Scenarios & Testing *(mandatory)*

En tant qu'administrateur d'une bibliothèque audio, je veux pointer l'outil vers un répertoire local contenant mes audiobooks (organisés en dossiers avec des fichiers MP3 par chapitre), afin qu'il les uploade automatiquement sur Google Drive en conservant la structure, génère des liens publics pour chaque chapitre, et produise un fichier JSON d'index exploitable par une application de lecture.

**Why this priority**: This is the primary user story that delivers the core value — automated sync of audiobooks to Google Drive with proper indexing.

**Independent Test**: Can be tested by pointing the tool at a directory containing an audiobook folder and verifying that files appear on Google Drive with public links and a JSON index is generated.

### User Story 1 - Upload audiobooks to Google Drive preserving structure (Priority: P1)

**Why this priority**: This is the core functionality — without upload, there is no value delivered to the user.

**Independent Test**: Given a directory with an audiobook folder, run the tool, then verify the corresponding folder exists on Google Drive with all MP3 files and each has a public read-only link.

**Acceptance Scenarios**:

1. **Given** a root directory containing a folder "Antoine de Saint-Exupéry - Le Petit Prince" with 3 numbered MP3 files, **When** the tool is executed, **Then** a corresponding folder is created on Google Drive containing 3 files, each with public read-only access links, and a file `le-petit-prince.json` is generated conforming to the target schema.
2. **Given** an existing audiobook on Google Drive, **When** the tool is re-run on the same source directory, **Then** no files are duplicated on Google Drive (idempotency).

---

### User Story 2 - Metadata override and cover handling (Priority: P2)

**Why this priority**: Allows users to customize their audiobook metadata without renaming folders, which improves flexibility.

**Independent Test**: Given a folder with a `metadata.json` defining title, author, cover, and minimum-age, run the tool and verify those values override the defaults in the generated JSON.

**Acceptance Scenarios**:

1. **Given** an audiobook folder containing a `metadata.json` file defining title, author, cover, and minimum-age, **When** the tool is executed, **Then** those values override those automatically derived from the folder name.
2. **Given** an audiobook folder without a cover file and no `metadata.json` specifying a cover, **When** the tool is executed, **Then** the cover field in the JSON is empty or contains a default value without failing processing.

---

### User Story 3 - Chapter ordering and error resilience (Priority: P3)

**Why this priority**: Ensures robustness when MP3 files lack proper numbering and when files are corrupted.

**Independent Test**: Given a folder with MP3 files without numerical prefixes, run the tool and verify a warning is logged but chapters are still processed in alphabetical order.

**Acceptance Scenarios**:

1. **Given** a folder containing MP3 files without a numerical prefix for ordering, **When** the tool is executed, **Then** chapters are sorted alphabetically and a warning is logged indicating the order is not guaranteed.
2. **Given** an audiobook with a corrupted or unreadable MP3 file, **When** the tool is executed, **Then** processing of other audiobooks continues normally and an error is logged for the specific affected book without interrupting overall execution.

---

### Edge Cases

- What happens when the Google Drive upload quota is exceeded during processing?
- What happens when a folder contains a mix of MP3 files and other audio formats (WAV, M4A)?
- What happens when two different folders produce the same derived title (name collision)?
- What happens when execution is interrupted mid-upload (partial recovery)?
- What happens when an MP3 file contains no exploitable duration metadata?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST scan recursively a root directory provided as input to identify folders representing audiobooks.
- **FR-002**: The system MUST consider a folder as an audiobook if it directly contains at least one `.mp3` file.
- **FR-003**: The system MUST derive title and author from the folder name following the convention "Author - Title", unless a `metadata.json` file is present, in which case the latter takes priority.
- **FR-004**: The system MUST sort the MP3 files of an audiobook by numerical prefix (e.g., "01 -", "02 -") to determine chapter order.
- **FR-005**: The system MUST log a warning when chapter order cannot be reliably determined (absence of numerical prefix).
- **FR-006**: The system MUST extract duration from each MP3 file's audio metadata.
- **FR-007**: The system MUST calculate total audiobook duration as the sum of chapter durations.
- **FR-008**: The system MUST reproduce the source folder structure on Google Drive (one Drive folder per audiobook, under a configurable root).
- **FR-009**: The system MUST upload each MP3 file of an audiobook to the corresponding Drive folder.
- **FR-010**: The system MUST upload the cover image file if it is a local file; if cover is already a public external URL, it MUST be preserved as-is.
- **FR-011**: The system MUST configure a public read-only sharing permission on each uploaded file (MP3 and local cover).
- **FR-012**: The system MUST produce, for each publicly shared file, a link accessible without authentication.
- **FR-013**: The system MUST generate, for each processed audiobook, a JSON file conforming to the schema defined in the Key Entities section, including title, author, cover, chapters, duration, minimum-age, and chapters_list.
- **FR-014**: The system MUST guarantee idempotency: re-running on an already-processed directory MUST NOT duplicate Drive files or folders nor regenerate existing public links.
- **FR-015**: The system MUST continue processing other audiobooks in case of an error on one of them (corrupted file, upload failure), and log the associated error.
- **FR-016**: The system MUST allow configuration of the destination root folder on Google Drive.
- **FR-017**: The system MUST allow choosing behavior when a file already exists on Drive (ignore / overwrite).

### Requirements Requiring Clarification

- **FR-018**: The system MUST authenticate Google Drive API calls via [NEEDS CLARIFICATION: auth method — Service Account or user OAuth2?].
- **FR-019**: The duration field format MUST follow [INFORMED DEFAULT: formatted as "Xh MMmin" for durations over 60 minutes and "MMmin" for shorter durations, with a raw total_seconds field also included for programmatic consumption].
- **FR-020**: The type of public link generated MUST be [NEEDS CLARIFICATION: direct download link (uc?export=download) for use with standard HTML5 audio players, or a standard sharing link (/view)?].
- **FR-021**: The system MUST handle API quota and rate limit exceeded errors via [INFORMED DEFAULT: exponential backoff with jitter, retrying up to 5 times before giving up on the specific file and logging the error].
- **FR-022**: Support for multi-level folder structures (e.g., series/seasons) MUST be [NEEDS CLARIFICATION: required in V1 or deferred to V2?].
- **FR-023**: In the absence of a cover, the expected behavior is [INFORMED DEFAULT: cover field is empty string, processing continues without error].

### Key Entities *(include if feature involves data)*

- **Audiobook**: Represents an audio book detected in the directory tree. Attributes: title (string), author (string), cover (URL string or empty), chapters (integer count), duration (formatted string), minimum-age (integer, default 0), chapters_list (ordered list of Chapter objects).
- **Chapitre (Chapter)**: An individual audio unit belonging to an audiobook. Attributes: title (string), audio (public URL string), duration (formatted string).
- **Metadata source (optional)**: A local configuration file per audiobook allowing override of automatically derived values (title, author, cover, minimum-age).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of audiobooks in a source directory with up to 50 books (each with up to 30 MP3 chapters) are processed and uploaded within 2 hours on a standard broadband connection (50 Mbps upload).
- **SC-002**: The tool achieves idempotency — re-running on an unchanged directory results in 0 new Drive file uploads and 0 new folders created.
- **SC-003**: When a single MP3 file is corrupted, the system continues processing all remaining audiobooks with 0 failures outside the corrupted file.
- **SC-004**: 95% of generated JSON index files match the target schema with valid public links for all chapters.
- **SC-005**: User can configure the Drive root folder and conflict resolution behavior (ignore/overwrite) before first run.

## Assumptions

- Users have access to a Google Drive account with sufficient storage quota for the audiobook collection.
- MP3 files use standard ID3 tags for duration metadata extraction.
- Folder naming convention "Author - Title" is followed unless metadata.json overrides it.
- Non-MP3 audio files (WAV, M4A) are ignored by the tool (MP3-only processing as specified in dependencies).
- A metadata.json file, if present, is well-formed JSON with expected fields.
- Network connectivity to Google Drive API endpoints is available during processing.
- Public sharing links remain valid for at least 24 hours after generation.
