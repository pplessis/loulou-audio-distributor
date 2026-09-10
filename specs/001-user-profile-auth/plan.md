# Implementation Plan: User Profile Authentication & Reading Position

**Branch**: `[001-user-profile-auth]` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-user-profile-auth/spec.md`

## Summary

Add user registration/login/logout and per-user reading position persistence to the Flask audio book application. Authentication uses Flask sessions with bcrypt password hashing. Reading positions are stored in per-user JSON files on the server. The implementation extends the existing Flask app without modifying book metadata JSON files.

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: Flask, Flask-Login, Flask-Bcrypt

**Storage**: Per-user JSON files (`app/books/progress/`) for reading positions; Flask session cookies for authentication

**Testing**: pytest, pytest-flask

**Target Platform**: Linux server (Vercel or Python App Service)

**Project Type**: web-service

**Performance Goals**: Registration under 2 minutes; position restore within 3 seconds; progress view under 5 seconds; 95% accuracy on position restoration

**Constraints**: Per-user JSON file storage (last write wins); chapter-level position granularity; no per-book access restrictions; sessions persist until explicit logout; passwords min 8 characters

**Scale/Scope**: Small-to-medium audio book library; casual listener users; per-user progress files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file contains only template placeholders with no defined principles or gates. No violations to enforce. Proceeding with standard practices.

**Post-Design Re-check**: No constitution violations detected in design artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/001-user-profile-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── README.md
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── app.py               # Extended with auth routes, position routes, progress route
├── templates/
│   ├── base.html        # Extended with auth UI
│   ├── index.html       # Extended with progress display
│   └── book.html        # Extended with position restoration
├── static/
│   ├── css/
│   ├── js/
│   │   └── player.js    # May need position update integration
│   └── images/
├── books/
│   ├── metadata/        # Existing book JSON files (unchanged)
│   ├── progress/        # NEW: Per-user reading position JSON files
│   └── covers/
```

**Structure Decision**: Single Flask project extending existing app.py and templates. New `app/books/progress/` directory for per-user JSON position files. No new directories or services needed.

## Complexity Tracking

No constitution violations to justify. The implementation stays within the existing Flask project structure with minimal additions.
