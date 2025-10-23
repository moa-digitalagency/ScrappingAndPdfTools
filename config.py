"""
PdfTools
MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
www.myoneart.com
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (pour VPS)
# Si .env n'existe pas, utilise les variables d'environnement système (pour Replit)
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'instance', 'uploads')
    TEMP_FOLDER = os.path.join(os.getcwd(), 'tmp')
    MAX_CONTENT_LENGTH = 350 * 1024 * 1024  # 350 MB max upload size
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
