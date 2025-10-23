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
from app.services.pdf_jurisprudence_extractor import extract_jurisprudence_from_zip
from app.utils.storage import cleanup_temp_file
from app.models import add_log

bp = Blueprint('jurisprudence', __name__, url_prefix='/jurisprudence')

jurisprudence_sessions = {}

@bp.route('/')
def index():
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        return render_template('error_api_key.html', service='jurisprudence')
    return render_template('jurisprudence.html')

@bp.route('/process_zip', methods=['POST'])
def process_zip():
    try:
        if 'zip_file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier ZIP fourni'}), 400
        
        zip_file = request.files['zip_file']
        if zip_file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier ZIP vide'}), 400
        
        add_log(
            'jurisprudence',
            f'Démarrage de l\'extraction jurisprudence depuis ZIP: {zip_file.filename}',
            status='info'
        )
        
        zip_filename = secure_filename(zip_file.filename or 'upload.zip')
        zip_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{uuid.uuid4()}_{zip_filename}')
        zip_file.save(zip_path)
        
        result_excel = extract_jurisprudence_from_zip(zip_path, current_app.config['TEMP_FOLDER'], 'excel')
        result_csv = extract_jurisprudence_from_zip(zip_path, current_app.config['TEMP_FOLDER'], 'csv')
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        if result_excel['success'] and result_csv['success']:
            session_id = str(uuid.uuid4())
            jurisprudence_sessions[session_id] = {
                'excel_path': result_excel['output_path'],
                'csv_path': result_csv['output_path'],
                'excel_filename': result_excel['filename'],
                'csv_filename': result_csv['filename'],
                'total': result_excel['total'],
                'successful': result_excel['successful'],
                'failed': result_excel['failed']
            }
            
            add_log(
                'jurisprudence',
                f'Extraction terminée: {result_excel["successful"]} documents traités avec succès, {result_excel["failed"]} échecs',
                status='success'
            )
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'total': result_excel['total'],
                'success_count': result_excel['successful'],
                'failed_count': result_excel['failed']
            })
        else:
            error_msg = result_excel.get('error') or result_csv.get('error') or 'Erreur lors de l\'extraction'
            add_log('jurisprudence', f'Échec de l\'extraction: {error_msg}', status='error')
            return jsonify({'success': False, 'error': error_msg}), 500
    
    except Exception as e:
        add_log('jurisprudence', f'Erreur exception: {str(e)}', status='error')
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/download/<session_id>/<format_type>')
def download(session_id, format_type):
    try:
        if session_id not in jurisprudence_sessions:
            return "Session non trouvée", 404
        
        session = jurisprudence_sessions[session_id]
        
        if format_type == 'excel':
            file_path = session['excel_path']
            filename = session['excel_filename']
        elif format_type == 'csv':
            file_path = session['csv_path']
            filename = session['csv_filename']
        else:
            return "Format invalide", 400
        
        if not os.path.exists(file_path):
            return "Fichier non trouvé", 404
        
        def cleanup():
            cleanup_temp_file(file_path)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        return f"Erreur: {str(e)}", 500
