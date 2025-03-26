# backend/app/__init__.py
import builtins

if not hasattr(builtins, 'basestring'):
    builtins.basestring = str

import os
from flask import Flask
from flask_cors import CORS
from flask_cas import CAS 
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Loading our environment variables from .env file
db = SQLAlchemy()

# Delay imports of routes until after db is initialized
from .routes.login_routes import login_bp
from .routes.person_routes import person_bp
from .routes.course_routes import course_bp
from .routes.student_routes import student_bp
from .routes.ula_routes import ula_bp
from .routes.admin_routes import admin_bp
from .routes.queue_routes import queue_bp
from .routes.queue_entry_routes import queue_entry_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')  # TODO: Use AWS Secret Manager or something for prod
    # Enabling cors for cross origin reqs from frontend
    # Specifying extra params for cookies + session mgmt
    CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True)


    app.config['CAS_SERVER'] = 'https://secure.its.yale.edu/cas'
    app.config['CAS_AFTER_LOGIN'] = 'login.after_login'
    
    # Explicitly set ourr CAS login route so that it appends "/login/" otherwise we get incorrect URL
    app.config['CAS_LOGIN_ROUTE'] = '/cas/login'
    
    # Set the logout route later:
    app.config['CAS_LOGOUT_ROUTE'] = '/cas/logout'
    # Redirection route after logout. Not needed since we have custom logout route defined in routes, but here as a backup.
    app.config['CAS_AFTER_LOGOUT'] = os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/goodbye'

    
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'
    app.config['SESSION_COOKIE_SECURE'] = False     # set to True in production with HTTPS
    
    # Initialize Flask-CAS-NG with route prefix ("/cas")
    cas = CAS(app, '/cas')

    app.extensions['cas'] = cas


    # Initialize DB connection
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
    db.init_app(app)

    # Create the Tables if they don't already exist
    with app.app_context():
        db.create_all()

    app.register_blueprint(login_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(ula_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(queue_bp)
    app.register_blueprint(queue_entry_bp)

    return app
