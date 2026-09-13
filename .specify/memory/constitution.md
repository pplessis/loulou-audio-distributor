# loulou-audio-distributor Constitution

## Core Principles

### I. Simplicité orientée usage familial
L'application sert un unique objectif : permettre à un enfant d'écouter des chapitres audio de livres pour s'endormir, en toute autonomie et sans friction. Toute fonctionnalité doit être justifiée par cet usage ; pas de complexité superflue (pas d'authentification lourde, pas de fonctionnalités multi-utilisateurs sauf besoin explicite). YAGNI strict : on n'ajoute que ce qui sert directement l'expérience d'écoute.

### II. Contrats de données stables (métadonnées JSON)
Les métadonnées des livres/chapitres (JSON) constituent un contrat explicite entre le stockage, le backend Flask et le lecteur audio. Tout changement de schéma JSON doit être rétrocompatible ou versionné, documenté dans `specs/`, et couvert par un test de contrat (`tests/contract/`) avant toute implémentation.

### III. Test-First (NON-NÉGOCIABLE)
Toute nouvelle fonctionnalité ou correctif suit le cycle TDD : écrire le test → le faire valider → constater l'échec (Red) → implémenter (Green) → refactorer. Les tests de contrat (`tests/contract/`) valident les interfaces (API Flask, format JSON des métadonnées) ; les tests d'intégration (`tests/integration/`) valident les parcours utilisateur bout en bout (lister les livres, lire un chapitre, streaming audio).

### IV. Intégration Test réelle du stockage cloud et du streaming audio
Toute fonctionnalité touchant à l'intégration avec le stockage cloud (upload, lecture, URLs signées) ou au streaming audio doit être couverte par un test d'intégration réaliste, pas seulement des mocks. Les changements de contrat (routes Flask, format de réponse, structure des métadonnées) exigent un test de contrat mis à jour en priorité.

### V. Simplicité de déploiement (Vercel-first)
Le projet cible un déploiement serverless simple via Vercel. Toute dépendance ou choix d'architecture doit rester compatible avec ce mode de déploiement (pas d'état serveur lourd, pas de dépendance à un processus long-running non supporté). Les dépendances Python doivent rester minimales et documentées dans `requirements.txt`.

## Contraintes techniques

- **Backend** : Python / Flask, structuré en `app/` (routes dans `app.py`, `models/` pour les données, `services/` pour la logique métier, `templates/` pour le rendu HTML, `books/` pour le contenu).
- **Déploiement** : Vercel, configuration dans `vercel.json`.
- **Dépendances** : doivent être déclarées dans `requirements.txt` (racine et `app/`) ; toute nouvelle dépendance doit être justifiée et légère.
- **Données** : les chapitres audio et leurs métadonnées (JSON) sont stockés en cloud ; aucune donnée sensible ou personnelle d'enfant ne doit transiter ou être journalisée en clair.
- **Accessibilité et simplicité d'usage** : l'interface doit rester utilisable par un enfant (navigation minimale, lecteur audio simple, pas de dépendance à la lecture pour naviguer si possible).

## Workflow de développement

- Toute nouvelle fonctionnalité démarre par une spécification dans `specs/` (via le workflow speckit : `/specify` → `/plan` → `/tasks` → implémentation).
- Les tests de contrat sont écrits avant les tests d'intégration, eux-mêmes écrits avant le code applicatif.
- Toute pull request doit démontrer que les tests (`tests/contract/`, `tests/integration/`) passent avant merge.
- Les changements de schéma JSON ou de routes Flask exposées doivent être signalés explicitement dans la description de la PR.

## Governance

Cette constitution prévaut sur toute pratique de développement ad hoc. Toute dérogation à un principe (notamment le Test-First ou la stabilité des contrats JSON) doit être justifiée explicitement dans la spec ou le plan concerné, et documentée comme complexité assumée.

Les amendements à cette constitution nécessitent : documentation du changement, justification, et mise à jour de la version ci-dessous. Utiliser `AGENTS.md` et `.specify/` pour le guidage opérationnel des agents de développement.

**Version**: 1.0.0 | **Ratifiée**: 2026-09-13 | **Dernière modification**: 2026-09-13