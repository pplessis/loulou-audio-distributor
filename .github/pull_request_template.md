<!-- Pull Request Template — loulou-audio-distributor
Conforme au Manifeste "Développement Assisté par LLM".
À remplir intégralement par l'auteur (LLM ou humain) avant toute revue. -->

## Description

<!-- Résumé court et factuel de la contribution.
Quel problème résout-elle ? Quel comportement ajoute-t-elle ou modifie-t-elle ?
Lier le ticket / l'issue concernée. -->

- Ticket / issue :
- Résumé :
- Portée (fichiers / modules touchés) :

## Type de changement

<!-- Cocher UNE case. -->

- [ ] Nouvelle fonctionnalité (feature)
- [ ] Correction de bug (fix)
- [ ] Refactoring (sans changement de comportement observable)
- [ ] Documentation uniquement
- [ ] Changement de contrat (schéma JSON des métadonnées, route Flask, format JSON)
- [ ] Changement de configuration de déploiement (vercel.json, env, serverless)
- [ ] Autre (préciser) :

## Checklist Tests & Preuves

<!-- Articles 1, 2, 3, 4 du Manifeste. -->

- [ ] Des **tests unitaires** ont été ajoutés ou mis à jour pour le code modifié
- [ ] Des **tests d'intégration** ont été ajoutés ou mis à jour (notamment sur les zones critiques — voir checklist ci-dessous)
- [ ] Des **tests de contrat** ont été ajoutés ou mis à jour si la PR touche un schéma JSON, une route Flask, ou un format de métadonnées
- [ ] Le **cycle Red-Green est démontré** dans le rapport d'exécution joint (trace de l'état Red avant implémentation puis Green après)
- [ ] Le **rapport d'exécution** complet est joint à cette PR (chemin ou lien ci-dessous dans la section dédiée)
- [ ] La **couverture sur le code modifié** est mesurée et reportée (pas seulement la couverture globale)
- [ ] Les **statuts par catégorie** (Contract / Unit / Integration) sont distingués dans le rapport, avec le nombre de tests passés / échoués / skip
- [ ] Les **échecs connus** (skip / xfail) sont justifiés explicitement dans le rapport
- [ ] Le rapport d'exécution contient la **commande exacte exécutée**, l'**environnement** (version Python, OS / CI, dépendances figées) et un **horodatage**
- [ ] Le rapport d'exécution est généré par l'outil de test lui-même — **aucune reformulation par le LLM** sans le texte source en annexe

## Checklist Sécurité & Données

<!-- Articles 8 et 7 du Manifeste. -->

- [ ] **Aucune donnée sensible** (identité enfant, contenu personnel, données réelles d'utilisateur) dans les rapports d'exécution, logs de test ou fixtures
- [ ] Les jeux de données de test utilisés sont **synthétiques ou anonymisés**
- [ ] Aucun secret (clé API, token, identifiant cloud) n'est commité ni loggé
- [ ] Aucune dépendance n'est ajoutée sans être déclarée et figée (pinned)

## Checklist Contrats & Déploiement

<!-- Articles 3 et 7 du Manifeste. -->

- [ ] Si la PR modifie un **schéma JSON de métadonnées**, un **test de contrat** a été écrit **avant** l'implémentation et validé
- [ ] Si la PR modifie une **route Flask** ou le **format JSON** retourné, un test d'intégration réel (pas mock seul) couvre l'appel HTTP et la réponse
- [ ] Si la PR modifie **`vercel.json`** ou la **configuration de déploiement**, une **vérification de compatibilité serverless** est jointe au rapport d'exécution
- [ ] Les **zones critiques** suivantes sont testées par au moins un **test d'intégration réel** (pas mock seul) :
  - [ ] **Stockage cloud** (upload, lecture, URLs signées)
  - [ ] **Streaming audio**
  - [ ] **Routes Flask** exposées
  - [ ] **Format JSON** des métadonnées
- [ ] Aucun test existant n'a été **supprimé ou désactivé** sans justification écrite dans la PR

## Dérogations documentées (si applicable)

<!-- Article 6 du Manifeste : ne remplir que si une dérogation existe. -->

- Dérogation n° :
- Principe concerné (article du Manifeste) :
- Justification :
- Ticket de dette technique associé :
- Validation humaine explicite et argumentée (relecteur, date) :

> **Rappel** : aucune dérogation ne peut concerner une zone critique sans validation humaine explicite et argumentée.

## Revue humaine obligatoire

<!-- Article 5 du Manifeste : le LLM ne s'auto-certifie pas. -->

- [ ] La PR a été **relue par un humain** avant demande de merge
- [ ] Nom du relecteur humain :
- [ ] Date de la revue :
- [ ] Commentaire du relecteur :

> **Rappel** : tous les tests passent n'est pas une certification suffisante. En cas de doute sur la fiabilité d'un rapport, relancer les tests manuellement avant validation.

## Rapport d'exécution joint

<!-- Article 4 du Manifeste : rapport généré par l'outil de test, jamais reformulé. -->

- Chemin ou lien vers le rapport :
- Format utilisé : `reports/TEMPLATE.md`
- Commande exacte exécutée (reproductible) :
- Horodatage d'exécution :
- Auteurs (LLM + relecteur humain) :

<!-- Fin du template -->
