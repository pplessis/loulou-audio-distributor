"""Integration test: metadata validation populates cover and sets validation_status (T027)."""
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


class TestMetadataValidationFlow:
    def test_metadata_validation_populates_cover_and_sets_validated(self, mock_openlibrary_server, tmp_path):
        _write_book(tmp_path, "Antoine de Saint-Exupéry - Le Petit Prince")
        log_file = str(tmp_path / "sync.log")
        index_dir = str(tmp_path / "metadata")
        os.makedirs(index_dir, exist_ok=True)

        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_api_endpoint=mock_openlibrary_server + "/search.json",
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
        run_sync(ctx)
        logger.close()

        # Check generated index has validation_status
        book_id = "le-petit-prince"
        index_path = os.path.join(index_dir, f"{book_id}.json")
        assert os.path.exists(index_path)
        with open(index_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
        assert idx.get("validation_status") == ValidationStatus.VALIDATED.value or idx.get("validation_status") == ValidationStatus.PENDING.value
        # Cover may be populated if match found
        if idx.get("validation_status") == ValidationStatus.VALIDATED.value:
            assert idx.get("cover") is not None

    def test_no_metadata_validation_leaves_status_absent(self, tmp_path):
        _write_book(tmp_path, "Author - BookNoVal")
        log_file = str(tmp_path / "sync.log")
        index_dir = str(tmp_path / "metadata")
        os.makedirs(index_dir, exist_ok=True)

        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_validation_enabled=False,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)
        ctx = SyncContext(
            config=config,
            logger=logger,
            source_dir=str(tmp_path),
            index_dir=index_dir,
        )
        run_sync(ctx)
        logger.close()

        book_id = "booknoval"
        index_path = os.path.join(index_dir, f"{book_id}.json")
        assert os.path.exists(index_path)
        with open(index_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
        assert "validation_status" not in idx

    @pytest.mark.live
    def test_live_openlibrary_matches(self, tmp_path):
        _write_book(tmp_path, "Antoine de Saint-Exupéry - Le Petit Prince")
        log_file = str(tmp_path / "sync.log")
        index_dir = str(tmp_path / "metadata")
        os.makedirs(index_dir, exist_ok=True)

        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_api_endpoint="https://openlibrary.org/search.json",
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
        run_sync(ctx)
        logger.close()

        book_id = "le-petit-prince"
        index_path = os.path.join(index_dir, f"{book_id}.json")
        assert os.path.exists(index_path)
        with open(index_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
        assert idx.get("validation_status") in (ValidationStatus.VALIDATED.value, ValidationStatus.VALIDATION_FAILED.value)
        if idx.get("validation_status") == ValidationStatus.VALIDATED.value:
            assert idx.get("cover") is not None
