"""
PdfTools
MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
www.myoneart.com
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app.services.pdf_jurisprudence_extractor import (
    extract_jurisprudence_from_zip,
    extract_jurisprudence_from_single_pdf
)
from app.utils.storage import cleanup_temp_file
from app.models import add_log

bp = Blueprint('jurisprudence', __name__, url_prefix='/jurisprudence')

jurisprudence_registry = {}

@bp.route('/')
def index():
    return render_template('jurisprudence.html')

@bp.route('/process', methods=['POST'])
def process():
    try:
        input_type = request.form.get('input_type')
        output_format = request.form.get('output_format', 'excel')
        
        if not input_type:
            return jsonify({'success': False, 'error': 'Type d\'input non spécifié'}), 400
        
        if input_type == 'zip':
            # Traitement du fichier ZIP
            if 'zip_file' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier ZIP fourni'}), 400
            
            zip_file = request.files['zip_file']
            if zip_file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier ZIP vide'}), 400
            
            # Logger le démarrage
            add_log(
                'jurisprudence',
                f'Démarrage de l\'extraction jurisprudence depuis ZIP: {zip_file.filename}',
                status='info'
            )
            
            # Sauvegarder temporairement le ZIP
            zip_filename = secure_filename(zip_file.filename or 'upload.zip')
            zip_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{uuid.uuid4()}_{zip_filename}')
            zip_file.save(zip_path)
            
            result = extract_jurisprudence_from_zip(zip_path, current_app.config['TEMP_FOLDER'], output_format)
            
            # Nettoyer le fichier ZIP temporaire
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
        elif input_type == 'single':
            # Traitement d'un seul PDF
            if 'pdf_file' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier PDF fourni'}), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier PDF vide'}), 400
            
            # Logger le démarrage
            add_log(
                'jurisprudence',
                f'Démarrage de l\'extraction jurisprudence d\'un PDF: {pdf_file.filename}',
                status='info'
            )
            
            # Sauvegarder temporairement le PDF
            pdf_filename = secure_filename(pdf_file.filename or 'upload.pdf')
            pdf_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{uuid.uuid4()}_{pdf_filename}')
            pdf_file.save(pdf_path)
            
            result = extract_jurisprudence_from_single_pdf(
                pdf_path, 
                current_app.config['TEMP_FOLDER'], 
                pdf_filename,
                output_format
            )
            
            # Nettoyer le fichier PDF temporaire
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        else:
            return jsonify({'success': False, 'error': 'Type d\'input invalide'}), 400
        
        if result['success']:
            extraction_id = str(uuid.uuid4())
            jurisprudence_registry[extraction_id] = {
                'file_path': result['output_path'],
                'filename': result['filename']
            }
            
            # Logger le succès
            add_log(
                'jurisprudence',
                f'Extraction terminée: {result["successful"]} documents traités avec succès, {result["failed"]} échecs',
                status='success'
            )
            
            return jsonify({
                'success': True,
                'extraction_id': extraction_id,
                'filename': result['filename'],
                'total': result['total'],
                'successful': result['successful'],
                'failed': result['failed'],
                'format': output_format
            })
        else:
            # Logger l'échec
            add_log(
                'jurisprudence',
                f'Échec de l\'extraction: {result.get("error", "Erreur inconnue")}',
                status='error'
            )
            return jsonify({'success': False, 'error': result.get('error', 'Erreur inconnue')}), 500
    
    except Exception as e:
        # Logger l'exception
        add_log(
            'jurisprudence',
            f'Exception lors de l\'extraction: {str(e)}',
            status='error'
        )
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/download/<extraction_id>')
def download(extraction_id):
    if extraction_id not in jurisprudence_registry:
        return "Fichier introuvable", 404
    
    file_info = jurisprudence_registry[extraction_id]
    file_path = file_info['file_path']
    filename = file_info['filename']
    
    if not os.path.exists(file_path):
        return "Fichier introuvable", 404
    
    response = send_file(file_path, as_attachment=True, download_name=filename)
    
    @response.call_on_close
    def cleanup():
        cleanup_temp_file(file_path)
        if extraction_id in jurisprudence_registry:
            del jurisprudence_registry[extraction_id]
    
    return response
