# PDF Tools - Solution Professionnelle de Gestion PDF

![PDF Tools](https://img.shields.io/badge/PDF-Tools-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.1+-red)

[English Version](README_EN.md)

## 📋 Description

PDF Tools est une plateforme web professionnelle pour la gestion avancée de fichiers PDF. Elle offre des fonctionnalités de téléchargement massif, fusion intelligente et analyse automatique par intelligence artificielle.

## ✨ Fonctionnalités Principales

### 🔽 Téléchargeur & Zipper
- **Téléchargement massif** : Support pour 10,000+ documents simultanés
- **Retry automatique** : Logique de retry avec backoff exponentiel
- **Traitement parallèle** : 10 workers simultanés pour performances optimales
- **Timeout étendu** : 300 secondes par document
- **Compression ZIP** : Téléchargement direct des fichiers compressés

### 🔀 Fusionner PDFs avec Analyse Intelligente
- **Upload illimité** : Aucune restriction de taille, volume ou nombre de fichiers
- **Fusion robuste** : Combine plusieurs PDFs en un seul document
- **Analyse AI** : Extraction intelligente de texte et structure avec OpenRouter
- **Base de données Excel** : Génération automatique de données structurées
- **Métadonnées détaillées** : Extraction de titres, dates, entités, mots-clés

### 🤖 Analyse Intelligente (Nouveau)
- **Extraction de texte** : Analyse complète du contenu PDF
- **Reconnaissance de structure** : Identification du type de document
- **Extraction d'entités** : Détection d'organisations, personnes, dates
- **Génération de résumés** : Résumé automatique en 2-3 phrases
- **Champs personnalisés** : Extraction de données spécifiques

## 🚀 Installation

### Prérequis
- Python 3.11+
- Compte OpenRouter (pour analyse intelligente)

### Installation Locale

```bash
# Cloner le dépôt
git clone <votre-repo>
cd pdf-tools

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export SECRET_KEY="votre-clé-secrète"
export OPENROUTER_API_KEY="votre-clé-openrouter"

# Lancer l'application
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

### Déploiement sur Replit

1. Importer le projet sur Replit
2. Configurer les secrets dans l'interface Replit :
   - `SECRET_KEY`
   - `OPENROUTER_API_KEY`
3. Cliquer sur "Run"

Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour plus de détails.

## 🔧 Configuration

### Variables d'Environnement Requises

| Variable | Description | Requis |
|----------|-------------|--------|
| `SECRET_KEY` | Clé secrète Flask | Oui |
| `OPENROUTER_API_KEY` | Clé API OpenRouter pour analyse AI | Optionnel* |

*Si non configurée, l'analyse intelligente sera désactivée mais les autres fonctionnalités continueront de fonctionner.

### Obtenir une Clé OpenRouter

1. Créer un compte sur [OpenRouter.ai](https://openrouter.ai)
2. Aller dans Settings > API Keys
3. Créer une nouvelle clé API
4. Copier et ajouter dans vos secrets

## 📊 Architecture

```
pdf-tools/
├── app/
│   ├── routes/          # Routes Flask (downloader, merger, main)
│   ├── services/        # Logique métier
│   │   ├── pdf_downloader.py    # Téléchargement parallèle avec retry
│   │   ├── pdf_merger.py        # Fusion de PDFs
│   │   └── pdf_analyzer.py      # Analyse AI intelligente (NOUVEAU)
│   ├── templates/       # Templates HTML
│   └── utils/          # Utilitaires (storage, etc.)
├── instance/           # Dossier uploads
├── tmp/               # Fichiers temporaires
├── config.py          # Configuration
├── main.py           # Point d'entrée
└── requirements.txt  # Dépendances Python
```

## 🎯 Utilisation

### Télécharger & Zipper

1. Aller sur `/downloader`
2. Entrer une liste d'URLs de PDFs (une par ligne)
3. Cliquer sur "Commencer"
4. Télécharger le fichier ZIP généré

### Fusionner avec Analyse Intelligente

1. Aller sur `/merger`
2. Uploader un fichier ZIP contenant des PDFs
3. L'application va :
   - Extraire les PDFs du ZIP
   - Les fusionner en un seul document
   - Analyser le contenu avec AI
   - Générer un Excel avec analyse détaillée
4. Télécharger le ZIP contenant le PDF fusionné + Excel d'analyse

## 📈 Performances

- **Téléchargement** : 10,000+ documents supportés
- **Upload** : Aucune limite de taille
- **Parallélisation** : 10 workers simultanés
- **Timeout** : 300s par document
- **Retry** : 3 tentatives avec backoff exponentiel

## 🔒 Sécurité

- Validation stricte des types de fichiers
- Noms de fichiers sécurisés avec `secure_filename`
- Gestion sécurisée des secrets
- Nettoyage automatique des fichiers temporaires
- Pas de limite d'upload (gestion mémoire optimisée)

## 🛠️ Technologies

- **Backend** : Flask 3.1+
- **PDF Processing** : PyPDF 6.1+
- **Excel** : OpenPyXL 3.1+
- **AI** : OpenRouter API (Llama 3.1)
- **Server** : Gunicorn
- **Frontend** : Tailwind CSS

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des modifications.

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la [documentation de déploiement](DEPLOYMENT.md)

---

Développé avec ❤️ pour simplifier la gestion de vos PDFs
