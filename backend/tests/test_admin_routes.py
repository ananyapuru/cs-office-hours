import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# Sample test data
test_person = {
    "net_id": "admin123",
    "first_name": "Admin",
    "last_name": "User",
    "yale_email": "admin123@yale.edu",
    "class_year": 2025,
    "residential_college": "Pierson"
}

test_course = {
    "course_id": "CPSC_323_AY24-25_S25",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5,
    "queue_status": True
}

test_admin = {
    "net_id": "admin123",
    "course_id": "CPSC_323_AY24-25_S25"
}

def setup_module():
    """Ensure the required Person and Course exist before tests"""
    requests.post(f"{BASE_URL}/person", json=test_person)
    requests.post(f"{BASE_URL}/course", json=test_course)

def teardown_module():
    """Cleanup: Remove test Person and Course after tests"""
    requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")

def test_assign_admin():
    """Test assigning an admin to a course"""
    response = requests.post(f"{BASE_URL}/admin", json=test_admin)
    assert response.status_code in [201, 409]

    if response.status_code == 201:
        assert "assigned" in response.json().get("message", "")
    elif response.status_code == 409:
        assert "already assigned" in response.json().get("error", "")

def test_duplicate_assignment():
    """Test assigning the same admin again (should fail)"""
    response = requests.post(f"{BASE_URL}/admin", json=test_admin)
    assert response.status_code == 409
    assert "already assigned" in response.json().get("error", "")

def test_assign_admin_missing_fields():
    """Test assigning an admin with missing fields (should fail)"""
    response = requests.post(f"{BASE_URL}/admin", json={"net_id": "admin123"})
    assert response.status_code == 400
    assert "Missing required fields" in response.json().get("error", "")

def test_get_all_admins():
    """Test retrieving all admins"""
    response = requests.get(f"{BASE_URL}/admins")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_admins_by_course():
    """Test retrieving all admins assigned to a course"""
    response = requests.get(f"{BASE_URL}/admins/course/{test_admin['course_id']}")
    assert response.status_code in [200, 404]

def test_get_admins_by_netid():
    """Test retrieving all courses assigned to an admin"""
    response = requests.get(f"{BASE_URL}/admins/person/{test_admin['net_id']}")
    assert response.status_code in [200, 404]

def test_get_admins_by_invalid_course():
    """Test retrieving admins from a non-existent course (should fail)"""
    response = requests.get(f"{BASE_URL}/admins/course/FAKE_COURSE")
    assert response.status_code == 404
    assert "No Admins found" in response.json().get("error", "")

def test_get_admins_by_invalid_netid():
    """Test retrieving courses for a non-existent admin (should fail)"""
    response = requests.get(f"{BASE_URL}/admins/person/FAKE_ADMIN")
    assert response.status_code == 404
    assert "No courses found" in response.json().get("error", "")

def test_unassign_admin():
    """Test unassigning an admin from a course"""
    response = requests.delete(f"{BASE_URL}/admin/{test_admin['net_id']}/{test_admin['course_id']}")
    assert response.status_code == 200
    assert "removed" in response.json().get("message", "")

def test_unassign_invalid_admin():
    """Test unassigning a non-existent admin (should fail)"""
    response = requests.delete(f"{BASE_URL}/admin/FAKE_ADMIN/{test_admin['course_id']}")
    assert response.status_code == 404
    assert "not assigned" in response.json().get("error", "")
