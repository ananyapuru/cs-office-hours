import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# Sample test person data
test_person = {
    "net_id": "test123",
    "first_name": "Test",
    "last_name": "User",
    "yale_email": "test123@yale.edu",
    "class_year": 2025,
    "residential_college": "Pierson"
}

def test_create_person():
    """Test creating a new person"""
    response = requests.post(f"{BASE_URL}/person", json=test_person)
    assert response.status_code == 201
    assert "Person" in response.json()["message"]

def test_create_duplicate_person():
    """Test creating a duplicate person (should fail with 409)"""
    response = requests.post(f"{BASE_URL}/person", json=test_person)
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]

def test_create_person_with_missing_fields():
    """Test creating a person with missing required fields"""
    data = {
        "net_id": "missing_fields",
        "first_name": "Missing",
        "last_name": "Fields"
        # Missing yale_email and class_year
    }
    response = requests.post(f"{BASE_URL}/person", json=data)
    assert response.status_code == 400
    assert "Missing required fields" in response.json()["error"]

def test_create_person_with_invalid_email():
    """Test creating a person with an invalid Yale email"""
    data = test_person.copy()
    data["net_id"] = "invalid_email"
    data["yale_email"] = "invalidemail@gmail.com" 
    response = requests.post(f"{BASE_URL}/person", json=data)
    assert response.status_code == 400
    assert "Invalid Yale email format" in response.json()["error"]

def test_get_all_people():
    """Test retrieving all people"""
    response = requests.get(f"{BASE_URL}/person")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_person():
    """Test retrieving a specific person"""
    response = requests.get(f"{BASE_URL}/person/{test_person['net_id']}")
    assert response.status_code == 200
    assert response.json()["net_id"] == test_person["net_id"]

def test_get_nonexistent_person():
    """Test retrieving a person that doesn't exist"""
    response = requests.get(f"{BASE_URL}/person/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]

def test_update_person():
    """Test updating a person's first name"""
    update_data = {"first_name": "Updated"}
    response = requests.put(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]

def test_update_person_with_invalid_email():
    """Test updating a person with an invalid email"""
    update_data = {"yale_email": "notyale@harvard.edu"}
    response = requests.put(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 400
    assert "Invalid Yale email format" in response.json()["error"]

def test_update_person_with_empty_required_field():
    """Test updating a person with an empty required field (should fail)"""
    update_data = {"first_name": ""}
    response = requests.put(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["error"]

def test_update_nonexistent_person():
    """Test updating a nonexistent person (should fail with 404)"""
    update_data = {"first_name": "Ghost"}
    response = requests.put(f"{BASE_URL}/person/nonexistent", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["error"]

def test_patch_update_multiple_fields():
    """Test updating multiple fields using PATCH"""
    update_data = {"first_name": "John", "last_name": "Doe", "residential_college": "Branford"}
    response = requests.patch(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]

def test_patch_update_empty_required_field():
    """Test PATCH updating a required field with an empty value (should fail)"""
    update_data = {"first_name": ""}
    response = requests.patch(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["error"]

def test_patch_update_invalid_email():
    """Test PATCH updating email to an invalid format (should fail)"""
    update_data = {"yale_email": "invalid@notyale.com"}
    response = requests.patch(f"{BASE_URL}/person/{test_person['net_id']}", json=update_data)
    assert response.status_code == 400
    assert "Invalid Yale email format" in response.json()["error"]

def test_patch_update_nonexistent_person():
    """Test PATCH updating a nonexistent person (should return 404)"""
    update_data = {"first_name": "Ghost"}
    response = requests.patch(f"{BASE_URL}/person/nonexistent", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["error"]
    
def test_delete_person():
    """Test deleting a person"""
    response = requests.delete(f"{BASE_URL}/person/{test_person['net_id']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_delete_nonexistent_person():
    """Test deleting a person that does not exist"""
    response = requests.delete(f"{BASE_URL}/person/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["error"]
