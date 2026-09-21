"""CLI entry point for the sync tool (contracts/cli.md)."""

import os
import sys

from .config import load_config, parse_source_dir
from .services.logger import SyncLogger
from .services.openlibrary import OpenLibraryClient
from .services.metadata_validator import MetadataValidator
from .sync import SyncContext, run_sync


def main(argv=None) -> int:
    config = load_config(argv)
    source_dir = parse_source_dir(argv)
    index_dir = os.path.join("app", "books", "metadata")

    # --- Drive integration ---
    # Dictionnaire pour stocker les ids des dossiers créés (par titre de livre)
    def upload_file_to_drive(file_path: str, current_book=None) -> bool:
        """Upload callback injected into the sync context."""
        try:
            from .services.drive_uploader import upload_file as drive_upload
            from .services.drive_uploader import create_folder
        except ImportError:
            # Fallback si les librairies google ne sont pas installées
            print("[WARN] google-api-python-client not installed. Skipping upload.")
            return False

        # Stockage interne pour les dossiers créés
        if not hasattr(upload_file_to_drive, "folder_cache"):
            upload_file_to_drive.folder_cache = {}

        # Récupère le book_id au contexte
        book_id = current_book.book_id if current_book else None
        folder_id = upload_file_to_drive.folder_cache.get(book_id)

        if book_id and not folder_id:
            folder = create_folder(book_id)
            if folder:
                folder_id = folder["id"]
                upload_file_to_drive.folder_cache[book_id] = folder_id

        result = drive_upload(file_path, folder_id=folder_id)
        return result is not None

    # Adaptateur pour faire le lien entre sync.run_sync et l'upload
    # (le sync_tool actuel appelle upload_file avec juste le chemin du fichier,
    # on va stocker le livre courant dans une variable globale temporaire)
    _upload_state = {"current_book": None}

    def _per_file_upload(file_path: str) -> bool:
        return upload_file_to_drive(file_path, _upload_state.get("current_book"))

    with SyncLogger(config.log_path, config.log_level) as logger:
        validator = None
        if config.metadata_validation_enabled:
            client = OpenLibraryClient(config.metadata_api_endpoint)
            validator = MetadataValidator(client=client, logger=logger)

        ctx = SyncContext(
            config=config, logger=logger, source_dir=source_dir,
            index_dir=index_dir, metadata_validator=validator,
            upload_file=_per_file_upload,
        )

        # On utilise un hook process_book pour transmettre le livre courant à l'upload
        def _set_current_book(book):
            _upload_state["current_book"] = book

        return run_sync(ctx, process_book=_set_current_book)


if __name__ == "__main__":
    sys.exit(main())