#!/bin/bash

# Script de déploiement pour VPS
# Usage: ./deploy_vps.sh

set -e

echo "🚀 Début du déploiement..."

# 1. Pull les dernières modifications
echo "📥 Récupération des dernières modifications..."
git pull origin main || git pull origin master || echo "⚠️  Pas de modifications à récupérer"

# 2. Activation de l'environnement virtuel
echo "🔧 Configuration de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé, création..."
    python3 -m venv venv
fi

# Activer le venv
source venv/bin/activate

# Mettre à jour pip
echo "📦 Mise à jour de pip..."
pip install --upgrade pip

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

# 6. Créer les dossiers nécessaires
echo "📁 Création des dossiers nécessaires..."
mkdir -p instance/uploads
mkdir -p tmp

# 7. Arrêt de l'application existante
echo "🛑 Arrêt de l'application existante..."
pkill -f "gunicorn.*main:app" || echo "Aucune application en cours d'exécution"
sleep 2

# 8. Lancement de l'application avec gunicorn depuis le venv
echo "🚀 Lancement de l'application..."
echo "   Port: 5000"
echo "   Workers: 4"

# Lancer gunicorn en arrière-plan
nohup venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --reuse-port main:app > gunicorn.log 2>&1 &

# Attendre que l'application démarre
sleep 3

# Vérifier si l'application est lancée
if pgrep -f "gunicorn.*main:app" > /dev/null; then
    echo ""
    echo "✅ Déploiement terminé avec succès!"
    echo ""
    echo "📊 Informations:"
    echo "   - Application lancée sur: http://localhost:5000"
    echo "   - Logs: tail -f gunicorn.log"
    echo "   - Process ID: $(pgrep -f 'gunicorn.*main:app' | head -1)"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "   - Voir les logs: tail -f gunicorn.log"
    echo "   - Arrêter l'app: pkill -f 'gunicorn.*main:app'"
    echo "   - Redémarrer: ./deploy_vps.sh"
else
    echo ""
    echo "❌ Erreur: L'application n'a pas démarré correctement"
    echo "📊 Vérifiez les logs: tail -f gunicorn.log"
    exit 1
fi
