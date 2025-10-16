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
import logging
from werkzeug.utils import secure_filename
from app.services.pdf_downloader import download_pdfs_and_zip
from app.utils.storage import cleanup_temp_file, cleanup_old_temp_files
from app.utils.progress import progress_manager
from app.models import add_log

logger = logging.getLogger(__name__)
bp = Blueprint('downloader', __name__, url_prefix='/downloader')

downloads_registry = {}
batches_registry = {}

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
            
            # Logger le succès
            failed_count = len(result.get('failed_urls', []))
            success_count = result.get('success_count', 0)
            add_log(
                'download',
                f'Téléchargement ZIP terminé: {success_count} fichiers réussis, {failed_count} échecs',
                status='success'
            )
    except Exception as e:
        progress_manager.update(session_id,
            status='error',
            message=f'Erreur: {str(e)}'
        )
        
        # Logger l'erreur
        add_log(
            'download',
            f'Erreur lors du téléchargement: {str(e)}',
            status='error'
        )

@bp.route('/prepare_batches', methods=['POST'])
def prepare_batches():
    """Prépare les lots sans les télécharger"""
    logger.info("=" * 80)
    logger.info("NOUVELLE REQUÊTE /downloader/prepare_batches")
    
    data = request.get_json()
    urls = data.get('urls', [])
    batch_size = data.get('batch_size', 100)
    
    if not urls:
        return jsonify({'success': False, 'error': 'Aucune URL fournie'}), 400
    
    urls_list = [url.strip() for url in urls if url.strip()]
    
    if not urls_list:
        return jsonify({'success': False, 'error': 'Aucune URL valide fournie'}), 400
    
    session_id = str(uuid.uuid4())
    logger.info(f"Session créée: {session_id} avec {len(urls_list)} URLs et lots de {batch_size}")
    
    # Découper en lots
    batches = {}
    total_batches = (len(urls_list) + batch_size - 1) // batch_size
    
    for i in range(total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(urls_list))
        batch_num = i + 1
        
        batches[batch_num] = {
            'start': start_idx + 1,
            'end': end_idx,
            'count': end_idx - start_idx,
            'urls': urls_list[start_idx:end_idx],
            'completed': False,
            'download_id': None
        }
    
    # Créer un dossier de session persistant
    session_folder = os.path.join(current_app.config['TEMP_FOLDER'], f'session_{session_id}')
    os.makedirs(session_folder, exist_ok=True)
    
    batches_registry[session_id] = {
        'total_urls': len(urls_list),
        'batch_size': batch_size,
        'batches': batches,
        'session_folder': session_folder
    }
    
    # Sauvegarder la session sur disque (persistant)
    session_file = os.path.join(session_folder, 'session.json')
    with open(session_file, 'w') as f:
        json.dump({
            'session_id': session_id,
            'total_urls': len(urls_list),
            'batch_size': batch_size,
            'total_batches': total_batches,
            'batches': {str(k): {**v, 'urls': v['urls']} for k, v in batches.items()}
        }, f)
    
    logger.info(f"Lots préparés: {total_batches} lots pour session {session_id}")
    logger.info(f"Session sauvegardée dans {session_folder}")
    logger.info("=" * 80)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'total_urls': len(urls_list),
        'total_batches': total_batches,
        'batches': batches
    })

@bp.route('/download_batch', methods=['POST'])
def download_batch():
    """Télécharge un lot spécifique"""
    logger.info("=" * 80)
    logger.info("NOUVELLE REQUÊTE /downloader/download_batch")
    
    data = request.get_json()
    session_id = data.get('session_id')
    batch_num = data.get('batch_num')
    
    if not session_id or session_id not in batches_registry:
        return jsonify({'success': False, 'error': 'Session invalide'}), 400
    
    batch_data = batches_registry[session_id]['batches'].get(batch_num)
    if not batch_data:
        return jsonify({'success': False, 'error': 'Lot invalide'}), 400
    
    batch_session_id = str(uuid.uuid4())
    session_folder = batches_registry[session_id]['session_folder']
    
    logger.info(f"Téléchargement lot {batch_num} de session {session_id}, batch_session {batch_session_id}")
    
    progress_manager.create_session(batch_session_id)
    progress_manager.update(batch_session_id,
        status='analyzing',
        total=batch_data['count'],
        message=f"Téléchargement du lot {batch_num}..."
    )
    
    # Stocker dans le dossier de session
    thread = threading.Thread(
        target=download_worker,
        args=(batch_session_id, batch_data['urls'], session_folder)
    )
    thread.daemon = True
    thread.start()
    
    logger.info(f"Thread démarré pour lot {batch_num}")
    logger.info("=" * 80)
    
    return jsonify({
        'success': True,
        'batch_session_id': batch_session_id,
        'batch_num': batch_num
    })

@bp.route('/start_auto_download', methods=['POST'])
def start_auto_download():
    """Lance automatiquement tous les lots séquentiellement"""
    logger.info("=" * 80)
    logger.info("NOUVELLE REQUÊTE /downloader/start_auto_download")
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in batches_registry:
        return jsonify({'success': False, 'error': 'Session invalide'}), 400
    
    auto_session_id = str(uuid.uuid4())
    
    def auto_download_worker(main_session_id, auto_sess_id):
        """Worker qui lance séquentiellement tous les lots"""
        try:
            session_data = batches_registry[main_session_id]
            batches = session_data['batches']
            session_folder = session_data['session_folder']
            total_batches = len(batches)
            
            progress_manager.create_session(auto_sess_id)
            
            for batch_num in sorted(batches.keys()):
                batch_data = batches[batch_num]
                
                # Créer une sous-session pour ce lot
                batch_session_id = str(uuid.uuid4())
                
                logger.info(f"AUTO: Démarrage lot {batch_num}/{total_batches}")
                
                progress_manager.update(auto_sess_id,
                    status='processing',
                    current=batch_num,
                    total=total_batches,
                    message=f"Téléchargement automatique - Lot {batch_num}/{total_batches}"
                )
                
                # Télécharger ce lot
                result = download_pdfs_and_zip(
                    batch_data['urls'],
                    session_folder,
                    session_id=batch_session_id
                )
                
                if result['success']:
                    download_id = str(uuid.uuid4())
                    downloads_registry[download_id] = {
                        'file_path': result['zip_path'],
                        'filename': result['filename'],
                        'session_id': batch_session_id
                    }
                    
                    # Mettre à jour le batch
                    batch_data['completed'] = True
                    batch_data['download_id'] = download_id
                    
                    # Sauvegarder la progression dans le fichier session
                    session_file = os.path.join(session_folder, 'session.json')
                    with open(session_file, 'r') as f:
                        session_info = json.load(f)
                    session_info['batches'][str(batch_num)]['completed'] = True
                    session_info['batches'][str(batch_num)]['download_id'] = download_id
                    with open(session_file, 'w') as f:
                        json.dump(session_info, f)
                    
                    logger.info(f"AUTO: Lot {batch_num} terminé avec succès")
                else:
                    logger.error(f"AUTO: Lot {batch_num} échoué")
            
            # Tous les lots terminés
            progress_manager.update(auto_sess_id,
                status='ready',
                current=total_batches,
                total=total_batches,
                message=f"Tous les lots téléchargés ({total_batches}/{total_batches})"
            )
            
            logger.info(f"AUTO: Tous les lots terminés pour session {main_session_id}")
            
        except Exception as e:
            logger.error(f"AUTO: Erreur globale: {str(e)}", exc_info=True)
            progress_manager.update(auto_sess_id,
                status='error',
                message=f"Erreur: {str(e)}"
            )
    
    thread = threading.Thread(
        target=auto_download_worker,
        args=(session_id, auto_session_id)
    )
    thread.daemon = True
    thread.start()
    
    logger.info(f"Thread automatique démarré pour session {session_id}")
    logger.info("=" * 80)
    
    return jsonify({
        'success': True,
        'auto_session_id': auto_session_id,
        'message': 'Téléchargement automatique démarré'
    })

@bp.route('/list_sessions', methods=['GET'])
def list_sessions():
    """Liste toutes les sessions disponibles"""
    try:
        temp_folder = current_app.config['TEMP_FOLDER']
        sessions = []
        
        for item in os.listdir(temp_folder):
            if item.startswith('session_'):
                session_folder = os.path.join(temp_folder, item)
                session_file = os.path.join(session_folder, 'session.json')
                
                if os.path.exists(session_file):
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        
                        # Compter les lots complétés
                        completed_count = sum(1 for b in session_data['batches'].values() if b.get('completed', False))
                        
                        sessions.append({
                            'session_id': session_data['session_id'],
                            'total_urls': session_data['total_urls'],
                            'total_batches': session_data['total_batches'],
                            'completed_batches': completed_count,
                            'batch_size': session_data['batch_size']
                        })
        
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        logger.error(f"Erreur liste sessions: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/load_session/<session_id>', methods=['GET'])
def load_session(session_id):
    """Charge une session existante"""
    try:
        temp_folder = current_app.config['TEMP_FOLDER']
        session_folder = os.path.join(temp_folder, f'session_{session_id}')
        session_file = os.path.join(session_folder, 'session.json')
        
        if not os.path.exists(session_file):
            return jsonify({'success': False, 'error': 'Session introuvable'}), 404
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Recharger dans le registre
        batches = {}
        for batch_num_str, batch_info in session_data['batches'].items():
            batch_num = int(batch_num_str)
            batches[batch_num] = batch_info
            
            # Recharger les download_ids dans le registre
            if batch_info.get('download_id') and batch_info.get('completed'):
                download_id = batch_info['download_id']
                # Trouver le fichier ZIP correspondant
                zip_files = [f for f in os.listdir(session_folder) if f.endswith('.zip')]
                for zip_file in zip_files:
                    zip_path = os.path.join(session_folder, zip_file)
                    downloads_registry[download_id] = {
                        'file_path': zip_path,
                        'filename': zip_file,
                        'session_id': session_id
                    }
        
        batches_registry[session_id] = {
            'total_urls': session_data['total_urls'],
            'batch_size': session_data['batch_size'],
            'batches': batches,
            'session_folder': session_folder
        }
        
        logger.info(f"Session {session_id} chargée avec succès")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_urls': session_data['total_urls'],
            'total_batches': session_data['total_batches'],
            'batches': batches
        })
        
    except Exception as e:
        logger.error(f"Erreur chargement session: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/merge_batches', methods=['POST'])
def merge_batches():
    """Fusionne tous les lots téléchargés en un seul ZIP"""
    logger.info("=" * 80)
    logger.info("NOUVELLE REQUÊTE /downloader/merge_batches")
    
    data = request.get_json()
    session_id = data.get('session_id')
    download_ids = data.get('download_ids', [])
    
    if not session_id or session_id not in batches_registry:
        return jsonify({'success': False, 'error': 'Session invalide'}), 400
    
    if not download_ids:
        return jsonify({'success': False, 'error': 'Aucun lot à fusionner'}), 400
    
    try:
        import zipfile
        
        # Créer le ZIP final
        final_zip_id = str(uuid.uuid4())[:8]
        final_zip_name = f'pdfs_merged_{final_zip_id}.zip'
        final_zip_path = os.path.join(current_app.config['TEMP_FOLDER'], final_zip_name)
        
        total_files = 0
        
        with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as final_zipf:
            for download_id in download_ids:
                if download_id in downloads_registry:
                    batch_zip_path = downloads_registry[download_id]['file_path']
                    
                    if os.path.exists(batch_zip_path):
                        logger.info(f"Extraction de {batch_zip_path}")
                        
                        with zipfile.ZipFile(batch_zip_path, 'r') as batch_zipf:
                            for file_info in batch_zipf.filelist:
                                file_data = batch_zipf.read(file_info.filename)
                                final_zipf.writestr(file_info.filename, file_data)
                                total_files += 1
        
        download_id = str(uuid.uuid4())
        downloads_registry[download_id] = {
            'file_path': final_zip_path,
            'filename': final_zip_name,
            'session_id': session_id
        }
        
        logger.info(f"Fusion terminée: {total_files} fichiers dans {final_zip_name}")
        logger.info("=" * 80)
        
        add_log(
            'download',
            f'Fusion terminée: {total_files} fichiers PDF fusionnés',
            status='success'
        )
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'filename': final_zip_name,
            'total_files': total_files,
            'total_urls': batches_registry[session_id]['total_urls']
        })
        
    except Exception as e:
        logger.error(f"Erreur fusion: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/progress/<session_id>')
def progress(session_id):
    """Server-Sent Events endpoint pour la progression en temps réel"""
    logger.info(f"SSE: Nouvelle connexion pour session {session_id}")
    
    def generate():
        last_data_json = None
        heartbeat_counter = 0
        iteration = 0
        
        while True:
            iteration += 1
            data = progress_manager.get(session_id)
            
            if data:
                data_json = json.dumps(data)
                
                if data_json != last_data_json or heartbeat_counter >= 10:
                    logger.debug(f"SSE [{session_id}] Iter {iteration}: Envoi données - {data_json[:100]}...")
                    yield f"data: {data_json}\n\n"
                    last_data_json = data_json
                    heartbeat_counter = 0
                else:
                    logger.debug(f"SSE [{session_id}] Iter {iteration}: Heartbeat")
                    yield f": heartbeat\n\n"
                    heartbeat_counter += 1
                
                if data.get('status') in ['completed', 'ready', 'error']:
                    logger.info(f"SSE [{session_id}] Terminé avec status: {data.get('status')}")
                    break
            else:
                logger.warning(f"SSE [{session_id}] Session non trouvée!")
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break
            
            time.sleep(0.3)
        
        logger.info(f"SSE [{session_id}] Connexion fermée après {iteration} itérations")
    
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
