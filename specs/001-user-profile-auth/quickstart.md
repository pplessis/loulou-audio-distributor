# Quickstart — User Profile Authentication & Reading Position

**Feature**: [001-user-profile-auth](spec.md)
**Date**: 2026-09-10

---

## Prerequisites

- Python 3.x with pip
- Flask installed (`pip install flask flask-login flask-bcrypt`)
- Existing Flask app at `app/app.py` with book metadata in `app/books/metadata/`

## Setup

1. **Create progress directory**:
   ```bash
   mkdir -p app/books/progress
   ```

2. **Install dependencies**:
   ```bash
   pip install flask flask-login flask-bcrypt
   ```

3. **Ensure book metadata exists**:
   ```bash
   ls app/books/metadata/*.json
   ```

## Running Validation

### 1. Registration Flow

```bash
# Start the app
cd app && python app.py

# Open browser to http://localhost:5000
# Register a new account with username and password (≥8 chars)
# Verify: redirected to book list, session cookie set
```

### 2. Login & Position Restoration

```bash
# Play a chapter in a book (e.g., chapter 3 of "Le Petit Prince")
# Close browser, return to localhost:5000
# Verify: chapter 3 is highlighted when book opens
```

### 3. Progress View

```bash
# Navigate to the book list page while logged in
# Verify: each book shows the last chapter played
```

### 4. Logout

```bash
# Click logout
# Verify: session cleared, redirected to login
# Verify: reading position still saved server-side
```

### 5. Edge Case: Duplicate Registration

```bash
# Attempt to register with an existing username
# Verify: registration rejected, prompted to choose another username
```

### 6. Edge Case: Unauthenticated Access

```bash
# Try to access a book without being logged in
# Verify: redirected to login page
```

## Running Tests

```bash
# Install pytest
pip install pytest pytest-flask

# Run tests
cd app && python -m pytest ../specs/001-user-profile-auth/
```

## Expected Outcomes

| Scenario | Expected Result |
|----------|-----------------|
| Register with valid credentials | Account created, logged in, session set |
| Register with duplicate username | 409, error message shown |
| Login with valid credentials | Authenticated, redirected to book list |
| Login with invalid credentials | 401, error message shown |
| Open previously-listened book | Last chapter highlighted within 3 seconds |
| Open new book | Starts at chapter 1 |
| View book list while logged in | Each book shows last played chapter |
| Logout | Session cleared, redirected to login |
| Access book without login | Redirected to login page |
