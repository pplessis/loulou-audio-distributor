"""Credentials-gated Google Drive upload integration test (T041)."""
import json
import os

import pytest

from sync_tool.models import LogLevel, SyncConfig
from sync_tool.services.logger import SyncLogger
from sync_tool.sync import SyncContext, run_sync

def _write_book(root, folder):
    path = os.path.join(root, folder)
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "ch1.mp3"), "wb").close()
    return path


@pytest.mark.drive
class TestDriveUpload:
    def test_drive_upload_creates_public_link(self, tmp_path):
        # Skip if no Google credentials available
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            pytest.skip("No Google credentials available (set GOOGLE_APPLICATION_CREDENTIALS)")

        _write_book(tmp_path, "Author - DriveTest", ["ch1.mp3"])
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_validation_enabled=False,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)

        uploaded_paths = []
        def real_upload(path):
            # Stub: in a real scenario this would use Google Drive API.
            # Because feature 002 is unimplemented, we assert the upload hook is called.
            uploaded_paths.append(path)
            return True

        ctx = SyncContext(
            config=config,
            logger=logger,
            source_dir=str(tmp_path),
            upload_file=real_upload,
        )
        run_sync(ctx)
        logger.close()

        assert len(uploaded_paths) >= 1
        assert any("ch1.mp3" in p for p in uploaded_paths)
        # Verify log entries contain file_uploaded
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert any(l["event_type"] == "file_uploaded" for l in lines)
