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

test_chat_message = {
    "net_id": test_person["net_id"],
    "message": "Hello, I need help with recursion!"
}

def setup_module(module):
    """Setup test data before running chat message tests."""
    # Create test person and course
    resp1 = requests.post(f"{BASE_URL}/person", json=test_person)
    assert resp1.status_code in [201, 409], f"Failed to create person: {resp1.text}"
    
    resp2 = requests.post(f"{BASE_URL}/course", json=test_course)
    assert resp2.status_code in [201, 409], f"Failed to create course: {resp2.text}"

    # Ensure student is enrolled
    student_enrollment_response = requests.post(
        f"{BASE_URL}/student", 
        json={"net_id": test_person["net_id"], "course_id": test_course["course_id"]}
    )
    assert student_enrollment_response.status_code in [201, 409], f"Student enrollment failed: {student_enrollment_response.json()}"
    
    # Create a Chat instance for the course 
    chat_resp = requests.post(f"{BASE_URL}/chat/course/{test_course['course_id']}/create")
    assert chat_resp.status_code in [201, 409], f"Chat creation failed: {chat_resp.text}"

def teardown_module(module):
    """Clean up test data after running tests."""
    # Clear chat messages for the course and delete the Chat instance.
    requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/clear")
    requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/delete")
    # Remove course and person
    requests.delete(f"{BASE_URL}/course/{test_course['course_id']}")
    requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")


def test_add_chat_message():
    """Test adding a chat message to a course's chat."""
    response = requests.post(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/message/add",
        json=test_chat_message
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "chat_message_id" in data, "No chat_message_id returned"

def test_get_chat_messages():
    """Test retrieving all chat messages for a course."""
    # Add a message (in case none exist)
    add_resp = requests.post(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/message/add",
        json=test_chat_message
    )
    assert add_resp.status_code in [201, 409], f"Failed to add chat message: {add_resp.text}"
    
    response = requests.get(f"{BASE_URL}/chat/course/{test_course['course_id']}/messages")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    messages = response.json()
    # Even if there are no messages, our route returns an empty list.
    assert isinstance(messages, list)

def test_get_chat_messages_by_person():
    """Test retrieving chat messages for a course by a specific sender."""
    # Ensure at least one message from test_person exists.
    post_resp = requests.post(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/message/add",
        json=test_chat_message
    )
    assert post_resp.status_code in [201, 409], f"Failed to add chat message: {post_resp.text}"
    
    response = requests.get(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/person/{test_person['net_id']}/messages"
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    messages = response.json()
    assert isinstance(messages, list)
    for m in messages:
        assert m.get("net_id") == test_person["net_id"]

def test_get_chat_messages_by_nonexistent_person():
    """Test retrieving chat messages for a sender that does not exist returns an empty list."""
    response = requests.get(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/person/nonexistent_netid/messages"
    )

    assert response.status_code == 404
    # Check that the error message indicates that the student wasn't found.
    assert "student" in response.json().get("error", "").lower()


def test_delete_chat_message():
    """Test deleting a specific chat message (admin use)."""
    # Add a message first.
    post_resp = requests.post(
        f"{BASE_URL}/chat/course/{test_course['course_id']}/message/add",
        json=test_chat_message
    )
    assert post_resp.status_code == 201, f"Message add failed: {post_resp.text}"
    chat_message_id = post_resp.json()["chat_message_id"]
    
    # Now delete the message.
    del_resp = requests.delete(f"{BASE_URL}/chat/message/{chat_message_id}")
    assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"

def test_clear_chat_messages():
    """Test clearing all chat messages for a course (admin use)."""
    # Add two messages.
    for _ in range(2):
        resp = requests.post(
            f"{BASE_URL}/chat/course/{test_course['course_id']}/message/add",
            json=test_chat_message
        )
        assert resp.status_code == 201, f"Message add failed: {resp.text}"
    
    # Clear all messages.
    clear_resp = requests.delete(f"{BASE_URL}/chat/course/{test_course['course_id']}/clear")
    assert clear_resp.status_code == 200, f"Expected 200, got {clear_resp.status_code}: {clear_resp.text}"
    
    # Verify that getting messages returns an empty list.
    get_resp = requests.get(f"{BASE_URL}/chat/course/{test_course['course_id']}/messages")
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    messages = get_resp.json()
    assert isinstance(messages, list)
    assert len(messages) == 0
