import pytest
from flask import Flask, session
from app.utils import get_welcome_message, fetch_from_yalies

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.secret_key = "test_secret"
    return app

def test_get_welcome_message_authenticated(app_context):
    with app_context.test_request_context():
        session['CAS_USERNAME'] = 'jz123'
        message = get_welcome_message()
        assert "jz123" in message
        assert "Hello" in message

def test_get_welcome_message_unauthenticated(app_context):
    with app_context.test_request_context():
        session.clear()
        message = get_welcome_message()
        assert message == "Hello from Jason!"

def test_fetch_from_yalies_valid(monkeypatch):
    # Mock requests.post to return fake data
    import requests

    class MockResponse:
        def __init__(self):
            self.status_code = 200
        def json(self):
            return [{
                "netid": "abc123",
                "first_name": "Alice",
                "last_name": "Coder",
                "email": "alice.coder@yale.edu",
                "year": 2025,
                "college": "Pauli Murray"
            }]

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    result = fetch_from_yalies("abc123")
    assert result["first_name"] == "Alice"
    assert result["netid"] == "abc123"

def test_fetch_from_yalies_not_found(monkeypatch):
    import requests

    class MockResponse:
        def __init__(self):
            self.status_code = 200
        def json(self):
            return []

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())

    result = fetch_from_yalies("unknown")
    assert result is None
