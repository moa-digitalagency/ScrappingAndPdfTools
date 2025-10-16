from flask import Blueprint, render_template, request, jsonify, send_file, current_app, Response, stream_with_context
import os
import uuid
import json
import time
import threading
from werkzeug.utils import secure_filename
from app.services.pdf_downloader import download_pdfs_and_zip
from app.utils.storage import cleanup_temp_file
from app.utils.progress import progress_manager

bp = Blueprint('downloader', __name__, url_prefix='/downloader')

downloads_registry = {}

@bp.route('/')
def index():
    return render_template('downloader.html')

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
                filename=result['filename']
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
        while True:
            data = progress_manager.get(session_id)
            if data:
                yield f"data: {json.dumps(data)}\n\n"
                
                if data.get('status') in ['completed', 'ready', 'error']:
                    break
            else:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break
            
            time.sleep(0.5)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

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
