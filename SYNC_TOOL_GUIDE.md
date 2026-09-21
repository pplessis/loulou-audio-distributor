# Guide d'utilisation — `sync_tool`

Ce guide explique comment utiliser l'outil de synchronisation `sync_tool` pour indexer, compresser (optionnel) et valider les métadonnées de ta bibliothèque d'audiolivres.

---

## Qu'est-ce que `sync_tool` ?

`sync_tool` est un outil en ligne de commande (CLI) qui :

1. **Scanne** un dossier contenant tes audiolivres (dossiers avec des fichiers `.mp3`)
2. **Génère un journal structuré** (JSON Lines) de toutes les opérations
3. **Compresse les MP3** avant traitement (optionnel, désactivé par défaut)
4. **Valide les métadonnées** (titre, auteur, couverture) via l'API OpenLibrary (optionnel)
5. **Crée des fichiers JSON** dans `app/books/metadata/` pour chaque livre détecté

---

## Prérequis

- **Python 3.11+**
- **`ffmpeg` installé** et accessible dans le `PATH` (nécessaire uniquement si tu utilises la compression)
- **Dépendances Python** installées :

```bash
pip install -r requirements.txt
```

> Si tu es sur **Python 3.13**, le paquet `audioop-lts` est inclus automatiquement dans `requirements.txt` pour assurer la compatibilité avec `pydub`.

### Vérifier ffmpeg

```bash
ffmpeg -version
```

Si ce n'est pas installé :
- **macOS** : `brew install ffmpeg`
- **Ubuntu/Debian** : `sudo apt-get install ffmpeg`

---

## Organisation de tes fichiers audio

`sync_tool` attend une structure de dossiers simple :

```
/mon_dossier_audiolivres/
├── Antoine de Saint-Exupéry - Le Petit Prince/
│   ├── chapitre-01.mp3
│   ├── chapitre-02.mp3
│   └── chapitre-03.mp3
├── Roald Dahl - Coup de gigot/
│   ├── partie-01.mp3
│   └── partie-02.mp3
└── Alice au pays des merveilles/
    ├── ch1.mp3
    └── ch2.mp3
```

### Règles de détection

- Chaque **sous-dossier** qui contient au moins un fichier `.mp3` est considéré comme un livre
- Le nom du dossier peut être au format **`Auteur - Titre`** (recommandé)
- Si le nom ne contient pas ` - `, tout le nom est utilisé comme **titre** et l'**auteur** reste vide
- L'identifiant du livre (`book_id`) est dérivé du titre : tout en minuscules, espaces remplacés par des tirets (`le-petit-prince`)

---

## Commandes de base

### 1. Synchronisation simple (journal + index)

```bash
python -m sync_tool /chemin/vers/mon_dossier_audiolivres --log-path /tmp/sync.log
```

**Ce que ça fait :**
- Scanne le dossier
- Écrit un journal structuré dans `/tmp/sync.log`
- Génère/ met à jour les fichiers JSON dans `app/books/metadata/`
- Valide les métadonnées via OpenLibrary (par défaut)

**Exemple de sortie dans le log :**
```json
{"timestamp": "2026-09-20T08:30:00+00:00", "level": "INFO", "source": "scan", "audiobook_id": null, "event_type": "scan_start", "message": "Scanning /chemin/vers/mon_dossier_audiolivres"}
{"timestamp": "2026-09-20T08:30:01+00:00", "level": "INFO", "source": "upload", "audiobook_id": "le-petit-prince", "event_type": "file_uploaded", "message": "chapitre-01.mp3"}
{"timestamp": "2026-09-20T08:30:02+00:00", "level": "INFO", "source": "scan", "audiobook_id": null, "event_type": "summary", "message": "Processed 2 audiobooks, 5 files uploaded, 0 errors"}
```

---

### 2. Avec compression MP3

```bash
python -m sync_tool /chemin/vers/mon_dossier_audiolivres \
  --compress \
  --compression-level 64k \
  --log-path /tmp/sync.log
```

**Ce que ça fait :**
- Avant chaque opération sur un fichier MP3, il est re-compressé à **64 kbps**
- Si le fichier compressé est plus gros que l'original, l'original est conservé (et un avertissement est loggué)
- Le niveau par défaut est `64k` (modifiable : `32k`, `96k`, `128k`, etc.)

> La compression est **désactivée par défaut** pour préserver la qualité audio originale.

---

### 3. Sans validation de métadonnées

```bash
python -m sync_tool /chemin/vers/mon_dossier_audiolivres \
  --no-metadata-validation \
  --log-path /tmp/sync.log
```

**Ce que ça fait :**
- Désactive la recherche sur OpenLibrary
- Les fichiers JSON générés ne contiendront **pas** de champ `validation_status`
- Plus rapide si tu n'as pas besoin de récupérer les couvertures ou vérifier les titres

---

### 4. Avec un endpoint personnalisé

```bash
python -m sync_tool /chemin/vers/mon_dossier_audiolivres \
  --metadata-endpoint https://openlibrary.org/search.json \
  --log-path /tmp/sync.log
```

Par défaut, l'outil utilise déjà `https://openlibrary.org/search.json`. Tu peux changer ce endpoint si tu as une autre source de métadonnées compatible.

---

### 5. Journal minimal (uniquement erreurs)

```bash
python -m sync_tool /chemin/vers/mon_dossier_audiolivres \
  --log-level ERROR \
  --log-path /tmp/sync.log
```

Niveaux disponibles : `INFO` (défaut), `WARN`, `ERROR`

---

## Options complètes

| Option | Description | Défaut |
|--------|-------------|--------|
| `source_dir` | Dossier racine contenant les audiolivres | *(obligatoire)* |
| `--log-path PATH` | Chemin du fichier de journal | `./sync.log` |
| `--log-level LEVEL` | Niveau de log : `INFO`, `WARN`, `ERROR` | `INFO` |
| `--compress` | Active la compression MP3 | désactivé |
| `--compression-level LEVEL` | Bitrate cible (ex: `64k`, `96k`) | `64k` |
| `--metadata-endpoint URL` | URL de l'API de métadonnées | `https://openlibrary.org/search.json` |
| `--no-metadata-validation` | Désactive la validation OpenLibrary | activé par défaut |

---

## Fichiers générés

### Journal (`--log-path`)

Fichier texte où chaque ligne est un objet JSON (format **JSON Lines**).

Types d'événements enregistrés :
- `scan_start` / `scan_end` — début et fin du scan
- `audiobook_processed` — un livre est en cours de traitement
- `folder_created` — dossier traité pour un livre
- `file_uploaded` — fichier MP3 traité
- `compression_result` — résultat de la compression (si activée)
- `compression_skipped` — compression ignorée car le fichier compressé était plus gros
- `error` — erreur sur un livre (le traitement continue quand même)
- `summary` — résumé final (nombre de livres, fichiers, erreurs)

### Index JSON (`app/books/metadata/`)

Pour chaque livre, un fichier `{book_id}.json` est créé ou mis à jour :

```json
{
  "title": "Le Petit Prince",
  "author": "Antoine de Saint-Exupery",
  "cover": "https://covers.openlibrary.org/b/id/10708272-L.jpg",
  "chapters": 3,
  "validation_status": "validated"
}
```

> Le champ `validation_status` n'apparaît **que** si la validation des métadonnées a été exécutée. Il est totalement optionnel pour préserver la compatibilité avec l'application Flask existante.

---

## Exemple complet pas à pas

### Étape 1 : Préparer tes fichiers

```bash
mkdir -p ~/MesAudiolivres/Antoine\ de\ Saint-Exupery\ -\ Le\ Petit\ Prince
# Copier tes fichiers MP3 dans ce dossier...
```

### Étape 2 : Exécuter la synchro complète

```bash
cd /chemin/vers/loulou-audio-distributor
python -m sync_tool ~/MesAudiolivres \
  --log-path /tmp/sync_$(date +%F).log \
  --compress \
  --compression-level 64k
```

### Étape 3 : Vérifier le journal

```bash
cat /tmp/sync_$(date +%F).log | python -m json.tool --compact
```

### Étape 4 : Vérifier les métadonnées générées

```bash
ls app/books/metadata/
cat app/books/metadata/le-petit-prince.json
```

### Étape 5 : Relancer l'application Flask

```bash
cd app
python app.py
```

Tes nouveaux livres apparaîtront sur la page d'accueil !

---

## Dépannage

### `ModuleNotFoundError: No module named 'audioop'` (Python 3.13)

```bash
pip install audioop-lts
```

Ce paquet est déjà dans `requirements.txt`, mais vérifie qu'il est bien installé.

### `ffmpeg not found` lors de la compression

Installe `ffmpeg` :
- macOS : `brew install ffmpeg`
- Ubuntu : `sudo apt install ffmpeg`

Puis vérifie :
```bash
which ffmpeg
```

### Le fichier de log ne se crée pas

Si le dossier parent n'existe pas, l'outil écrit les logs sur **`stderr`** (la console) au lieu d'un fichier, et la synchronisation continue quand même. C'est le comportement attendu pour éviter qu'une erreur de permission bloque tout le processus.

### Aucune couverture n'est trouvée

L'API OpenLibrary ne possède pas toutes les couvertures. Si un livre est bien reconnu (`validation_status: validated`) mais sans couverture, c'est normal. Tu peux toujours ajouter manuellement l'URL de couverture dans le fichier JSON généré.

---

## Besoin d'aide ?

Lance la commande d'aide intégrée :

```bash
python -m sync_tool --help
```

Sortie attendue :
```
usage: sync_tool [-h] [--log-path LOG_PATH] [--log-level {INFO,WARN,ERROR}]
                 [--compress] [--compression-level COMPRESSION_LEVEL]
                 [--metadata-endpoint METADATA_ENDPOINT]
                 [--no-metadata-validation]
                 source_dir

Audiobook drive sync tool

positional arguments:
  source_dir            Root directory containing audiobook folders

options:
  -h, --help            show this help message and exit
  --log-path LOG_PATH   File path for structured logs
  --log-level {INFO,WARN,ERROR}
                        Minimum log level
  --compress            Enable MP3 compression before upload
  --compression-level COMPRESSION_LEVEL
                        Bitrate/quality target (ffmpeg-compatible)
  --metadata-endpoint METADATA_ENDPOINT
                        Metadata API endpoint URL
  --no-metadata-validation
                        Disable metadata validation
```
