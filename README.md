# Loulou Audio Distributor 📚🎧

Un site web Flask pour distribuer des chapitres audio de livres afin d'aider un enfant à s'endormir. Le projet inclut :

- **Un lecteur audio intégré** pour écouter les chapitres directement sur le site.
- **Un système de métadonnées JSON** pour décrire les livres et leurs chapitres.
- **Un stockage cloud** via OneDrive pour les fichiers MP3.
- **Déploiement facile** sur Vercel.

---

## 📁 Structure du Projet

```
loulou-audio-distributor/
│
├── /app/                          # Application Flask
│   ├── static/                    # Fichiers statiques (CSS, JS, images)
│   │   ├── audio/                 # Fichiers MP3 (optionnel pour test)
│   │   ├── css/
│   │   │   └── style.css         # Styles pour le lecteur audio
│   │   ├── js/
│   │   │   └── player.js         # Script pour le lecteur audio
│   │   └── images/               # Images de couvertures
│   │
│   ├── templates/                 # Modèles Flask (HTML)
│   │   ├── base.html              # Modèle de base
│   │   ├── index.html             # Page d'accueil (liste des livres)
│   │   ├── book.html              # Page d'un livre (lecteur audio)
│   │   └── upload.html            # Page pour ajouter un livre (optionnel)
│   │
│   ├── books/
│   │   ├── metadata/             # Métadonnées JSON des livres
│   │   │   ├── livre1.json
│   │   │   └── ...
│   │   └── covers/               # Images de couvertures
│   │
│   ├── app.py                     # Application Flask principale
│   ├── routes.py                  # Routes de l'application
│   ├── config.py                  # Configuration (OneDrive, etc.)
│   └── requirements.txt           # Dépendances Python
│
├── vercel.json                    # Configuration pour Vercel
└── README.md                      # Documentation
```

---

## 🚀 Fonctionnalités

### 1️⃣ **Métadonnées des Livres (JSON)**
Chaque livre est décrit par un fichier JSON dans `/app/books/metadata/` avec cette structure :

```json
{
  "title": "Le Petit Prince",
  "author": "Antoine de Saint-Exupéry",
  "chapters": 27,
  "duration": "5 heures",
  "cover": "/static/images/covers/le-petit-prince.jpg",
  "chapters_list": [
    {"id": 1, "title": "Chapitre 1", "audio": "https://1drv.ms/u/s!AurlExemple/Chapitre1?e=123456"},
    {"id": 2, "title": "Chapitre 2", "audio": "https://1drv.ms/u/s!AurlExemple/Chapitre2?e=123456"},
    ...
  ]
}
```

- **`audio`** : Lien public OneDrive vers le fichier MP3 (partage public).
- **`cover`** : Chemin vers l'image de couverture (stockée dans `/static/images/covers/`).

---

### 2️⃣ **Lecteur Audio Intégré**
- Une page `book.html` affiche la couverture, les métadonnées, et un lecteur audio HTML5.
- Le lecteur utilise la balise `<audio>` avec des contrôles personnalisés (play/pause, barre de progression).
- Exemple de code pour le lecteur (dans `templates/book.html`) :

```html
<audio id="audioPlayer" controls>
    <source src="{{ chapter.audio }}" type="audio/mpeg">
</audio>
<script src="{{ url_for('static', filename='js/player.js') }}"></script>
```

---

### 3️⃣ **Stockage Cloud (OneDrive)**
- Les fichiers MP3 sont stockés dans **OneDrive** avec un **partage public**.
- Exemple de lien OneDrive public : `https://1drv.ms/u/s!AurlExemple/Chapitre1?e=123456`
- Pour obtenir un lien public :
  1. Uploade le fichier MP3 sur OneDrive.
  2. Clique droit sur le fichier → **Partager** → **Créer un lien de partage**.
  3. Sélectionne **Public** (ou **Toute personne ayant le lien**).
  4. Copie le lien généré et utilise-le dans le fichier JSON.

---

### 4️⃣ **Déploiement sur Vercel**
- Le fichier `vercel.json` configure le déploiement pour Flask.
- Déploiement automatique depuis GitHub :
  1. Lie ton compte Vercel à ton dépôt GitHub.
  2. Vercel détectera automatiquement la configuration Flask.
  3. Ajoute les variables d'environnement nécessaires (ex: `ONEDRIVE_API_KEY` si tu utilises l'API).

---

## 🛠️ Prérequis

- Python 3.8+
- Flask (`pip install flask`)
- Un compte **Vercel** (gratuit)
- Un compte **OneDrive** (pour stocker les fichiers MP3)

---

## 📥 Installation et Lancement

### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/pplessis/loulou-audio-distributor.git
cd loulou-audio-distributor
```

### 2️⃣ Installer les dépendances
```bash
touch app/requirements.txt
echo "Flask==2.3.3" >> app/requirements.txt
pip install -r app/requirements.txt
```

### 3️⃣ Configurer les métadonnées
- Ajoute un fichier JSON dans `/app/books/metadata/` (voir exemple ci-dessus).
- Uploade les fichiers MP3 sur OneDrive et mets à jour les liens dans le JSON.
- Place les images de couverture dans `/app/static/images/covers/`.

### 4️⃣ Lancer l'application localement
```bash
cd app
python app.py
```
- L'application sera disponible à l'adresse : [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 5️⃣ Déployer sur Vercel
1. Pousse ton code sur GitHub (si ce n'est pas déjà fait).
2. Va sur [Vercel](https://vercel.com/) et crée un nouveau projet.
3. Sélectionne ton dépôt GitHub.
4. Vercel détectera automatiquement la configuration Flask.
5. Déploie !

---

## 🎯 Exemple de Métadonnées JSON

Voici un exemple complet pour un livre :

```json
{
  "title": "Le Petit Prince",
  "author": "Antoine de Saint-Exupéry",
  "chapters": 27,
  "duration": "5 heures",
  "cover": "/static/images/covers/le-petit-prince.jpg",
  "chapters_list": [
    {
      "id": 1,
      "title": "Chapitre 1 : L'atterrissage",
      "audio": "https://1drv.ms/u/s!AurlExemple/Chapitre1?e=123456"
    },
    {
      "id": 2,
      "title": "Chapitre 2 : La rencontre avec le renard",
      "audio": "https://1drv.ms/u/s!AurlExemple/Chapitre2?e=123456"
    },
    {
      "id": 3,
      "title": "Chapitre 3 : Apprivoiser",
      "audio": "https://1drv.ms/u/s!AurlExemple/Chapitre3?e=123456"
    }
  ]
}
```

---

## 🔧 Personnalisation

- **Ajouter un livre** :
  1. Crée un fichier JSON dans `/app/books/metadata/`.
  2. Uploade les chapitres sur OneDrive et mets à jour les liens.
  3. Ajoute l'image de couverture dans `/app/static/images/covers/`.

- **Personnaliser le lecteur audio** :
  Modifie le fichier `static/js/player.js` pour ajouter des fonctionnalités (lecture aléatoire, minuterie, etc.).

---

## 📄 Licence

Ce projet est sous licence **MIT**. Tu es libre de l'utiliser, le modifier et le partager.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvre une **issue** ou soumets une **pull request** pour améliorer le projet.

---

## 📧 Contact

Pour toute question, tu peux me contacter via GitHub.

---

**Bon développement !** 🎉
