# backend/app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from flask_cas import CAS 
from dotenv import load_dotenv
from .routes import main_bp

load_dotenv()  # Loading our environment variables from .env file

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')  # TODO: Use AWS Secret Manager or something for prod
    CORS(app)  # Enabling cors for cross origin reqs

    app.config['CAS_SERVER'] = 'https://secure.its.yale.edu/cas'
    app.config['CAS_AFTER_LOGIN'] = 'main.index'
    
    # Explicitly set ourr CAS login route so that it appends "/login/" otherwise we get incorrect URL
    app.config['CAS_LOGIN_ROUTE'] = '/cas/login'
    
    # Set the logout route later:
    # app.config['CAS_LOGOUT_ROUTE'] = '/logout/'
    
    # Initialize Flask-CAS-NG with route prefix ("/cas")
    cas = CAS(app, '/cas')

    app.extensions['cas'] = cas

    app.register_blueprint(main_bp)

    return app
