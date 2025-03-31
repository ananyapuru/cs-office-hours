import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")


# Sample test Data
test_course = {
    "course_id": "CPSC_323_AY24-25_S25",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5,
    "queue_status": True
}


def setup_module(module):
    """Setup test data before running chat route tests."""
    response = requests.post(f"{BASE_URL}/course", json=test_course)
    assert response.status_code in [201, 409], f"Failed to create course: {response.text}"

def teardown_module(module):
    """Clean up test data after running tests."""
    # Delete the chat for the test course if it exists.
    requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/delete")
    # Delete the test course.
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")

def test_create_chat():
    """Test creating a chat instance for a course."""
    response = requests.post(f"{BASE_URL}/chat/course/{test_course['course_id']}/create")
    # Expect a 201 if the chat was successfully created.
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "chat_id" in data, "chat_id not returned in response"

def test_create_chat_existing():
    """Test that creating a chat for a course that already has one returns an error (409)."""
    # First, ensure the chat exists
    response = requests.post(f"{BASE_URL}/chat/course/{test_course['course_id']}/create")
    # Now, try to create it again; expecting a conflict (409)
    response = requests.post(f"{BASE_URL}/chat/course/{test_course['course_id']}/create")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

def test_delete_chat():
    """Test deleting an existing chat instance for a course."""
    # Ensure the chat exists
    _ = requests.post(f"{BASE_URL}/chat/course/{test_course['course_id']}/create")
    # Now delete the chat
    delete_response = requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/delete")
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"

def test_delete_chat_nonexistent():
    """Test deleting a chat instance for a course that does not have one."""
    # First, delete the chat if it exists.
    requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/delete")
    # Now, try deleting again – since no chat exists, we expect a 404.
    response = requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/delete")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
