"""Integration test: a sync run produces structured log entries (T012)."""
import json
import os
import tempfile

import pytest

from sync_tool.models import LogLevel, SyncConfig, ValidationStatus
from sync_tool.services.logger import SyncLogger
from sync_tool.sync import SyncContext, run_sync, discover_audiobooks


def _write_book(root, folder, chapters):
    path = os.path.join(root, folder)
    os.makedirs(path, exist_ok=True)
    for ch in chapters:
        open(os.path.join(path, ch), "wb").close()
    return path


class TestSyncLogging:
    def test_sync_produces_scan_and_summary_entries(self, tmp_path):
        _write_book(tmp_path, "Author - Title1", ["ch1.mp3", "ch2.mp3"])
        _write_book(tmp_path, "Title2", ["ch1.mp3"])

        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_validation_enabled=False,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)
        ctx = SyncContext(config=config, logger=logger, source_dir=str(tmp_path))
        run_sync(ctx)
        logger.close()

        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        event_types = [l["event_type"] for l in lines]
        assert "scan_start" in event_types
        assert "scan_end" in event_types
        assert "summary" in event_types

    def test_sync_logs_folder_created_and_file_uploaded(self, tmp_path):
        _write_book(tmp_path, "Author - Title1", ["ch1.mp3", "ch2.mp3"])
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(log_path=log_file, log_level=LogLevel.INFO, compression_enabled=False, metadata_validation_enabled=False)
        logger = SyncLogger(log_file, LogLevel.INFO)
        ctx = SyncContext(config=config, logger=logger, source_dir=str(tmp_path))
        run_sync(ctx)
        logger.close()

        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        assert any(l["event_type"] == "folder_created" for l in lines)
        file_uploads = [l for l in lines if l["event_type"] == "file_uploaded"]
        assert len(file_uploads) == 2
        assert all(l["audiobook_id"] == "title1" for l in file_uploads)

    def test_sync_logs_error_and_continues(self, tmp_path):
        _write_book(tmp_path, "Author - BookA", ["ch1.mp3"])
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(log_path=log_file, log_level=LogLevel.INFO, compression_enabled=False, metadata_validation_enabled=False)
        logger = SyncLogger(log_file, LogLevel.INFO)

        def failing_upload(path):
            raise RuntimeError("upload failed")

        ctx = SyncContext(
            config=config, logger=logger, source_dir=str(tmp_path), upload_file=failing_upload
        )
        errors = run_sync(ctx)
        logger.close()

        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        assert any(l["event_type"] == "error" and l["level"] == "ERROR" for l in lines)
        assert errors >= 1
        # other book still scanned and attempted (only 1 book in this test)

    def test_summary_counts_match(self, tmp_path):
        _write_book(tmp_path, "A - Book1", ["c1.mp3", "c2.mp3"])
        _write_book(tmp_path, "B - Book2", ["c1.mp3"])
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(log_path=log_file, log_level=LogLevel.INFO, compression_enabled=False, metadata_validation_enabled=False)
        logger = SyncLogger(log_file, LogLevel.INFO)
        ctx = SyncContext(config=config, logger=logger, source_dir=str(tmp_path))
        run_sync(ctx)
        logger.close()

        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        summary = [l for l in lines if l["event_type"] == "summary"][0]
        assert "2 audiobooks" in summary["message"]
        assert "3 files uploaded" in summary["message"]
        assert "0 errors" in summary["message"]
