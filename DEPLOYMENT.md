# Guide de Déploiement - PDF Tools

Ce guide vous accompagne dans le déploiement de PDF Tools sur différentes plateformes.

## Table des Matières

- [Prérequis](#prérequis)
- [Configuration des Secrets](#configuration-des-secrets)
- [Déploiement sur Replit](#déploiement-sur-replit)
- [Déploiement sur Heroku](#déploiement-sur-heroku)
- [Déploiement sur VPS (DigitalOcean, AWS, etc.)](#déploiement-sur-vps)
- [Déploiement avec Docker](#déploiement-avec-docker)
- [Variables d'Environnement](#variables-denvironnement)
- [Résolution de Problèmes](#résolution-de-problèmes)

---

## Prérequis

- Python 3.11 ou supérieur
- Compte OpenRouter (optionnel, pour analyse AI)
- Git (pour cloner le projet)

## Configuration des Secrets

### Secrets Requis

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `SECRET_KEY` | Clé secrète Flask pour sessions | ✅ Oui |
| `OPENROUTER_API_KEY` | Clé API OpenRouter | ⚠️ Optionnel* |

*Si `OPENROUTER_API_KEY` n'est pas configurée, l'analyse intelligente sera désactivée mais toutes les autres fonctionnalités continueront de fonctionner normalement.

### Générer une SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Obtenir une Clé OpenRouter

1. Créer un compte sur [https://openrouter.ai](https://openrouter.ai)
2. Aller dans **Settings** > **API Keys**
3. Cliquer sur **Create Key**
4. Copier la clé générée
5. Ajouter des crédits si nécessaire (modèle gratuit disponible)

---

## Déploiement sur Replit

### Étape 1 : Importer le Projet

1. Aller sur [Replit](https://replit.com)
2. Cliquer sur **+ Create Repl**
3. Sélectionner **Import from GitHub**
4. Coller l'URL du dépôt
5. Cliquer sur **Import from GitHub**

### Étape 2 : Configurer les Secrets

1. Dans votre Repl, cliquer sur l'icône **🔒 Secrets** (Tools > Secrets)
2. Ajouter les secrets suivants :
   ```
   SECRET_KEY = <votre-secret-key>
   OPENROUTER_API_KEY = <votre-clé-openrouter>
   ```

### Étape 3 : Vérifier la Configuration

Le projet est déjà configuré avec :
- ✅ `pyproject.toml` avec toutes les dépendances
- ✅ Workflow configuré pour Gunicorn
- ✅ Configuration de déploiement automatique

### Étape 4 : Lancer l'Application

1. Cliquer sur **Run**
2. L'application sera accessible sur le port 5000
3. Replit générera automatiquement une URL publique

### Étape 5 : Publier (Optionnel)

1. Cliquer sur **Deploy** en haut à droite
2. Choisir **Autoscale** pour une application web
3. Suivre les instructions pour obtenir un domaine personnalisé

---

## Déploiement sur Heroku

### Étape 1 : Prérequis

```bash
# Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Se connecter
heroku login
```

### Étape 2 : Créer l'Application

```bash
# Créer une nouvelle app
heroku create pdf-tools-app

# Ajouter buildpack Python
heroku buildpacks:add heroku/python
```

### Étape 3 : Configurer les Variables d'Environnement

```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set OPENROUTER_API_KEY=<votre-clé>
```

### Étape 4 : Créer un Procfile

```bash
echo "web: gunicorn --bind 0.0.0.0:\$PORT main:app" > Procfile
```

### Étape 5 : Déployer

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Étape 6 : Ouvrir l'Application

```bash
heroku open
```

---

## Déploiement sur VPS

### Étape 1 : Préparer le Serveur

```bash
# Connexion SSH
ssh user@your-server-ip

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Installer Nginx
sudo apt install nginx -y
```

### Étape 2 : Cloner le Projet

```bash
cd /var/www
sudo git clone <votre-repo> pdf-tools
cd pdf-tools
```

### Étape 3 : Créer un Environnement Virtuel

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Étape 4 : Configurer les Variables d'Environnement

```bash
# Créer un fichier .env
sudo nano .env
```

Ajouter :
```
SECRET_KEY=<votre-secret-key>
OPENROUTER_API_KEY=<votre-clé>
```

### Étape 5 : Configurer Gunicorn avec Systemd

```bash
sudo nano /etc/systemd/system/pdf-tools.service
```

Ajouter :
```ini
[Unit]
Description=PDF Tools Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/pdf-tools
Environment="PATH=/var/www/pdf-tools/venv/bin"
EnvironmentFile=/var/www/pdf-tools/.env
ExecStart=/var/www/pdf-tools/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```

### Étape 6 : Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/pdf-tools
```

Ajouter :
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Pour uploads illimités
        client_max_body_size 0;
        proxy_request_buffering off;
    }
}
```

### Étape 7 : Activer et Démarrer

```bash
# Activer le site Nginx
sudo ln -s /etc/nginx/sites-available/pdf-tools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Démarrer le service
sudo systemctl start pdf-tools
sudo systemctl enable pdf-tools
sudo systemctl status pdf-tools
```

### Étape 8 : Configurer SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Déploiement avec Docker

### Étape 1 : Créer un Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p instance/uploads tmp

# Exposer le port
EXPOSE 5000

# Variables d'environnement par défaut
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Lancer Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "600", "main:app"]
```

### Étape 2 : Créer docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./instance:/app/instance
      - ./tmp:/app/tmp
    restart: unless-stopped
```

### Étape 3 : Créer .env

```bash
SECRET_KEY=<votre-secret-key>
OPENROUTER_API_KEY=<votre-clé>
```

### Étape 4 : Lancer

```bash
docker-compose up -d
```

---

## Variables d'Environnement

### Variables Principales

| Variable | Type | Défaut | Description |
|----------|------|--------|-------------|
| `SECRET_KEY` | String | - | Clé secrète Flask (obligatoire) |
| `OPENROUTER_API_KEY` | String | - | Clé API OpenRouter (optionnel) |
| `ADMIN_SECRET` | String | - | Secret pour mise à jour Git (obligatoire en production) |

### Variables Optionnelles (Avancées)

| Variable | Type | Défaut | Description |
|----------|------|--------|-------------|
| `FLASK_ENV` | String | production | Environnement Flask |
| `FLASK_DEBUG` | Boolean | False | Mode debug Flask |
| `MAX_WORKERS` | Integer | 10 | Nombre de workers pour téléchargement parallèle |

---

## Résolution de Problèmes

### Problème : L'analyse intelligente ne fonctionne pas

**Solution :**
1. Vérifier que `OPENROUTER_API_KEY` est configurée
2. Vérifier les crédits sur votre compte OpenRouter
3. Consulter les logs : `gunicorn --log-level debug main:app`

### Problème : Upload échoue pour gros fichiers

**Solution :**
1. Pour Nginx, ajouter `client_max_body_size 0;`
2. Vérifier l'espace disque disponible
3. La limite MAX_CONTENT_LENGTH a été supprimée du code

### Problème : Téléchargement massif lent

**Solution :**
1. Augmenter le nombre de workers : modifier `max_workers` dans `pdf_downloader.py`
2. Vérifier la bande passante du serveur
3. Utiliser un serveur plus proche géographiquement

### Problème : Erreur 502 Bad Gateway

**Solution :**
1. Vérifier que Gunicorn tourne : `systemctl status pdf-tools`
2. Augmenter le timeout Nginx :
   ```nginx
   proxy_read_timeout 600;
   proxy_connect_timeout 600;
   proxy_send_timeout 600;
   ```

### Problème : Mémoire insuffisante

**Solution :**
1. Réduire le nombre de workers Gunicorn
2. Augmenter la RAM du serveur
3. Utiliser Redis/Celery pour les tâches longues (implémentation future)

---

## Logs et Monitoring

### Voir les Logs en Production

**Systemd (VPS) :**
```bash
sudo journalctl -u pdf-tools -f
```

**Docker :**
```bash
docker-compose logs -f web
```

**Heroku :**
```bash
heroku logs --tail
```

---

## Mise à Jour de l'Application

### Via l'Interface Web (Recommandé)

L'application dispose d'une fonctionnalité de mise à jour automatique via l'interface web :

1. **Configurer ADMIN_SECRET** (obligatoire) :
   ```bash
   # Générer un secret sécurisé
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Ajouter à vos variables d'environnement
   export ADMIN_SECRET="votre_secret_généré"
   ```

2. **Utiliser l'interface web** :
   - Cliquer sur le bouton **"Mise à jour Git"** dans la navigation
   - Entrer le secret administrateur (ADMIN_SECRET)
   - Confirmer l'opération
   - Le serveur va automatiquement exécuter `git pull`
   - Redémarrer l'application si nécessaire

3. **Sécurité** :
   - ✅ Accès protégé par secret d'administration
   - ✅ Logs de toutes les tentatives d'accès
   - ✅ Retour 403 pour accès non autorisés
   - ✅ Idéal pour les mises à jour rapides en production

### Sur VPS (Méthode Manuelle)

```bash
cd /var/www/pdf-tools
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pdf-tools
```

### Sur Heroku

```bash
git push heroku main
```

### Sur Docker

```bash
docker-compose down
git pull origin main
docker-compose up -d --build
```

### Sur Replit

```bash
# Option 1 : Interface Web (Recommandé)
# Utiliser le bouton "Mise à jour Git" dans la navigation

# Option 2 : Shell
git pull origin main
# L'application redémarrera automatiquement
```

---

## Performance et Optimisation

### Recommandations pour Production

1. **Serveur :** Minimum 2 CPU, 4GB RAM
2. **Workers Gunicorn :** `(2 × CPU) + 1`
3. **Timeout :** 600 secondes minimum
4. **Stockage :** SSD recommandé
5. **CDN :** Pour fichiers statiques (optionnel)

### Configuration Gunicorn Optimale

```bash
gunicorn \
  --workers 4 \
  --timeout 600 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --bind 0.0.0.0:5000 \
  --reuse-port \
  main:app
```

---

## Sécurité

### Checklist de Sécurité

- ✅ SECRET_KEY unique et complexe
- ✅ ADMIN_SECRET configuré pour mise à jour Git
- ✅ HTTPS activé (SSL/TLS)
- ✅ Firewall configuré
- ✅ Mises à jour régulières
- ✅ Logs activés
- ✅ Backup réguliers
- ✅ Rate limiting (à implémenter si nécessaire)

---

## Support

Pour toute question ou problème :
- Consulter la [documentation principale](README.md)
- Ouvrir une issue sur GitHub
- Consulter le [CHANGELOG](CHANGELOG.md)

---

**Déploiement réussi !** 🚀 Votre plateforme PDF Tools est maintenant en production.
