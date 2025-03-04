import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# Sample test data
test_person = {
    "net_id": "student123",
    "first_name": "John",
    "last_name": "Doe",
    "yale_email": "student123@yale.edu",
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

test_student = {
    "net_id": "student123",
    "course_id": "CPSC_323_AY24-25_S25",
    "feedback": ["Doesn't understand C", "Gaslighter"]
}

test_feedback_append = ["New feedback message"]
test_feedback_edit = "Updated feedback message"


# SETUP: Ensure test Person, Course, and Student exist before running tests
def setup_module(module):
    requests.post(f"{BASE_URL}/person", json=test_person)
    requests.post(f"{BASE_URL}/course", json=test_course)
    requests.post(f"{BASE_URL}/student", json=test_student)

# CLEANUP: Remove the data after tests
def teardown_module(module):
    requests.delete(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}")
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")
    requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")

def test_enroll_student():
    response = requests.post(f"{BASE_URL}/student", json=test_student)
    
    if response.status_code == 201:  # Successfully enrolled
        assert "enrolled" in response.json().get("message", "")
    
    elif response.status_code == 409:  # Already enrolled
        assert "already enrolled" in response.json().get("error", "")

    else:  # Unexpected response
        assert False, f"Unexpected status code: {response.status_code}, Response: {response.json()}"


def test_duplicate_enrollment():
    response = requests.post(f"{BASE_URL}/student", json=test_student)
    assert response.status_code == 409
    assert "already enrolled" in response.json().get("error", "")


def test_enroll_student_missing_fields():
    response = requests.post(f"{BASE_URL}/student", json={"net_id": "student123"})
    assert response.status_code == 400
    assert "Missing required fields" in response.json().get("error", "")


def test_get_all_students():
    response = requests.get(f"{BASE_URL}/students")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_students_by_course():
    response = requests.get(f"{BASE_URL}/students/course/{test_student['course_id']}")
    assert response.status_code in [200, 404]


def test_get_students_by_netid():
    response = requests.get(f"{BASE_URL}/students/person/{test_student['net_id']}")
    assert response.status_code in [200, 404]


def test_get_students_by_invalid_course():
    response = requests.get(f"{BASE_URL}/students/course/FAKE_COURSE")
    assert response.status_code == 404


def test_get_students_by_invalid_netid():
    response = requests.get(f"{BASE_URL}/students/person/FAKE_STUDENT")
    assert response.status_code == 404


def test_replace_feedback():
    new_feedback = {"feedback": ["Comprehensive explanations", "Good examples"]}
    response = requests.put(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback", json=new_feedback)
    assert response.status_code == 200
    assert "Feedback replaced" in response.json().get("message", "")


def test_replace_feedback_invalid():
    response = requests.put(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback", json={"feedback": "Not a list"})
    assert response.status_code == 400
    assert "Feedback must be a list" in response.json().get("error", "")


def test_append_feedback():
    response = requests.patch(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback", json={"feedback": test_feedback_append})
    assert response.status_code == 200
    assert "Feedback added" in response.json().get("message", "")


def test_append_feedback_invalid():
    response = requests.patch(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback", json={"feedback": "Not a list"})
    assert response.status_code == 400


def test_edit_feedback():
    response = requests.patch(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback/0", json={"feedback": test_feedback_edit})
    assert response.status_code == 200
    assert "updated" in response.json().get("message", "")


def test_edit_feedback_invalid_index():
    response = requests.patch(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback/99", json={"feedback": test_feedback_edit})
    assert response.status_code == 400
    assert "Invalid feedback index" in response.json().get("error", "")


def test_delete_feedback_entry():
    response = requests.delete(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback/0")
    assert response.status_code == 200
    assert "deleted" in response.json().get("message", "")


def test_delete_feedback_entry_invalid():
    response = requests.delete(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback/99")
    assert response.status_code == 400


def test_clear_feedback():
    response = requests.delete(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}/feedback")
    assert response.status_code == 200
    assert "All feedback cleared" in response.json().get("message", "")


def test_unenroll_student():
    response = requests.delete(f"{BASE_URL}/student/{test_student['net_id']}/{test_student['course_id']}")
    assert response.status_code == 200
    assert "unenrolled" in response.json().get("message", "")


def test_unenroll_invalid_student():
    response = requests.delete(f"{BASE_URL}/student/FAKE_STUDENT/{test_student['course_id']}")
    assert response.status_code == 404
    assert "not enrolled" in response.json().get("error", "")

