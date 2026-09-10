# Feature Specification: User Profile Authentication & Reading Position

**Feature Branch**: `[001-user-profile-auth]`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "Creation d'un system de Profile (login+PWD) pour sauvegarder la position de lecture des chapitres par livre."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Registration & Login (Priority: P1)

A new user can create an account with a username and password, then log in to access the application. Returning users can authenticate with their credentials to continue using the service.

**Why this priority**: Authentication is the foundational requirement — without it, no reading position tracking is possible. This is the most critical user journey.

**Independent Test**: A user can register with a username and password, then log in and access the application. This works without any other feature.

**Acceptance Scenarios**:

1. **Given** a new user visits the application, **When** they register with a unique username and password, **Then** their account is created and they are logged in.
2. **Given** a registered user returns to the application, **When** they enter their credentials, **Then** they are authenticated and redirected to the book list.
3. **Given** a user enters invalid credentials, **When** they attempt to log in, **Then** an appropriate error message is displayed.

---

### User Story 2 - Reading Position Persistence Per Book (Priority: P1)

A logged-in user can navigate through audio chapters, and the system automatically saves their current chapter position for each book they listen to.

**Why this priority**: This is the core value proposition — saving reading positions per book is the primary feature that justifies the authentication system.

**Independent Test**: A logged-in user can play a chapter in a book, close the browser, return later, and find their last played chapter restored.

**Acceptance Scenarios**:

1. **Given** a logged-in user plays chapter 3 of "Le Petit Prince", **When** they close the browser, **Then** their position (chapter 3) is saved.
2. **Given** the same user returns to "Le Petit Prince", **When** the page loads, **Then** chapter 3 is automatically highlighted or resumed.
3. **Given** a user has not listened to a book before, **When** they open it, **Then** they start from chapter 1 or the beginning.

---

### User Story 3 - Viewing Reading Progress Across Books (Priority: P2)

A logged-in user can see a summary of their reading progress for all books in the library.

**Why this priority**: Provides visibility into progress across the library, enhancing user engagement. Valuable but not required for the core functionality.

**Independent Test**: A logged-in user can view their last played chapter for each book without needing any other feature beyond authentication and position saving.

**Acceptance Scenarios**:

1. **Given** a logged-in user has progress in multiple books, **When** they view the book list, **Then** each book shows the last chapter they were on.

---

### User Story 4 - Account Logout (Priority: P3)

A logged-in user can log out, which clears their session and ensures their reading position data is no longer accessible until they log back in.

**Why this priority**: Standard security and session management feature.

**Acceptance Scenarios**:

1. **Given** a logged-in user clicks logout, **When** the action completes, **Then** their session ends and they are redirected to the login page.

---

### Edge Cases

- What happens when a user attempts to register with an already-existing username? The system rejects the registration and prompts them to choose another username.
- What happens when a user is not logged in and tries to access a book? They are redirected to the login page.
- What happens when a user's session ends (e.g., browser closed without logout)? Their reading position remains saved server-side and is restored when they log back in.
- What happens when a book has no chapters defined? The system shows an appropriate empty state message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to register with a username and password.
- **FR-002**: System MUST authenticate users with their username and password.
- **FR-003**: System MUST persist each user's reading position (last chapter played) per book.
- **FR-004**: System MUST retrieve and restore the last played chapter when a user opens a book they have previously listened to.
- **FR-005**: System MUST display reading progress (last chapter) for each book on the book list view.
- **FR-006**: System MUST allow users to log out and invalidate their session.
- **FR-007**: System MUST protect book chapter pages so that only authenticated users can access them.
- **FR-008**: System MUST associate each reading position with the correct user account.

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered user with a username and hashed password. Each user has a unique identifier and a collection of reading positions.
- **ReadingPosition**: Tracks the last played chapter for each book per user, stored in a per-user JSON file. Contains the user ID, book ID, and last chapter number.
- **Book**: The chapter book from JSON metadata, with chapters that can be played.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete account registration in under 2 minutes.
- **SC-002**: Users can log in and see their saved reading position within 3 seconds of accessing a book they previously listened to.
- **SC-003**: 95% of logged-in users have their reading position correctly restored when returning to a book.
- **SC-004**: The system supports multiple concurrent authenticated users without data leakage between accounts.
- **SC-005**: Users can view their reading progress for all books in under 5 seconds.

## Assumptions

- Users will access the application via a web browser with session cookies enabled.
- Passwords will be stored securely with hashing (industry-standard hashing such as bcrypt).
- Passwords must be at least 8 characters.
- Sessions persist until the user explicitly logs out.
- The existing Flask application architecture will be extended; the books/metadata JSON structure remains unchanged.
- Reading positions are stored server-side (per-user JSON files), not client-side only.
- Each user can listen to all available books; there are no per-user book access restrictions.
- The application runs in a standard Flask environment with no external authentication provider.
- Storage is hybrid: Flask sessions handle authentication, while reading positions are persisted as per-user JSON files in the server's file system.

## Dependencies

- Flask session management for authentication and session cookies.
- Per-user JSON files stored server-side for reading position persistence.
- The existing book metadata JSON files in `books/metadata/`.
- The existing Flask templates (`base.html`, `index.html`, `book.html`).

## Out of Scope

- Admin controls and user management interfaces
- Social features (sharing, recommendations, leaderboards)
- Per-book access restrictions or premium content gating
- Bookmarking within chapters (beyond chapter-level position)
- Audio playback controls (handled by existing `player.js`)

## Clarifications

### Session 2026-09-10

- Q: What storage mechanism should be used for reading positions and user data? → A: Hybrid approach — Flask sessions for authentication, per-user JSON files for reading position persistence.
- Q: What are the session and password security requirements? → A: Sessions persist until explicit logout; passwords must be at least 8 characters.
- Q: What is the granularity of reading position tracking? → A: Chapter-level only (last chapter number).
- Q: How are concurrent session conflicts handled when a user listens on multiple devices? → A: Last write wins — most recent position save overwrites previous.
- Q: What is explicitly out of scope? → A: Admin controls, social features, and per-book access restrictions.
