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
import zipfile
from werkzeug.utils import secure_filename
from app.services.pdf_merger import merge_pdfs_from_zip
from app.utils.storage import cleanup_temp_file

bp = Blueprint('merger', __name__, url_prefix='/merger')

downloads_registry = {}

@bp.route('/')
def index():
    return render_template('merger.html')

@bp.route('/process', methods=['POST'])
def process():
    if 'zip_file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['zip_file']
    
    if not file.filename or file.filename == '':
        return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
    
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'success': False, 'error': 'Le fichier doit être un ZIP'}), 400
    
    try:
        filename = secure_filename(file.filename) if file.filename else 'upload.zip'
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '_' + filename)
        
        chunk_size = 8192
        with open(upload_path, 'wb') as f:
            while True:
                chunk = file.stream.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        
        result = merge_pdfs_from_zip(upload_path, current_app.config['TEMP_FOLDER'])
        
        cleanup_temp_file(upload_path)
        
        if result['success']:
            unique_id = str(uuid.uuid4())[:8]
            zip_filename = f'merged_output_{unique_id}.zip'
            zip_path = os.path.join(current_app.config['TEMP_FOLDER'], zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(result['pdf_path'], result['pdf_filename'])
                if result.get('has_analysis') and result.get('excel_path'):
                    zipf.write(result['excel_path'], result['excel_filename'])
            
            cleanup_temp_file(result['pdf_path'])
            if result.get('excel_path'):
                cleanup_temp_file(result['excel_path'])
            
            download_id = str(uuid.uuid4())
            downloads_registry[download_id] = {
                'zip_path': zip_path,
                'zip_filename': zip_filename
            }
            
            return jsonify({
                'success': True,
                'download_id': download_id,
                'zip_filename': zip_filename,
                'total_pdfs': result['total_pdfs'],
                'total_pages': result['total_pages']
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Erreur inconnue')}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/download/<download_id>')
def download(download_id):
    if download_id not in downloads_registry:
        return "Fichier introuvable", 404
    
    file_info = downloads_registry[download_id]
    zip_path = file_info['zip_path']
    zip_filename = file_info['zip_filename']
    
    if not os.path.exists(zip_path):
        return "Fichier introuvable", 404
    
    response = send_file(zip_path, as_attachment=True, download_name=zip_filename)
    
    @response.call_on_close
    def cleanup():
        cleanup_temp_file(zip_path)
        downloads_registry.pop(download_id, None)
    
    return response
