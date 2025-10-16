"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

import os
import tempfile
from flask import Flask, Request
from config import Config

class StreamingRequest(Request):
    """Request personnalisée pour streaming upload direct vers disque"""
    
    @property
    def stream_factory(self):
        """Factory pour écrire uploads directement sur disque sans buffer mémoire"""
        def factory(total_content_length, filename, content_type, content_length=None):
            tmpfile = tempfile.NamedTemporaryFile(
                delete=False, 
                dir=Config.TEMP_FOLDER, 
                suffix='.upload',
                prefix='stream_'
            )
            return tmpfile
        return factory

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.request_class = StreamingRequest
    Config.init_app(app)
    
    # Initialiser la base de données des logs
    from app.models import init_db
    init_db()
    
    # Enregistrer les blueprints
    from app.routes import downloader, merger, analyzer, logs, contact
    app.register_blueprint(downloader.bp)
    app.register_blueprint(merger.bp)
    app.register_blueprint(analyzer.bp)
    app.register_blueprint(logs.bp)
    app.register_blueprint(contact.bp)
    
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app
