import os
import sys

# Allow imports when running as script (cd app && python app.py)
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import requests
from urllib.parse import unquote
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import json
import logging

from app.models.user import User
from app.services.auth_service import (
    hash_password,
    verify_password,
    save_user_record,
    get_user_by_username,
    get_user_by_id,
)
from app.services.progress_service import (
    read_user_progress,
    write_user_progress,
    get_book_position,
    update_book_position,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

BOOKS_METADATA_DIR = os.path.join(os.path.dirname(__file__), 'books', 'metadata')
PROGRESS_DIR = os.path.join(os.path.dirname(__file__), 'books', 'progress')

# Create progress directory if it doesn't exist (local development)
# Vercel Serverless has read-only filesystem, so this dir must already exist
try:
    os.makedirs(PROGRESS_DIR, exist_ok=True)
except OSError:
    pass  # Read-only filesystem on Vercel (ignored)

logging.basicConfig(level=logging.INFO)


@login_manager.user_loader
def load_user(user_id):
    user, _ = get_user_by_id(user_id)
    return user


@app.errorhandler(401)
def unauthorized(e):
    if request.is_json:
        return jsonify({'error': 'Authentication required'}), 401
    return redirect(url_for('login_page'))


@app.errorhandler(404)
def not_found(e):
    if request.is_json:
        return jsonify({'error': 'Resource not found'}), 404
    return "Livre introuvable", 404


@app.route('/')
def index():
    books = []
    if os.path.isdir(BOOKS_METADATA_DIR):
        for filename in os.listdir(BOOKS_METADATA_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(BOOKS_METADATA_DIR, filename), 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                    books.append(book_data)
    progress_data = {}
    if current_user.is_authenticated:
        progress_data = read_user_progress(str(current_user.id))
    return render_template('index.html', books=books, progress=progress_data, user=current_user)


@app.route('/book/<book_id>')
@login_required
def book(book_id):
    book_path = os.path.join(BOOKS_METADATA_DIR, f'{book_id}.json')
    if not os.path.exists(book_path):
        return "Livre introuvable", 404
    with open(book_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    last_chapter = get_book_position(str(current_user.id), book_id)
    return render_template('book.html', book=book_data, last_chapter=last_chapter, user=current_user)


@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    return "Fonctionnalité avancée : À implémenter si besoin"


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    existing_uid, _ = get_user_by_username(username)
    if existing_uid:
        return jsonify({'error': 'Username already exists'}), 409
    user_id = str(len(os.listdir(PROGRESS_DIR)) + 1)
    password_hash = hash_password(bcrypt, password)
    save_user_record(user_id, username, password_hash)
    user = User(user_id, username)
    login_user(user)
    return jsonify({'message': 'Account created', 'redirect': url_for('index')}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    uid, user_data = get_user_by_username(username)
    if not uid or not verify_password(bcrypt, password, user_data['password_hash']):
        return jsonify({'error': 'Invalid credentials'}), 401
    user = User(uid, user_data['username'])
    login_user(user)
    return jsonify({'message': 'Logged in', 'redirect': url_for('index')}), 200


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/progress')
@login_required
def progress():
    prog = read_user_progress(str(current_user.id))
    books = []
    if os.path.isdir(BOOKS_METADATA_DIR):
        for filename in os.listdir(BOOKS_METADATA_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(BOOKS_METADATA_DIR, filename), 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                    book_id = filename.replace('.json', '')
                    last_chapter = prog.get(book_id, {}).get('last_chapter') if prog else None
                    books.append({'book_id': book_id, 'title': book_data['title'], 'last_chapter': last_chapter})
    return jsonify(books)


@app.route('/book/<book_id>/position', methods=['POST'])
@login_required
def save_position(book_id):
    data = request.get_json()
    chapter_number = data.get('chapter_number', 1)
    update_book_position(str(current_user.id), book_id, chapter_number)
    return jsonify({'message': 'Position saved'}), 200


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/audio')
@login_required
def audio_proxy():
    audio_url = request.args.get('url', '')
    if not audio_url:
        return jsonify({'error': 'URL parameter required'}), 400
    
    # Handle Google Drive URLs - convert to direct download format
    if 'drive.google.com' in audio_url:
        if '/uc?export=download' in audio_url:
            # Already in download format
            pass
        elif '/file/d/' in audio_url:
            # Extract file ID and convert to download URL
            file_id = audio_url.split('/file/d/')[1].split('/')[0]
            audio_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = requests.get(audio_url, headers=headers, stream=True, timeout=30)
        req.raise_for_status()
        content_type = req.headers.get('Content-Type', 'audio/mpeg')
        def generate():
            for chunk in req.iter_content(chunk_size=8192):
                yield chunk
        return Response(generate(), mimetype=content_type, headers={
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=3600'
        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Audio proxy error: {e}")
        return jsonify({'error': str(e)}), 502


if __name__ == '__main__':
    app.run(debug=True)
