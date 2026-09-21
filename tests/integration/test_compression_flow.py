"""Integration test: compression produces smaller, valid MP3s (T019)."""
import json
import os
import tempfile

import pytest

from sync_tool.models import LogLevel, SyncConfig, CompressionSettings
from sync_tool.services.logger import SyncLogger
from sync_tool.services.compression import compress_mp3
from sync_tool.sync import SyncContext, run_sync


def _write_real_book(root, folder, source_mp3_path, chapters=3):
    book_path = os.path.join(root, folder)
    os.makedirs(book_path, exist_ok=True)
    for i in range(chapters):
        import shutil
        dest = os.path.join(book_path, f"chapter-{i:02d}.mp3")
        shutil.copy2(source_mp3_path, dest)
    return book_path


class TestCompressionFlow:
    def test_compressed_files_are_smaller_and_playable(self, mp3_fixture, tmp_path):
        _write_real_book(tmp_path, "Author - TestBook", mp3_fixture, chapters=3)
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=True,
            compression_level="64k",
            metadata_validation_enabled=False,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)
        compressed_paths = []

        def upload_file(path):
            # Verify compressed files are valid MP3s
            from pydub import AudioSegment
            assert os.path.exists(path)
            seg = AudioSegment.from_mp3(path)
            assert seg.duration_seconds > 0
            compressed_paths.append(path)
            return True

        ctx = SyncContext(
            config=config,
            logger=logger,
            source_dir=str(tmp_path),
            upload_file=upload_file,
        )
        run_sync(ctx)
        logger.close()

        # Parse log to confirm compression entries
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert any(l["source"] == "compress" and l["level"] == "INFO" for l in lines)

        # Ensure compressed files are smaller than a fresh copy
        original_size = os.path.getsize(mp3_fixture)
        for ch in compressed_paths:
            assert os.path.getsize(ch) < original_size

    def test_compression_off_does_not_modify_files(self, mp3_fixture, tmp_path):
        _write_real_book(tmp_path, "Author - NoCompress", mp3_fixture, chapters=1)
        log_file = str(tmp_path / "sync.log")
        config = SyncConfig(
            log_path=log_file,
            log_level=LogLevel.INFO,
            compression_enabled=False,
            metadata_validation_enabled=False,
        )
        logger = SyncLogger(log_file, LogLevel.INFO)
        original_sizes = []

        def upload_file(path):
            original_sizes.append(os.path.getsize(path))
            return True

        ctx = SyncContext(
            config=config, logger=logger, source_dir=str(tmp_path), upload_file=upload_file
        )
        run_sync(ctx)
        logger.close()

        assert original_sizes == [os.path.getsize(mp3_fixture)]
