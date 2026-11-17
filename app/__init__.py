"""
Phishing URL Detection System Package Initialization.
"""

import os
from flask import Flask
from app.routes import main_bp

def create_app():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        'app',
        static_folder=os.path.join(app_dir, 'static'),
        template_folder=os.path.join(app_dir, 'templates')
    )
    app.config['SECRET_KEY'] = 'phishing-url-detection-secret-key-2026'
    app.register_blueprint(main_bp)
    return app
