from flask import Blueprint, request, jsonify, session
from app.models import db, ULA, Person, Course
from ..auth import roles_required, login_required

# Create a Blueprint for the ULA routes
ula_bp = Blueprint("ula", __name__)

# GET: Fetch all ULAs
@ula_bp.route("/ulas", methods=["GET"])
@roles_required(['instructor'])
def get_all_ulas():
    ulas = ULA.query.all()
    return jsonify([
        {
            "net_id": u.net_id,
            "course_id": u.course_id,
            "feedback": u.feedback,
            "zoom_link": u.zoom_link
        } for u in ulas
    ]), 200

# GET: Fetch ULAs by CourseID
@ula_bp.route("/ulas/course/<course_id>", methods=["GET"])
@roles_required(['instructor'])
def get_ulas_by_course(course_id):
    ulas = ULA.query.filter_by(course_id=course_id).all()

    return jsonify([
        {
            "net_id": u.net_id,
            "course_id": u.course_id,
            "feedback": u.feedback,
            "zoom_link": u.zoom_link
        } for u in ulas
    ]), 200

# GET: Fetch courses ULAs are teaching by NetID
@ula_bp.route("/ulas/person", methods=["GET"])
@login_required
def get_ulas_by_netid():
    net_id = session.get("CAS_USERNAME")
    if not net_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    ulas = ULA.query.filter_by(net_id=net_id).all()
    if not ulas:
        return jsonify({"error": f"No courses found for ULA {net_id}"}), 404

    return jsonify([
        {
            "net_id": u.net_id,
            "course_id": u.course_id,
            "feedback": u.feedback,
            "zoom_link": u.zoom_link
        } for u in ulas
    ]), 200

# POST: Enroll a ULA in a course
@ula_bp.route("/ula", methods=["POST"])
@roles_required(['instructor'])
def enroll_ula():
    data = request.json

    # Required fields
    required_fields = ["net_id", "course_id"]

    # Ensure required fields exist
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # The person and course must exist before enrolling a ULA in a course
    person_exists = Person.query.get(data["net_id"])
    course_exists = Course.query.get(data["course_id"])
    if not person_exists:
        return jsonify({"error": f"Person {data['net_id']} does not exist"}), 404
    if not course_exists:
        return jsonify({"error": f"Course {data['course_id']} does not exist"}), 404
    
    # Check if ULA is already enrolled
    if ULA.query.get((data["net_id"], data["course_id"])):
        return jsonify({"error": f"ULA {data['net_id']} is already assigned to course {data['course_id']}"}), 409

    new_ula = ULA(
        net_id=data["net_id"].strip(),
        course_id=data["course_id"].strip(),
        feedback=data.get("feedback", []),
        zoom_link=data.get("zoom_link")  # Optional
    )

    try:
        db.session.add(new_ula)
        db.session.commit()
        return jsonify({"message": f"ULA {new_ula.net_id} assigned to course {new_ula.course_id}"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE: Remove a ULA from a course
@ula_bp.route("/ula/<net_id>/<course_id>", methods=["DELETE"])
@roles_required(['instructor'])
def unenroll_ula(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    db.session.delete(ula)
    db.session.commit()
    return jsonify({"message": f"ULA {net_id} removed from course {course_id}"}), 200

# PUT: Replace all feedback
@ula_bp.route("/ula/<net_id>/<course_id>/feedback", methods=["PUT"])
@roles_required(['instructor'])
def replace_ula_feedback(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a Python List (SQLALChemy handles this conversion to ARRAY)
    if "feedback" not in data or not isinstance(data["feedback"], list):
        return jsonify({"error": "Feedback must be a list"}), 400

    ula.feedback = data["feedback"]
    db.session.commit()
    return jsonify({"message": f"Feedback replaced for ULA {net_id} in course {course_id}"}), 200

# PATCH: Append new feedback messages
@ula_bp.route("/ula/<net_id>/<course_id>/feedback", methods=["PATCH"])
@roles_required(['student', 'instructor'])
def append_ula_feedback(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a Python List (SQLALChemy handles this conversion to ARRAY)
    if "feedback" not in data or not isinstance(data["feedback"], list):
        return jsonify({"error": "Feedback must be a list"}), 400

    if ula.feedback is None:
        ula.feedback = []
    ula.feedback.extend(data["feedback"]) # Append new message
    db.session.commit()
    return jsonify({"message": f"Feedback added for ULA {net_id} in course {course_id}"}), 200

# PATCH: Edit specific feedback message by index
@ula_bp.route("/ula/<net_id>/<course_id>/feedback/<int:index>", methods=["PATCH"])
@roles_required(['instructor'])
def edit_ula_feedback(net_id, course_id, index):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as feedback is a string
    if "feedback" not in data or not isinstance(data["feedback"], str):
        return jsonify({"error": "Feedback must be a string"}), 400

    # Ensure the index is valid
    if not ula.feedback or index < 0 or index >= len(ula.feedback):
        return jsonify({"error": "Invalid feedback index"}), 400

    ula.feedback[index] = data["feedback"]
    db.session.commit()
    return jsonify({"message": f"Feedback at index {index} updated for ULA {net_id}"}), 200

# DELETE: Remove specific feedback message by index
@ula_bp.route("/ula/<net_id>/<course_id>/feedback/<int:index>", methods=["DELETE"])
@roles_required(['instructor'])
def delete_ula_feedback_entry(net_id, course_id, index):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    # Ensure the index is valid
    if not ula.feedback or index < 0 or index >= len(ula.feedback):
        return jsonify({"error": "Invalid feedback index"}), 400

    ula.feedback.pop(index) # Remove the specific feedback entry
    db.session.commit()
    return jsonify({"message": f"Feedback at index {index} deleted for ULA {net_id}"}), 200

# DELETE: Clear all feedback messages
@ula_bp.route("/ula/<net_id>/<course_id>/feedback", methods=["DELETE"])
@roles_required(['instructor'])
def clear_ula_feedback(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    ula.feedback = [] # Reset feedback to an empty list
    db.session.commit()
    return jsonify({"message": f"All feedback cleared for ULA {net_id} in course {course_id}"}), 200

# PATCH: Update Zoom Link
@ula_bp.route("/ula/<net_id>/<course_id>/zoom", methods=["PATCH"])
@roles_required(['instructor', 'student', 'ULA'])
def update_zoom_link(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    data = request.json

    # Ensure that what we are trying to send in as a zoom link is a string
    if "zoom_link" not in data or not isinstance(data["zoom_link"], str):
        return jsonify({"error": "Zoom link must be a string"}), 400

    ula.zoom_link = data["zoom_link"].strip()
    db.session.commit()
    return jsonify({"message": f"Zoom link updated for ULA {net_id} in course {course_id}"}), 200

# DELETE: Remove Zoom Link (set to NULL)
@ula_bp.route("/ula/<net_id>/<course_id>/zoom", methods=["DELETE"])
@roles_required(['instructor', 'student', 'ULA'])
def delete_zoom_link(net_id, course_id):
    ula = ULA.query.get((net_id, course_id))
    if not ula:
        return jsonify({"error": f"ULA {net_id} is not assigned to course {course_id}"}), 404

    ula.zoom_link = None  # Set Zoom link to NULL
    db.session.commit()
    return jsonify({"message": f"Zoom link removed for ULA {net_id} in course {course_id}"}), 200
