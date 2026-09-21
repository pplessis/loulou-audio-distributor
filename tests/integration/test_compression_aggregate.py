"""Aggregate compression test over >=10 MP3 files (T020 / SC-002)."""
import os

import pytest

from sync_tool.services.compression import compress_mp3


class TestCompressionAggregate:
    @pytest.mark.slow
    def test_at_least_95_percent_reduced_by_20_percent(self, mp3_corpus):
        reduced = 0
        total = 0
        for mp3_path in mp3_corpus:
            total += 1
            original_size = os.path.getsize(str(mp3_path))
            result = compress_mp3(str(mp3_path), target_bitrate="64k")
            assert result["did_compress"] is True
            compressed_size = result["compressed_size"]
            assert compressed_size > 0
            # Verify playability
            from pydub import AudioSegment
            seg = AudioSegment.from_mp3(result["output_path"])
            assert seg.duration_seconds > 0
            if compressed_size <= original_size * 0.80:
                reduced += 1
        assert total >= 10
        # Allow tiny tolerance: at least 95% reduced by >=20%
        assert reduced / total >= 0.95, f"Only {reduced}/{total} files reduced by >=20%"
