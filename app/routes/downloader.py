from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app.services.pdf_downloader import download_pdfs_and_zip
from app.utils.storage import cleanup_temp_file

bp = Blueprint('downloader', __name__, url_prefix='/downloader')

downloads_registry = {}

@bp.route('/')
def index():
    return render_template('downloader.html')

@bp.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'success': False, 'error': 'Aucune URL fournie'}), 400
    
    urls_list = [url.strip() for url in urls if url.strip()]
    
    if not urls_list:
        return jsonify({'success': False, 'error': 'Aucune URL valide fournie'}), 400
    
    try:
        result = download_pdfs_and_zip(urls_list, current_app.config['TEMP_FOLDER'])
        
        if result['success']:
            download_id = str(uuid.uuid4())
            downloads_registry[download_id] = {
                'file_path': result['zip_path'],
                'filename': result['filename']
            }
            
            return jsonify({
                'success': True,
                'download_id': download_id,
                'filename': result['filename'],
                'total': result['total'],
                'successful': result['successful'],
                'failed': result['failed']
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
    file_path = file_info['file_path']
    filename = file_info['filename']
    
    if not os.path.exists(file_path):
        return "Fichier introuvable", 404
    
    response = send_file(file_path, as_attachment=True, download_name=filename)
    
    @response.call_on_close
    def cleanup():
        cleanup_temp_file(file_path)
        if download_id in downloads_registry:
            del downloads_registry[download_id]
    
    return response
