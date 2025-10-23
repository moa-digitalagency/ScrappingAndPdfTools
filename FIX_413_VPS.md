# 🔧 Correction de l'erreur 413 sur votre VPS

## Problème
Erreur "Request Entity Too Large (413)" lors de l'upload de fichiers sur votre VPS.

## Solution en 2 étapes

### Étape 1: Mettre à jour l'application sur votre VPS

Connectez-vous à votre VPS en SSH et exécutez:

```bash
cd /chemin/vers/votre/projet
git pull
./deploy_vps.sh
```

Le script `deploy_vps.sh` a été mis à jour pour supporter:
- ✅ Fichiers jusqu'à 500 MB
- ✅ Timeout de 10 minutes (600 secondes)
- ✅ Pas de limite sur la taille des requêtes

### Étape 2: Configurer Nginx (si vous utilisez nginx)

Si vous utilisez nginx comme reverse proxy, vous devez aussi le configurer.

#### 2.1 Éditer la configuration nginx

```bash
sudo nano /etc/nginx/sites-available/votre-site
```

#### 2.2 Ajouter/modifier dans le bloc `location /`

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
        
        # ⚡ IMPORTANT: Support pour fichiers jusqu'à 500 MB
        client_max_body_size 500M;
        client_body_timeout 600s;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

#### 2.3 Tester et redémarrer nginx

```bash
# Tester la configuration
sudo nginx -t

# Si OK, redémarrer nginx
sudo systemctl restart nginx
```

## Vérification

Après ces changements, testez l'upload sur votre VPS. L'erreur 413 devrait être résolue.

## Si le problème persiste

### Vérifier que gunicorn utilise la bonne configuration

```bash
# Sur votre VPS
ps aux | grep gunicorn
```

Vous devriez voir `--timeout 600` et `--limit-request-line 0` dans la commande.

### Vérifier les logs

```bash
# Logs de l'application
tail -f gunicorn.log

# Logs nginx (si applicable)
sudo tail -f /var/log/nginx/error.log
```

## Configuration alternative sans nginx

Si vous n'utilisez pas nginx et accédez directement à gunicorn, le problème devrait être résolu uniquement avec l'Étape 1.

## Résumé des modifications

| Fichier modifié | Changement |
|----------------|------------|
| `deploy_vps.sh` | Timeout: 120s → 600s, Ajout de `--limit-request-line 0 --limit-request-field_size 0` |
| Configuration nginx | `client_max_body_size`: 100M → 500M, Ajout timeouts 600s |

---

**Note**: Ces modifications sont déjà synchronisées avec votre dépôt Git. Il suffit de faire `git pull` sur votre VPS pour les récupérer.
