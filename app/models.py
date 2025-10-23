"""
PdfTools
MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
www.myoneart.com
"""

from datetime import datetime
import sqlite3
import os
import json

DATABASE_PATH = os.path.join(os.getcwd(), 'instance', 'logs.db')

def init_db():
    """Initialise la base de données des logs et sessions"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            user_info TEXT,
            status TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_sessions (
            session_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            target_total INTEGER NOT NULL,
            current_count INTEGER NOT NULL,
            folder TEXT NOT NULL,
            files TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jurisprudence_sessions (
            session_id TEXT PRIMARY KEY,
            excel_path TEXT NOT NULL,
            csv_path TEXT NOT NULL,
            excel_filename TEXT NOT NULL,
            csv_filename TEXT NOT NULL,
            total INTEGER NOT NULL,
            successful INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS library_pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_log(type, action, details=None, user_info=None, status='success'):
    """
    Ajoute un log dans la base de données
    
    Args:
        type: Type de log (download, merge, analyze, system, error)
        action: Description de l'action
        details: Détails supplémentaires (optionnel)
        user_info: Information utilisateur (IP, etc.) (optionnel)
        status: Statut (success, error, warning, info)
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (timestamp, type, action, details, user_info, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            type,
            action,
            details,
            user_info,
            status
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout du log: {e}")
        return False

def get_logs(limit=100, type_filter=None, status_filter=None):
    """
    Récupère les logs de la base de données
    
    Args:
        limit: Nombre maximum de logs à récupérer
        type_filter: Filtrer par type (optionnel)
        status_filter: Filtrer par statut (optionnel)
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        
        if type_filter:
            query += ' AND type = ?'
            params.append(type_filter)
        
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            logs.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'type': row['type'],
                'action': row['action'],
                'details': row['details'],
                'user_info': row['user_info'],
                'status': row['status']
            })
        
        conn.close()
        return logs
    except Exception as e:
        print(f"Erreur lors de la récupération des logs: {e}")
        return []

def clear_old_logs(days=30):
    """Supprime les logs de plus de X jours"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        cursor.execute('''
            DELETE FROM logs
            WHERE datetime(timestamp) < datetime(?, 'unixepoch')
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    except Exception as e:
        print(f"Erreur lors du nettoyage des logs: {e}")
        return 0

def save_upload_session(session_id, name, target_total, current_count, folder, files):
    """Sauvegarde ou met à jour une session d'upload"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO upload_sessions 
            (session_id, name, target_total, current_count, folder, files, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            name,
            target_total,
            current_count,
            folder,
            json.dumps(files),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la session d'upload: {e}")
        return False

def get_upload_session(session_id):
    """Récupère une session d'upload"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM upload_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['session_id'],
                'name': row['name'],
                'target_total': row['target_total'],
                'current_count': row['current_count'],
                'folder': row['folder'],
                'files': json.loads(row['files'])
            }
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la session d'upload: {e}")
        return None

def delete_upload_session(session_id):
    """Supprime une session d'upload"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM upload_sessions WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression de la session d'upload: {e}")
        return False

def save_jurisprudence_session(session_id, excel_path, csv_path, excel_filename, csv_filename, total, successful, failed):
    """Sauvegarde une session de résultats jurisprudence"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO jurisprudence_sessions 
            (session_id, excel_path, csv_path, excel_filename, csv_filename, total, successful, failed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            excel_path,
            csv_path,
            excel_filename,
            csv_filename,
            total,
            successful,
            failed,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la session jurisprudence: {e}")
        return False

def get_jurisprudence_session(session_id):
    """Récupère une session de résultats jurisprudence"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jurisprudence_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'excel_path': row['excel_path'],
                'csv_path': row['csv_path'],
                'excel_filename': row['excel_filename'],
                'csv_filename': row['csv_filename'],
                'total': row['total'],
                'successful': row['successful'],
                'failed': row['failed']
            }
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la session jurisprudence: {e}")
        return None

def add_library_pdf(original_name, stored_name, file_path, file_size):
    """Ajoute un PDF à la bibliothèque"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO library_pdfs (original_name, stored_name, file_path, file_size, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            original_name,
            stored_name,
            file_path,
            file_size,
            datetime.now().isoformat()
        ))
        
        pdf_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pdf_id
    except Exception as e:
        print(f"Erreur lors de l'ajout du PDF: {e}")
        return None

def get_library_pdfs():
    """Récupère tous les PDFs de la bibliothèque"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM library_pdfs ORDER BY uploaded_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        pdfs = []
        for row in rows:
            pdfs.append({
                'id': row['id'],
                'original_name': row['original_name'],
                'stored_name': row['stored_name'],
                'file_path': row['file_path'],
                'file_size': row['file_size'],
                'uploaded_at': row['uploaded_at']
            })
        
        return pdfs
    except Exception as e:
        print(f"Erreur lors de la récupération des PDFs: {e}")
        return []

def get_library_pdf_by_id(pdf_id):
    """Récupère un PDF spécifique par son ID"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM library_pdfs WHERE id = ?', (pdf_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'original_name': row['original_name'],
                'stored_name': row['stored_name'],
                'file_path': row['file_path'],
                'file_size': row['file_size'],
                'uploaded_at': row['uploaded_at']
            }
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du PDF: {e}")
        return None

def update_library_pdf_name(pdf_id, new_name):
    """Met à jour le nom d'un PDF"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE library_pdfs SET original_name = ? WHERE id = ?', (new_name, pdf_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du nom: {e}")
        return False

def delete_library_pdf(pdf_id):
    """Supprime un PDF de la bibliothèque"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM library_pdfs WHERE id = ?', (pdf_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression du PDF: {e}")
        return False
