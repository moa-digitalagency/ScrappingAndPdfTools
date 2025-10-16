# Application de Traitement de PDFs

## Vue d'ensemble
Application web Flask professionnelle pour le traitement avancé de fichiers PDF avec analyse intelligente par IA :
1. **Téléchargement Massif & ZIP** : Téléchargement de PDFs depuis des URLs (10,000+ documents) avec compression en ZIP
2. **Fusion de PDFs** : Fusion de PDFs depuis un ZIP avec génération de métadonnées Excel
3. **Analyse Intelligente par IA** (NOUVEAU) : Extraction automatique de données de PDFs avec OpenRouter et génération de base de données Excel structurée

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
    /downloader.py     # Route téléchargement & ZIP
    /merger.py         # Route fusion de PDFs
    /analyzer.py       # Route analyse intelligente (NOUVEAU)
  /services/           # Logique de traitement PDF
    /pdf_downloader.py # Téléchargement parallèle avec batching
    /pdf_merger.py     # Fusion de PDFs
    /pdf_intelligent_analyzer.py # Analyse intelligente avec IA (NOUVEAU)
  /utils/              # Utilitaires (gestion du stockage)
  /templates/          # Templates HTML
    /index.html        # Page d'accueil avec 3 cartes
    /downloader.html   # Interface téléchargement
    /merger.html       # Interface fusion
    /analyzer.html     # Interface analyse IA (NOUVEAU)
    /base.html         # Template de base
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

### 1. Téléchargement Massif & ZIP
- **10,000+ documents supportés** avec traitement par batch optimisé (50 URLs par batch)
- **Téléchargement parallèle** : 20 workers simultanés avec ThreadPoolExecutor
- **Retry automatique** : 3 tentatives avec backoff exponentiel plafonné à 10s
- **Timeout optimisé** : (30, 300) secondes (connexion, lecture) par document
- **Gestion robuste des erreurs** : logs détaillés, gestion par type d'erreur, rapports d'échec
- **Double entrée** : Coller des liens texte OU uploader un fichier CSV
- **Validation des fichiers** : Vérification de la taille (min 100 bytes)
- **Noms de fichiers sécurisés** : Numérotation avec zfill(6) pour éviter les conflits
- Nettoyage automatique du ZIP après téléchargement

### 2. Fusion de PDFs
- **Upload illimité** : Aucune restriction de taille, volume ou nombre de fichiers
- **Streaming upload** : Lecture par chunks pour économiser la mémoire
- **Fusion automatique** : Combine tous les PDFs du ZIP en un seul document
- **Génération Excel** : Métadonnées détaillées (nombre de pages, nom de fichier, etc.)
- Nettoyage automatique des fichiers après téléchargement

### 3. Analyse Intelligente par IA (NOUVEAU - 15 octobre 2025)
- **Trois types d'inputs supportés** :
  - CSV de liens PDF (pour analyser des PDFs en ligne)
  - ZIP de plusieurs PDFs (pour analyser des fichiers locaux en batch)
  - Un seul fichier PDF (pour une analyse simple)
- **Analyse intelligente avec OpenRouter API** :
  - Extraction automatique de texte de chaque PDF
  - Reconnaissance du type de document (rapport, facture, contrat, etc.)
  - Extraction d'entités (organisations, personnes mentionnées)
  - Extraction de dates et mots-clés importants
  - Génération de résumés automatiques
  - Détection de champs personnalisés
- **Base de données Excel exportable** :
  - Feuille de synthèse avec statut d'analyse et métadonnées
  - Feuilles séparées pour chaque tableau extrait
  - Feuilles d'informations clés pour chaque PDF
- **Traitement parallèle** : Analyse de plusieurs PDFs simultanément (5 workers)
- Nettoyage automatique des fichiers après téléchargement

## Gestion des Fichiers Temporaires
- **Téléchargement & ZIP**: Le fichier ZIP est automatiquement supprimé après téléchargement
- **Fusion & Analyse**: Les fichiers (PDF fusionné et Excel d'analyse) sont supprimés immédiatement après téléchargement
- **Streaming upload**: Les uploads sont écrits directement sur disque par chunks pour économiser la mémoire
- **Nettoyage automatique**: Tous les fichiers temporaires sont supprimés après traitement

## Performance & Robustesse
- **Téléchargement massif**: Support pour 1000+ documents via batching optimisé (50 URLs par batch)
- **Upload illimité**: Aucune restriction de taille grâce au streaming et suppression de MAX_CONTENT_LENGTH
- **Parallélisation**: 20 workers simultanés pour téléchargements optimisés
- **Retry logic**: 3 tentatives avec backoff exponentiel plafonné à 10s
- **Timeout**: (30, 300) secondes (connexion, lecture) pour téléchargements fiables
- **Gestion d'erreurs robuste**: Validation des fichiers, gestion par type d'exception, fallbacks garantis

## Configuration Requise
- **SECRET_KEY**: Clé secrète Flask (obligatoire)
- **OPENROUTER_API_KEY**: Clé API OpenRouter pour analyse intelligente (OBLIGATOIRE)
  - Nécessaire pour l'analyse IA des PDFs
  - Disponible sur https://openrouter.ai/

## Préférences Utilisateur
- Interface en français
- Interface professionnelle avec Tailwind CSS

## Changements Récents
- **16 octobre 2025 (Version 3.3 - Améliorations SSE et Gestion des Erreurs)** :
  - ✅ **SSE ultra-robuste pour gros volumes (2900+ URLs)** :
    - Système de heartbeat pour maintenir la connexion active
    - Reconnexion automatique avec 5 tentatives progressives
    - Correction du bug de payload 'ready' final (comparaison JSON vs références)
    - Fréquence mise à jour optimisée (0.3s au lieu de 0.5s)
    - Headers anti-buffering pour streaming fiable
  - ✅ **Nettoyage automatique des fichiers temporaires** :
    - Nettoyage automatique au chargement/refresh de la page
    - Suppression des fichiers > 1h d'ancienneté
    - Endpoint `/cleanup` dédié pour libérer l'espace
  - ✅ **Affichage des liens en erreur** :
    - Liste détaillée des URLs en échec avec messages d'erreur
    - Interface pliable/dépliable pour consultation facile
    - Transmission complète des `failed_urls` du backend au frontend
  
- **16 octobre 2025 (Version 3.2 - Progression en Temps Réel)** :
  - ✅ **Progression en temps réel** : Affichage détaillé de l'avancement pour toutes les opérations
    - Compteur de fichiers traités (ex: 150/3000)
    - Affichage des lots en cours (ex: Lot 8/150)
    - Nombre de réussites et d'échecs en temps réel
    - Barre de progression visuelle avec pourcentage
    - Messages d'état pour chaque étape du processus
  - ✅ **Server-Sent Events (SSE)** : Communication en temps réel serveur-client
  - ✅ **Découpage intelligent automatique** : Analyse et découpage en lots de 20 PDFs
  - ✅ **Traitement asynchrone** : Téléchargement et analyse en arrière-plan
  - ✅ **Optimisation mémoire** : Réduction des workers de 20 à 5 pour éviter les crashs
  - ✅ **Correction erreur "Unexpected token"** : Résolution des plantages serveur
  - ✅ **Timeout serveur** : Augmentation à 300s pour opérations longues
  
- **15 octobre 2025 (Version 3.1 - Améliorations UX et Robustesse)** :
  - ✅ **Layout responsive amélioré** : 2 blocs en colonnes (Télécharger & Fusionner) + Analyse IA en bas pleine largeur
  - ✅ **Option CSV pour le téléchargeur** : Possibilité de coller des liens OU uploader un fichier CSV
  - ✅ **Robustesse 1000+ liens** : Batching optimisé (50/batch), 20 workers, timeout tuple, retry plafonné
  - ✅ **Extraction PDF complète** : Prompt IA amélioré pour extraire TOUS les éléments (tableaux, texte, métadonnées)
  - ✅ **Gestion d'erreur robuste** : Valeurs par défaut garanties, fallbacks JSON, aucune KeyError possible
  - ✅ **Excel enrichi** : Colonnes Type, Entreprise, Pages + feuille de texte complet pour chaque PDF
  - ✅ **Validation des fichiers** : Vérification de taille, noms sécurisés, gestion des erreurs par type
  
- **15 octobre 2025 (Version 3.0 - Analyse Intelligente par IA)** :
  - ✅ Nouvelle fonctionnalité d'analyse intelligente de PDF avec OpenRouter API
  - ✅ Support de 3 types d'inputs : CSV de liens, ZIP de PDFs, un seul PDF
  - ✅ Extraction automatique de données structurées avec IA
  - ✅ Génération de base de données Excel avec feuilles multiples
  - ✅ Interface utilisateur avec onglets pour les différents types d'inputs
  - ✅ Traitement parallèle avec 5 workers pour l'analyse IA
  - ✅ Gestion d'erreur pour clé API manquante
  - ✅ Format d'API OpenRouter corrigé selon la documentation officielle

- **15 octobre 2025 (Version 2.0 - Améliorations majeures)** :
  - ✅ Téléchargement massif robuste pour 10,000+ documents avec batching
  - ✅ Upload illimité avec streaming pour fichiers de toute taille
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
