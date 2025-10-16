"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

import time
from datetime import datetime
from collections import defaultdict
import threading

class ProgressManager:
    def __init__(self):
        self.sessions = defaultdict(dict)
        self.lock = threading.Lock()
    
    def create_session(self, session_id):
        with self.lock:
            self.sessions[session_id] = {
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
    
    def update(self, session_id, **kwargs):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].update(kwargs)
                self.sessions[session_id]['last_update'] = time.time()
    
    def get(self, session_id):
        with self.lock:
            return self.sessions.get(session_id, {}).copy()
    
    def delete(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def cleanup_old_sessions(self, max_age=3600):
        with self.lock:
            current_time = time.time()
            to_delete = [
                sid for sid, data in self.sessions.items()
                if current_time - data.get('last_update', 0) > max_age
            ]
            for sid in to_delete:
                del self.sessions[sid]

progress_manager = ProgressManager()
