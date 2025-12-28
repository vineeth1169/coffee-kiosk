from flask import Flask, render_template
from .config import DevConfig, ProdConfig
from .extensions import db, migrate, socketio
from .api import bp as api_bp
import os


import os

def create_app(config_name=None):
    # Ensure templates/static are resolved from the project root (one level up from src)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode='eventlet')

    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
