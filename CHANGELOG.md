# Changelog

Toutes les modifications notables apportées à PDF Tools seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
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
- Augmentation du timeout de téléchargement de 30s à 300s
- Suppression de la limite MAX_CONTENT_LENGTH (50MB) pour uploads illimités
- Amélioration de la gestion des erreurs avec logs détaillés
- Remplacement de l'Excel basique du merger par analyseur intelligent

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
