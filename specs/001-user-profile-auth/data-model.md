# Data Model — User Profile Authentication & Reading Position

**Feature**: [001-user-profile-auth](spec.md)
**Date**: 2026-09-10

---

## Entities

### User

**Description**: A registered user of the audio book application.

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string (UUID or username) | Yes | Unique identifier |
| username | string | Yes | Unique username for login |
| password_hash | string | Yes | bcrypt hash of password (min 8 chars) |
| created_at | datetime | Yes | Account creation timestamp |
| last_login | datetime | No | Last login timestamp |

**Relationships**:
- One-to-many with ReadingPosition (one user has many reading positions)

**Validation Rules**:
- Username must be unique across all users
- Password must be at least 8 characters
- Password stored as bcrypt hash (never plaintext)
- Username used as login identifier

**State Transitions**:
- `registered` → `active` (after successful registration)
- `active` → `authenticated` (after successful login)
- `authenticated` → `logged_out` (after logout)
- `logged_out` → `authenticated` (after re-login)

**Storage**: Authentication data stored in server-side session. User credentials verified against stored bcrypt hash.

---

### ReadingPosition

**Description**: Tracks the last played chapter for each book per user.

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | Reference to User |
| book_id | string | Yes | Reference to Book |
| last_chapter | integer | Yes | Chapter number (1-indexed) |
| last_updated | datetime | Yes | Timestamp of last position update |

**Relationships**:
- Many-to-one with User (many positions belong to one user)
- Many-to-one with Book (many positions reference one book)

**Validation Rules**:
- last_chapter must be ≥ 1
- last_chapter must not exceed total chapters in the book
- Combination of (user_id, book_id) must be unique
- Stored in per-user JSON file (not database)

**State Transitions**:
- `new` (first chapter) → `updated` (when user progresses)
- Any update replaces previous position (last write wins)

**Storage**: Per-user JSON file in `app/books/progress/{user_id}.json`. Format: `{"book_id": {"last_chapter": N, "last_updated": "ISO8601"}}`.

---

### Book

**Description**: A chapter book loaded from JSON metadata.

**Fields** (from metadata):
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Filename without .json extension |
| title | string | Yes | Book title |
| author | string | Yes | Book author |
| chapters | list | Yes | List of chapter objects |
| cover | string | No | Cover image filename |

**Relationships**:
- One-to-many with ReadingPosition (one book has many positions across users)

**Source**: Loaded from `books/metadata/{book_id}.json` at `app/books/metadata/`.

**Validation Rules**:
- Must have at least one chapter (otherwise empty state shown)
- Chapters referenced by index in ReadingPosition
- Metadata JSON structure must remain unchanged per spec assumption

---

## Entity Relationship Summary

```
User (1) ──── (N) ReadingPosition (N) ──── (1) Book
```

- Each User has zero or more ReadingPosition records
- Each ReadingPosition belongs to exactly one User and one Book
- Each Book can have zero or more ReadingPosition records across users

---

## Data Flow

1. **Registration**: User submits username + password → bcrypt hash stored → session created
2. **Login**: User submits credentials → hash verified → session authenticated
3. **Position update**: User plays chapter → ReadingPosition JSON updated (last write wins)
4. **Position restore**: User opens book → JSON read → last chapter loaded → book page highlights position
5. **Logout**: Session invalidated → JSON files remain on disk for future restoration

---

## Storage Architecture

```
app/
├── books/
│   ├── metadata/          # Existing book JSON files (unchanged)
│   │   ├── le-petit-prince.json
│   │   └── ...
│   └── progress/          # NEW: Per-user reading position JSON files
│       ├── {user_id_1}.json
│       ├── {user_id_2}.json
│       └── ...
├── app.py                 # Extended with auth and position routes
└── ...
```

Per-user JSON file structure example (`app/books/progress/{user_id}.json`):
```json
{
  "le-petit-prince": {"last_chapter": 3, "last_updated": "2026-09-10T14:30:00Z"},
  "another-book": {"last_chapter": 1, "last_updated": "2026-09-09T10:00:00Z"}
}
```
