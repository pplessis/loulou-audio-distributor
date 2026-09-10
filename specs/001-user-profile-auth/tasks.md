# Tasks: User Profile Authentication & Reading Position

**Input**: Design documents from `/specs/001-user-profile-auth/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: pytest, pytest-flask — test tasks included per plan.md testing dependency

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project (this project)**: `app/` at repository root
- Source code: `app/app.py`, `app/models/`, `app/services/`, `app/templates/`, `app/books/progress/`
- Tests: `tests/` at repository root
- Existing book metadata: `app/books/metadata/` (unchanged)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `app/books/progress/` directory for per-user reading position JSON files
- [ ] T002 [P] Install Flask dependencies: `flask-login`, `flask-bcrypt`, `pytest`, `pytest-flask` via pip
- [ ] T003 [P] Configure Flask app secret key and session settings in `app/app.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Setup Flask-Login with user loader callback in `app/app.py` — load user from session on each request
- [ ] T005 [P] Create password hashing utilities (`hash_password`, `verify_password`) in `app/services/auth_service.py` using `flask-bcrypt`
- [ ] T006 [P] Create progress file management utilities (`read_user_progress`, `write_user_progress`, `get_book_position`) in `app/services/progress_service.py` using JSON file I/O at `app/books/progress/{user_id}.json`
- [ ] T007 [P] Setup session cookie configuration and security headers in `app/app.py`
- [ ] T008 Configure error handling and logging infrastructure in `app/app.py` — 401/404 handlers, request logging

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Account Registration & Login (Priority: P1) 🎯 MVP

**Goal**: Enable new users to register with a unique username (min 8-char password) and log in to access the application. Return users authenticate with credentials.

**Independent Test**: A user can register with a username and password, then log in and access the book list. This works without any other feature.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract test for POST /register endpoint in `tests/contract/test_register.py`
- [ ] T010 [P] [US1] Contract test for POST /login endpoint in `tests/contract/test_login.py`
- [ ] T011 [P] [US1] Integration test for registration and login flow in `tests/integration/test_auth_flow.py`

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create User model with validation (unique username, password min 8 chars, bcrypt hash) in `app/models/user.py`
- [ ] T013 [US1] Implement registration endpoint (POST /register) in `app/app.py` — creates user, hashes password, creates session, redirects to book list
- [ ] T014 [US1] Implement login endpoint (POST /login) in `app/app.py` — verifies credentials, creates session, redirects to book list
- [ ] T015 [US1] Add duplicate username rejection logic in `app/app.py` — returns 409 with error message
- [ ] T016 [US1] Update `app/templates/index.html` to show login/registration forms
- [ ] T017 [US1] Add error handling for invalid credentials in `app/app.py` — returns 401 with error message

**Checkpoint**: User Story 1 fully functional and testable independently — registration, login, session management working

---

## Phase 4: User Story 2 — Reading Position Persistence Per Book (Priority: P1)

**Goal**: Enable logged-in users to navigate through audio chapters and automatically save their current chapter position per book. Positions restored when returning to previously-listened books.

**Independent Test**: A logged-in user can play chapter 3 of a book, close the browser, return later, and find chapter 3 automatically highlighted or resumed.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US2] Contract test for POST /book/<book_id>/position endpoint in `tests/contract/test_position_save.py`
- [ ] T019 [P] [US2] Integration test for position persistence across session restart in `tests/integration/test_position_persistence.py`

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create ReadingPosition entity in `app/models/reading_position.py` — validates last_chapter ≥ 1, enforces last-write-wins
- [ ] T021 [US2] Implement position save endpoint (POST /book/<book_id>/position) in `app/app.py` — writes to `app/books/progress/{user_id}.json`
- [ ] T022 [US2] Implement position restore in `app/app.py` GET /book/<book_id> route — reads `app/books/progress/{user_id}.json`, passes last_chapter to template
- [ ] T023 [US2] Update `app/templates/book.html` to highlight last played chapter and pass position data from Flask context
- [ ] T024 [US2] Add chapter-level position tracking integration with `app/static/js/player.js` — send chapter position to server on chapter change

**Checkpoint**: User Story 2 fully functional — positions saved and restored correctly across sessions

---

## Phase 5: User Story 3 — Viewing Reading Progress Across Books (Priority: P2)

**Goal**: Enable logged-in users to see a summary of their reading progress for all books in the library. Each book shows the last chapter they were on.

**Independent Test**: A logged-in user can view their last played chapter for each book without needing any other feature beyond authentication and position saving.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T025 [P] [US3] Contract test for GET /progress endpoint in `tests/contract/test_progress.py`

### Implementation for User Story 3

- [ ] T026 [US3] Implement progress summary endpoint (GET /progress) in `app/app.py` — returns JSON list of books with last_chapter per book from `app/books/progress/{user_id}.json`
- [ ] T027 [US3] Update `app/templates/index.html` to display last played chapter for each book when user is logged in
- [ ] T028 [US3] Add null handling for books with no progress in `app/app.py` and `app/templates/index.html`

**Checkpoint**: User Stories 1-3 all independently functional — registration/login, position persistence, and progress view all working

---

## Phase 6: User Story 4 — Account Logout (Priority: P3)

**Goal**: Enable logged-in users to log out, clearing their session and ensuring reading position data remains saved server-side for future restoration.

**Independent Test**: A logged-in user clicks logout, session ends, redirected to login page. Reading position data persists server-side and is restored on next login.

### Implementation for User Story 4

- [ ] T029 [US4] Implement logout endpoint (POST /logout) in `app/app.py` — clears Flask session via Flask-Login, redirects to login page
- [ ] T030 [US4] Update `app/templates/base.html` to show logout button when user is authenticated

**Checkpoint**: All user stories independently functional — registration/login, position persistence, progress view, and logout all working

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T031 [P] Update `quickstart.md` validation scenarios to match all implemented endpoints
- [ ] T032 [P] Add security hardening: session cookie flags (HttpOnly, Secure), CSRF protection in `app/app.py`
- [ ] T033 [P] Add file locking or atomic writes for progress JSON files to handle concurrent access in `app/services/progress_service.py`
- [ ] T034 [P] Run full test suite: `pytest tests/` and verify all tests pass
- [ ] T035 [P] Code cleanup and refactoring: extract route handlers, consolidate imports in `app/app.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (US1 → US2 → US3 → US4)
  - US1 and US2 are both P1 and can overlap on Foundational dependencies
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) — Depends on US1 for authentication (only session/cookie, not code)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) — Depends on US2 for position data to display
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) — Depends on US1 for session management

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All test tasks within a story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on sequentially (US1 → US2 → US3 → US4) or in parallel if team capacity allows

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all parallel foundational tasks together:
Task: "Create password hashing utilities in app/services/auth_service.py" [P]
Task: "Create progress file management utilities in app/services/progress_service.py" [P]
Task: "Setup session cookie configuration in app/app.py" [P]
```

---

## Parallel Example: Phase 3 (US1 — Registration & Login)

```bash
# Launch all parallel US1 tasks together:
Task: "Contract test for POST /register in tests/contract/test_register.py" [P]
Task: "Contract test for POST /login in tests/contract/test_login.py" [P]
Task: "Create User model in app/models/user.py" [P]
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test registration and login independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration & Login)
   - Developer B: User Story 2 (Position Persistence)
   - Developer C: User Story 3 (Progress View)
   - Developer D: User Story 4 (Logout)
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
- File paths use `app/` prefix (project structure is `app/app.py`, not `src/`)
- Per-user JSON files stored at `app/books/progress/{user_id}.json`
- Existing book metadata at `app/books/metadata/` must not be modified
