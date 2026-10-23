# 🤖 Agents OpenCode

Ce dossier définit les agents IA du projet. Chaque fichier `.md` correspond à un agent : son nom est celui du fichier, sa configuration est dans l'en-tête YAML et son prompt système dans le corps du fichier.

## Vue d'ensemble

| Agent        | Mode     | Rôle                                               | Modifie les fichiers | Bash                                                     |
| ------------ | -------- | -------------------------------------------------- | -------------------- | -------------------------------------------------------- |
| **build**    | primary  | Implémente et modifie le code                      | ✅ Oui                | ✅ (commandes risquées : confirmation)                    |
| **plan**     | primary  | Conçoit l'architecture et le plan d'implémentation | ❌ Non                | 🔒 Lecture seule                                         |
| **ask**      | primary  | Répond aux questions sur le codebase               | ❌ Non                | 🔒 Lecture seule                                         |
| **debug**    | primary  | Diagnostique les bugs et trouve la cause racine    | ⚠️ Sur accord        | ⚠️ Tests et lecture autorisés, le reste sur confirmation |
| **explore**  | subagent | Localise rapidement fichiers et symboles           | ❌ Non                | 🔒 Recherche seule                                       |
| **reviewer** | subagent | Relit un diff (bugs, sécurité, performance)        | ❌ Non                | 🔒 `git diff` / `git status`                             |

## Utilisation

* **Tab** : passer d'un agent principal à l'autre (build → plan → ask → debug).
* **`@explore`, `@reviewer`** : appeler un sous-agent dans un message.
* **`opencode --agent <nom>`** : démarrer directement avec un agent.
* **`opencode agent list`** : vérifier que les agents sont bien chargés.

## Workflow recommandé

```
ask  →  plan  →  build  →  @reviewer
                   ↑
                 debug   (en cas de bug ou de régression)
```

1. **ask** : comprendre le code existant.
2. **plan** : produire un plan étape par étape et le valider.
3. **build** : exécuter le plan, puis lancer lint, typecheck et tests.
4. **@reviewer** : relire le diff avant le commit.
5. **debug** : reproduire, formuler des hypothèses, trouver la cause racine, corriger et ajouter un test de non-régression.

## Permissions

Les agents utilisent le système `permission` d'OpenCode :

* `allow` : l'action est exécutée sans confirmation.
* `ask` : OpenCode demande votre confirmation.
* `deny` : l'action est interdite.

Les motifs bash (par exemple `"git push*": ask`) donnent un contrôle commande par commande, et la règle `"*"` sert de valeur par défaut.

## Paramètres clés

| Champ         | Rôle                                                                         |
| ------------- | ---------------------------------------------------------------------------- |
| `description` | Affichée dans l'interface ; sert aussi à choisir quand appeler un sous-agent |
| `mode`        | `primary` (accessible via Tab) ou `subagent` (appelé avec `@`)               |
| `temperature` | 0.1 pour l'analyse, 0.2 à 0.3 pour l'implémentation et la conception         |
| `steps`       | Nombre maximal d'itérations, pour éviter les boucles                         |
| `model`       | (Facultatif) modèle propre à l'agent                                         |
| `permission`  | Droits d'édition, bash et webfetch                                           |

### Modèle conseillé par agent

* **plan / debug** : le modèle le plus fort en raisonnement
* **build** : un modèle performant en code
* **ask / explore / reviewer** : un modèle rapide et peu coûteux

## Ajouter un agent

1. Créez `<nom>.md` dans ce dossier (ou lancez `opencode agent create`).
2. Ajoutez l'en-tête YAML (`description`, `mode`, `permission`…).
3. Rédigez le prompt avec cette structure : **Rôle**, **Méthode**, **Contraintes**, **Format de sortie**.
4. Vérifiez qu'il est chargé avec `opencode agent list`.

## Bonnes pratiques

* Gardez à jour le fichier `AGENTS.md` à la racine : commandes du projet, conventions et architecture. Tous les agents le lisent.
* Appliquez le principe du moindre privilège : n'accordez à chaque agent que les droits dont il a besoin.
* Des prompts courts et structurés donnent de meilleurs résultats que de longs prompts vagues.
* Versionnez ce dossier avec Git pour que toute l'équipe partage les mêmes agents.

```bash 
opencode mcp auth jira

opencode mcp list             # le serveur jira doit être "connected" 
opencode agent list           # l'agent jira doit apparaître
```

## Compatibilité

Les champs `permission` et `steps` nécessitent une version récente d'OpenCode. Sur une version plus ancienne, utilisez `maxSteps` et `tools: { write: false, ... }`. Vérifiez votre version avec `opencode --version`.

## Files and Folders for AI Configuration & Project

### Standards & Guidelines (12 files)
- [standards/context-loading-policy.md](../standards/context-loading-policy.md)
- [standards/api-conventions.md](../standards/api-conventions.md)
- [standards/windows-dev.md](../standards/windows-dev.md)
- [standards/linux-dev.md](../standards/linux-dev.md)
- [standards/coding-standards.md](../standards/coding-standards.md)
- [standards/README.md](../standards/README.md)
- [standards/testing.md](../standards/testing.md)
- [standards/security/secrets-management.md](../standards/security/secrets-management.md)
- [standards/security/dependency-policy.md](../standards/security/dependency-policy.md)
- [standards/security/security-rules.md](../standards/security/security-rules.md)
- [standards/code-style.md](../standards/code-style.md)
- [standards/global-rules.md](../standards/global-rules.md)

### AI Configuration (18 files)
- .ai/commands/speckit.tasks.md through .ai/commands/speckit.checklist.md (11 files)
- [.ai/README.md](../.ai/README.md)
- .ai/agents/ask.md, .ai/agents/review.md, .ai/agents/plan.md, .ai/agents/build.md, .ai/agents/explore.md, .ai/agents/jira.md, .ai/agents/debug.md

### Specification Templates (5 files)
- .specify/templates/plan-template.md through .specify/templates/checklist-template.md

### Documentation (3 files)
- doc/YR-Ai4Codes/README.md
- doc/YR-Ai4Codes/EXTENSION_LIFECYCLE.md

### Templates (4 files)
- templates/jira/jira-country-deployment-comment.md
- templates/jira/jira-feedback-comment.md
- templates/markdown/markdom_standards.md
- templates/changelog.md
- templates/gitlab/gitlab-mr-review-comment.md
- templates/gitlab/gitlab-country-deployment-comment.md

### Project Files (11 files)
- [AGENTS.md](../AGENTS.md)
- [CHANGELOG.md](../CHANGELOG.md)
- .github/copilot-instructions.md
- .specify/memory/constitution.md
