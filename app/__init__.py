from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    from app.routes import downloader, merger
    app.register_blueprint(downloader.bp)
    app.register_blueprint(merger.bp)
    
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app
