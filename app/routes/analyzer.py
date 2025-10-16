"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app.services.pdf_intelligent_analyzer import (
    analyze_pdfs_from_csv,
    analyze_pdfs_from_zip,
    analyze_single_pdf
)
from app.utils.storage import cleanup_temp_file

bp = Blueprint('analyzer', __name__, url_prefix='/analyzer')

analysis_registry = {}

@bp.route('/')
def index():
    return render_template('analyzer.html')

@bp.route('/process', methods=['POST'])
def process():
    try:
        input_type = request.form.get('input_type')
        
        if not input_type:
            return jsonify({'success': False, 'error': 'Type d\'input non spécifié'}), 400
        
        if input_type == 'csv':
            # Traitement du fichier CSV
            if 'csv_file' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier CSV fourni'}), 400
            
            csv_file = request.files['csv_file']
            if csv_file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier CSV vide'}), 400
            
            csv_content = csv_file.read()
            result = analyze_pdfs_from_csv(csv_content, current_app.config['TEMP_FOLDER'])
            
        elif input_type == 'zip':
            # Traitement du fichier ZIP
            if 'zip_file' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier ZIP fourni'}), 400
            
            zip_file = request.files['zip_file']
            if zip_file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier ZIP vide'}), 400
            
            # Sauvegarder temporairement le ZIP
            zip_filename = secure_filename(zip_file.filename or 'upload.zip')
            zip_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{uuid.uuid4()}_{zip_filename}')
            zip_file.save(zip_path)
            
            result = analyze_pdfs_from_zip(zip_path, current_app.config['TEMP_FOLDER'])
            
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
            
            # Sauvegarder temporairement le PDF
            pdf_filename = secure_filename(pdf_file.filename or 'upload.pdf')
            pdf_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{uuid.uuid4()}_{pdf_filename}')
            pdf_file.save(pdf_path)
            
            result = analyze_single_pdf(pdf_path, current_app.config['TEMP_FOLDER'], pdf_filename)
            
            # Nettoyer le fichier PDF temporaire
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        else:
            return jsonify({'success': False, 'error': 'Type d\'input invalide'}), 400
        
        if result['success']:
            analysis_id = str(uuid.uuid4())
            analysis_registry[analysis_id] = {
                'file_path': result['excel_path'],
                'filename': result['filename']
            }
            
            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'filename': result['filename'],
                'total': result['total'],
                'successful': result['successful'],
                'failed': result['failed']
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Erreur inconnue')}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/download/<analysis_id>')
def download(analysis_id):
    if analysis_id not in analysis_registry:
        return "Fichier introuvable", 404
    
    file_info = analysis_registry[analysis_id]
    file_path = file_info['file_path']
    filename = file_info['filename']
    
    if not os.path.exists(file_path):
        return "Fichier introuvable", 404
    
    response = send_file(file_path, as_attachment=True, download_name=filename)
    
    @response.call_on_close
    def cleanup():
        cleanup_temp_file(file_path)
        if analysis_id in analysis_registry:
            del analysis_registry[analysis_id]
    
    return response
