import os
import json
import tempfile
from datetime import datetime, timezone

PROGRESS_DIR = os.path.join(os.path.dirname(__file__), '..', 'books', 'progress')


def _ensure_progress_dir():
    # Create progress directory if it doesn't exist (local development)
    # Vercel Serverless has read-only filesystem, so this dir must already exist
    try:
        os.makedirs(PROGRESS_DIR, exist_ok=True)
    except OSError:
        pass  # Read-only filesystem on Vercel (ignored)


def get_user_file_path(user_id):
    _ensure_progress_dir()
    return os.path.join(PROGRESS_DIR, f'{user_id}.json')


def read_user_progress(user_id):
    progress_file = get_user_file_path(user_id)
    if not os.path.exists(progress_file):
        return {}
    with open(progress_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_user_progress(user_id, data):
    progress_file = get_user_file_path(user_id)
    # Atomic write using temp file + rename
    fd, temp_path = tempfile.mkstemp(dir=PROGRESS_DIR, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(temp_path, progress_file)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def get_book_position(user_id, book_id):
    progress = read_user_progress(user_id)
    if book_id in progress:
        return progress[book_id].get('last_chapter', 1)
    return 1


def update_book_position(user_id, book_id, chapter_number):
    progress = read_user_progress(user_id)
    progress[book_id] = {
        'last_chapter': chapter_number,
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
    write_user_progress(user_id, progress)
