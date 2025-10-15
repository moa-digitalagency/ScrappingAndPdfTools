import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'instance', 'uploads')
    TEMP_FOLDER = os.path.join(os.getcwd(), 'tmp')
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
