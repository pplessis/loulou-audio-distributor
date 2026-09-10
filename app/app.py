from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
import json
from datetime import datetime, timezone

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

os.makedirs(PROGRESS_DIR, exist_ok=True)


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    users_file = os.path.join(PROGRESS_DIR, '_users.json')
    if not os.path.exists(users_file):
        return None
    with open(users_file, 'r') as f:
        users = json.load(f)
    if user_id in users:
        return User(user_id, users[user_id]['username'])
    return None


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def verify_password(password, password_hash):
    return bcrypt.check_password_hash(password_hash, password)


def read_user_progress(user_id):
    progress_file = os.path.join(PROGRESS_DIR, f'{user_id}.json')
    if not os.path.exists(progress_file):
        return {}
    with open(progress_file, 'r') as f:
        return json.load(f)


def write_user_progress(user_id, data):
    progress_file = os.path.join(PROGRESS_DIR, f'{user_id}.json')
    with open(progress_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def get_book_position(user_id, book_id):
    progress = read_user_progress(user_id)
    if book_id in progress:
        return progress[book_id].get('last_chapter', 1)
    return 1


def get_user_file_path(user_id):
    return os.path.join(PROGRESS_DIR, f'{user_id}.json')


def save_user_record(user_id, username, password_hash):
    users_file = os.path.join(PROGRESS_DIR, '_users.json')
    users = {}
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
    users[user_id] = {'username': username, 'password_hash': password_hash}
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)


def get_user_by_username(username):
    users_file = os.path.join(PROGRESS_DIR, '_users.json')
    if not os.path.exists(users_file):
        return None
    with open(users_file, 'r') as f:
        users = json.load(f)
    for uid, data in users.items():
        if data['username'] == username:
            return uid, data
    return None, None


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Authentication required'}), 401


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.route('/')
def index():
    books = []
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
    password_hash = hash_password(password)
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
    if not uid or not verify_password(password, user_data['password_hash']):
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
    progress = read_user_progress(str(current_user.id))
    books = []
    for filename in os.listdir(BOOKS_METADATA_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(BOOKS_METADATA_DIR, filename), 'r', encoding='utf-8') as f:
                book_data = json.load(f)
                book_id = filename.replace('.json', '')
                last_chapter = progress.get(book_id, {}).get('last_chapter') if progress else None
                books.append({'book_id': book_id, 'title': book_data['title'], 'last_chapter': last_chapter})
    return jsonify(books)


@app.route('/book/<book_id>/position', methods=['POST'])
@login_required
def save_position(book_id):
    data = request.get_json()
    chapter_number = data.get('chapter_number', 1)
    progress = read_user_progress(str(current_user.id))
    progress[book_id] = {'last_chapter': chapter_number, 'last_updated': datetime.now(timezone.utc).isoformat()}
    write_user_progress(str(current_user.id), progress)
    return jsonify({'message': 'Position saved'}), 200


@app.route('/login')
def login_page():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
