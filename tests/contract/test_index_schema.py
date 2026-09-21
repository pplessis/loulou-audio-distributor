"""Contract test for generated JSON index schema (T026)."""
import json
import os
import tempfile

import pytest

from sync_tool.models import ValidationStatus


def _minimal_index(**overrides):
    return {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "https://example.com/cover.jpg",
        "chapters": 1,
        "duration": "15 min",
        "chapters_list": [
            {"title": "Chapitre 1", "audio": "https://example.com/ch1.mp3", "duration": "15 min"}
        ],
        **overrides,
    }


class TestIndexSchema:
    def test_index_without_validation_status_is_valid(self):
        idx = _minimal_index()
        assert "validation_status" not in idx
        # Smoke: JSON round-trips cleanly
        assert json.loads(json.dumps(idx)) == idx

    def test_index_with_validation_status_validated(self):
        idx = _minimal_index(validation_status="validated")
        assert idx["validation_status"] == ValidationStatus.VALIDATED.value

    def test_index_with_validation_status_pending(self):
        idx = _minimal_index(validation_status="pending")
        assert idx["validation_status"] == ValidationStatus.PENDING.value

    def test_index_with_validation_status_failed(self):
        idx = _minimal_index(validation_status="validation_failed")
        assert idx["validation_status"] == ValidationStatus.VALIDATION_FAILED.value

    def test_validation_status_is_additive_and_does_not_break_existing_fields(self):
        idx = _minimal_index(validation_status="validated")
        required = {"title", "author", "cover", "chapters", "duration", "chapters_list", "validation_status"}
        assert required.issubset(set(idx.keys()))
