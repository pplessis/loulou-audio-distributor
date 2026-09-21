<!-- Rapport d'exécution de tests — loulou-audio-distributor
Conforme à l'Article 4 du Manifeste "Développement Assisté par LLM".
Ce rapport est généré à partir de la sortie réelle de l'outil de test. Aucune reformulation par le LLM n'est acceptée : le texte source doit figurer en annexe. -->

# Rapport d'exécution de tests

- **PR / Contribution** :
- **Branche** :
- **Auteur LLM** (modèle / version) :
- **Relecteur humain** (nom, date de revue) :
- **Ticket / Issue** :
- **Date de génération** :

---

## 1. Commande exécutée

<!-- Doit être exacte, reproductible, copiable telle quelle. -->

```bash
# Commande complète exécutée (exemples : pytest, npm test, etc.)
```

```text
# Si plusieurs commandes ont été lancées, les lister ici dans l'ordre exact.
```

## 2. Environnement

<!-- Version Python, OS ou CI, dépendances figées (versions exactes, pinned). -->

- **Version Python** :
- **OS / CI** (ex : ubuntu-22.04, GitHub Actions run #…) :
- **Dépendances figées** (versions exactes, hashes si disponibles) :

```text
# Sortie de `pip freeze` / `poetry lock --no-update` / équivalent, collée telle quelle.
```

## 3. Résultat brut

<!-- Sortie complète du test runner, NON RÉSUMÉE par le LLM.
     Coller ici le bloc tel quel, sans paraphrase. -->

```text
# === SORTIE COMPLÈTE DU TEST RUNNER ===
# (coller ici, sans modification, sans coupe, sans reformulation)
```

> **Avertissement** : toute reformulation ou coupe de cette sortie invalide le rapport (Article 4 du Manifeste).

## 4. Couverture

### 4.1 Couverture globale

<!-- % global, lisible depuis l'outil. -->

- **Taux global** :
- **Source** (sortie de l'outil, ex : `coverage report`, `pytest-cov`) :

```text
# Sortie brute de l'outil de couverture (rapport global).
```

### 4.2 Couverture sur le code modifié

<!-- % ciblé sur les fichiers / lignes touchés par la PR — pas seulement le global. -->

- **Fichiers modifiés** :
- **Taux sur code modifié** :
- **Lignes non couvertes** (le cas échéant) :

```text
# Sortie brute ciblée (diff coverage / per-file coverage).
```

## 5. Statut par catégorie

<!-- Distinguer Contract / Unit / Integration, conformément à l'Article 4. -->

### 5.1 Tests de contrat (Contract)

- **Nombre total** :
- **Passés** :
- **Échoués** :
- **Skip / xfail** :

### 5.2 Tests unitaires (Unit)

- **Nombre total** :
- **Passés** :
- **Échoués** :
- **Skip / xfail** :

### 5.3 Tests d'intégration (Integration)

- **Nombre total** :
- **Passés** :
- **Échoués** :
- **Skip / xfail** :

### 5.4 Zones critiques — tests d'intégration réels (pas mock seul)

<!-- Article 3 du Manifeste : stockage cloud, streaming audio, routes Flask, format JSON des métadonnées. -->

- [ ] **Stockage cloud** (upload, lecture, URLs signées) — test d'intégration réel
- [ ] **Streaming audio** — test d'intégration réel
- [ ] **Routes Flask** exposées — test d'intégration réel
- [ ] **Format JSON** des métadonnées — test d'intégration réel

## 6. Échecs connus et justifications

<!-- Skip / xfail documentés, jamais silencieux. -->

| Test | Catégorie | Statut | Justification | Ticket de dette |
|------|-----------|--------|---------------|-----------------|
|      |           |        |               |                 |

## 7. Cycle Red-Green (Article 2)

<!-- Le rapport doit contenir la trace Red puis Green. Un test qui passe du premier coup est suspect sauf justification (ex : non-régression sur bug déjà corrigé). -->

### 7.1 État RED — avant implémentation

- **Date / horodatage Red** :
- **Test(s) en échec attendu** :
- **Commande exécutée (Red)** :
- **Extrait pertinent de la sortie Red** (preuve d'échec attendu) :

```text
# Sortie Red — partie montrant les échecs attendus.
```

### 7.2 État GREEN — après implémentation

- **Date / horodatage Green** :
- **Test(s) désormais passants** :
- **Commande exécutée (Green)** :
- **Extrait pertinent de la sortie Green** (preuve de réussite) :

```text
# Sortie Green — partie montrant les tests désormais passants.
```

### 7.3 Justification si premier coup (exception)

<!-- À remplir UNIQUEMENT si un test est passé sans passer par Red.
     Exemple acceptable : non-régression sur bug déjà corrigé. -->

- Justification :

## 8. Horodatage

- **Début d'exécution** :
- **Fin d'exécution** :
- **Durée totale** :
- **Identifiant de run CI** (si applicable) :

## 9. Signature / Auteurs

<!-- Le LLM ne s'auto-certifie pas (Article 5). -->

- **Auteur LLM** (modèle / version) :
- **Outil de test utilisé** (ex : `pytest`, `coverage`) :
- **Relecteur humain** (nom, date, commentaire) :

> **Rappel** : ce rapport est nécessaire mais non suffisant. Toute PR générée par un LLM doit être relue par un humain avant merge, même si tous les tests passent.

---

## Annexes

<!-- Joindre ici tout artefact supplémentaire non encore inclus : logs CI, captures, sorties d'outils de couverture complète, fichiers de fixtures anonymisés. -->

```text
# Annexe — artefacts complémentaires
```
