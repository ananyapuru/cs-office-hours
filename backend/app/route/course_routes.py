from flask import Blueprint, request, jsonify
from app.models import db, Course

# Create a Blueprint for the Course routes
course_bp = Blueprint("course", __name__)

# GET: Fetch all courses
@course_bp.route("/course", methods=["GET"])
def get_all_courses():
    courses = Course.query.all()
    return jsonify([
        {
            "course_id": c.course_id,
            "academic_year": c.academic_year,
            "academic_term": c.academic_term,
            "enrollment_size": c.enrollment_size,
            "course_staff_size": c.course_staff_size,
            "queue_status": c.queue_status
        } for c in courses
    ]), 200

# GET: Fetch a single course by CourseID
@course_bp.route("/course/<course_id>", methods=["GET"])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} was not found"}), 404
    return jsonify({
        "course_id": course.course_id,
        "academic_year": course.academic_year,
        "academic_term": course.academic_term,
        "enrollment_size": course.enrollment_size,
        "course_staff_size": course.course_staff_size,
        "queue_status": course.queue_status
    }), 200

# POST: Create a new course
@course_bp.route("/course", methods=["POST"])
def create_course():
    data = request.json

    # Required fields
    required_fields = ["course_id", "academic_year", "academic_term", "enrollment_size", "course_staff_size", "queue_status"]

    # Enforce that all the required fields are there in the POST request
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Ensure course does not already exist
    if Course.query.get(data["course_id"]):
        return jsonify({"error": f"Course {data['course_id']} already exists"}), 409

    new_course = Course(
        course_id = data["course_id"].strip(),
        academic_year = data["academic_year"].strip(),
        academic_term = data["academic_term"].strip(),
        enrollment_size = int(data["enrollment_size"]),
        course_staff_size = int(data["course_staff_size"]),
        queue_status = bool(data["queue_status"])
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": f"Course {new_course.course_id} was added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# PUT: Update an existing course
@course_bp.route("/course/<course_id>", methods=["PUT"])
def update_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} was not found"}), 404

    data = request.json
    required_fields = ["course_id", "academic_year", "academic_term", "enrollment_size", "course_staff_size", "queue_status"]

    for key, value in data.items():
        if hasattr(course, key):

            # Prevent updating required columns with empty strings
            if key in required_fields and value == "":
                return jsonify({"error": f"{key} cannot be empty, required field"}), 400
            
            # Ensure that these fields are still ints if updated
            if key in ["enrollment_size", "course_staff_size"]:
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({"error": f"{key} must be an integer"}), 400
            elif key == "queue_status": # Ensure that queue_status is a Bool
                value = bool(value)
            setattr(course, key, value.strip() if isinstance(value, str) else value)

    db.session.commit()
    return jsonify({"message": f"Course {course_id} was updated successfully"}), 200

# DELETE: Remove a course from the database
@course_bp.route("/course/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} was not found"}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": f"Course {course_id} was deleted successfully"}), 200
