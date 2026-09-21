"""MP3 compression service (FR-004, FR-005, FR-006)."""
import os
import tempfile
from typing import Optional

from pydub import AudioSegment


def compress_mp3(
    source_path: str,
    target_bitrate: str = "64k",
    output_path: Optional[str] = None,
) -> dict:
    """Compress an MP3 to target bitrate via pydub+ffmpeg.

    Returns a dict with:
        output_path (str): path to use (compressed or original)
        did_compress (bool): True if a new compressed file was produced and used
        original_size (int): size of source file in bytes
        compressed_size (int): size of output file in bytes
    """
    original_size = os.path.getsize(source_path)

    seg = AudioSegment.from_mp3(source_path)

    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
    else:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    seg.export(output_path, format="mp3", bitrate=target_bitrate)
    compressed_size = os.path.getsize(output_path)

    if compressed_size >= original_size:
        # Edge case: compressed output is larger than original → keep original
        os.remove(output_path)
        return {
            "output_path": source_path,
            "did_compress": False,
            "original_size": original_size,
            "compressed_size": original_size,
        }

    return {
        "output_path": output_path,
        "did_compress": True,
        "original_size": original_size,
        "compressed_size": compressed_size,
    }
