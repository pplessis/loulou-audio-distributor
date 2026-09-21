# Guide : Connecter Google Drive au sync_tool

Ce guide explique comment faire en sorte que le `sync_tool` uploade réellement tes fichiers MP3 sur Google Drive, et insère les liens publics dans les fichiers JSON de l'application.

---

## 1. Créer un projet Google Cloud (étapes obligatoires)

### 1.1. Accéder à Google Cloud Console

Va sur [https://console.cloud.google.com/](https://console.cloud.google.com/) avec ton compte Google.

### 1.2. Créer un nouveau projet
- Clique sur le sélecteur de projet (en haut à gauche)
- **New Project**
- Donne-lui un nom : `Loulou Audio Sync`

### 1.3. Activer l'API Google Drive
- Va dans **APIs & Services > Library**
- Cherche **Google Drive API**
- Clique sur **Enable**

### 1.4. Créer des identifiants OAuth2
- Va dans **APIs & Services > Credentials**
- Clique **+ Create Credentials > OAuth 2.0 Client ID**
- Sélectionne **Application type** : **Desktop app**
- Donne un nom : `Loulou Sync Desktop`
- Clique **Create**
- Télécharge le fichier JSON : clique sur l'icône de téléchargement à droite
- **Renomme ce fichier** en `google-credentials.json` et place-le à la racine du projet

### 1.5. Configurer l'écran de consentement
- Va dans **APIs & Services > OAuth consent screen**
- Si ce n'est pas déjà fait, choisis **External**
- Remplis les champs obligatoires (nom de l'app, email)
- Dans **Scopes**, clique sur **Add or Remove Scopes**
  - Ajoute : `.../auth/drive.file` (créer/modifier uniquement les fichiers créés par l'app)
- Dans **Test users**, ajoute ton email Google personnel
- **Enregistre**

> **Important** : tant que l'app reste en mode "Testing", seuls les utilisateurs test peuvent s'y connecter. C'est suffisant pour un usage personnel/familial.

---

## 2. Installer les dépendances Python

Le `requirements.txt` actuel ne contient pas les librairies Google. Ajoute-les :

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Puis ajoute cette ligne à ton `requirements.txt` :

```
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.1
```

---

## 3. Créer le service d'upload

Crée le fichier `sync_tool/services/drive_uploader.py` :

```python
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
```

---

## 4. Adapter le `sync_tool` pour utiliser Google Drive

Modifie `sync_tool/cli.py` :

```python
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
```

---

## 5. Stocker les liens dans les fichiers JSON

Actuellement, `sync_tool` génère un JSON simple (`title`, `author`, `cover`, `chapters`).
Pour que l'application puisse lire les fichiers depuis Google Drive, il faut aussi stocker le lien de chaque chapitre.

Modifie la fonction `_write_book_index` dans `sync_tool/sync.py` pour ajouter cette structure si les liens sont disponibles :

```python
# Dans la boucle for book in audiobooks:
#   après l'upload, on stockerait: book.chapter_links = { 'ch1.mp3': 'https://drive.google.com/...' }
#   et on utiliserait ça pour générer chapters_list
```

Un exemple de JSON attendu par l'app Flask :

```json
{
  "title": "Le Petit Prince",
  "author": "Antoine de Saint-Exupery",
  "cover": "https://covers.openlibrary.org/b/id/10708272-L.jpg",
  "chapters": 2,
  "chapters_list": [
    {"title": "Chapitre 1", "audio": "https://drive.google.com/file/d/ABC123/view"},
    {"title": "Chapitre 2", "audio": "https://drive.google.com/file/d/DEF456/view"}
  ]
}
```

---

## 6. Tester la connexion

Première exécution (ouvre le navigateur) :

```bash
cd loulou-audio-distributor
python -m sync_tool ~/MesAudiolivres --log-path /tmp/sync.log
```

- Un onglet de navigateur s'ouvrira pour te demander l'autorisation
- Choisis ton compte Google
- Accepte TOUTES les permissions
- Retourne au terminal : une fois authentifié, le token est sauvegardé dans `.drive_token.json`

**Prochaines exécutions** : la connexion est automatique (ton token est réutilisé) jusqu'à ce que tu révoques l'accès dans Google.

---

## 7. Vérifier l'upload dans Drive

Va sur [https://drive.google.com/](https://drive.google.com/), tu verras un dossier du nom du livre, et à l'intérieur les chapitres MP3. Chaque fichier est public (lien "Toute personne ayant le lien").

---

## Résumé des fichiers nécessaires

| Fichier | Description |
|---------|-------------|
| `google-credentials.json` | Tes credentials OAuth2 (ne le commite **jamais**) |
| `.drive_token.json` | Ton token de session (généré automatiquement, ne le commite **jamais**) |
| `requirements.txt` | Doit contenir les 3 librairies Google |
| `sync_tool/services/drive_uploader.py` | Code d'upload (à créer) |
| `sync_tool/cli.py` | Injecter `upload_file_to_drive` dans le SyncContext |

---

## Sécurité

> **⚠️ Ne jamais ajouter ces fichiers dans Git :**
> - `google-credentials.json`
> - `.drive_token.json`

Ils donnent accès à ton Google Drive. Ajoute-les dans le `.gitignore` :

```
google-credentials.json
.drive_token.json
```

---

## Besoin d'aide ?

Si tu veux que je **fasse toutes ces modifications dans le code** (fichier drive_uploader.py, modification du cli, ajout des chapitres dans le JSON, update du .gitignore), réponds-moi avec : **"Oui, implémente l'upload Drive"** et je m'occupe de tout !
