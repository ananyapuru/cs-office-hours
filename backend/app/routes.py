# backend/app/routes.py
from flask import Blueprint, session, jsonify, redirect, current_app
from flask_cas import logout as cas_logout
from .utils import get_welcome_message

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return get_welcome_message()

@main_bp.route('/check')
def check():
    username = session.get('CAS_USERNAME')
    if username:
        return jsonify({'auth': True, 'user': {'netId': username}})
    return jsonify({'auth': False})


@main_bp.route('/after_login')
def after_login():
    username = session.get('CAS_USERNAME')
    # Redirecting to the frontend welcome page after successful login.
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    return redirect(f"{frontend_url}/welcome")

@main_bp.route('/logout')
def my_logout():
    """
    Custom logout route that calls the CAS logout function and then redirects
    the user to the 'goodbye' page on the frontend.
    """
    # clear local session to ensure we are actually logged out and not just redirected
    session.clear()
    
    # Do a service redirect to your frontend goodbye page.
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    cas_server = current_app.config.get('CAS_SERVER', 'https://secure.its.yale.edu/cas')
    
    # Apparently, the CAS server expects a "service" parameter which == the URL to redirect to after CAS logout.
    return redirect(f"{cas_server}/logout?service={frontend_url}/goodbye")
