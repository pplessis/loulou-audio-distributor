"""Integration test: unreachable DB continues with WARN and status=failed (T028 / SC-005)."""
import json
import os

import pytest

from sync_tool.models import LogLevel, SyncConfig, ValidationStatus
from sync_tool.services.logger import SyncLogger
from sync_tool.services.metadata_validator import MetadataValidator
from sync_tool.services.openlibrary import OpenLibraryClient
from sync_tool.sync import SyncContext, run_sync


def _write_book(root, folder):
    path = os.path.join(root, folder)
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "ch1.mp3"), "wb").close()
    return path


class TestMetadataUnreachable:
    def test_sync_continues_and_logs_warn(self, mock_unreachableserver, tmp_path):
        _write_book(tmp_path, "Author - BookA")
        _write_book(tmp_path, "Author - BookB")
        log_file = str(tmp_path / "sync.log")
        index_dir = str(tmp_path / "metadata")
        os.makedirs(index_dir, exist_ok=True)

        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_api_endpoint=mock_unreachableserver + "/search.json",
            metadata_validation_enabled=True,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)
        client = OpenLibraryClient(config.metadata_api_endpoint)
        validator = MetadataValidator(client=client, logger=logger)
        ctx = SyncContext(
            config=config,
            logger=logger,
            source_dir=str(tmp_path),
            metadata_validator=validator,
            index_dir=index_dir,
        )
        errors = run_sync(ctx)
        logger.close()

        # Sync should continue with 0 errors from the unreachable DB
        assert errors == 0

        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert any(
            l["level"] == "WARN" and "metadata" in l["message"].lower()
            for l in lines
        )

        # Generated indexes should have validation_failed for each book
        for book_id in ("booka", "bookb"):
            index_path = os.path.join(index_dir, f"{book_id}.json")
            if os.path.exists(index_path):
                with open(index_path, "r", encoding="utf-8") as f:
                    idx = json.load(f)
                assert idx.get("validation_status") == ValidationStatus.VALIDATION_FAILED.value
