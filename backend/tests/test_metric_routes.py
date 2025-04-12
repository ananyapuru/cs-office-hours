import os
import requests
import jwt
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load environment variables from .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

# Get the secret from your testing configuration (or set it to a known value)
TEST_SECRET = os.getenv('FLASK_SECRET_KEY')
def generate_test_token():
    # Create a payload with the required keys; for instance:
    payload = {
        "netid": "instructor1",
        "roles": {
            "fakecourse": ["instructor", 'ULA', 'student']
        }
        # Optionally include an expiration (exp) if needed
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return token

token = generate_test_token()
headers = {"Authorization": f"Bearer {token}"}

# Define 5 test students
test_students = [
    {
        "net_id": f"student{i}",
        "first_name": f"StudentFirst{i}",
        "last_name": f"StudentLast{i}",
        "yale_email": f"student{i}@yale.edu",
        "class_year": 2025,
        "residential_college": "Pierson"
    }
    for i in range(1, 6)
]

# Define 5 test ULAs
test_ulas = [
    {
        "net_id": f"ula{i}",
        "first_name": f"ULAFirst{i}",
        "last_name": f"ULALast{i}",
        "yale_email": f"ula{i}@yale.edu",
        "class_year": 2024,
        "residential_college": "Edwards"
    }
    for i in range(1, 6)
]

test_course = {
    "course_id": "fakecourse",
    "academic_year": "2024-2025",
    "academic_term": "Spring",
    "enrollment_size": 100,
    "course_staff_size": 5
}

test_queue = {
    "course_id": test_course["course_id"]
}

# We define a "test" endpoint for adding queue entries with timestamp overrides.
# Our test endpoint is assumed to be at /test/queue/course/<course_id>/add

def setup_module(module):
    """Setup test data for metrics testing."""
    # Create all students and ULAs
    for person in test_students + test_ulas:
        requests.post(f"{BASE_URL}/person", json=person, headers=headers)
    
    # Create course
    r = requests.post(f"{BASE_URL}/course", json=test_course, headers=headers)
    assert r.status_code in [201, 409], f"Course creation failed: {r.json()}"
    
    # Enroll all students
    for student in test_students:
        r = requests.post(
            f"{BASE_URL}/student",
            json={"net_id": student["net_id"], "course_id": test_course["course_id"]},
            headers=headers
        )
        assert r.status_code in [201, 409], f"Enrollment failed for {student['net_id']}: {r.json()}"
    
    # Create queue for course
    r = requests.post(f"{BASE_URL}/queue/course/{test_queue['course_id']}/create", headers=headers)
    assert r.status_code in [201, 400, 409], f"Queue creation failed: {r.json()}"
    
    # Assign each ULA to the course
    for ula in test_ulas:
        ula_assignment = {"net_id": ula["net_id"], "course_id": test_course["course_id"]}
        r = requests.post(f"{BASE_URL}/ula", json=ula_assignment, headers=headers)
        assert r.status_code in [201, 409], f"ULA assignment failed for {ula['net_id']}: {r.json()}"
    
    # Controlled timestamp generation:
    now = datetime.now(timezone.utc)
    # Define two entry scenarios per student.
    # Entry 1: wait time = 10 sec, session duration = 10 sec.
    # Entry 2: wait time = 20 sec, session duration = 20 sec.
    def iso(dt):
        # Convert to ISO 8601 string, strip microseconds
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


    entry_1_times = {
        "time_entered": iso(now - timedelta(seconds=60)),
        "time_started": iso(now - timedelta(seconds=50)),
        "time_finished": iso(now - timedelta(seconds=40))
    }
    entry_2_times = {
        "time_entered": iso(now - timedelta(seconds=120)),
        "time_started": iso(now - timedelta(seconds=100)),
        "time_finished": iso(now - timedelta(seconds=80))
    }
    
    # Define a predetermined ULA assignment mapping:
    # For example:
    # s1: both -> u1
    # s2: entry1 -> u2, entry2 -> u3
    # s3: entry1 -> u1, entry2 -> u2
    # s4: both -> u3
    # s5: entry1 -> u4, entry2 -> u5
    ula_mapping = {
        test_students[0]["net_id"]: [test_ulas[0]["net_id"], test_ulas[0]["net_id"]],
        test_students[1]["net_id"]: [test_ulas[1]["net_id"], test_ulas[2]["net_id"]],
        test_students[2]["net_id"]: [test_ulas[0]["net_id"], test_ulas[1]["net_id"]],
        test_students[3]["net_id"]: [test_ulas[2]["net_id"], test_ulas[2]["net_id"]],
        test_students[4]["net_id"]: [test_ulas[3]["net_id"], test_ulas[4]["net_id"]]
    }
    
    # For each student, create 2 test queue entries.
    for student in test_students:
        netid = student["net_id"]
        assignments = ula_mapping[netid]
        
        # --- Entry 1 ---
        entry1_data = {
            "net_id": netid,
            "topic_name": f"Test entry 1 for {netid}",
            "mode": "in-person",
            "time_entered": entry_1_times["time_entered"],
            "time_started": entry_1_times["time_started"],
            "time_finished": entry_1_times["time_finished"]
        }
        r = requests.post(
            f"{BASE_URL}/test/queue/course/{test_course['course_id']}/add",
            json=entry1_data,
            headers=headers
        )
        assert r.status_code == 201, f"Adding entry 1 failed: {r.json()}"
        entry1 = r.json()
        queue_entry_id = entry1.get("queue_entry_id")
        
        # Assign ULA for entry 1 (include course_id in JSON so roles check passes)
        r = requests.patch(
            f"{BASE_URL}/queue/entry/{queue_entry_id}/assign",
            json={"ula_net_id": assignments[0], "course_id": test_course["course_id"]},
            headers=headers
        )
        assert r.status_code == 200, f"Assigning ULA for entry 1 failed: {r.json()}"
        
        # Mark entry 1 as completed. This ensures it is no longer active.
        r = requests.patch(f"{BASE_URL}/queue/entry/{queue_entry_id}/complete", json={"course_id": test_course["course_id"]}, headers=headers)

        assert r.status_code == 200, f"Completing entry 1 failed: {r.json()}"
        
        # --- Entry 2 ---
        entry2_data = {
            "net_id": netid,
            "topic_name": f"Test entry 2 for {netid}",
            "mode": "in-person",
            "time_entered": entry_2_times["time_entered"],
            "time_started": entry_2_times["time_started"],
            "time_finished": entry_2_times["time_finished"]
        }
        r = requests.post(
            f"{BASE_URL}/test/queue/course/{test_course['course_id']}/add",
            json=entry2_data,
            headers=headers
        )
        assert r.status_code == 201, f"Adding entry 2 failed: {r.json()}"
        entry2 = r.json()
        queue_entry_id = entry2.get("queue_entry_id")
        
        # Assign ULA for entry 2
        r = requests.patch(
            f"{BASE_URL}/queue/entry/{queue_entry_id}/assign",
            json={"ula_net_id": assignments[1], "course_id": test_course["course_id"]},
            headers=headers
        )
        assert r.status_code == 200, f"Assigning ULA for entry 2 failed: {r.json()}"
        
        # Complete entry 2 so it is no longer active.
        r = requests.patch(f"{BASE_URL}/queue/entry/{queue_entry_id}/complete", json={"course_id": test_course["course_id"]}, headers=headers)

        assert r.status_code == 200, f"Completing entry 2 failed: {r.json()}"


def teardown_module(module):
    """Cleanup test data."""
    # requests.delete(f"{BASE_URL}/queue/course/{test_queue['course_id']}/delete", headers=headers)
    # requests.delete(f"{BASE_URL}/course/{test_course['course_id']}", headers=headers)
    # for person in test_students:
    #     requests.delete(f"{BASE_URL}/person/{person['net_id']}", headers=headers)
    # for person in test_ulas:
    #     requests.delete(f"{BASE_URL}/person/{person['net_id']}", headers=headers)

# -------------------------------
# Metrics Endpoint Tests
# -------------------------------

def test_average_wait_time():
    """Test average wait time for the whole course and for a specific student."""
    # Expected average wait = (10 + 20) sec for each student, hence overall = 15 sec.
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_wait_time", headers=headers)
    assert response.status_code == 200, response.json()

    data = response.json()
    assert abs(data.get("average_wait_time", 0) - 15.0) < 0.5, f"Expected ~15 sec, got {data.get('average_wait_time')}"
    
    # Test for a specific student (e.g., student1)
    student_netid = test_students[0]["net_id"]
    params = {"student_netid": student_netid}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_wait_time", params=params, headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    # For student1, wait times are 10 and 20 seconds → average = 15 sec.
    assert abs(data.get("average_wait_time", 0) - 15.0) < 0.5

def test_average_session_duration():
    """Test average session duration endpoint."""
    # Expected average session duration = (10 + 20) / 2 = 15 sec overall.
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_session_duration", headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert abs(data.get("average_session_duration", 0) - 15.0) < 0.5
    
    # For a specific student (e.g., student1)
    student_netid = test_students[0]["net_id"]
    params = {"student_netid": student_netid}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_session_duration", params=params, headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert abs(data.get("average_session_duration", 0) - 15.0) < 0.5

def test_average_resolution_time_by_staff():
    """Test average resolution time by staff endpoint."""
    # For ULA1, expected average = (10 + 20 + 10)/3 = 13.33 sec.
    params = {"staff_netid": test_ulas[0]["net_id"]}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_resolution_time", params=params, headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    expected = 13.33
    actual = data.get("average_resolution_time", 0)
    assert abs(actual - expected) < 0.5, f"Expected ~{expected}, got {actual}"
    
    # Overall, if we do not filter by staff, we expect a dictionary mapping.
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/average_resolution_time", headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    # Expect keys for each ULA (u1 through u5)
    for ula in test_ulas:
        assert ula["net_id"] in data.get("average_resolution_time", {})

def test_student_queue_count():
    """Test student queue count endpoint."""
    # Each student has 2 entries.
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/student_queue_count", headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    # When not filtering by a specific student, we expect a list of tuples.
    # We can verify that each student has a count of 2.
    counts = data.get("student_queue_count", [])
    for item in counts:
        netid, count = item[0], item[1]
        assert count == 2, f"Expected 2 entries for {netid}, got {count}"
    
    # For a specific student:
    student_netid = test_students[0]["net_id"]
    params = {"student_netid": student_netid}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/student_queue_count", params=params, headers=headers)
    assert response.status_code == 200, f"Error: {response.status_code} - {response.text}"
    data = response.json()
    assert data.get("student_queue_count") == 2

def test_staff_help_count():
    """Test staff help count endpoint."""
    # For ULA1: expected distinct students helped = 2 (Student1 and Student3).
    params = {"staff_netid": test_ulas[0]["net_id"]}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/staff_help_count", params=params, headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data.get("staff_help_count") == 2, f"Expected 2, got {data.get('staff_help_count')}"
    
    # When not filtering by staff, expect a dictionary mapping for all ULAs.
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/staff_help_count", headers=headers)
    data = response.json()
    mapping = data.get("staff_help_count", {})
    # Expected mapping:
    # ULA1: 2, ULA2: 2, ULA3: 2, ULA4: 1, ULA5: 1
    expected_mapping = {
        test_ulas[0]["net_id"]: 2,
        test_ulas[1]["net_id"]: 2,
        test_ulas[2]["net_id"]: 2,
        test_ulas[3]["net_id"]: 1,
        test_ulas[4]["net_id"]: 1
    }
    for ula_netid, expected_count in expected_mapping.items():
        assert mapping.get(ula_netid) == expected_count, f"Expected {expected_count} for {ula_netid}, got {mapping.get(ula_netid)}"

def test_interaction_counts():
    """Test the student-staff interaction counts endpoint."""
    # Query interactions for a specific student and staff.
    params = {"student_netid": test_students[0]["net_id"], "staff_netid": test_ulas[0]["net_id"]}
    response = requests.get(f"{BASE_URL}/api/metrics/course/{test_course['course_id']}/interaction_counts", params=params, headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    student_mapping = data.get("student_to_staff", {})
    staff_mapping = data.get("staff_to_student", {})
    
    # For Student1 and ULA1, expected interaction count is 2.
    student_entry = student_mapping.get(test_students[0]["net_id"])
    assert student_entry is not None, "Missing mapping for student"
    staff_for_student = student_entry.get("staff", {})
    assert staff_for_student.get(test_ulas[0]["net_id"], {}).get("interaction_count") == 2, \
           f"Expected 2 interactions, got {staff_for_student.get(test_ulas[0]['net_id'])}"
    
    # For ULA1, check student mapping
    staff_entry = staff_mapping.get(test_ulas[0]["net_id"])
    assert staff_entry is not None, "Missing mapping for staff"
    students_for_staff = staff_entry.get("students", {})
    assert students_for_staff.get(test_students[0]["net_id"], {}).get("interaction_count") == 2

