# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from .routes import main_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enablingg CORS 

    app.register_blueprint(main_bp)

    return app
