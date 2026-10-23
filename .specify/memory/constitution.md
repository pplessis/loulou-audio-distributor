# loulou-audio-distributor Constitution

## Core Principles

### I. Simplicité orientée usage familial

L'application a un objectif principal : permettre à un enfant d'écouter des chapitres audio de livres pour s'endormir, en toute autonomie et sans friction. Toute fonctionnalité doit être justifiée par cet usage. Pas d'authentification lourde ni de fonctionnalités multi-utilisateurs sauf besoin explicite. YAGNI strict : on n'ajoute que ce qui sert l'expérience d'écoute ou son alimentation (ajout de livres). L'outil de synchronisation (`sync_tool/`) est un outil d'administration pour le parent ; il ne doit jamais alourdir l'expérience de l'enfant.

### II. Contrats de données stables (métadonnées JSON)

Les métadonnées des livres et chapitres (JSON dans `app/books/metadata/`) forment un contrat explicite entre le stockage, le backend Flask, le lecteur audio et `sync_tool/`. Le schéma de référence comprend : `title`, `author`, `chapters`, `duration`, `cover`, `chapters_list[{id, title, audio}]`. Tout changement de schéma doit être rétrocompatible ou versionné, documenté dans `specs/` et couvert par un test de contrat (`tests/contract/`) avant toute implémentation. Le contrat s'applique aussi au journal JSON Lines de `sync_tool` (événements : scan, upload, erreur, résumé) et à ses options CLI.

### III. Test-First (NON-NÉGOCIABLE)

Toute fonctionnalité ou correctif suit le cycle TDD : écrire le test → le faire valider → constater l'échec (Red) → implémenter (Green) → refactorer. Les tests de contrat (`tests/contract/`) valident les interfaces (routes Flask, format JSON des métadonnées, format du journal, options CLI). Les tests d'intégration (`tests/integration/`) valident les parcours bout en bout (lister les livres, lire un chapitre, streaming audio, synchronisation d'un répertoire).

### IV. Tests d'intégration réalistes (stockage cloud, streaming, APIs externes)

Toute fonctionnalité touchant au stockage cloud (OneDrive pour la diffusion web, Google Drive pour la synchronisation), au streaming audio, à la compression ffmpeg ou à l'API OpenLibrary doit être couverte par au moins un test d'intégration réaliste, pas seulement des mocks. Les tests dépendant de ressources externes sont isolés par marqueurs Pytest :

- `@pytest.mark.live` : API OpenLibrary réelle (internet requis)
- `@pytest.mark.drive` : credentials Google Drive requis
- `@pytest.mark.slow` : tests longs (compression sur 10+ fichiers)

Ces marqueurs doivent être documentés et ne doivent pas bloquer la suite par défaut. Les changements de contrat exigent un test de contrat mis à jour en priorité.

### V. Simplicité de déploiement (Vercel-first)

L'application web cible un déploiement serverless via Vercel (`vercel.json`). Toute dépendance ou choix d'architecture du backend doit rester compatible : pas d'état serveur lourd, pas de processus long-running, pas de dépendance système (ex. ffmpeg) dans l'app déployée. Les dépendances Python restent minimales et déclarées dans `requirements.txt`.

### VI. Séparation app web / outil de synchronisation

`sync_tool/` est un outil CLI local (Python 3.11+) exécuté hors Vercel. Il ne doit pas être importé par l'app Flask ni alourdir son déploiement. Ses dépendances (ffmpeg, clients Drive) sont isolées de celles de l'app. Ses comportements à risque sont opt-in ou désactivables : compression MP3 désactivée par défaut, validation des métadonnées désactivable (`--no-metadata-validation`). Il doit être idempotent (relancer une synchronisation ne duplique pas les fichiers) et journaliser de façon structurée (JSON Lines).

## Contraintes techniques

- **Backend** : Python / Flask, dans `app/` (`app.py` pour l'initialisation, `routes.py` pour les routes, `config.py` pour la configuration, `templates/`, `static/`, `books/metadata/`, `books/covers/`).
- **Versions Python** : 3.8+ minimum pour l'app web ; 3.11+ pour `sync_tool`. Toute montée de version est documentée.
- **Stockage** : MP3 hébergés dans le cloud (OneDrive, liens de partage publics pour la lecture web ; Google Drive pour la synchronisation). Les métadonnées JSON sont versionnées dans le dépôt.
- **Dépendances** : déclarées dans `requirements.txt` (racine et `app/`), justifiées et légères.
- **Secrets** : clés API, tokens et credentials (ex. `ONEDRIVE_API_KEY`, credentials Google Drive) ne sont jamais committés ; ils passent par variables d'environnement (Vercel) ou fichiers ignorés par git.
- **Vie privée** : aucune donnée sensible ou personnelle d'enfant ne transite ni n'est journalisée en clair. Les journaux de synchronisation ne contiennent que des informations techniques (chemins, statuts, erreurs).
- **Accessibilité** : interface utilisable par un enfant (navigation minimale, lecteur simple, couvertures visuelles, pas de dépendance à la lecture pour naviguer si possible). Les fonctions d'aide à l'endormissement (minuterie, etc.) restent simples et optionnelles.
- **Liens publics** : les liens OneDrive étant publics, ne diffuser que du contenu dont l'usage familial est légitime et ne pas exposer le site largement.

## Workflow de développement

- Toute nouvelle fonctionnalité démarre par une spécification dans `specs/` (workflow speckit : `/specify` → `/plan` → `/tasks` → implémentation).
- Les tests de contrat sont écrits avant les tests d'intégration, eux-mêmes avant le code applicatif.
- Toute PR doit démontrer que `pytest tests/` passe (hors marqueurs `live`/`drive` si les credentials sont indisponibles, à signaler dans la PR).
- Les changements de schéma JSON, de routes Flask, de format de journal ou d'options CLI sont signalés explicitement dans la description de la PR.
- Le `README.md` est mis à jour avec toute modification d'installation, d'utilisation ou de structure du projet.

## Governance

Cette constitution prévaut sur toute pratique ad hoc. Toute dérogation (notamment au Test-First ou à la stabilité des contrats) doit être justifiée explicitement dans la spec ou le plan concerné et documentée comme complexité assumée.

Les amendements exigent : documentation du changement, justification et mise à jour de la version ci-dessous. `AGENTS.md` et `.specify/` servent de guide opérationnel aux agents de développement.

**Version**: 1.1.0 | **Ratifiée**: 2026-09-13 | **Dernière modification**: 2026-10-23