from flask import Blueprint, request, jsonify
from app.models import db, Student, Person, Course
from app.utils import fetch_from_yalies
from ..auth import roles_required, login_required

# Create a Blueprint for the Student routes
student_bp = Blueprint("student", __name__)

# GET: Fetch all students
@student_bp.route("/students", methods=["GET"])
@roles_required(['instructor'])
def get_all_students():
    students = Student.query.all()
    return jsonify([
        {
            "net_id": s.net_id,
            "course_id": s.course_id,
            "feedback": s.feedback
        } for s in students
    ]), 200

# GET: Fetch students by CourseID
@student_bp.route("/students/course/<course_id>", methods=["GET"])
@roles_required(['instructor'])
def get_students_by_course(course_id):
    students = Student.query.filter_by(course_id=course_id).all()
    if not students:
        return jsonify({"error": f"No students found for course {course_id}"}), 404

    return jsonify([
        {
            "net_id": s.net_id,
            "course_id": s.course_id,
            "feedback": s.feedback
        } for s in students
    ]), 200

# GET: Fetch courses students are enrolled in by NetID
@student_bp.route("/students/person/<net_id>", methods=["GET"])
@login_required
def get_students_by_netid(net_id):
    students = Student.query.filter_by(net_id=net_id).all()
    if not students:
        return jsonify({"error": f"No courses found for student {net_id}"}), 404

    return jsonify([
        {
            "net_id": s.net_id,
            "course_id": s.course_id,
            "feedback": s.feedback
        } for s in students
    ]), 200

# POST: Enroll a student in a course
@student_bp.route("/student", methods=["POST"])
@login_required
def enroll_student():
    data = request.json

    # Required fields
    required_fields = ["net_id", "course_id"]

    # Ensure required fields exist
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # The person and course must exist before enrolling a student in a course
    person_exists = Person.query.get(data["net_id"])
    course_exists = Course.query.get(data["course_id"])
    if not person_exists:
        return jsonify({"error": f"Person {data['net_id']} does not exist"}), 404
    if not course_exists:
        return jsonify({"error": f"Course {data['course_id']} does not exist"}), 404

    # Check if student is already enrolled
    if Student.query.get((data["net_id"], data["course_id"])):
        return jsonify({"error": f"Student {data['net_id']} is already enrolled in course {data['course_id']}"}), 409

    new_student = Student(
        net_id = data["net_id"].strip(),
        course_id = data["course_id"].strip(),
        feedback = data.get("feedback", [])
    )

    try:
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": f"Student {new_student.net_id} enrolled in course {new_student.course_id}"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE: Remove a student from a course
@student_bp.route("/student/<net_id>/<course_id>", methods=["DELETE"])
@roles_required(['instructor'])
def unenroll_student(net_id, course_id):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"Student {net_id} unenrolled from course {course_id}"}), 200

# PUT: Replace all feedback
@student_bp.route("/student/<net_id>/<course_id>/feedback", methods=["PUT"])
@roles_required(['instructor'])
def replace_student_feedback(net_id, course_id):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a Python List (SQLALChemy handles this conversion to ARRAY)
    if "feedback" not in data or not isinstance(data["feedback"], list):
        return jsonify({"error": "Feedback must be a list-like ARRAY"}), 400

    student.feedback = data["feedback"]
    db.session.commit()
    return jsonify({"message": f"Feedback replaced for student {net_id} in course {course_id}"}), 200

# PATCH: Append new feedback messages
@student_bp.route("/student/<net_id>/<course_id>/feedback", methods=["PATCH"])
@roles_required(['instructor', 'ULA'])
def append_student_feedback(net_id, course_id):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a Python List (SQLALChemy handles this conversion to ARRAY)
    if "feedback" not in data or not isinstance(data["feedback"], list):
        return jsonify({"error": "Feedback must be a list"}), 400

    if student.feedback is None:
        student.feedback = []
    student.feedback.extend(data["feedback"])  # Append new message
    db.session.commit()
    return jsonify({"message": f"Feedback added for student {net_id} in course {course_id}"}), 200

# PATCH: Edit specific feedback message by index
@student_bp.route("/student/<net_id>/<course_id>/feedback/<int:index>", methods=["PATCH"])
@roles_required(['instructor', 'ULA'])
def edit_student_feedback(net_id, course_id, index):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a string
    if "feedback" not in data or not isinstance(data["feedback"], str):
        return jsonify({"error": "Feedback must be a string"}), 400

    # Ensure the index is valid
    if not student.feedback or index < 0 or index >= len(student.feedback):
        return jsonify({"error": "Invalid feedback index"}), 400

    student.feedback[index] = data["feedback"]
    db.session.commit()
    return jsonify({"message": f"Feedback at index {index} updated for student {net_id}"}), 200

# DELETE: Remove specific feedback message by index
@student_bp.route("/student/<net_id>/<course_id>/feedback/<int:index>", methods=["DELETE"])
@roles_required(['instructor', 'ULA'])
def delete_student_feedback_entry(net_id, course_id, index):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    # Ensure the index is valid
    if not student.feedback or index < 0 or index >= len(student.feedback):
        return jsonify({"error": "Invalid feedback index"}), 400

    student.feedback.pop(index)  # Remove the specific feedback entry
    db.session.commit()
    return jsonify({"message": f"Feedback at index {index} deleted for student {net_id}"}), 200

# DELETE: Clear all feedback messages
@student_bp.route("/student/<net_id>/<course_id>/feedback", methods=["DELETE"])
@roles_required(['instructor', 'ULA'])
def clear_student_feedback(net_id, course_id):
    student = Student.query.get((net_id, course_id))
    if not student:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    student.feedback = []  # Reset feedback to an empty list
    db.session.commit()
    return jsonify({"message": f"All feedback cleared for student {net_id} in course {course_id}"}), 200


@student_bp.route("/enroll-via-yalies", methods=["POST"])
@login_required
def enroll_student_via_yalies():
    data = request.json
    net_id = data.get("net_id", "").strip()
    course_id = data.get("course_id", "").strip()

    if not net_id or not course_id:
        return jsonify({"error": "net_id and course_id are required"}), 400

    # Ensure course exists
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404

    # Check if Person exists
    person = Person.query.get(net_id)
    if not person:
        yalies_data = fetch_from_yalies(net_id)
        if not yalies_data:
            return jsonify({"error": f"Person with NetID {net_id} not found via Yalies API"}), 404

        try:
            person = Person(
                net_id = net_id,
                first_name = yalies_data.get("first_name", ""),
                last_name = yalies_data.get("last_name", ""),
                yale_email = yalies_data.get("email", f"{net_id}@yale.edu"),
                class_year = yalies_data.get("year", 0),
                residential_college = yalies_data.get("college", None)
            )
            db.session.add(person)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create Person: {str(e)}"}), 500

    # Check if Student already exists
    existing_student = Student.query.get((net_id, course_id))
    if existing_student:
        return jsonify({"error": f"Student {net_id} already enrolled in {course_id}"}), 409

    # Enroll Student
    new_student = Student(net_id=net_id, course_id=course_id, feedback=[])
    try:
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": f"Student {net_id} enrolled in {course_id} successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
