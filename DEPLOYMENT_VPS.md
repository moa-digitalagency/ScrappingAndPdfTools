# Guide de Déploiement VPS

Ce guide explique comment déployer et mettre à jour l'application sur votre VPS.

## Prérequis

- Python 3.11+ installé
- Git installé
- Un environnement virtuel Python (`venv`) déjà créé
- Accès SSH au VPS

## Installation Initiale

1. **Cloner le projet** (première fois seulement):
```bash
git clone <votre-repo-url>
cd <nom-du-projet>
```

2. **Créer l'environnement virtuel** (première fois seulement):
```bash
python3 -m venv venv
```

3. **Lancer le script de déploiement**:
```bash
./deploy.sh
```

## Mise à Jour de l'Application

Pour mettre à jour l'application après avoir fait des modifications:

```bash
./deploy.sh
```

Le script effectue automatiquement:
- ✅ Pull des dernières modifications Git
- ✅ Activation de l'environnement virtuel
- ✅ Installation/mise à jour des dépendances
- ✅ Création/mise à jour du fichier `.env`
- ✅ Redémarrage du serveur

## Configuration Manuelle du Service

### Option 1: Systemd (Recommandé pour production)

1. Créez un fichier service:
```bash
sudo nano /etc/systemd/system/pdftools.service
```

2. Ajoutez le contenu suivant:
```ini
[Unit]
Description=PDF Tools Application
After=network.target

[Service]
Type=notify
User=votre_user
WorkingDirectory=/chemin/vers/votre/projet
Environment="PATH=/chemin/vers/votre/projet/venv/bin"
ExecStart=/chemin/vers/votre/projet/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Activez et démarrez le service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pdftools
sudo systemctl start pdftools
```

4. Modifiez `deploy.sh` pour utiliser systemd (décommentez la ligne):
```bash
sudo systemctl restart pdftools
```

### Option 2: PM2 (Alternative)

1. Installez PM2:
```bash
npm install -g pm2
```

2. Créez un fichier `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'pdftools',
    script: 'venv/bin/gunicorn',
    args: '--bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app',
    cwd: '/chemin/vers/votre/projet',
    env: {
      'PATH': '/chemin/vers/votre/projet/venv/bin:' + process.env.PATH
    }
  }]
}
```

3. Démarrez avec PM2:
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Nginx (Reverse Proxy Recommandé)

Pour une configuration en production, utilisez Nginx comme reverse proxy:

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;
    }
}
```

## Vérification

Après le déploiement, vérifiez que l'application fonctionne:

```bash
# Vérifier les logs
tail -f gunicorn.log

# Tester l'application
curl http://localhost:5000
```

## Dépannage

### L'interface n'est pas mise à jour

1. Vider le cache du navigateur (Ctrl+F5 ou Ctrl+Shift+R)
2. Redémarrer le serveur:
```bash
./deploy.sh
```

### Problèmes de permissions

```bash
chmod +x deploy.sh
chmod 755 venv/bin/activate
```

### Voir les logs d'erreur

```bash
tail -f gunicorn.log
# ou pour systemd
sudo journalctl -u pdftools -f
```

## Sécurité

⚠️ **Important**: Le fichier `.env` contient des clés secrètes et ne doit JAMAIS être commis dans Git. Il est déjà dans `.gitignore`.

Pour changer les clés:
```bash
nano .env
# Modifier les valeurs
./deploy.sh
```
