"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from flask import Blueprint, render_template, jsonify
import subprocess
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/git_pull', methods=['POST'])
def git_pull():
    """Effectue un git pull pour mettre à jour le code - PROTÉGÉ PAR SECRET"""
    import os
    from flask import request
    
    # Vérification du secret d'administration
    admin_secret = os.environ.get('ADMIN_SECRET')
    provided_secret = request.headers.get('X-Admin-Secret')
    if not provided_secret and request.is_json and request.json:
        provided_secret = request.json.get('admin_secret')
    
    if not admin_secret:
        logger.error("ADMIN_SECRET non configuré - git pull désactivé")
        return jsonify({
            'success': False,
            'error': 'Fonctionnalité désactivée - ADMIN_SECRET requis'
        }), 403
    
    if not provided_secret or provided_secret != admin_secret:
        logger.warning("Tentative d'accès non autorisée à git_pull")
        return jsonify({
            'success': False,
            'error': 'Accès non autorisé'
        }), 403
    
    try:
        logger.info("Début de git pull (authentifié)")
        
        # Vérifier le statut git
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if status_result.stdout.strip():
            logger.warning(f"Modifications non committées détectées:\n{status_result.stdout}")
        
        # Effectuer git pull
        pull_result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if pull_result.returncode == 0:
            logger.info(f"Git pull réussi:\n{pull_result.stdout}")
            return jsonify({
                'success': True,
                'message': 'Code mis à jour avec succès',
                'output': pull_result.stdout,
                'has_changes': status_result.stdout.strip() != ''
            })
        else:
            logger.error(f"Git pull échoué:\n{pull_result.stderr}")
            return jsonify({
                'success': False,
                'error': f'Erreur git pull: {pull_result.stderr}'
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors du git pull")
        return jsonify({
            'success': False,
            'error': 'Timeout lors de la mise à jour'
        }), 500
    except Exception as e:
        logger.error(f"Erreur lors du git pull: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500
