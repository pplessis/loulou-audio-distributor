"""Base sync orchestration (extends feature 002 scan -> upload -> index flow).

This module defines the sync context contract that the enhancements integrate
with: a logger, config, and per-audiobook processing hook. The Drive upload
step itself is provided by the base feature (002); here it is a replaceable
function so stories are independently testable (research.md Task 3).
"""

import json
import os
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .models import Audiobook, LogLevel, SyncConfig, ValidationStatus

EVENT_SCAN_START = "scan_start"
EVENT_SCAN_END = "scan_end"
EVENT_FOLDER_CREATED = "folder_created"
EVENT_FILE_UPLOADED = "file_uploaded"
EVENT_ERROR = "error"
EVENT_SUMMARY = "summary"

SOURCE_SCAN = "scan"
SOURCE_UPLOAD = "upload"
SOURCE_COMPRESS = "compress"
SOURCE_VALIDATE = "validate"


@dataclass
class SyncContext:
    """Shared context threaded through a sync run."""

    config: SyncConfig
    logger: object
    source_dir: str
    upload_file: Callable[[str], bool] = lambda path: True
    metadata_validator: Optional[object] = None
    index_dir: Optional[str] = None
    errors: List[str] = field(default_factory=list)


def discover_audiobooks(source_dir: str) -> List[Audiobook]:
    """Scan a directory tree for audiobook folders (base feature FR-001/FR-002).

    A folder is considered an audiobook if it directly contains at least one
    `.mp3` file. Title/author are derived from the folder name "Author - Title".
    """
    audiobooks: List[Audiobook] = []
    if not os.path.isdir(source_dir):
        return audiobooks
    for entry in sorted(os.listdir(source_dir)):
        path = os.path.join(source_dir, entry)
        if not os.path.isdir(path):
            continue
        mp3s = [f for f in os.listdir(path) if f.lower().endswith(".mp3")]
        if not mp3s:
            continue
        book = _audiobook_from_folder(entry, sorted(mp3s))
        audiobooks.append(book)
    return audiobooks


def _audiobook_from_folder(folder_name: str, mp3s: List[str]) -> Audiobook:
    if " - " in folder_name:
        author, title = folder_name.split(" - ", 1)
    else:
        author, title = None, folder_name
    book_id = title.strip().lower().replace(" ", "-")
    return Audiobook(
        book_id=book_id,
        title=title.strip(),
        author=author.strip() if author else None,
        chapters=mp3s,
        folder_name=folder_name,
    )


def _write_book_index(book: Audiobook, index_dir: str) -> None:
    """Persist audiobook metadata with optional validation_status to JSON index."""
    os.makedirs(index_dir, exist_ok=True)
    path = os.path.join(index_dir, f"{book.book_id}.json")
    entry: dict = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                entry = json.load(f)
            except json.JSONDecodeError:
                entry = {}
    for k, v in (
        ("title", book.title),
        ("author", book.author),
        ("cover", book.cover),
    ):
        if v is not None:
            entry[k] = v
    entry["chapters"] = len(book.chapters)
    # Only write validation_status when validation actually ran (not PENDING default)
    if book.validation_status != ValidationStatus.PENDING:
        entry["validation_status"] = book.validation_status.value
    else:
        entry.pop("validation_status", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)


def run_sync(ctx: SyncContext, process_book: Optional[Callable[[Audiobook], None]] = None) -> int:
    """Execute a sync run, emitting structured log entries (FR-001).

    Returns the number of errors encountered. Process hooks run per audiobook
    (e.g., compression, validation) and may be injected for testability.
    """
    logger = ctx.logger
    config = ctx.config
    logger.log_entry(
        LogLevel.INFO, SOURCE_SCAN, EVENT_SCAN_START, f"Scanning {ctx.source_dir}"
    )

    audiobooks = discover_audiobooks(ctx.source_dir)
    uploaded_files = 0
    error_count = 0

    for book in audiobooks:
        try:
            logger.log_entry(
                LogLevel.INFO, SOURCE_SCAN, "audiobook_processed",
                f"Processing {book.title}", book.book_id,
            )
            logger.log_entry(
                LogLevel.INFO, SOURCE_UPLOAD, EVENT_FOLDER_CREATED,
                f"Creating Drive folder for {book.title}", book.book_id,
            )
            if process_book is not None:
                process_book(book)

            if config.metadata_validation_enabled and ctx.metadata_validator is not None:
                ctx.metadata_validator.validate(book)

            # Per-chapter compression and upload
            for chapter in book.chapters:
                chapter_path = os.path.join(ctx.source_dir, book.folder_name, chapter)
                upload_path = chapter_path
                if config.compression_enabled:
                    from .services.compression import compress_mp3
                    result = compress_mp3(chapter_path, target_bitrate=config.compression_level)
                    upload_path = result["output_path"]
                    if result["did_compress"]:
                        logger.log_entry(
                            LogLevel.INFO, SOURCE_COMPRESS, "compression_result",
                            (
                                f"Compressed {chapter}: {result['original_size']} -> "
                                f"{result['compressed_size']} bytes"
                            ),
                            book.book_id,
                        )
                    else:
                        logger.log_entry(
                            LogLevel.WARN, SOURCE_COMPRESS, "compression_skipped",
                            f"Compressed larger than original for {chapter}; kept original",
                            book.book_id,
                        )

                if ctx.upload_file(upload_path):
                    uploaded_files += 1
                    logger.log_entry(
                        LogLevel.INFO, SOURCE_UPLOAD, EVENT_FILE_UPLOADED,
                        f"Uploaded {chapter}", book.book_id,
                    )

            if ctx.index_dir is not None:
                _write_book_index(book, ctx.index_dir)

        except Exception as exc:  # keep processing other audiobooks (FR-015)
            error_count += 1
            ctx.errors.append(str(exc))
            logger.log_entry(
                LogLevel.ERROR, SOURCE_SCAN, EVENT_ERROR,
                f"Error processing {book.title}: {exc}", book.book_id,
            )

    logger.log_entry(
        LogLevel.INFO, SOURCE_SCAN, EVENT_SUMMARY,
        f"Processed {len(audiobooks)} audiobooks, "
        f"{uploaded_files} files uploaded, {error_count} errors",
    )
    logger.log_entry(LogLevel.INFO, SOURCE_SCAN, EVENT_SCAN_END, "Scan complete")
    return error_count
