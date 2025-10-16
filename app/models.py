"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

from datetime import datetime
import sqlite3
import os

DATABASE_PATH = os.path.join(os.getcwd(), 'instance', 'logs.db')

def init_db():
    """Initialise la base de données des logs"""
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
