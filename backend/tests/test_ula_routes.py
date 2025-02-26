import requests

BASE_URL = "http://127.0.0.1:5002"  

# Sample test data
test_person = {
    "net_id": "ula123",
    "first_name": "John",
    "last_name": "Doe",
    "yale_email": "ula123@yale.edu",
    "class_year": 2025,
    "residential_college": "Branford"
}

test_course = {
    "course_id": "CPSC_323_AY24-25_S25",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5,
    "queue_status": True
}

test_ula = {
    "net_id": "ula123",
    "course_id": "CPSC_323_AY24-25_S25",
    "feedback": ["Very helpful!", "Needs better examples"],
    "zoom_link": "https://yale.zoom.us/j/123456789"
}

test_feedback_append = ["Explains concepts well"]
test_feedback_edit = "Clarified a tough topic"

# SETUP: Ensure Person and Course exist before tests
def setup_module(module):
    """Ensure required records exist before running tests"""
    requests.post(f"{BASE_URL}/person", json=test_person)
    requests.post(f"{BASE_URL}/course", json=test_course)
    requests.post(f"{BASE_URL}/ula", json=test_ula)

# CLEANUP: Remove the ULA after tests
def teardown_module(module):
    """Remove test data after tests"""
    requests.delete(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}")
    requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")

def test_enroll_ula():
    response = requests.post(f"{BASE_URL}/ula", json=test_ula)
    assert response.status_code in [201, 409] 

    # Adjust assertion based on response status
    if response.status_code == 201:
        assert "assigned" in response.json().get("message", "")
    elif response.status_code == 409:
        assert "already assigned" in response.json().get("error", "")

def test_duplicate_enrollment():
    response = requests.post(f"{BASE_URL}/ula", json=test_ula)
    assert response.status_code == 409
    assert "already assigned" in response.json().get("error", "")

def test_enroll_ula_missing_fields():
    response = requests.post(f"{BASE_URL}/ula", json={"net_id": "ula123"})
    assert response.status_code == 400
    assert "Missing required fields" in response.json().get("error", "")

def test_get_all_ulas():
    response = requests.get(f"{BASE_URL}/ulas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_ulas_by_course():
    response = requests.get(f"{BASE_URL}/ulas/course/{test_ula['course_id']}")
    assert response.status_code in [200, 404]

def test_get_ulas_by_netid():
    response = requests.get(f"{BASE_URL}/ulas/person/{test_ula['net_id']}")
    assert response.status_code in [200, 404]

def test_replace_feedback():
    new_feedback = {"feedback": ["Great explanations!", "Very patient"]}
    response = requests.put(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback", json=new_feedback)
    assert response.status_code == 200
    assert "Feedback replaced" in response.json().get("message", "")

def test_replace_feedback_invalid():
    response = requests.put(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback", json={"feedback": "Not a list"})
    assert response.status_code == 400
    assert "Feedback must be a list" in response.json().get("error", "")

def test_append_feedback():
    response = requests.patch(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback", json={"feedback": test_feedback_append})
    assert response.status_code == 200
    assert "Feedback added" in response.json().get("message", "")

def test_edit_feedback():
    response = requests.patch(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback/0", json={"feedback": test_feedback_edit})
    assert response.status_code == 200
    assert "updated" in response.json().get("message", "")

def test_delete_feedback_entry():
    response = requests.delete(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback/0")
    assert response.status_code == 200
    assert "deleted" in response.json().get("message", "")

def test_clear_feedback():
    response = requests.delete(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/feedback")
    assert response.status_code == 200
    assert "All feedback cleared" in response.json().get("message", "")

def test_update_zoom_link():
    new_zoom = {"zoom_link": "https://yale.zoom.us/j/987654321"}
    response = requests.patch(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/zoom", json=new_zoom)
    assert response.status_code == 200
    assert "Zoom link updated" in response.json().get("message", "")

def test_delete_zoom_link():
    response = requests.delete(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}/zoom")
    assert response.status_code == 200
    assert "Zoom link removed" in response.json().get("message", "")

def test_unenroll_ula():
    response = requests.delete(f"{BASE_URL}/ula/{test_ula['net_id']}/{test_ula['course_id']}")
    assert response.status_code == 200
    assert "removed" in response.json().get("message", "")

def test_unenroll_invalid_ula():
    response = requests.delete(f"{BASE_URL}/ula/FAKE_ULA/{test_ula['course_id']}")
    assert response.status_code == 404
    assert "not assigned" in response.json().get("error", "")
