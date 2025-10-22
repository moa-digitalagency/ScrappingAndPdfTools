#!/bin/bash

# Script de déploiement pour VPS
# Usage: ./deploy.sh

set -e

echo "🚀 Début du déploiement..."

# 1. Pull les dernières modifications
echo "📥 Récupération des dernières modifications..."
git pull origin main || git pull origin master

# 2. Activation de l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# 3. Installation/mise à jour des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# 4. Création du fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cat > .env << 'EOF'
# Flask Configuration
SESSION_SECRET=your_secret_key_here_change_this_in_production

# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Database Configuration (si nécessaire)
# DATABASE_URL=postgresql://user:password@localhost/dbname
EOF
    echo "✅ Fichier .env créé"
else
    echo "ℹ️  Le fichier .env existe déjà, mise à jour de l'API key..."
    # Mise à jour de l'API key si le fichier existe
    if grep -q "OPENROUTER_API_KEY" .env; then
        sed -i 's/^OPENROUTER_API_KEY=.*/OPENROUTER_API_KEY=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/' .env
    else
        echo "OPENROUTER_API_KEY=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" >> .env
    fi
fi

# 5. Génération d'une nouvelle clé secrète si nécessaire
if grep -q "your_secret_key_here_change_this_in_production" .env; then
    echo "🔐 Génération d'une nouvelle clé secrète..."
    NEW_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/your_secret_key_here_change_this_in_production/$NEW_SECRET/" .env
fi

# 6. Redémarrage du service (adaptez selon votre configuration)
echo "🔄 Redémarrage du service..."

# Option 1: Si vous utilisez systemd
# sudo systemctl restart pdftools

# Option 2: Si vous utilisez supervisor
# sudo supervisorctl restart pdftools

# Option 3: Si vous utilisez PM2
# pm2 restart pdftools

# Option 4: Si vous lancez avec gunicorn directement
pkill -f "gunicorn.*main:app" || true
sleep 2
nohup gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app > gunicorn.log 2>&1 &

echo "✅ Déploiement terminé avec succès!"
echo "📊 Vérifiez les logs avec: tail -f gunicorn.log"
