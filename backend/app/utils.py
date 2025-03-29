# backend/app/utils.py
import os
import requests
from flask import session

def get_welcome_message():
    username = session.get('CAS_USERNAME')
    if username:
        return f"Hello, {username}! This is cool hehe. How tf do I sign out whoops."
    return "Hello from Jason!"


def fetch_from_yalies(netid):
    url = os.getenv("YALIES_API_URL")
    headers = {
        "Authorization": os.getenv("YALIES_API_KEY"),
        "Content-Type": "application/json"
    }
    body = {
        "filters": {
            "netid": [netid]
        }
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]  # Return first match
    return None
