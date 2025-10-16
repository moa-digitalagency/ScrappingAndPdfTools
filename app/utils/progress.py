"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)

class ProgressManager:
    def __init__(self, storage_dir='tmp/progress'):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        logger.info(f"ProgressManager initialisé avec stockage persistant: {self.storage_dir}")
    
    def _get_session_file(self, session_id):
        return self.storage_dir / f"{session_id}.json"
    
    def create_session(self, session_id):
        with self.lock:
            session_data = {
                'status': 'initializing',
                'total': 0,
                'current': 0,
                'batch_current': 0,
                'batch_total': 0,
                'successful': 0,
                'failed': 0,
                'message': 'Initialisation...',
                'start_time': time.time(),
                'last_update': time.time()
            }
            session_file = self._get_session_file(session_id)
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            logger.info(f"Session créée et sauvegardée: {session_id}")
    
    def update(self, session_id, **kwargs):
        with self.lock:
            session_file = self._get_session_file(session_id)
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                session_data.update(kwargs)
                session_data['last_update'] = time.time()
                with open(session_file, 'w') as f:
                    json.dump(session_data, f)
            else:
                logger.warning(f"Tentative de mise à jour d'une session inexistante: {session_id}")
    
    def get(self, session_id):
        with self.lock:
            session_file = self._get_session_file(session_id)
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
            return {}
    
    def delete(self, session_id):
        with self.lock:
            session_file = self._get_session_file(session_id)
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Session supprimée: {session_id}")
    
    def cleanup_old_sessions(self, max_age=3600):
        with self.lock:
            current_time = time.time()
            deleted_count = 0
            for session_file in self.storage_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                    if current_time - data.get('last_update', 0) > max_age:
                        session_file.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"Erreur lors du nettoyage de {session_file}: {e}")
            logger.info(f"Nettoyage: {deleted_count} sessions supprimées")
            return deleted_count

progress_manager = ProgressManager()
