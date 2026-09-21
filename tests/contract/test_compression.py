"""Contract tests for MP3 compression service (T018)."""
import os

import pytest

from sync_tool.models import CompressionSettings
from sync_tool.services.compression import compress_mp3


class TestCompressionSettingsDefaults:
    def test_defaults(self):
        cs = CompressionSettings()
        assert cs.enabled is False
        assert cs.compression_level == "64k"

    def test_custom_level(self):
        cs = CompressionSettings(enabled=True, compression_level="96k")
        assert cs.enabled is True
        assert cs.compression_level == "96k"


class TestCompressMp3:
    def test_compresses_when_source_is_higher_bitrate(self, mp3_fixture):
        original_size = os.path.getsize(mp3_fixture)
        result = compress_mp3(mp3_fixture, target_bitrate="64k")
        assert result["did_compress"] is True
        assert result["compressed_size"] < result["original_size"]
        assert os.path.exists(result["output_path"])

    def test_output_is_valid_playable_mp3(self, mp3_fixture, tmp_path):
        result = compress_mp3(mp3_fixture, target_bitrate="64k")
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(result["output_path"])
        assert seg.duration_seconds > 0

    def test_keeps_original_when_output_larger(self, mp3_fixture):
        """Edge case: if compressed output is larger than original, keep original."""
        # Compress at a very low bitrate should reduce size; but test the contract
        # by compressing to a bitrate that might produce larger output due to format
        # overhead. We'll simulate by passing an absurdly high bitrate target (320k).
        # For a 128k source, 320k target shouldn't shrink; but pydub may still rewrite.
        # Instead, we'll compress with a very high target and verify fallback logic.
        result = compress_mp3(mp3_fixture, target_bitrate="320k")
        # If the compressed file is larger than original, contract says keep original
        if result["did_compress"]:
            assert result["compressed_size"] <= result["original_size"]
        else:
            assert result["output_path"] == mp3_fixture

    def test_returns_dict_with_expected_keys(self, mp3_fixture):
        result = compress_mp3(mp3_fixture, target_bitrate="64k")
        assert set(result.keys()) >= {"output_path", "did_compress", "original_size", "compressed_size"}
