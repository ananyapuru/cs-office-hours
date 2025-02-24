# backend/app/utils.py
from flask import session

def get_welcome_message():
    username = session.get('CAS_USERNAME')
    if username:
        return f"Hello, {username}! This is cool hehe. How tf do I sign out whoops."
    return "Hello from Jason!"
