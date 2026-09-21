"""Integration test: >=80% match rate over well-known corpus (T030 / SC-003)."""
import json
import os

import pytest

from sync_tool.models import LogLevel, SyncConfig, ValidationStatus
from sync_tool.services.logger import SyncLogger
from sync_tool.services.metadata_validator import MetadataValidator
from sync_tool.services.openlibrary import OpenLibraryClient
from sync_tool.sync import SyncContext, run_sync


class TestMetadataMatchRate:
    def test_match_rate_at_least_80_percent(self, mock_openlibrary_server, tmp_path):
        corpus = json.load(open("tests/fixtures/well_known_audiobooks.json"))
        index_dir = str(tmp_path / "metadata")
        os.makedirs(index_dir, exist_ok=True)
        log_file = str(tmp_path / "sync.log")

        # Write each corpus book as a folder
        for book in corpus:
            folder = f"{book['author']} - {book['title']}"
            path = os.path.join(tmp_path, folder)
            os.makedirs(path, exist_ok=True)
            open(os.path.join(path, "ch1.mp3"), "wb").close()

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

        matched = 0
        for book in corpus:
            book_id = book["title"].strip().lower().replace(" ", "-")
            index_path = os.path.join(index_dir, f"{book_id}.json")
            assert os.path.exists(index_path)
            with open(index_path, "r", encoding="utf-8") as f:
                idx = json.load(f)
            if idx.get("validation_status") == ValidationStatus.VALIDATED.value:
                matched += 1
            elif idx.get("validation_status") == ValidationStatus.VALIDATION_FAILED.value:
                pass  # no match
            else:
                pytest.fail(f"Unexpected validation_status for {book_id}: {idx.get('validation_status')}")

        total = len(corpus)
        assert total >= 10
        assert matched / total >= 0.80, f"Matched only {matched}/{total} (need >=80%)"
