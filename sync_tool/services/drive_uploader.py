"""Google Drive upload service for the sync tool."""
import os
import pickle
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Scopes : on ne demande que l'accès aux fichiers créés par l'application
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Fichier de sauvegarde du token (pour éviter de se reconnecter à chaque fois)
TOKEN_FILE = ".drive_token.json"
CREDENTIALS_FILE = "google-credentials.json"


def _get_credentials() -> Credentials:
    """Authenticate with Google Drive via OAuth2 (opens browser on first run)."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file not found: {CREDENTIALS_FILE}\n"
                    "Please download it from Google Cloud Console and place it here."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Sauvegarde le token pour les prochaines exécutions
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def _build_service():
    """Build the Google Drive service."""
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds, static_discovery=False)


def upload_file(file_path: str, folder_id: Optional[str] = None) -> Optional[dict]:
    """Upload a file to Google Drive and return its metadata (id, webViewLink, webContentLink).

    Args:
        file_path: Path to the local file to upload.
        folder_id: Optional Google Drive folder ID to upload into.

    Returns:
        dict with keys 'id', 'webViewLink', 'webContentLink' on success, or None on failure.
    """
    try:
        service = _build_service()
        file_name = os.path.basename(file_path)

        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink, webContentLink")
            .execute()
        )

        # Rendre le fichier public (lecture seule pour tout le monde)
        service.permissions().create(
            fileId=file["id"],
            body={"role": "reader", "type": "anyone"},
        ).execute()

        return file
    except HttpError as e:
        print(f"Drive upload error: {e}")
        return None


def create_folder(folder_name: str) -> Optional[dict]:
    """Create a folder on Google Drive and return its metadata."""
    try:
        service = _build_service()
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = (
            service.files()
            .create(body=file_metadata, fields="id, webViewLink")
            .execute()
        )
        # Rendre le dossier public
        service.permissions().create(
            fileId=folder["id"],
            body={"role": "reader", "type": "anyone"},
        ).execute()
        return folder
    except HttpError as e:
        print(f"Drive folder creation error: {e}")
        return None
    