"""Contract tests for structured logging (T011)."""
import json
import os
from datetime import datetime, timezone

import pytest

from sync_tool.models import LogEntry, LogLevel
from sync_tool.services.logger import SyncLogger


class TestLogEntrySerialization:
    def test_to_dict_has_all_contract_fields(self):
        ts = datetime(2026, 9, 19, 14, 30, 0, tzinfo=timezone.utc)
        entry = LogEntry(
            timestamp=ts,
            level=LogLevel.INFO,
            source="scan",
            event_type="scan_start",
            message="Scanning /books",
            audiobook_id=None,
        )
        d = entry.to_dict()
        assert set(d.keys()) == {"timestamp", "level", "source", "audiobook_id", "event_type", "message"}
        assert d["timestamp"] == ts.isoformat()
        assert d["level"] == "INFO"
        assert d["source"] == "scan"
        assert d["event_type"] == "scan_start"
        assert d["message"] == "Scanning /books"
        assert d["audiobook_id"] is None

    def test_to_dict_with_audiobook_id(self):
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=LogLevel.WARN,
            source="upload",
            event_type="file_uploaded",
            message="chapter-01.mp3",
            audiobook_id="le-petit-prince",
        )
        d = entry.to_dict()
        assert d["audiobook_id"] == "le-petit-prince"

    def test_json_lines_round_trip(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        logger = SyncLogger(log_file, LogLevel.INFO)
        logger.log_entry(LogLevel.INFO, "scan", "scan_start", "start")
        logger.log_entry(LogLevel.WARN, "upload", "file_uploaded", "warn msg", "book1")
        logger.close()

        with open(log_file, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        assert len(lines) == 2
        d0 = json.loads(lines[0])
        assert d0["event_type"] == "scan_start"
        d1 = json.loads(lines[1])
        assert d1["level"] == "WARN"
        assert d1["audiobook_id"] == "book1"


class TestLevelFiltering:
    def test_info_level_records_all(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        logger = SyncLogger(log_file, LogLevel.INFO)
        logger.log_entry(LogLevel.INFO, "s", "e", "info")
        logger.log_entry(LogLevel.WARN, "s", "e", "warn")
        logger.log_entry(LogLevel.ERROR, "s", "e", "err")
        logger.close()
        with open(log_file, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        assert len(lines) == 3

    def test_warn_level_filters_info(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        logger = SyncLogger(log_file, LogLevel.WARN)
        logger.log_entry(LogLevel.INFO, "s", "e", "info")
        logger.log_entry(LogLevel.WARN, "s", "e", "warn")
        logger.log_entry(LogLevel.ERROR, "s", "e", "err")
        logger.close()
        with open(log_file, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        assert len(lines) == 2
        assert all(json.loads(l)["level"] in ("WARN", "ERROR") for l in lines)

    def test_error_level_filters_info_and_warn(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        logger = SyncLogger(log_file, LogLevel.ERROR)
        logger.log_entry(LogLevel.INFO, "s", "e", "info")
        logger.log_entry(LogLevel.WARN, "s", "e", "warn")
        logger.log_entry(LogLevel.ERROR, "s", "e", "err")
        logger.close()
        with open(log_file, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["level"] == "ERROR"


class TestUnwritablePathFallback:
    def test_falls_back_to_stderr(self, tmp_path, capsys):
        bad_path = "/nonexistent_dir_sync_tool/log.jsonl"
        logger = SyncLogger(bad_path, LogLevel.INFO)
        logger.log_entry(LogLevel.INFO, "scan", "scan_start", "fallback test")
        captured = capsys.readouterr()
        assert "fallback test" in captured.err
        assert not os.path.exists(bad_path)
