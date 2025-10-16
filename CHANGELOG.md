# Changelog

Toutes les modifications notables apportées à PDF Tools seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- 🎯 **Progression en temps réel** : Affichage de la progression détaillée pour toutes les opérations
  - Compteur de fichiers traités (ex: 150/3000)
  - Affichage des lots en cours (ex: Lot 8/150)
  - Nombre de réussites et d'échecs en temps réel
  - Barre de progression visuelle avec pourcentage
  - Messages d'état pour chaque étape du processus
- 🔄 **Server-Sent Events (SSE)** : Communication en temps réel entre serveur et client
- 📊 **Découpage intelligent** : Analyse automatique et découpage en lots optimaux (20 PDFs par lot)
- 🧵 **Traitement asynchrone** : Téléchargement et analyse en arrière-plan sans bloquer l'interface
- Système d'analyse intelligente de PDFs avec OpenRouter API
- Extraction automatique de texte et analyse de structure
- Génération de base de données Excel exportable à partir de l'analyse
- Support pour analyse de multiples fichiers PDFs simultanément
- Traitement asynchrone par batch pour téléchargement de 10,000+ documents
- Système de retry automatique pour téléchargements échoués
- Upload streaming sans limite de taille
- Documentation complète de déploiement
- README en français et anglais
- Requirements.txt pour déploiement simplifié

### Modifié
- 🚀 **Optimisation mémoire** : Réduction des workers simultanés de 20 à 5 pour éviter les crashs
- 📦 **Taille des lots** : Réduction de 50 à 20 PDFs par lot pour meilleure stabilité
- ⏱️ **Timeout serveur** : Augmentation de 30s à 300s pour opérations longues
- 🎨 **Interface utilisateur** : Ajout de tableaux de bord de progression interactifs
- Suppression de la limite MAX_CONTENT_LENGTH (50MB) pour uploads illimités
- Amélioration de la gestion des erreurs avec logs détaillés
- Remplacement de l'Excel basique du merger par analyseur intelligent

### Corrigé
- ❌ **Erreur "Unexpected token '<'"** : Correction du plantage serveur lors de téléchargements massifs
- 🔧 **Worker timeout** : Résolution des erreurs WORKER TIMEOUT lors du traitement de nombreux PDFs
- 💾 **Gestion mémoire** : Prévention des crashs "out of memory" avec traitement par lots optimisé

### Supprimé
- Limitation de taille d'upload de 50MB
- Génération Excel basique dans le processus de fusion

## [1.0.0] - 2025-10-15

### Ajouté
- Fonctionnalité de téléchargement et compression de PDFs depuis URLs
- Fonctionnalité de fusion de PDFs depuis fichier ZIP
- Génération de manifeste Excel pour PDFs fusionnés
- Interface utilisateur moderne avec Tailwind CSS
- Support multilingue (français)
- Téléchargement direct des fichiers générés
