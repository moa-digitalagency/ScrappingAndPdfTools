# Application de Traitement de PDFs

## Vue d'ensemble
Application web Flask professionnelle pour le traitement avancé de fichiers PDF avec analyse intelligente par IA :
1. Téléchargement massif de PDFs depuis des URLs (10,000+ documents) avec compression en ZIP
2. Fusion de PDFs depuis un ZIP avec analyse intelligente et génération de base de données Excel

## Créé le
15 octobre 2025

## Architecture
- **Backend**: Flask avec blueprints modulaires
- **Frontend**: HTML/CSS avec Tailwind CSS (CDN)
- **Bibliothèques PDF**: pypdf pour la manipulation de PDFs
- **Bibliothèque Excel**: openpyxl pour la génération de fichiers Excel
- **Téléchargement**: requests avec ThreadPoolExecutor pour téléchargement parallèle
- **IA**: OpenRouter API (Llama 3.1) pour analyse intelligente des PDFs

## Structure du Projet
```
/app                    # Package d'application Flask
  /__init__.py         # Flask factory avec StreamingRequest
  /routes/             # Blueprints pour les routes
  /services/           # Logique de traitement PDF
    /pdf_downloader.py # Téléchargement parallèle avec batching
    /pdf_merger.py     # Fusion de PDFs
    /pdf_analyzer.py   # Analyse intelligente avec IA (NOUVEAU)
  /utils/              # Utilitaires (gestion du stockage)
/templates/            # Templates Jinja2
/static/               # Fichiers CSS/JS
/instance/uploads/     # Fichiers uploadés
/tmp/                  # Fichiers temporaires et générés
config.py              # Configuration
main.py                # Point d'entrée
requirements.txt       # Dépendances Python
CHANGELOG.md          # Historique des modifications
README.md / README_EN.md  # Documentation FR/EN
DEPLOYMENT.md         # Guide de déploiement
```

## Fonctionnalités

### 1. Téléchargement Massif & ZIP (Amélioré)
- **10,000+ documents supportés** avec traitement par batch de 100 URLs
- **Téléchargement parallèle** : 10 workers simultanés avec ThreadPoolExecutor
- **Retry automatique** : 3 tentatives avec backoff exponentiel
- **Timeout étendu** : 300 secondes par document (au lieu de 30s)
- **Gestion robuste des erreurs** : logs détaillés et rapports d'échec
- Nettoyage automatique du ZIP après téléchargement

### 2. Fusion & Analyse Intelligente (NOUVEAU)
- **Upload illimité** : Aucune restriction de taille, volume ou nombre de fichiers
- **Streaming upload** : Lecture par chunks pour économiser la mémoire
- **Fusion automatique** : Combine tous les PDFs du ZIP en un seul document
- **Analyse intelligente par IA** (OpenRouter) :
  - Extraction automatique de texte de chaque PDF
  - Reconnaissance du type de document (rapport, facture, contrat, etc.)
  - Extraction d'entités (organisations, personnes mentionnées)
  - Extraction de dates et mots-clés importants
  - Génération de résumés automatiques
  - Détection de champs personnalisés
- **Base de données Excel exportable** :
  - Feuille principale avec analyse complète de chaque PDF
  - Feuille secondaire avec champs personnalisés extraits
  - Métadonnées détaillées (nombre de pages, longueur texte, etc.)
- Nettoyage automatique des fichiers après téléchargement

## Gestion des Fichiers Temporaires
- **Téléchargement & ZIP**: Le fichier ZIP est automatiquement supprimé après téléchargement
- **Fusion & Analyse**: Les fichiers (PDF fusionné et Excel d'analyse) sont supprimés immédiatement après téléchargement
- **Streaming upload**: Les uploads sont écrits directement sur disque par chunks pour économiser la mémoire
- **Nettoyage automatique**: Tous les fichiers temporaires sont supprimés après traitement

## Performance & Robustesse
- **Téléchargement massif**: Support pour 10,000+ documents via batching (100 URLs par batch)
- **Upload illimité**: Aucune restriction de taille grâce au streaming et suppression de MAX_CONTENT_LENGTH
- **Parallélisation**: 10 workers simultanés pour téléchargements optimisés
- **Retry logic**: 3 tentatives avec backoff exponentiel (2^n secondes)
- **Timeout**: 300 secondes par document pour téléchargements fiables

## Configuration Requise
- **SECRET_KEY**: Clé secrète Flask (obligatoire)
- **OPENROUTER_API_KEY**: Clé API OpenRouter pour analyse intelligente (optionnel)
  - Si non configurée, l'analyse IA sera désactivée mais les autres fonctionnalités continueront de fonctionner

## Préférences Utilisateur
- Interface en français
- Interface professionnelle avec Tailwind CSS

## Changements Récents
- **15 octobre 2025 (Version 2.0 - Améliorations majeures)** :
  - ✅ Téléchargement massif robuste pour 10,000+ documents avec batching
  - ✅ Upload illimité avec streaming pour fichiers de toute taille
  - ✅ Analyse intelligente par IA (OpenRouter) avec extraction de texte et métadonnées
  - ✅ Base de données Excel exportable avec données structurées
  - ✅ Retry automatique avec backoff exponentiel
  - ✅ Timeout étendu à 300 secondes par document
  - ✅ Parallélisation avec ThreadPoolExecutor (10 workers)
  - ✅ Documentation complète (CHANGELOG, README FR/EN, DEPLOYMENT, requirements.txt)
  
- **15 octobre 2025 (Version 1.0 - Création initiale)** :
  - Implémentation de la structure Flask avec blueprints
  - Création de l'interface utilisateur avec Tailwind CSS
  - Implémentation du téléchargement et compression de PDFs
  - Implémentation de la fusion de PDFs et génération Excel basique
  - Gestion automatique des fichiers temporaires
