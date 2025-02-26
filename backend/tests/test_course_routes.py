import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# Sample course data
test_course = {
    "course_id": "CPSC_323_AY24-25_S25",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5,
    "queue_status": True
}

def test_create_course():
    """Test creating a new course"""
    response = requests.post(f"{BASE_URL}/course", json=test_course)
    assert response.status_code == 201
    assert "Course" in response.json()["message"]

def test_create_duplicate_course():
    """Test creating a duplicate course (should fail with 409)"""
    response = requests.post(f"{BASE_URL}/course", json=test_course)
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]

def test_create_course_missing_fields():
    """Test creating a course with missing required fields"""
    data = {
        "course_id": "MATH_120_AY24-25_F25"
        # Missing required fields: academic_year, academic_term, etc.
    }
    response = requests.post(f"{BASE_URL}/course", json=data)
    assert response.status_code == 400
    assert "Missing required fields" in response.json()["error"]

def test_get_all_courses():
    """Test retrieving all courses"""
    response = requests.get(f"{BASE_URL}/course")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_course():
    """Test retrieving a specific course"""
    response = requests.get(f"{BASE_URL}/course/{test_course['course_id']}")
    assert response.status_code == 200
    assert response.json()["course_id"] == test_course["course_id"]

def test_get_nonexistent_course():
    """Test retrieving a course that does not exist"""
    response = requests.get(f"{BASE_URL}/course/FAKE_123")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]

def test_update_course():
    """Test updating a course"""
    update_data = {"enrollment_size": 120}
    response = requests.put(f"{BASE_URL}/course/{test_course['course_id']}", json=update_data)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]

def test_update_course_invalid_data():
    """Test updating a course with an invalid enrollment size (string instead of integer)"""
    update_data = {"enrollment_size": "invalid"}
    response = requests.put(f"{BASE_URL}/course/{test_course['course_id']}", json=update_data)
    assert response.status_code == 400
    assert "must be an integer" in response.json()["error"]

def test_update_nonexistent_course():
    """Test updating a nonexistent course"""
    update_data = {"enrollment_size": 150}
    response = requests.put(f"{BASE_URL}/course/FAKE_999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["error"]

def test_delete_course():
    """Test deleting a course"""
    response = requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_delete_nonexistent_course():
    """Test deleting a course that does not exist"""
    response = requests.delete(f"{BASE_URL}/course/FAKE_123")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]
