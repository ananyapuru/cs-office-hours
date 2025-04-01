import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

#########################################
#       Test Data Definitions           #
#########################################

# Create 10 people with different roles.
people = [
    {"net_id": "person1", "first_name": "Alice",   "last_name": "Anderson", "yale_email": "person1@yale.edu",  "class_year": 2025, "residential_college": "CollegeA"},
    {"net_id": "person2", "first_name": "Bob",     "last_name": "Brown",    "yale_email": "person2@yale.edu",  "class_year": 2024, "residential_college": "CollegeB"},
    {"net_id": "person3", "first_name": "Charlie", "last_name": "Clark",    "yale_email": "person3@yale.edu",  "class_year": 2025, "residential_college": "CollegeC"},
    {"net_id": "person4", "first_name": "Diana",   "last_name": "Davis",    "yale_email": "person4@yale.edu",  "class_year": 2023, "residential_college": "CollegeD"},
    {"net_id": "person5", "first_name": "Ethan",   "last_name": "Edwards",  "yale_email": "person5@yale.edu",  "class_year": 2025, "residential_college": "CollegeE"},
    {"net_id": "person6", "first_name": "Fiona",   "last_name": "Foster",   "yale_email": "person6@yale.edu",  "class_year": 2024, "residential_college": "CollegeF"},
    {"net_id": "person7", "first_name": "George",  "last_name": "Gonzalez","yale_email": "person7@yale.edu",  "class_year": 2023, "residential_college": "CollegeG"},
    {"net_id": "person8", "first_name": "Hannah",  "last_name": "Hughes",   "yale_email": "person8@yale.edu",  "class_year": 2025, "residential_college": "CollegeH"},
    {"net_id": "person9", "first_name": "Ian",     "last_name": "Ingram",   "yale_email": "person9@yale.edu",  "class_year": 2024, "residential_college": "CollegeI"},
    {"net_id": "person10","first_name": "Julia",   "last_name": "Jones",    "yale_email": "person10@yale.edu", "class_year": 2025, "residential_college": "CollegeJ"}
]

# Define three courses.
courses = [
    {"course_id": "COURSE_1", "academic_year": "2024-2025", "academic_term": "Spring", "enrollment_size": 100, "course_staff_size": 3},
    {"course_id": "COURSE_2", "academic_year": "2024-2025", "academic_term": "Fall",   "enrollment_size": 80,  "course_staff_size": 2},
    {"course_id": "COURSE_3", "academic_year": "2024-2025", "academic_term": "Summer", "enrollment_size": 50,  "course_staff_size": 1}
]

# Role assignments:
# ULAs:
#   - Persons 1,2,3 are ULAs for COURSE_1 and COURSE_2.
#   - Persons 4,5,6 are ULAs for COURSE_3.
# Students:
#   - person7 in COURSE_1 and COURSE_2.
#   - person8 in COURSE_1 and COURSE_3.
#   - person9 in COURSE_2 and COURSE_3.
#   - person10 in all courses.

#########################################
#           Setup and Teardown          #
#########################################

def setup_module(module):
    """Setup test data: create people, courses, queues, and assign ULAs and students."""
    # Create all persons.
    for person in people:
        r = requests.post(f"{BASE_URL}/person", json=person)
        assert r.status_code in [201, 409], f"Failed to create person {person['net_id']}: {r.json()}"
    
    # Create courses.
    for course in courses:
        r = requests.post(f"{BASE_URL}/course", json=course)
        assert r.status_code in [201, 409], f"Failed to create course {course['course_id']}: {r.json()}"
    
    # Create a queue for each course.
    for course in courses:
        r = requests.post(f"{BASE_URL}/queue/course/{course['course_id']}/create")
        assert r.status_code in [201, 400], f"Failed to create queue for {course['course_id']}: {r.json()}"
    
    # Assign ULAs.
    for course_id in ["COURSE_1", "COURSE_2"]:
        for ula in ["person1", "person2", "person3"]:
            data = {"net_id": ula, "course_id": course_id}
            r = requests.post(f"{BASE_URL}/ula", json=data)
            assert r.status_code in [201, 409], f"Failed to assign ULA {ula} to {course_id}: {r.json()}"
    for ula in ["person4", "person5", "person6"]:
        data = {"net_id": ula, "course_id": "COURSE_3"}
        r = requests.post(f"{BASE_URL}/ula", json=data)
        assert r.status_code in [201, 409], f"Failed to assign ULA {ula} to COURSE_3: {r.json()}"
    
    # Enroll Students.
    for course_id in ["COURSE_1", "COURSE_2"]:
        r = requests.post(f"{BASE_URL}/student", json={"net_id": "person7", "course_id": course_id})
        assert r.status_code in [201, 409], f"Failed to enroll person7 in {course_id}: {r.json()}"
    for course_id in ["COURSE_1", "COURSE_3"]:
        r = requests.post(f"{BASE_URL}/student", json={"net_id": "person8", "course_id": course_id})
        assert r.status_code in [201, 409], f"Failed to enroll person8 in {course_id}: {r.json()}"
    for course_id in ["COURSE_2", "COURSE_3"]:
        r = requests.post(f"{BASE_URL}/student", json={"net_id": "person9", "course_id": course_id})
        assert r.status_code in [201, 409], f"Failed to enroll person9 in {course_id}: {r.json()}"
    for course in courses:
        r = requests.post(f"{BASE_URL}/student", json={"net_id": "person10", "course_id": course["course_id"]})
        assert r.status_code in [201, 409], f"Failed to enroll person10 in {course['course_id']}: {r.json()}"

def teardown_module(module):
    """Cleanup test data: delete queues, courses, and persons."""
    for course in courses:
        requests.delete(f"{BASE_URL}/queue/course/{course['course_id']}/delete")
        requests.delete(f"{BASE_URL}/course/{course['course_id']}")
    for person in people:
        requests.delete(f"{BASE_URL}/person/{person['net_id']}")

#########################################
#       End-to-End and Edge Case Tests  #
#########################################

def test_end_to_end():
    """
    Comprehensive end-to-end test that:
      - Adds queue entries for students in each course.
      - Assigns a ULA to each entry and marks the entry as complete.
      - Verifies that completed entries cannot be updated.
      - Ensures a student cannot have multiple active entries in the same queue.
      - Tests that after deletion a student may re-enroll.
      - Verifies editing of fields via predefined routes.
      - Verifies Admin assignment and querying.
      - Tests duplicate enrollment and duplicate ULA assignment constraints.
      - Confirms that only one queue exists per course.
    """
    # Mapping: enrolled students for each course.
    enrollment = {
        "COURSE_1": ["person7", "person8", "person10"],
        "COURSE_2": ["person7", "person9", "person10"],
        "COURSE_3": ["person8", "person9", "person10"]
    }
    
    queue_entry_ids = {}  # Store created queue entry IDs per course.

    #################################
    # 1. Create and test queue entries.
    #################################
    for course_id, student_list in enrollment.items():
        for student in student_list:
            data = {
                "net_id": student,
                "topic_name": f"Help needed by {student} in {course_id}"
            }
            r = requests.post(f"{BASE_URL}/queue/course/{course_id}/add", json=data)
            assert r.status_code == 201, f"Failed to add queue entry for {student} in {course_id}: {r.json()}"
            queue_entry_ids.setdefault(course_id, []).append(r.json()["queue_entry_id"])
    
    #################################
    # 2. Test unique active-entry constraint.
    #################################
    # For COURSE_1, try to add a second active entry for person7.
    duplicate_data = {"net_id": "person7", "topic_name": "Duplicate entry test"}
    r_dup = requests.post(f"{BASE_URL}/queue/course/COURSE_1/add", json=duplicate_data)
    assert r_dup.status_code == 409, f"Duplicate active entry allowed: {r_dup.json()}"
    
    #################################
    # 3. Assign ULAs and complete queue entries.
    #################################
    for course_id, entries in queue_entry_ids.items():
        # Choose ULA: person1 for COURSE_1 & COURSE_2, person4 for COURSE_3.
        ula = "person1" if course_id in ["COURSE_1", "COURSE_2"] else "person4"
        for entry_id in entries:
            r_assign = requests.patch(f"{BASE_URL}/queue/entry/{entry_id}/assign", json={"ula_net_id": ula})
            assert r_assign.status_code == 200, f"Failed to assign ULA for entry {entry_id} in {course_id}: {r_assign.json()}"
            r_complete = requests.patch(f"{BASE_URL}/queue/entry/{entry_id}/complete")
            assert r_complete.status_code == 200, f"Failed to complete entry {entry_id} in {course_id}: {r_complete.json()}"
            # Also check the response message.
            msg = r_complete.json().get("message", "")
            assert "marked as completed" in msg, f"Unexpected complete message: {msg}"
    
    #################################
    # 4. Verify editing restrictions.
    #################################
    # Attempt to update the topic of a completed entry (should fail).
    completed_entry = queue_entry_ids["COURSE_1"][0]
    r_update = requests.patch(f"{BASE_URL}/queue/entry/{completed_entry}/topic", json={"topic_name": "Should not update"})
    assert r_update.status_code == 400, f"Update on completed entry {completed_entry} should fail: {r_update.json()}"
    
    
    #################################
    # 6. Test re-enrollment while active and after completion.
    #################################
    # For COURSE_2, create three additional entries from person7, person9, person10.
    additional_entries = []
    for student in ["person7", "person9", "person10"]:
        data = {"net_id": student, "topic_name": f"Reordering test for {student} in COURSE_2"}
        r = requests.post(f"{BASE_URL}/queue/course/COURSE_2/add", json=data)
        assert r.status_code == 201, f"Failed to add additional entry for {student} in COURSE_2: {r.json()}"
        additional_entries.append(r.json()["queue_entry_id"])
    # For COURSE_2, attempt re-enrollment for person7 while an active entry exists.
    r_reenroll_active = requests.post(f"{BASE_URL}/queue/course/COURSE_2/add", json={
        "net_id": "person7",
        "topic_name": "Re-enrollment test while active for person7 in COURSE_2"
    })
    # Expect this to fail since person7 already has an active entry.
    assert r_reenroll_active.status_code == 409, (
        f"Re-enrollment should fail when an active entry exists, got: {r_reenroll_active.json()}"
    )
    
    # Now, get the active entry for person7 in COURSE_2.
    r_person7_entries = requests.get(f"{BASE_URL}/queue/course/COURSE_2/person/person7")
    assert r_person7_entries.status_code == 200, f"Failed to get entries for person7 in COURSE_2: {r_person7_entries.json()}"
    active_entries = [entry for entry in r_person7_entries.json() if entry["status"] in ["Pending", "In Progress"]]
    assert active_entries, "No active entry found for person7 in COURSE_2, but one was expected."
    
    # Mark the first active entry as completed.
    active_entry_id = active_entries[0]["queue_entry_id"]
    # Assign a ULA if needed (for the sake of completeness, we use person1 for COURSE_2)
    r_assign_active = requests.patch(f"{BASE_URL}/queue/entry/{active_entry_id}/assign", json={"ula_net_id": "person1"})
    assert r_assign_active.status_code == 200, f"Failed to assign ULA for active entry {active_entry_id}: {r_assign_active.json()}"
    r_complete_active = requests.patch(f"{BASE_URL}/queue/entry/{active_entry_id}/complete")
    assert r_complete_active.status_code == 200, f"Failed to complete active entry {active_entry_id}: {r_complete_active.json()}"
    
    # Now, reattempt re-enrollment for person7 in COURSE_2.
    r_reenroll_after = requests.post(f"{BASE_URL}/queue/course/COURSE_2/add", json={
        "net_id": "person7",
        "topic_name": "Re-enrollment test for person7 in COURSE_2 after completion"
    })
    assert r_reenroll_after.status_code == 201, (
        f"Re-enrollment after marking entry complete should succeed, got: {r_reenroll_after.json()}"
    )
    
    #################################
    # 7. Test editing fields via predefined routes.
    #################################
    # --- Person Editing ---
    r_patch_person = requests.patch(f"{BASE_URL}/person/person7", json={"first_name": "GeorgeUpdated"})
    assert r_patch_person.status_code == 200, f"Failed to update person7: {r_patch_person.json()}"
    r_get_person = requests.get(f"{BASE_URL}/person/person7")
    assert "GeorgeUpdated" in r_get_person.json().get("first_name", ""), "Person first name update did not persist."
    
    # --- Course Editing ---
    r_put_course = requests.put(f"{BASE_URL}/course/COURSE_1", json={
        "course_id": "COURSE_1",
        "academic_year": "2024-2025",
        "academic_term": "Spring",
        "enrollment_size": 120,  # updated size
        "course_staff_size": 3
    })
    assert r_put_course.status_code == 200, f"Failed to update COURSE_1: {r_put_course.json()}"
    
    # --- Student Feedback Editing ---
    # For person10 in COURSE_1, replace feedback.
    r_put_feedback = requests.put(f"{BASE_URL}/student/person10/COURSE_1/feedback", json={"feedback": ["Great session!"]})
    assert r_put_feedback.status_code == 200, f"Failed to update student feedback: {r_put_feedback.json()}"
    # Then append additional feedback.
    r_patch_feedback = requests.patch(f"{BASE_URL}/student/person10/COURSE_1/feedback", json={"feedback": ["Really appreciated it."]})
    assert r_patch_feedback.status_code == 200, f"Failed to append student feedback: {r_patch_feedback.json()}"
    
    # --- ULA Zoom Link Editing ---
    # For person1 as ULA in COURSE_1, update the zoom link.
    r_patch_zoom = requests.patch(f"{BASE_URL}/ula/person1/COURSE_1/zoom", json={"zoom_link": "https://zoom.us/j/123456789"})
    assert r_patch_zoom.status_code == 200, f"Failed to update ULA zoom link: {r_patch_zoom.json()}"
    
    #################################
    # 8. Test Admin Assignment and Querying.
    #################################
    admin_assignments = [
        {"net_id": "person1", "course_id": "COURSE_3"},
        {"net_id": "person2", "course_id": "COURSE_1"}
    ]
    for admin_data in admin_assignments:
        r_admin = requests.post(f"{BASE_URL}/admin", json=admin_data)
        assert r_admin.status_code in [201, 409], f"Failed to assign admin {admin_data}: {r_admin.json()}"
    
    r_admins_course1 = requests.get(f"{BASE_URL}/admins/course/COURSE_1")
    assert r_admins_course1.status_code == 200, f"Failed to retrieve admins for COURSE_1: {r_admins_course1.json()}"
    
    #################################
    # 9. Test Duplicate Enrollment/ULA and Queue Uniqueness.
    #################################
    # Duplicate student enrollment should fail.
    r_duplicate_enroll = requests.post(f"{BASE_URL}/student", json={"net_id": "person7", "course_id": "COURSE_1"})
    assert r_duplicate_enroll.status_code == 409, f"Duplicate enrollment allowed for student in same course: {r_duplicate_enroll.json()}"
    
    # Duplicate ULA assignment for same course should fail.
    r_duplicate_ula = requests.post(f"{BASE_URL}/ula", json={"net_id": "person1", "course_id": "COURSE_1"})
    assert r_duplicate_ula.status_code == 409, f"Duplicate ULA assignment allowed for same course: {r_duplicate_ula.json()}"
    
    # Verify that a person can be enrolled in multiple courses.
    r_student_courses = requests.get(f"{BASE_URL}/students/person/person10")
    assert r_student_courses.status_code == 200, f"Failed to get student courses for person10: {r_student_courses.json()}"
    assert len(r_student_courses.json()) >= 3, f"Person10 should be enrolled in at least 3 courses, found: {len(r_student_courses.json())}"
    
    # Verify that a person can be a ULA for multiple courses.
    r_ula_courses = requests.get(f"{BASE_URL}/ulas/person/person1")
    assert r_ula_courses.status_code == 200, f"Failed to get ULA assignments for person1: {r_ula_courses.json()}"
    assert len(r_ula_courses.json()) >= 2, f"Person1 should be a ULA for at least 2 courses, found: {len(r_ula_courses.json())}"
    
    # Attempt to create a duplicate queue for COURSE_1 should fail.
    r_duplicate_queue = requests.post(f"{BASE_URL}/queue/course/COURSE_1/create")
    assert r_duplicate_queue.status_code in [400, 409], f"Duplicate queue creation should fail: {r_duplicate_queue.json()}"
    
    # End-to-end test complete.
