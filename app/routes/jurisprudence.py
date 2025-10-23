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
import zipfile
import shutil
from werkzeug.utils import secure_filename
from app.services.pdf_jurisprudence_extractor import extract_jurisprudence_from_zip
from app.utils.storage import cleanup_temp_file
from app.models import add_log
from config import Config

bp = Blueprint('jurisprudence', __name__, url_prefix='/jurisprudence')

upload_sessions = {}
jurisprudence_sessions = {}

@bp.route('/')
def index():
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        return render_template('error_api_key.html', service='jurisprudence')
    return render_template('jurisprudence.html')

@bp.route('/create_session', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        total = data.get('total', 0)
        name = data.get('name', 'Session sans nom')
        
        if total < 1:
            return jsonify({'success': False, 'error': 'Le nombre total doit être supérieur à 0'}), 400
        
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(current_app.config['TEMP_FOLDER'], f'session_{session_id}')
        os.makedirs(session_folder, exist_ok=True)
        
        upload_sessions[session_id] = {
            'id': session_id,
            'name': name,
            'target_total': total,
            'current_count': 0,
            'folder': session_folder,
            'files': []
        }
        
        add_log('jurisprudence', f'Session créée: {name} (ID: {session_id}, Target: {total} PDFs)', status='info')
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'name': name,
            'target_total': total
        })
    
    except Exception as e:
        add_log('jurisprudence', f'Erreur création session: {str(e)}', status='error')
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/get_session/<session_id>', methods=['GET'])
def get_session(session_id):
    try:
        if session_id not in upload_sessions:
            return jsonify({'success': False, 'error': 'Session non trouvée'}), 404
        
        session = upload_sessions[session_id]
        
        return jsonify({
            'success': True,
            'session_id': session['id'],
            'name': session['name'],
            'target_total': session['target_total'],
            'current_count': session['current_count'],
            'files': session['files']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/add_pdf', methods=['POST'])
def add_pdf():
    try:
        session_id = request.form.get('session_id')
        
        if not session_id or session_id not in upload_sessions:
            return jsonify({'success': False, 'error': 'Session invalide'}), 400
        
        session = upload_sessions[session_id]
        
        if session['current_count'] >= session['target_total']:
            return jsonify({'success': False, 'error': 'Nombre maximum de PDFs atteint'}), 400
        
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier PDF fourni'}), 400
        
        pdf_file = request.files['pdf_file']
        if not pdf_file.filename or pdf_file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Le fichier doit être un PDF'}), 400
        
        filename = secure_filename(pdf_file.filename)
        unique_filename = f'{uuid.uuid4()}_{filename}'
        file_path = os.path.join(session['folder'], unique_filename)
        
        pdf_file.save(file_path)
        
        session['files'].append({
            'original_name': filename,
            'stored_name': unique_filename,
            'path': file_path
        })
        session['current_count'] += 1
        
        return jsonify({
            'success': True,
            'current_count': session['current_count'],
            'filename': filename
        })
    
    except Exception as e:
        add_log('jurisprudence', f'Erreur ajout PDF: {str(e)}', status='error')
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analyze_session', methods=['POST'])
def analyze_session():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in upload_sessions:
            return jsonify({'success': False, 'error': 'Session invalide'}), 400
        
        session = upload_sessions[session_id]
        
        if session['current_count'] == 0:
            return jsonify({'success': False, 'error': 'Aucun PDF à analyser'}), 400
        
        add_log(
            'jurisprudence',
            f'Démarrage analyse session {session["name"]}: {session["current_count"]} PDFs',
            status='info'
        )
        
        zip_path = os.path.join(current_app.config['TEMP_FOLDER'], f'{session_id}_pdfs.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in session['files']:
                zipf.write(file_info['path'], arcname=file_info['stored_name'])
        
        result_excel = extract_jurisprudence_from_zip(zip_path, current_app.config['TEMP_FOLDER'], 'excel')
        result_csv = extract_jurisprudence_from_zip(zip_path, current_app.config['TEMP_FOLDER'], 'csv')
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        if os.path.exists(session['folder']):
            shutil.rmtree(session['folder'])
        
        if session_id in upload_sessions:
            del upload_sessions[session_id]
        
        if result_excel['success'] and result_csv['success']:
            result_session_id = str(uuid.uuid4())
            jurisprudence_sessions[result_session_id] = {
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
                f'Analyse terminée: {result_excel["successful"]} documents traités avec succès, {result_excel["failed"]} échecs',
                status='success'
            )
            
            return jsonify({
                'success': True,
                'session_id': result_session_id,
                'total': result_excel['total'],
                'success_count': result_excel['successful'],
                'failed_count': result_excel['failed']
            })
        else:
            error_msg = result_excel.get('error') or result_csv.get('error') or 'Erreur lors de l\'extraction'
            add_log('jurisprudence', f'Échec de l\'analyse: {error_msg}', status='error')
            return jsonify({'success': False, 'error': error_msg}), 500
    
    except Exception as e:
        add_log('jurisprudence', f'Erreur exception analyse: {str(e)}', status='error')
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
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        return f"Erreur: {str(e)}", 500

@bp.route('/process_zip', methods=['POST'])
def process_zip():
    """Route maintenue pour compatibilité ascendante"""
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
