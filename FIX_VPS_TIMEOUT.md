# Solution pour l'erreur "Unexpected token '<'" sur VPS

## Problème
Lors du traitement de 200+ PDFs, le serveur dépasse le délai d'attente (timeout) et retourne une page d'erreur HTML au lieu de JSON, causant l'erreur JavaScript : `Unexpected token '<'`

## Solutions

### 1. Augmenter le timeout de Gunicorn

Modifiez votre commande de démarrage Gunicorn sur le VPS :

```bash
# Au lieu de :
gunicorn --bind 0.0.0.0:5000 main:app

# Utilisez (timeout de 10 minutes) :
gunicorn --bind 0.0.0.0:5000 --timeout 600 --workers 2 --threads 4 main:app
```

Paramètres recommandés :
- `--timeout 600` : Timeout de 10 minutes (600 secondes)
- `--workers 2` : 2 workers pour gérer les requêtes
- `--threads 4` : 4 threads par worker
- Pour 200 PDFs : augmentez à `--timeout 900` (15 minutes)

### 2. Configuration Nginx (si vous utilisez Nginx)

Ajoutez dans votre configuration Nginx (`/etc/nginx/sites-available/votre-site`) :

```nginx
server {
    location / {
        proxy_pass http://127.0.0.1:5000;
        
        # Timeouts augmentés
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        send_timeout 600s;
        
        # Buffers pour grandes réponses
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
```

Puis redémarrez Nginx :
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Redémarrer le service systemd (si vous utilisez systemd)

Si vous avez un service systemd pour votre application, modifiez le fichier de service :

```bash
sudo nano /etc/systemd/system/pdftools.service
```

Ajoutez/modifiez :
```ini
[Service]
ExecStart=/chemin/vers/venv/bin/gunicorn --bind 0.0.0.0:5000 --timeout 600 --workers 2 --threads 4 main:app
TimeoutStartSec=600
TimeoutStopSec=600
```

Puis :
```bash
sudo systemctl daemon-reload
sudo systemctl restart pdftools
```

### 4. Alternative : Traitement par lots plus petits

Si les timeouts persistent, traitez par lots de 50-100 PDFs au lieu de 200 à la fois.

## Vérification

1. Uploadez un lot de test (40 PDFs) - devrait fonctionner
2. Uploadez 100 PDFs - devrait fonctionner avec les nouveaux timeouts
3. Uploadez 200 PDFs - devrait maintenant fonctionner

## Amélioration du code JavaScript

Le fichier `static/js/jurisprudence-batch.js` a été mis à jour pour détecter les erreurs HTML et afficher un message plus clair à l'utilisateur.

## En cas de problème persistant

Vérifiez les logs du serveur :
```bash
# Logs Gunicorn
journalctl -u pdftools -f

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
```
