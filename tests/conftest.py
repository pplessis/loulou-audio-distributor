import os
import subprocess
import sys
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Add repo root to Python path so package imports (app.models.*, sync_tool.*) work
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest
from app.app import app as flask_app


def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark tests that hit the real OpenLibrary API")
    config.addinivalue_line("markers", "drive: mark tests that require real Google Drive credentials")
    config.addinivalue_line("markers", "slow: mark tests that are slow (e.g., aggregate compression)")


class _MockOpenLibraryHandler(BaseHTTPRequestHandler):
    """Serve recorded OpenLibrary fixtures under /search.json?q=<encoded-query>"""

    def log_message(self, format, *args):
        pass  # silence request logging

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/search.json":
            self.send_error(404)
            return
        qs = parse_qs(parsed.query)
        # Build a deterministic key from title + author so tests can map fixtures
        title = qs.get("title", [""])[0]
        author = qs.get("author", [""])[0]
        key = f"{title}|{author}"
        # Find the fixture directory
        fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures", "openlibrary")
        # Map known keys to recorded fixture files using a lookup index
        lookup_path = os.path.join(fixture_dir, "lookup.json")
        response = {"numFound": 0, "docs": []}
        if os.path.exists(lookup_path):
            with open(lookup_path, "r", encoding="utf-8") as f:
                lookup = json.load(f)
            if key in lookup:
                rec_path = os.path.join(fixture_dir, lookup[key])
                if os.path.exists(rec_path):
                    with open(rec_path, "r", encoding="utf-8") as f:
                        response = json.load(f)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


@pytest.fixture(scope="session")
def mock_openlibrary_server():
    """Local HTTP server that mimics OpenLibrary Search API (deterministic, no network)."""
    server = HTTPServer(("127.0.0.1", 0), _MockOpenLibraryHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="session")
def mock_unreachableserver():
    """A local server that immediately goes down so requests fail."""
    server = HTTPServer(("127.0.0.1", 0), _MockOpenLibraryHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}"
    server.shutdown()
    thread.join(timeout=2)
    yield url


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret'
    # Use a temporary directory for progress files during tests
    import tempfile
    from app.services import auth_service, progress_service
    import app.app as app_module
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_progress_dir_auth = auth_service.PROGRESS_DIR
        orig_users_file = auth_service.USERS_FILE
        orig_progress_dir_prog = progress_service.PROGRESS_DIR
        orig_progress_dir_app = app_module.PROGRESS_DIR
        auth_service.PROGRESS_DIR = tmpdir
        auth_service.USERS_FILE = os.path.join(tmpdir, '_users.json')
        progress_service.PROGRESS_DIR = tmpdir
        app_module.PROGRESS_DIR = tmpdir
        with flask_app.test_client() as c:
            yield c
        auth_service.PROGRESS_DIR = orig_progress_dir_auth
        auth_service.USERS_FILE = orig_users_file
        progress_service.PROGRESS_DIR = orig_progress_dir_prog
        app_module.PROGRESS_DIR = orig_progress_dir_app


def _run_ffmpeg(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def _generate_mp3(path, frequency=440, duration=0.5, bitrate="128k", sample_rate=44100):
    """Generate a tiny valid MP3 via ffmpeg (T036)."""
    _run_ffmpeg([
        "-f", "lavfi",
        "-i", f"sine=frequency={frequency}:duration={duration}",
        "-b:a", bitrate, "-ar", str(sample_rate), "-ac", "1",
        path,
    ])
    return path


@pytest.fixture(scope="session")
def mp3_fixture(tmp_path_factory):
    """A tiny, valid, playable MP3 file (128kbps) shared by tests."""
    path = tmp_path_factory.mktemp("mp3") / "tiny.mp3"
    return _generate_mp3(str(path))


@pytest.fixture(scope="session")
def mp3_corpus(tmp_path_factory):
    """A corpus of >=10 varied, real MP3 files (SC-002 aggregate test, T020)."""
    root = tmp_path_factory.mktemp("mp3_corpus")
    specs = [
        (200, 2.5, "128k"), (440, 3.0, "128k"), (660, 2.0, "128k"),
        (880, 2.5, "192k"), (120, 3.5, "192k"), (330, 2.0, "192k"),
        (550, 3.0, "256k"), (770, 2.5, "256k"), (990, 2.0, "256k"),
        (165, 3.0, "320k"), (264, 2.5, "320k"), (392, 2.0, "128k"),
    ]
    paths = []
    for i, (freq, dur, bitrate) in enumerate(specs):
        path = root / f"corpus-{i:02d}-{freq}hz-{bitrate}.mp3"
        _generate_mp3(str(path), frequency=freq, duration=dur, bitrate=bitrate)
        paths.append(path)
    return paths


@pytest.fixture()
def temp_log_path(tmp_path):
    """A writable log file path (T003)."""
    return str(tmp_path / "sync.log")


@pytest.fixture()
def sync_context_factory(temp_log_path):
    """Build a SyncContext with a logger writing to a temp log file (T003)."""
    from sync_tool.models import LogLevel, SyncConfig
    from sync_tool.services.logger import SyncLogger
    from sync_tool.sync import SyncContext

    def _make(**overrides):
        defaults = {
            "log_path": temp_log_path,
            "log_level": LogLevel.INFO,
            "compression_enabled": False,
            "compression_level": "64k",
            "metadata_validation_enabled": True,
        }
        defaults.update(overrides)
        config = SyncConfig(**defaults)
        logger = SyncLogger(config.log_path, config.log_level)
        return SyncContext(config=config, logger=logger, source_dir="."), logger

    return _make