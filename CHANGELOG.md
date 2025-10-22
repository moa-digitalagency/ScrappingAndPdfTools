# Changelog

Toutes les modifications notables apportées à PDF Tools seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [3.5.0] - 2025-10-22

### Ajouté
- 🔒 **Mise à jour Git sécurisée** : Nouvelle fonctionnalité de mise à jour du code via interface web
  - Route POST `/git_pull` avec authentification par secret
  - Protection par variable d'environnement `ADMIN_SECRET` (obligatoire)
  - Interface utilisateur avec bouton dans la navigation
  - Logs des tentatives d'accès non autorisées
- 📦 **Téléchargement individuel des lots** : Boutons de téléchargement pour chaque lot ZIP terminé
  - Route dédiée `/download_batch_zip/<download_id>` sans suppression automatique
  - Fichiers ZIP conservés pour téléchargements multiples
  - Interface mise à jour dynamiquement avec JavaScript

### Modifié
- 🔄 **Téléchargement automatique robuste** : Amélioration majeure de la fiabilité
  - Rechargement de session.json depuis le disque pour robustesse après redémarrage
  - Skip automatique des lots déjà complétés (évite les doublons)
  - Gestion d'erreur avec continue sur échec (le processus ne s'arrête plus)
  - Rapport détaillé des lots en échec dans les logs
  - Persistance complète de l'état pour récupération après crash serveur

### Sécurité
- ✅ Élimination de la faille critique d'exécution de commandes git non authentifiées
- ✅ Documentation complète de ADMIN_SECRET dans Configuration Requise
- ✅ Système d'authentification robuste avec logging des tentatives d'accès

## [3.4.0] - 2025-10-16

### Ajouté
- 📋 **Système de logs persistants avec SQLite** :
  - Base de données SQLite pour stocker tous les logs d'actions
  - Enregistrement de tous les événements : démarrages, succès, erreurs
  - Filtrage par type (download, merger, analyzer) et statut (info, success, error)
  - Page dédiée `/logs/` pour consulter l'historique complet
- 📧 **Page de contact** :
  - Nouvelle page `/contact/` avec informations de MOA Digital Agency
  - Email : moa@myoneart.com
  - Site web : www.myoneart.com
- 🧭 **Navigation simplifiée** :
  - Header avec 3 liens : Accueil, Log, Contact
  - Interface claire et professionnelle
- ©️ **En-têtes de copyright** :
  - Tous les fichiers Python incluent les informations de développeur
  - Branding MOA Digital Agency LLC

## [3.3.0] - 2025-10-16

### Ajouté
- 💓 **Heartbeat SSE** : Système de heartbeat pour maintenir les connexions actives
- 🔄 **Reconnexion automatique** : 5 tentatives progressives pour SSE
- 🧹 **Nettoyage automatique** : Suppression des fichiers temporaires > 1h d'ancienneté
- 📍 **Endpoint de nettoyage** : Route `/cleanup` dédiée pour libérer l'espace
- ⚠️ **Affichage des erreurs** : Liste détaillée des URLs en échec avec messages d'erreur

### Modifié
- 🚀 **SSE ultra-robuste** : Support fiable pour 2900+ URLs
- ⚡ **Fréquence optimisée** : Mise à jour toutes les 0.3s au lieu de 0.5s
- 📤 **Headers anti-buffering** : Pour streaming fiable

### Corrigé
- 🐛 **Bug payload 'ready'** : Correction de la comparaison JSON vs références
- 📡 **Transmission des erreurs** : Transmission complète des `failed_urls` au frontend

## [3.2.0] - 2025-10-16

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
