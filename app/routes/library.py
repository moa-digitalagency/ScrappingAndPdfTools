"""
PdfTools
MOA Digital Agency LLC
Blueprint pour la bibliothèque PDF
"""

import os
import logging
from flask import Blueprint, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from app.services.pdf_text_extractor import PdfTextExtractor
from app.models import (
    add_library_pdf, 
    get_library_pdfs, 
    get_library_pdf_by_id, 
    update_library_pdf_name,
    delete_library_pdf,
    add_log
)

logger = logging.getLogger(__name__)
bp = Blueprint('library', __name__, url_prefix='/library')

# Dossier de stockage des PDFs de la bibliothèque
LIBRARY_FOLDER = os.path.join(os.getcwd(), 'instance', 'pdf_library')
os.makedirs(LIBRARY_FOLDER, exist_ok=True)

# Dossier pour les textes extraits
EXTRACTED_TEXTS_FOLDER = os.path.join(os.getcwd(), 'instance', 'extracted_texts')
os.makedirs(EXTRACTED_TEXTS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Vérifie si le fichier est un PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    """Page principale de la bibliothèque PDF"""
    return render_template('library.html')

@bp.route('/api/pdfs', methods=['GET'])
def get_pdfs():
    """Récupère la liste des PDFs de la bibliothèque"""
    try:
        pdfs = get_library_pdfs()
        return jsonify({
            'success': True,
            'pdfs': pdfs,
            'count': len(pdfs)
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des PDFs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/upload', methods=['POST'])
def upload_pdfs():
    """Upload multiple de fichiers PDF"""
    try:
        if 'files[]' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        files = request.files.getlist('files[]')
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Générer un nom de fichier unique
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    original_name = secure_filename(file.filename or 'document.pdf')
                    filename = f"{timestamp}_{original_name}"
                    filepath = os.path.join(LIBRARY_FOLDER, filename)
                    
                    # Sauvegarder le fichier
                    file.save(filepath)
                    
                    # Obtenir la taille du fichier
                    file_size = os.path.getsize(filepath)
                    
                    # Ajouter à la base de données
                    pdf_id = add_library_pdf(
                        original_name=original_name,
                        stored_name=filename,
                        file_path=filepath,
                        file_size=file_size
                    )
                    
                    uploaded_files.append({
                        'id': pdf_id,
                        'name': original_name,
                        'size': file_size
                    })
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'upload de {file.filename}: {e}")
                    errors.append(f"{file.filename}: {str(e)}")
            else:
                errors.append(f"{file.filename}: Type de fichier non autorisé")
        
        add_log('library', f"Upload de {len(uploaded_files)} fichiers PDF", 
                details=json.dumps({'uploaded': len(uploaded_files), 'errors': len(errors)}))
        
        return jsonify({
            'success': True,
            'uploaded': uploaded_files,
            'errors': errors,
            'count': len(uploaded_files)
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/rename/<int:pdf_id>', methods=['POST'])
def rename_pdf(pdf_id):
    """Renommer un PDF"""
    try:
        data = request.get_json()
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return jsonify({
                'success': False,
                'error': 'Nom invalide'
            }), 400
        
        # Ajouter .pdf si pas présent
        if not new_name.endswith('.pdf'):
            new_name += '.pdf'
        
        success = update_library_pdf_name(pdf_id, new_name)
        
        if success:
            add_log('library', f"Renommage du PDF #{pdf_id}", details=new_name)
            return jsonify({
                'success': True,
                'name': new_name
            })
        else:
            return jsonify({
                'success': False,
                'error': 'PDF non trouvé'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur lors du renommage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/delete/<int:pdf_id>', methods=['DELETE'])
def delete_pdf(pdf_id):
    """Supprimer un PDF"""
    try:
        pdf = get_library_pdf_by_id(pdf_id)
        if not pdf:
            return jsonify({
                'success': False,
                'error': 'PDF non trouvé'
            }), 404
        
        # Supprimer le fichier physique
        if os.path.exists(pdf['file_path']):
            os.remove(pdf['file_path'])
        
        # Supprimer de la base de données
        success = delete_library_pdf(pdf_id)
        
        if success:
            add_log('library', f"Suppression du PDF #{pdf_id}", details=pdf['original_name'])
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la suppression'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extraire le texte d'un ou plusieurs PDFs"""
    try:
        data = request.get_json()
        pdf_ids = data.get('pdf_ids', [])
        
        if not pdf_ids:
            return jsonify({
                'success': False,
                'error': 'Aucun PDF sélectionné'
            }), 400
        
        results = []
        
        for pdf_id in pdf_ids:
            pdf = get_library_pdf_by_id(pdf_id)
            if not pdf:
                results.append({
                    'id': pdf_id,
                    'success': False,
                    'error': 'PDF non trouvé'
                })
                continue
            
            # Extraire le texte
            extraction_result = PdfTextExtractor.extract_text_from_pdf(pdf['file_path'])
            extraction_result['id'] = pdf_id
            extraction_result['name'] = pdf['original_name']
            
            results.append(extraction_result)
        
        add_log('library', f"Extraction de texte de {len(pdf_ids)} PDFs")
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/extract-text-all', methods=['POST'])
def extract_text_all():
    """Extraire le texte de tous les PDFs et sauvegarder dans un fichier"""
    try:
        pdfs = get_library_pdfs()
        
        if not pdfs:
            return jsonify({
                'success': False,
                'error': 'Aucun PDF dans la bibliothèque'
            }), 400
        
        # Sauvegarder dans un fichier en streaming pour éviter les problèmes de mémoire
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"extraction_complete_{timestamp}.txt"
        output_path = os.path.join(EXTRACTED_TEXTS_FOLDER, output_filename)
        
        os.makedirs(EXTRACTED_TEXTS_FOLDER, exist_ok=True)
        
        successful = 0
        failed = 0
        text_preview = ""
        
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for pdf in pdfs:
                result = PdfTextExtractor.extract_text_from_pdf(pdf['file_path'])
                if result['success']:
                    # Vérifier si du texte a été extrait
                    if result.get('total_chars', 0) > 0:
                        header = f"\n\n{'='*80}\nFICHIER: {pdf['original_name']}\n{'='*80}\n\n"
                        output_file.write(header)
                        output_file.write(result['text'])
                        
                        # Capturer un aperçu du début
                        if successful == 0 and len(text_preview) < 500:
                            text_preview = (header + result['text'])[:500]
                        
                        successful += 1
                    else:
                        # PDF sans texte extractible (probablement images uniquement)
                        failed += 1
                        logger.warning(f"Aucun texte extractible pour {pdf['original_name']}")
                else:
                    failed += 1
                    logger.warning(f"Échec de l'extraction pour {pdf['original_name']}: {result.get('error', 'Unknown error')}")
        
        # Vérifier si au moins un PDF a produit du texte
        if successful == 0:
            # Supprimer le fichier vide
            if os.path.exists(output_path):
                os.remove(output_path)
            
            add_log('library', f"Extraction complète échouée - Aucun texte extractible", 
                    details=f"Total: {len(pdfs)}, Tous ont échoué", status='error')
            
            return jsonify({
                'success': False,
                'error': 'Aucun texte n\'a pu être extrait des PDFs. Ils contiennent peut-être uniquement des images.',
                'total': len(pdfs),
                'successful': 0,
                'failed': failed
            }), 400
        
        add_log('library', f"Extraction complète de {successful} PDFs", 
                details=f"Fichier: {output_filename}")
        
        return jsonify({
            'success': True,
            'total': len(pdfs),
            'successful': successful,
            'failed': failed,
            'output_file': output_filename,
            'text_preview': text_preview + '...' if len(text_preview) >= 500 else text_preview
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction complète: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/download-extracted/<filename>')
def download_extracted(filename):
    """Télécharger un fichier texte extrait"""
    try:
        filepath = os.path.join(EXTRACTED_TEXTS_FOLDER, secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({
                'success': False,
                'error': 'Fichier non trouvé'
            }), 404
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
