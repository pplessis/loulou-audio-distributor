# AGENTS.md

## Project Overview

Flask app ("Loulou Audio Distributor") that serves audio chapter books. MP3 files are hosted on OneDrive via public share links stored in JSON metadata files.

## Structure

- `app/app.py` — **Main entry point**. Run with `cd app && python app.py` (port 5000).
- `app/templates/` — Jinja2 templates: `base.html`, `index.html`, `book.html`
- `app/static/` — CSS, JS (`player.js`), images
- `app/books/metadata/` — JSON metadata files (one per book). **This directory does not exist yet**; the app will error if it's missing when `index()` runs.

## Key Architecture Notes

- `app.py` dynamically loads all `.json` files from `books/metadata/` at the `/` route. Each JSON filename (minus extension) becomes the `book_id` used in `/book/<book_id>` URLs.
- The URL slug in `index.html` uses `book.title|lower|replace(' ', '-')`, so JSON filenames must match this pattern (e.g., `le-petit-prince.json`).
- `routes.py`, `config.py`, `requirements.txt`, and `vercel.json` are referenced in `README.md` but **do not exist in the repo**. Do not assume they exist.

## Setup

```bash
cd app
pip install flask
mkdir -p books/metadata books/covers
# Add book JSON files to books/metadata/
python app.py
```

## Important Gaps

- No `requirements.txt` — dependencies not pinned
- No CI/CD, tests, lint, typecheck, or formatter config
- No `.github/` workflows
- No `vercel.json` (deployment config referenced in README but absent)
- No `.opencode.json`, `CLAUDE.md`, or other instruction files

## Deployment

README describes Vercel deployment, but `vercel.json` is missing. Vercel should auto-detect Flask if configured, but this is unverified in the repo.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan at
specs/001-user-profile-auth/plan.md
<!-- SPECKIT END -->
