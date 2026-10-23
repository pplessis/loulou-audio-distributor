# AGENTS.md — Loulou Audio Distributor

## Quickstart

**Run the Flask app locally:**

```bash
cd app
python -m pip install -r requirements.txt  # or: pip install Flask requests flask-login flask-bcrypt
mkdir -p books/metadata books/covers
python app.py  # runs on http://127.0.0.1:5000
```

**Run the sync tool CLI (local only, never deployed):**

```bash
python -m sync_tool /chemin/vers/audiolivres --log-path /tmp/sync.log
```

## Project structure (key directories only)

- `app/app.py` — **single entry point**. All routes, auth, and audiobook serving are defined inline. **Do not look for `routes.py` or `config.py`** — they don't exist; routes and config are in `app.py`.
- `app/books/metadata/` — one JSON per book. Filenames must be **slugified**: `title.lower().replace(' ', '-') + '.json'` (e.g. `le-petit-prince.json`). The route `/book/<book_id>` loads `{book_id}.json` from this dir.
- `app/books/progress/` — local user progress/_users.json. Created on‑demand; **Vercel serverless is read‑only**, so this dir must already exist before deploy.
- `sync_tool/` — independent CLI (Python 3.11+, ffmpeg in PATH). **Never import from `app/`**; separate dependencies and entry point.
- `tests/contract/` — contract tests (no external deps). Run: `pytest tests/contract/`
- `tests/integration/` — integration tests (requires services/markers). Run: `pytest tests/integration/ -m "not live and not drive"`
- `vercel.json` — Flask Python config for Vercel deployment. Only `app/` is deployed; `sync_tool/` stays local.

## High‑signal conventions & quirks

- **Dynamic JSON loading**: `app.py` loads `*.json` from `books/metadata/` at every `/` route. If the dir is missing, `index()` returns an empty book list (no crash), but `/book/<id>` returns 404.
- **Slug convention**: JSON filenames are derived from `book.title|lower|replace(' ', '-')`. Always name your JSON files to match this pattern or the book route will 404.
- **Audio proxy**: `/audio` route proxots MP3 URLs (supports Google Drive and OneDrive links). It adds `Access-Control-Allow-Origin: *`.
- **Authentication**: Login/register uses form POST to `/login` and `/register`. Passwords ≥8 chars. SESSION_COOKIE_HTTPONLY=True, SameSite=Lax. SECRET_KEY from env or defaults to `'dev-secret-key-change-in-production'`.
- **Sync tool is opt‑in**: `sync_tool/` is a standalone CLI. It is **not** importable from `app/`. Do not mix dependencies (Flask vs. google-api‑python‑client).
- **Pytest markers**:
  - `live` — real OpenLibrary API (internet required)
  - `drive` — Google Drive credentials required
  - `slow` — compression on 10+ files
  - Fast offline suite: `pytest tests/ -m "not live and not drive and not slow"`
- **Vercel‑first**: The deployed app has no long‑running processes, no ffmpeg dependency, and no persistent server state. Only `app/` is deployed; `sync_tool/` remains a local CLI.

## Commands you’ll actually use

| Goal | Command |
|---|---|
| Install deps (app) | `cd app && python -m pip install -r requirements.txt` |
| Run Flask dev server | `cd app && python app.py` |
| Run contract tests | `pytest tests/contract/` |
| Run integration tests (fast) | `pytest tests/integration/ -m "not live and not drive"` |
| Run sync tool (basic) | `python -m sync_tool /path/to/audiolivres --log-path /tmp/sync.log` |
| Run sync with compression | `python -m sync_tool /path/to/audiolivres --compress --compression-level 64k` |
| Sync without metadata validation | `python -m sync_tool /path/to/audiolivres --no-metadata-validation` |

## Known gaps (verify before assuming)

- `requirements.txt` exists at repo root **and** at `app/requirements.txt`. Both are consulted; prefer `app/requirements.txt`.
- `routes.py` and `config.py` are **not** separate files. Do not reference them outside `app.py`.
- `sync_tool/` requires `ffmpeg` in `$PATH` for compression. Without it, `--compress` is a no-op.
- The app uses `_users.json` under `books/progress/` for auth state. On first run the dir is auto‑created; on Vercel it must already exist.
- No CI/lint/formatter/typecheck is configured. Run those locally if you add them.