"""Metadata validation service (FR-007, FR-008, FR-009)."""
import logging
from typing import Optional

from sync_tool.models import Audiobook, DatabaseMatch, LogLevel, ValidationStatus
from sync_tool.services.openlibrary import OpenLibraryClient


class MetadataValidator:
    def __init__(self, client: OpenLibraryClient, logger=None):
        self.client = client
        self.logger = logger

    def validate(self, book: Audiobook) -> None:
        """Query OpenLibrary and populate missing metadata on the book in-place.

        On success: sets validation_status=validated, fills missing title/author/cover.
        On failure/no-match: sets validation_status=validation_failed and logs WARN.
        """
        try:
            match = self.client.search(title=book.title, author=book.author)
        except Exception as exc:
            self._log_warn(f"Metadata API unreachable for {book.title}: {exc}", book.book_id)
            book.validation_status = ValidationStatus.VALIDATION_FAILED
            return

        if match is None:
            self._log_warn(f"No metadata match found for {book.title}", book.book_id)
            book.validation_status = ValidationStatus.VALIDATION_FAILED
            return

        # Populate missing fields from match
        if not book.title:
            book.title = match.matched_title
        if not book.author and match.matched_author:
            book.author = match.matched_author
        if not book.cover and match.cover_url:
            book.cover = match.cover_url
        book.validation_status = ValidationStatus.VALIDATED

    def _log_warn(self, message: str, audiobook_id: Optional[str] = None) -> None:
        if self.logger is not None:
            self.logger.log_entry(
                LogLevel.WARN, "validate", "metadata_warning", message, audiobook_id
            )
