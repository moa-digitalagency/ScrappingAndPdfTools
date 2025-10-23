#!/usr/bin/env python3
"""
Script de patch pour corriger l'erreur JSON sur VPS
Usage: python3 patch_vps_jurisprudence.py

Ce script modifie automatiquement le fichier pdf_jurisprudence_extractor.py
pour corriger les problèmes de rate limiting avec l'API OpenRouter.
"""

import os
import re
import shutil
from datetime import datetime

def patch_jurisprudence_extractor():
    file_path = "app/services/pdf_jurisprudence_extractor.py"
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📦 Création d'une sauvegarde: {backup_path}")
    shutil.copy(file_path, backup_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patch 1: Ajouter import time si pas présent
    if 'import time' not in content:
        print("✅ Ajout de 'import time'")
        content = content.replace(
            'import io\nfrom config import Config',
            'import io\nimport time\nfrom config import Config'
        )
    
    # Patch 2: Réduire max_workers à 1
    print("✅ Réduction de max_workers de 3 à 1")
    content = re.sub(
        r'ThreadPoolExecutor\(max_workers=3\)',
        'ThreadPoolExecutor(max_workers=1)',
        content
    )
    
    # Patch 3: Améliorer la gestion d'erreur (lignes 91-100)
    old_api_call = '''        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90
        )
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']'''
    
    new_api_call = '''        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90
        )
        response.raise_for_status()
        
        # Vérifier si la réponse est du JSON valide
        try:
            result = response.json()
        except json.JSONDecodeError:
            # La réponse n'est pas du JSON (probablement du HTML)
            error_preview = response.text[:500] if len(response.text) > 500 else response.text
            logger.error(f"Réponse non-JSON de l'API: {error_preview}")
            raise Exception(f"L'API a renvoyé une réponse invalide (HTML au lieu de JSON). Limite de taux probablement atteinte. Réduisez le nombre de PDFs ou ajoutez des délais.")
        
        # Vérifier que la structure de la réponse est correcte
        if 'choices' not in result or not result['choices']:
            error_msg = result.get('error', {}).get('message', 'Structure de réponse invalide')
            raise Exception(f"Erreur de l'API OpenRouter: {error_msg}")
        
        ai_response = result['choices'][0]['message']['content']'''
    
    if old_api_call in content:
        print("✅ Amélioration de la gestion d'erreur API")
        content = content.replace(old_api_call, new_api_call)
    
    # Patch 4: Ajouter délai après extraction (après ligne 160 environ)
    old_return = '''    jurisprudence_data = extract_jurisprudence_data_with_ai(text, filename, api_key, pdf_path, num_pages)
    return {
        'success': True,
        'filename': filename,
        'data': jurisprudence_data
    }'''
    
    new_return = '''    jurisprudence_data = extract_jurisprudence_data_with_ai(text, filename, api_key, pdf_path, num_pages)
    
    # Ajouter un délai pour éviter de surcharger l'API
    time.sleep(2)  # Pause de 2 secondes entre chaque requête
    
    return {
        'success': True,
        'filename': filename,
        'data': jurisprudence_data
    }'''
    
    if old_return in content:
        print("✅ Ajout d'un délai de 2 secondes entre les requêtes")
        content = content.replace(old_return, new_return)
    
    # Sauvegarder le fichier modifié
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Fichier patché avec succès!")
        print(f"📁 Sauvegarde créée: {backup_path}")
        print("\n🔄 Redémarrez votre application pour appliquer les changements:")
        print("   - systemd: sudo systemctl restart votre-app")
        print("   - PM2: pm2 restart votre-app")
        print("   - Gunicorn: pkill gunicorn && gunicorn --bind 0.0.0.0:PORT main:app")
        
        return True
    else:
        print("⚠️  Aucune modification nécessaire (déjà patché?)")
        return False

if __name__ == "__main__":
    print("🔧 Patch VPS - Correction erreur JSON Jurisprudence\n")
    
    if not os.path.exists("app/services/pdf_jurisprudence_extractor.py"):
        print("❌ Erreur: fichier app/services/pdf_jurisprudence_extractor.py introuvable")
        print("   Assurez-vous d'exécuter ce script depuis la racine de votre projet")
        exit(1)
    
    try:
        success = patch_jurisprudence_extractor()
        if success:
            print("\n✅ Patch appliqué avec succès!")
            print("\n📝 Recommandations supplémentaires:")
            print("   - Analysez par lots de 30-50 PDFs au lieu de 200")
            print("   - Vérifiez votre solde OpenRouter: https://openrouter.ai/")
            print("   - En cas d'erreur persistante, réduisez max_workers à 1")
    except Exception as e:
        print(f"\n❌ Erreur lors du patch: {e}")
        exit(1)
