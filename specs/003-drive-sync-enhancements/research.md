# Research — Drive Sync Enhancements

**Feature**: [003-drive-sync-enhancements](spec.md)
**Date**: 2026-09-19

## Phase 0: Research Summary

This research resolves the technical unknowns for the Drive Sync Enhancements feature: MP3 compression library choice, OpenLibrary API integration, base sync tool dependency, and integration testing strategy.

---

### Research Task 1: MP3 Compression Library for Python

**Unknown**: Which library should compress MP3 files before upload while preserving MP3 format?

**Decision**: `pydub` with an `ffmpeg` backend

**Rationale**: `pydub` is the de facto Python standard for audio manipulation, supports MP3→MP3 re-encoding at a configurable bitrate, and is pure-Python with a thin wrapper over `ffmpeg`. `ffmpeg` is universally available and handles the actual LAME encoding. The spec requires preserving MP3 format (base FR-022) and a minimum ~64kbps VBR quality (spec assumption). `pydub`'s `export(format="mp3", bitrate="64k")` satisfies this directly.

**Alternatives considered**:
- `lameenc` — Lighter (pip-only, no system binary) but less documented and less robust for bitrate/quality control.
- Direct `ffmpeg` subprocess calls — No Python dependency but reimplements audio pipeline logic and error handling that `pydub` provides.
- `audioread`/`pydub` without ffmpeg — Insufficient for MP3 encoding; MP3 export requires an encoder.

**Note on Constitution V**: `pydub` + `ffmpeg` adds a justified external dependency for the compression feature. It does not affect the Vercel-deployed Flask app (CLI runs locally). `ffmpeg` is a system binary, not a Python dependency.

---

### Research Task 2: OpenLibrary Search API Integration

**Unknown**: How to query the OpenLibrary Search API for title/author metadata validation and cover images?

**Decision**: Use `GET https://openlibrary.org/search.json` with `title`, `author`, and `fields` query parameters via the existing `requests` library.

**Rationale**: Confirmed from official docs (https://openlibrary.org/dev/docs/api/search):
- Endpoint: `https://openlibrary.org/search.json?title=...&author=...&fields=title,author_name,cover_i,key`
- Response format: `{"numFound": N, "docs": [{ "title", "author_name": [...], "cover_i": N, "key": "/works/OL..." }]}`
- Cover images: `https://covers.openlibrary.org/b/id/{cover_i}-L.jpg`
- **No authentication required** — no API key or rate-limit headers needed (satisfies FR-010/FR-011 and the spec note).
- Schema is not guaranteed stable, but `title`, `author_name`, and `cover_i` are safe to depend on.

**Alternatives considered**:
- iTunes Search API — Music-focused, poor audiobook coverage, requires special `entity` handling.
- Google Books API — Requires API key; more complex auth.
- Audible API — Proprietary, requires credentials; not "free and public".

---

### Research Task 3: Base Sync Tool Dependency (Feature 002)

**Unknown**: Feature 003 extends the audiobook drive sync tool, but feature 002 has no implementation in the repo.

**Decision**: Define the base sync entrypoint contract (`sync_tool/sync.py`) as part of the Foundational phase (T004), with a stub fallback so feature 003's stories can be implemented and tested independently of the full Drive upload implementation.

**Rationale**: The spec's dependency section explicitly states 003 relies on 002 for core upload functionality. Since 002 is unimplemented, feature 003's tasks establish the minimal sync context interface (audiobook list, config, error hook) and mark Drive upload as an inherited capability. This keeps stories independently testable per constitution principle III/IV.

**Risk**: If the real Drive upload (002) is never implemented, the sync tool will upload nothing. Mitigation: T004 keeps the sync flow structured so the upload step is a single replaceable function.

---

### Research Task 4: Integration Testing Strategy (Constitution IV)

**Unknown**: How to satisfy "real integration tests, not just mocks" for compression and cloud/metadata integration?

**Decision**: 
- **Compression**: Integration test uses a real, tiny MP3 fixture (generated once via ffmpeg) and asserts the compressed output is a smaller, playable MP3 (size + duration/format assertion).
- **Metadata validation**: Integration test uses a recorded OpenLibrary response fixture for deterministic results, plus an opt-in live test (marked `@pytest.mark.live`) that queries the real API when network is available.
- **Drive upload**: Credentials-gated integration test (`@pytest.mark.drive`, task T041 in tasks.md) that requires real Google credentials; otherwise a realistic fixture-based test exercises the sync orchestration.

**Rationale**: Matches constitution IV — real files, real API contracts, minimal mocks. CI stays deterministic via fixtures; live tests are opt-in.

**Alternatives considered**:
- Mock-only tests — Rejected (violates constitution IV).
- Full live API in every test — Flaky and rate-limited; rejected.

---

## Research Summary Table

| Item | Decision | Confidence |
|------|----------|------------|
| Compression library | `pydub` + `ffmpeg` backend | High |
| Compression target | 64kbps MP3 (VBR-equivalent), skip if larger | High |
| Metadata API | OpenLibrary Search API (`search.json`) | High |
| Cover images | `https://covers.openlibrary.org/b/id/{cover_i}-L.jpg` | High |
| Metadata auth | None (public API) | High |
| Base sync entrypoint | `sync_tool/sync.py` stub/contract via T004 | Medium |
| Integration tests | Real fixtures + opt-in live/credentialed tests | High |
| Logging | Python stdlib `logging`, file handler, structured entries | High |