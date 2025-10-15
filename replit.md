# Application de Traitement de PDFs

## Vue d'ensemble
Application web Flask professionnelle pour le traitement de fichiers PDF avec deux fonctionnalités principales:
1. Téléchargement de PDFs depuis des URLs et compression en ZIP
2. Fusion de PDFs depuis un ZIP et génération d'un fichier Excel

## Créé le
15 octobre 2025

## Architecture
- **Backend**: Flask avec blueprints modulaires
- **Frontend**: HTML/CSS avec Tailwind CSS (CDN)
- **Bibliothèques PDF**: pypdf pour la manipulation de PDFs
- **Bibliothèque Excel**: openpyxl pour la génération de fichiers Excel
- **Téléchargement**: requests pour télécharger les PDFs depuis les URLs

## Structure du Projet
```
/app                    # Package d'application Flask
  /__init__.py         # Flask factory
  /routes/             # Blueprints pour les routes
  /services/           # Logique de traitement PDF
  /utils/              # Utilitaires (gestion du stockage)
/templates/            # Templates Jinja2
/static/               # Fichiers CSS/JS
/instance/uploads/     # Fichiers uploadés
/tmp/                  # Fichiers temporaires et générés
config.py              # Configuration
main.py                # Point d'entrée
```

## Fonctionnalités
1. **Téléchargement & ZIP**: Accepte une liste d'URLs de PDFs, les télécharge, et crée un ZIP téléchargeable
   - Nettoyage automatique du ZIP après téléchargement
   - Gestion des erreurs de téléchargement
   - Support d'URLs illimitées

2. **Fusion & Excel**: Accepte un ZIP de PDFs, les fusionne en un seul PDF, et génère un fichier Excel avec les métadonnées
   - Nettoyage automatique des fichiers après téléchargement
   - Génération d'un manifest Excel avec métadonnées (nombre de pages, noms de fichiers)
   - Support de téléchargement dans n'importe quel ordre (PDF en premier ou Excel en premier)

## Gestion des Fichiers Temporaires
- **Téléchargement & ZIP**: Le fichier ZIP est automatiquement supprimé après téléchargement
- **Fusion & Excel**: Chaque fichier (PDF ou Excel) est supprimé immédiatement après son téléchargement
- **Limitation MVP**: Si un utilisateur ne télécharge qu'un seul des deux fichiers générés (PDF ou Excel), le fichier non téléchargé restera dans le dossier tmp/ jusqu'à téléchargement ou nettoyage manuel
- **Amélioration future**: Implémenter un système de nettoyage basé sur un timeout pour les fichiers orphelins

## Préférences Utilisateur
- Interface en français
- Interface professionnelle avec Tailwind CSS

## Changements Récents
- **15 octobre 2025**: Création de l'application complète avec les deux fonctionnalités
  - Implémentation de la structure Flask avec blueprints
  - Création de l'interface utilisateur avec Tailwind CSS
  - Implémentation du téléchargement et compression de PDFs
  - Implémentation de la fusion de PDFs et génération Excel
  - Ajout de la gestion automatique des fichiers temporaires avec protection contre les race conditions
