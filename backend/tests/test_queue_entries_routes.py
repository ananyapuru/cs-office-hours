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
    "course_staff_size": 5
}

test_queue = {
    "course_id": test_course["course_id"]
}

# Base queue entry data (in-person default)
test_queue_entry = {
    "net_id": test_person["net_id"],
    "topic_name": "Need help with recursion",
    "mode": "in-person"
}

# Test entry data with virtual mode specified
test_queue_entry_virtual = {
    "net_id": test_person["net_id"],
    "topic_name": "Need help with recursion (virtual)",
    "mode": "virtual"
}

test_ula = {
    "net_id": "ula001",
    "first_name": "Alice",
    "last_name": "Brown",
    "yale_email": "ula001@yale.edu",
    "class_year": 2024,
    "residential_college": "Jonathan Edwards"
}

test_ula_assignment = {
    "net_id": test_ula["net_id"],
    "course_id": test_course["course_id"]
}

# SETUP: Ensure test Person, Course, Queue, and QueueEntry exist before running tests
def setup_module(module):
    """Setup test data before running tests"""
    requests.post(f"{BASE_URL}/person", json=test_person)
    requests.post(f"{BASE_URL}/person", json=test_ula)
    requests.post(f"{BASE_URL}/course", json=test_course)
    
    # Ensure student is enrolled
    student_enrollment_response = requests.post(
        f"{BASE_URL}/student", 
        json={"net_id": test_person["net_id"], "course_id": test_course["course_id"]}
    )
    assert student_enrollment_response.status_code in [201, 409], f"Student enrollment failed: {student_enrollment_response.json()}"

    # Ensure queue is created for the course
    queue_response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/create")
    assert queue_response.status_code in [201, 400], f"Queue creation failed: {queue_response.json()}"

    # Assign ULA to course
    ula_response = requests.post(f"{BASE_URL}/ula", json=test_ula_assignment)
    assert ula_response.status_code in [201, 400], f"ULA assignment failed: {ula_response.json()}"

# CLEANUP: Remove test data after tests
def teardown_module(module):
    """Delete test data after running tests"""
    requests.delete(f"{BASE_URL}/queue/course/{test_queue['course_id']}/delete")
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")
    requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")
    requests.delete(f"{BASE_URL}/person/nonexistent_netid")
    requests.delete(f"{BASE_URL}/person/{test_ula['net_id']}")

def test_add_to_queue_default_mode():
    """Test adding a student to the queue without specifying mode should default to 'in-person'"""
    response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/add", json=test_queue_entry)
    assert response.status_code == 201, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    # Now retrieve the entry to verify the mode.
    entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_person['net_id']}").json()
    assert entries, "Expected at least one queue entry"
    # Check that the first entry's mode is 'in-person'
    assert entries[0].get("mode") == "in-person"

def test_add_to_queue_virtual_mode():
    """Test adding a student to the queue with mode 'virtual'"""

    entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_person['net_id']}").json()
    for entry in entries:
        requests.delete(f"{BASE_URL}/queue/entry/{entry['queue_entry_id']}")
        
    response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/add", json=test_queue_entry_virtual)
    assert response.status_code == 201, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    # Retrieve the entries and filter for the one with virtual mode.
    entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_person['net_id']}").json()
    virtual_entries = [e for e in entries if e.get("mode") == "virtual"]
    assert virtual_entries, "Expected at least one virtual queue entry"

def test_add_duplicate_to_queue():
    """Test adding a duplicate queue entry (should fail with 409)"""
    response = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/add", json=test_queue_entry)
    assert response.status_code == 409
    assert "already has an active queue entry" in response.json().get("error", "")

def test_get_queue_by_student():
    """Test retrieving queue entries for a student"""
    response = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_queue_entry['net_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_queue_by_nonexistent_student():
    """Test retrieving queue entries for a student that does not exist in the system"""
    response = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/nonexistent_netid")
    assert response.status_code == 404
    # Check that the error message indicates that the student wasn't found.
    assert "student" in response.json().get("error", "").lower()

def test_assign_ula():
    """Test assigning a ULA to a queue entry"""
    queue_entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_queue_entry['net_id']}").json()
    assert queue_entries, "No queue entries found; ensure setup_module() ran correctly"
    
    queue_entry_id = queue_entries[0]["queue_entry_id"]
    
    response = requests.patch(f"{BASE_URL}/queue/entry/{queue_entry_id}/assign", json={"ula_net_id": test_ula["net_id"]})
    assert response.status_code == 200, f"Assign ULA failed: {response.json()}"
    assert "assigned to queue entry" in response.json().get("message", "")

def test_complete_queue_entry():
    """Test marking a queue entry as completed"""
    queue_entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_queue_entry['net_id']}").json()
    assert queue_entries, "No queue entries found; ensure setup_module() ran correctly"
    
    queue_entry_id = queue_entries[0]["queue_entry_id"]
    
    # Ensure ULA is assigned before marking as completed
    assign_response = requests.patch(f"{BASE_URL}/queue/entry/{queue_entry_id}/assign", json={"ula_net_id": test_ula["net_id"]})
    assert assign_response.status_code == 200, f"Assign ULA failed: {assign_response.json()}"

    # Mark queue entry as completed
    response = requests.patch(f"{BASE_URL}/queue/entry/{queue_entry_id}/complete")
    assert response.status_code == 200, f"Complete queue entry failed: {response.json()}"
    assert "marked as completed" in response.json().get("message", "")

def test_update_topic_name():
    """Test updating the topic name of a queue entry that is not completed."""
    # Retrieve the student's queue entries for the course.
    queue_entries = requests.get(
        f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_queue_entry['net_id']}"
    ).json()
    
    # Look for an entry that is not completed.
    entry_to_update = None
    for entry in queue_entries:
        if entry.get("status") in ["In Queue", "In Progress"]:
            entry_to_update = entry
            break
    
    # If no modifiable entry is found, create a new one.
    if not entry_to_update:
        new_entry_data = {
            "net_id": test_queue_entry["net_id"],
            "topic_name": "Need help with recursion (for topic update)"
        }
        add_response = requests.post(
            f"{BASE_URL}/queue/course/{test_queue['course_id']}/add", json=new_entry_data
        )
        assert add_response.status_code == 201, f"Failed to add new queue entry: {add_response.json()}"
        entry_to_update = {"queue_entry_id": add_response.json()["queue_entry_id"]}
    
    queue_entry_id = entry_to_update["queue_entry_id"]

    # Now attempt to update the topic name on a modifiable entry.
    response = requests.patch(
        f"{BASE_URL}/queue/entry/{queue_entry_id}/topic", json={"topic_name": "Updated topic"}
    )
    assert response.status_code == 200, f"Expected status 200, got {response.status_code} with {response.json()}"
    assert "Topic name updated" in response.json().get("message", "")


def test_delete_queue_entry():
    """Test deleting a queue entry"""
    queue_entries = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_queue_entry['net_id']}").json()
    queue_entry_id = queue_entries[0]["queue_entry_id"]
    
    response = requests.delete(f"{BASE_URL}/queue/entry/{queue_entry_id}")
    assert response.status_code == 200
    assert "has been removed" in response.json().get("message", "")

def test_clear_queue():
    """Test clearing all queue entries for a course"""
    response = requests.delete(f"{BASE_URL}/queue/course/{test_queue['course_id']}/clear")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "cleared" in response.json().get("message", "")

def test_get_queue_by_student_with_no_entries():
    """Test retrieving queue entries for a student who exists but hasn't joined the queue yet"""
    # First, ensure the student exists and is enrolled. (This should be done in your setup_module.)
    # Then request their queue entries.
    response = requests.get(f"{BASE_URL}/queue/course/{test_queue['course_id']}/person/{test_person['net_id']}")
    assert response.status_code == 200
    # Expect an empty list instead of an error since the student exists but has no entries.
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
