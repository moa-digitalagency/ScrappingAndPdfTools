"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, Response, stream_with_context
import os
import uuid
import json
import time
import threading
from werkzeug.utils import secure_filename
from app.services.pdf_downloader import download_pdfs_and_zip
from app.utils.storage import cleanup_temp_file, cleanup_old_temp_files
from app.utils.progress import progress_manager

bp = Blueprint('downloader', __name__, url_prefix='/downloader')

downloads_registry = {}

@bp.route('/')
def index():
    return render_template('downloader.html')

@bp.route('/cleanup', methods=['POST'])
def cleanup():
    """Nettoie les fichiers temporaires anciens"""
    try:
        cleaned_count = cleanup_old_temp_files(current_app.config['TEMP_FOLDER'], max_age_seconds=3600)
        progress_manager.cleanup_old_sessions(max_age=3600)
        return jsonify({'success': True, 'cleaned_count': cleaned_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def download_worker(session_id, urls_list, temp_folder):
    """Worker thread pour le téléchargement en arrière-plan"""
    try:
        result = download_pdfs_and_zip(urls_list, temp_folder, session_id=session_id)
        
        if result['success']:
            download_id = str(uuid.uuid4())
            downloads_registry[download_id] = {
                'file_path': result['zip_path'],
                'filename': result['filename'],
                'session_id': session_id
            }
            progress_manager.update(session_id,
                status='ready',
                download_id=download_id,
                filename=result['filename'],
                failed_urls=result.get('failed_urls', [])
            )
    except Exception as e:
        progress_manager.update(session_id,
            status='error',
            message=f'Erreur: {str(e)}'
        )

@bp.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'success': False, 'error': 'Aucune URL fournie'}), 400
    
    urls_list = [url.strip() for url in urls if url.strip()]
    
    if not urls_list:
        return jsonify({'success': False, 'error': 'Aucune URL valide fournie'}), 400
    
    session_id = str(uuid.uuid4())
    progress_manager.create_session(session_id)
    progress_manager.update(session_id,
        status='analyzing',
        total=len(urls_list),
        message=f'Analyse de {len(urls_list)} URLs...'
    )
    
    thread = threading.Thread(
        target=download_worker,
        args=(session_id, urls_list, current_app.config['TEMP_FOLDER'])
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'total': len(urls_list)
    })

@bp.route('/progress/<session_id>')
def progress(session_id):
    """Server-Sent Events endpoint pour la progression en temps réel"""
    def generate():
        last_data_json = None
        heartbeat_counter = 0
        
        while True:
            data = progress_manager.get(session_id)
            if data:
                data_json = json.dumps(data)
                
                if data_json != last_data_json or heartbeat_counter >= 10:
                    yield f"data: {data_json}\n\n"
                    last_data_json = data_json
                    heartbeat_counter = 0
                else:
                    yield f": heartbeat\n\n"
                    heartbeat_counter += 1
                
                if data.get('status') in ['completed', 'ready', 'error']:
                    break
            else:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break
            
            time.sleep(0.3)
    
    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

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
