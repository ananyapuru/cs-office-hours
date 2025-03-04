import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# Sample test data
test_course = {
    "course_id": "CPSC_323_AY24-25_S25",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5
}

test_queue = {
    "course_id": "CPSC_323_AY24-25_S25"
}

# SETUP: Ensure test Course exists before running tests
def setup_module(module):
    requests.post(f"{BASE_URL}/course", json=test_course)

# CLEANUP: Remove the test data after tests
def teardown_module(module):
    requests.delete(f"{BASE_URL}/queue/course/{test_queue['course_id']}/delete")
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")

def test_create_queue():
    """Test creating a queue for a course"""
    response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/create")
    assert response.status_code in [201, 409]  # Queue is created or already exists
    assert "Queue" in response.json().get("message", "") or "already exists" in response.json().get("error", "")

def test_create_duplicate_queue():
    """Test creating a duplicate queue (should fail with 409)"""
    response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/create")
    assert response.status_code == 409
    assert "already exists" in response.json().get("error", "")

def test_get_queue_status():
    """Test retrieving queue status for a course"""
    response = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/status")
    assert response.status_code == 200
    assert "is_active" in response.json()

def test_get_queue_status_nonexistent():
    """Test retrieving a queue for a non-existent course"""
    response = requests.get(f"{BASE_URL}/queue/course/FAKE_COURSE/status")
    assert response.status_code == 404
    assert "not found" in response.json().get("error", "")

def test_toggle_queue_status():
    """Test enabling/disabling the queue for a course"""
    toggle_data = {"is_active": True}
    response = requests.patch(f"{BASE_URL}/queue/course/{test_queue['course_id']}/toggle", json=toggle_data)
    assert response.status_code == 200
    assert "set to enabled" in response.json().get("message", "")

def test_toggle_queue_status_invalid():
    """Test toggling queue status with invalid data"""
    invalid_data = {"is_active": "not_a_boolean"}
    response = requests.patch(f"{BASE_URL}/queue/course/{test_queue['course_id']}/toggle", json=invalid_data)
    assert response.status_code == 400
    assert "Missing or invalid" in response.json().get("error", "")

def test_delete_queue():
    """Test deleting a queue for a course"""
    response = requests.delete(f"{BASE_URL}/queue/course/{test_queue['course_id']}/delete")
    assert response.status_code == 200
    assert "has been deleted" in response.json().get("message", "")

def test_delete_nonexistent_queue():
    """Test deleting a queue that doesn't exist"""
    response = requests.delete(f"{BASE_URL}/queue/course/FAKE_COURSE/delete")
    assert response.status_code == 404
    assert "not found" in response.json().get("error", "")
