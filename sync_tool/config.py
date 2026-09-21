"""Configuration loading for the sync tool (CLI args / env) per contracts/cli.md."""

import argparse
import os

from .models import LogLevel, SyncConfig

DEFAULT_LOG_PATH = "sync.log"
DEFAULT_METADATA_ENDPOINT = "https://openlibrary.org/search.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sync_tool", description="Audiobook drive sync tool")
    parser.add_argument("source_dir", help="Root directory containing audiobook folders")
    parser.add_argument("--log-path", default=DEFAULT_LOG_PATH, help="File path for structured logs")
    parser.add_argument(
        "--log-level", default=LogLevel.INFO.value, choices=["INFO", "WARN", "ERROR"], help="Minimum log level"
    )
    parser.add_argument("--compress", action="store_true", help="Enable MP3 compression before upload")
    parser.add_argument("--compression-level", default="64k", help="Bitrate/quality target (ffmpeg-compatible)")
    parser.add_argument(
        "--metadata-endpoint", default=DEFAULT_METADATA_ENDPOINT, help="Metadata API endpoint URL"
    )
    parser.add_argument(
        "--no-metadata-validation", action="store_true", help="Disable metadata validation"
    )
    return parser


def load_config(argv=None) -> SyncConfig:
    """Build a SyncConfig from CLI args, falling back to env vars for defaults."""
    args = build_parser().parse_args(argv)

    log_path = args.log_path or os.environ.get("SYNC_LOG_PATH", DEFAULT_LOG_PATH)
    log_level = args.log_level or os.environ.get("SYNC_LOG_LEVEL", LogLevel.INFO.value)
    endpoint = args.metadata_endpoint or os.environ.get("SYNC_METADATA_ENDPOINT", DEFAULT_METADATA_ENDPOINT)

    return SyncConfig(
        log_path=log_path,
        log_level=LogLevel(log_level.upper()),
        compression_enabled=args.compress,
        compression_level=args.compression_level or "64k",
        metadata_api_endpoint=endpoint,
        metadata_validation_enabled=not args.no_metadata_validation,
    )


def parse_source_dir(argv=None) -> str:
    """Extract the source directory positional argument (contracts/cli.md)."""
    return build_parser().parse_args(argv).source_dir