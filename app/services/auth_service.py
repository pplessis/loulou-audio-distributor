import os
import json

from app.models.user import User


PROGRESS_DIR = os.path.join(os.path.dirname(__file__), '..', 'books', 'progress')
USERS_FILE = os.path.join(PROGRESS_DIR, '_users.json')


def _ensure_progress_dir():
    # Create progress directory if it doesn't exist (local development)
    # Vercel Serverless has read-only filesystem, so this dir must already exist
    try:
        os.makedirs(PROGRESS_DIR, exist_ok=True)
    except OSError:
        pass  # Read-only filesystem on Vercel (ignored)


def hash_password(bcrypt, password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def verify_password(bcrypt, password, password_hash):
    return bcrypt.check_password_hash(password_hash, password)


def save_user_record(user_id, username, password_hash):
    _ensure_progress_dir()
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    users[user_id] = {'username': username, 'password_hash': password_hash}
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def get_user_by_username(username):
    _ensure_progress_dir()
    if not os.path.exists(USERS_FILE):
        return None, None
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    for uid, data in users.items():
        if data['username'] == username:
            return uid, data
    return None, None


def get_user_by_id(user_id):
    _ensure_progress_dir()
    if not os.path.exists(USERS_FILE):
        return None, None
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    if user_id in users:
        data = users[user_id]
        return User(user_id, data['username']), data
    return None, None
