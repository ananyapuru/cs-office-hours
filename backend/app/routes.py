# backend/app/routes.py
from flask import Blueprint
from .utils import get_welcome_message

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return get_welcome_message()
