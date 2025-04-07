# backend/app/routes.py
import os
import jwt
import datetime
from flask import Blueprint, session, jsonify, redirect, current_app
from flask_cas import logout as cas_logout
from ..utils import get_welcome_message, fetch_from_yalies
from app.models import Person, db

login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def index():
    return get_welcome_message()

@login_bp.route('/check')
def check():
    username = session.get('CAS_USERNAME')
    if not username:
        return jsonify({'auth': False})

    # Try fetching from Person table
    person = Person.query.filter_by(net_id=username).first()
    if person:
        return jsonify({'auth': True, 'user': {
            'netId': username,
            'firstName': person.first_name,
            'lastName': person.last_name
        }})

    # If not found, fetch from Yalies
    yalies_data = fetch_from_yalies(username)
    
    if yalies_data:
        try:
            first_name = yalies_data.get("first_name", "")
            last_name = yalies_data.get("last_name", "")
            email = yalies_data.get("email", f"{first_name.lower()}.{last_name.lower()}@yale.edu")
            class_year = yalies_data.get("year", 0)
            residential_college = yalies_data.get("college", None)
            
            person = Person(
                net_id=username,
                first_name=first_name,
                last_name=last_name,
                yale_email=email,
                class_year=class_year,
                residential_college=residential_college
            )
            db.session.add(person)
            db.session.commit()

            return jsonify({'auth': True, 'user': {
                'netId': username,
                'firstName': person.first_name,
                'lastName': person.last_name
            }})
        except Exception as e:
            db.session.rollback()
            logging.exception("Error creating person from Yalies API")
            return jsonify({'auth': True, 'user': {'netId': username}, 'error': str(e)})

    # If Yalies call fails, fallback to just netid
    return jsonify({'auth': True, 'user': {'netId': username}})

@login_bp.route('/after_login')
def after_login():
    username = session.get('CAS_USERNAME')
    # Redirecting to the frontend welcome page after successful login.
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    return redirect(f"{frontend_url}/welcome")

@login_bp.route('/logout')
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

# generate JWT
@login_bp.route('/token')
def generate_token():
    username = session.get('CAS_USERNAME')
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401

    # Get the user's record from the database
    person = Person.query.filter_by(net_id=username).first()
    if not person:
        return jsonify({'error': 'User not found'}), 404

    # Build a dictionary mapping course IDs to roles
    roles = {}

    # Populate token with roles
    def add_role(course_id, role):
        roles.setdefault(course_id, []).append(role)

    for s in person.students:
        add_role(s.course_id, "student")
    for u in person.ulas:
        add_role(u.course_id, "ULA")
    for a in person.admins:
        add_role(a.course_id, "instructor")

    # Create the payload, set expiration time = 
    payload = {
        'netid': username,
        'roles': roles,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    # hash
    token = jwt.encode(payload, current_app.secret_key, algorithm='HS256')

    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return jsonify({'token': token})