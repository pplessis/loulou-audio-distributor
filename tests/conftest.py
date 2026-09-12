import sys
import os

# Add repo root to Python path so package imports (app.models.* etc.) work
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest
from app.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret'
    # Use a temporary directory for progress files during tests
    import tempfile
    from app.services import auth_service, progress_service
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_progress_dir_auth = auth_service.PROGRESS_DIR
        orig_users_file = auth_service.USERS_FILE
        orig_progress_dir_prog = progress_service.PROGRESS_DIR
        auth_service.PROGRESS_DIR = tmpdir
        auth_service.USERS_FILE = os.path.join(tmpdir, '_users.json')
        progress_service.PROGRESS_DIR = tmpdir
        # Update app-level references if needed
        with flask_app.test_client() as c:
            yield c
        auth_service.PROGRESS_DIR = orig_progress_dir_auth
        auth_service.USERS_FILE = orig_users_file
        progress_service.PROGRESS_DIR = orig_progress_dir_prog
