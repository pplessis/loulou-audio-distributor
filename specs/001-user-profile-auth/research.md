# Research — User Profile Authentication & Reading Position

**Feature**: [001-user-profile-auth](spec.md)
**Date**: 2026-09-10

## Phase 0: Research Summary

This research resolves the remaining NEEDS CLARIFICATION items from the Technical Context section.

---

### Research Task 1: Testing Framework for Flask Application

**Unknown**: What testing framework should be used?

**Decision**: pytest with pytest-flask

**Rationale**: pytest is the de facto standard for Python/Flask testing. It integrates cleanly with Flask's test client, requires minimal configuration, and is well-documented. The project has no existing test infrastructure, so adopting pytest keeps things simple and consistent with the Flask ecosystem.

**Alternatives considered**:
- unittest (Python built-in) — Verbose, less ergonomic for Flask testing
- tox — Overkill for a small project with no multi-environment testing needs
- No testing framework — Constitution principle III (Test-First) would be violated if adopted

---

### Research Task 2: Deployment Target

**Unknown**: Where is the application deployed?

**Decision**: Vercel (per README reference) or Python App Service

**Rationale**: The README describes Vercel deployment. Vercel supports Python/Flask via serverless functions or prebuilt deployments. However, per-user JSON file storage and session management are more naturally suited to a traditional server deployment (Python App Service or similar). Vercel's serverless model may require adjustments for file-based storage.

**Alternatives considered**:
- Heroku/Container Apps — Additional infrastructure complexity
- Self-hosted — Maintenance burden not justified for this project scale
- Vercel serverless — File I/O limitations with per-user JSON storage; would require cloud storage abstraction

**Risk**: Per-user JSON file storage on Vercel serverless is problematic due to ephemeral filesystems. If Vercel is chosen, a cloud storage backend (or alternative platform) should be considered.

---

### Research Task 3: Session Management Implementation

**Unknown**: How to implement Flask sessions for authentication with server-side JSON storage?

**Decision**: Flask-Login for session management + Flask session cookies for auth; per-user JSON files for reading positions stored in a server-accessible directory

**Rationale**: Flask-Login provides the standard Flask extension for user session management. Combined with Flask's built-in session cookies (signed, not encrypted), this handles authentication. Per-user JSON files stored in `app/books/progress/` (server-accessible) persist reading positions across sessions.

**Alternatives considered**:
- Redis-backed sessions — Requires additional infrastructure; overkill for this scale
- Database (SQLite via SQLAlchemy) — Was considered in clarification but rejected in favor of simpler JSON files
- Client-side localStorage — Rejected per spec requirement that positions are server-side

---

### Research Task 4: Password Hashing Library

**Unknown**: Which library for bcrypt password hashing?

**Decision**: `flask-bcrypt` or `bcrypt` Python package

**Rationale**: The spec requires bcrypt hashing. The `bcrypt` Python package is the standard implementation. `flask-bcrypt` wraps it with Flask integration. Either works; `flask-bcrypt` provides slightly tighter Flask integration.

**Alternatives considered**:
- `werkzeug.security` — Uses pbkdf2, not bcrypt; doesn't meet spec requirement
- `passlib` — Feature-rich but adds unnecessary complexity for a single hashing need

---

### Research Task 5: JSON File Storage Structure

**Unknown**: How to structure per-user JSON files for reading positions?

**Decision**: One JSON file per user in `app/books/progress/` directory, named `{user_id}.json`

**Rationale**: Simple, readable, and aligns with the existing pattern of JSON-based metadata files. Each file contains a dict mapping book_id to last chapter number.

**File format example**:
```json
{"book_id": {"last_chapter": 5, "last_updated": "2026-09-10"}}
```

**Alternatives considered**:
- Single file with all users — Concurrency and file locking issues
- SQLite — Was rejected in clarification (hybrid JSON approach chosen)
- SQLite with Flask-SQLAlchemy — More complex than needed for this scale

---

## Research Summary Table

| Item | Decision | Confidence |
|------|----------|------------|
| Testing | pytest + pytest-flask | High |
| Deployment | Vercel or Python App Service (see risk note) | Medium |
| Session Auth | Flask-Login + Flask sessions | High |
| Password Hashing | `flask-bcrypt` | High |
| Position Storage | Per-user JSON in `app/books/progress/` | High |
| Concurrency | Last write wins (from clarifications) | High |
