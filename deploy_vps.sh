#!/bin/bash

# Script de déploiement pour VPS - Version Sécurisée
# Usage: ./deploy_vps.sh

set -e

echo "🚀 Début du déploiement..."

# 1. Pull les dernières modifications
echo "📥 Récupération des dernières modifications..."
git pull origin main || git pull origin master

# 2. Activation de l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé, création..."
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Installation/mise à jour des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# 4. Gestion du fichier .env
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cat > .env << 'EOF'
# Flask Configuration
SESSION_SECRET=CHANGEZ_MOI_EN_PRODUCTION

# OpenRouter API Configuration
OPENROUTER_API_KEY=VOTRE_CLE_API_ICI

# Database Configuration (si nécessaire)
# DATABASE_URL=postgresql://user:password@localhost/dbname
EOF
    echo "⚠️  IMPORTANT: Fichier .env créé. Vous DEVEZ modifier les valeurs:"
    echo "   1. Ajoutez votre clé OpenRouter API"
    echo "   2. Générez une nouvelle SESSION_SECRET"
    echo ""
    echo "   Pour éditer: nano .env"
else
    echo "✅ Le fichier .env existe déjà"
    
    # Vérification de la présence de OPENROUTER_API_KEY
    if ! grep -q "^OPENROUTER_API_KEY=" .env; then
        echo "➕ Ajout de OPENROUTER_API_KEY dans .env..."
        echo "" >> .env
        echo "# OpenRouter API Configuration" >> .env
        echo "OPENROUTER_API_KEY=VOTRE_CLE_API_ICI" >> .env
        echo "⚠️  IMPORTANT: Ajoutez votre clé OpenRouter dans .env"
    else
        # Vérifier si la clé n'est pas la valeur par défaut
        if grep -q "^OPENROUTER_API_KEY=VOTRE_CLE_API_ICI" .env; then
            echo "⚠️  WARNING: La clé OpenRouter API n'est pas configurée!"
            echo "   Éditez le fichier .env et remplacez VOTRE_CLE_API_ICI"
        else
            echo "✅ OPENROUTER_API_KEY est configurée"
        fi
    fi
fi

# 5. Génération d'une SESSION_SECRET sécurisée si nécessaire
if grep -q "SESSION_SECRET=CHANGEZ_MOI_EN_PRODUCTION" .env 2>/dev/null; then
    echo "🔐 Génération d'une nouvelle clé secrète..."
    NEW_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/SESSION_SECRET=CHANGEZ_MOI_EN_PRODUCTION/SESSION_SECRET=$NEW_SECRET/" .env
    echo "✅ SESSION_SECRET générée automatiquement"
fi

# 6. Vérification finale
echo ""
echo "🔍 Vérification de la configuration..."
if grep -q "VOTRE_CLE_API_ICI" .env; then
    echo "❌ ERREUR: Vous devez configurer votre clé OpenRouter API!"
    echo "   Éditez .env et remplacez VOTRE_CLE_API_ICI par votre vraie clé"
    echo ""
    echo "   Pour obtenir une clé: https://openrouter.ai/"
    exit 1
fi

# 7. Redémarrage du service
echo ""
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
nohup gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --reuse-port main:app > gunicorn.log 2>&1 &

echo ""
echo "✅ Déploiement terminé avec succès!"
echo "📊 Vérifiez les logs avec: tail -f gunicorn.log"
echo ""
echo "💡 Conseils de sécurité:"
echo "   - Ne commitez JAMAIS le fichier .env dans Git"
echo "   - Ajoutez .env dans .gitignore"
echo "   - Gardez vos clés API secrètes"
