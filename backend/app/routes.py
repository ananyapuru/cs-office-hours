# backend/app/routes.py
from flask import Blueprint, session, jsonify
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
