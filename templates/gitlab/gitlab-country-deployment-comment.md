## Déploiement Pays : {{template_name}} vers {{target_country_code}}

Ce déploiement active le traitement `{{template_name}}` pour le pays **{{target_country_code}}**.

**Ticket Jira associé :** [{{jira_id}}](lien_vers_le_ticket_jira)

---

### Fichiers Modifiés

- `composer/dags/dagfactory/dagfactory_{{target_country_code}}.yaml` : Ajout de la définition du DAG.
-   `custom_sql/tec__dc2__config.sql_tags.sql` : Ajout des variables SQL spécifiques au pays.

### Nouvelles Variables SQL

| Variable | Valeur pour `{{target_country_code}}` |
| :--- | :--- |
| `{{variable_1}}` | `{{valeur_1}}` |
| `{{variable_2}}` | `{{valeur_2}}` |

---
*Ce commentaire a été généré automatiquement par l'assistant IA.*
