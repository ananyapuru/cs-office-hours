from flask import Blueprint, request, jsonify
from app.models import db, Course, Person, Student

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
            "calendar_link": course.calendar_link 
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
        "calendar_link": course.calendar_link 
    }), 200

# POST: Create a new course
@course_bp.route("/course", methods=["POST"])
def create_course():
    data = request.json

    # Required fields
    required_fields = ["course_id", "academic_year", "academic_term"]
    # Enforce that all the required fields are there in the POST request
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Check if course already exists
    if Course.query.get(data["course_id"]):
        return jsonify({"error": f"Course {data['course_id']} already exists"}), 409

    try:
        new_course = Course(
            course_id=data["course_id"].strip(),
            academic_year=data["academic_year"].strip(),
            academic_term=data["academic_term"].strip(),
            enrollment_size=int(data["enrollment_size"]) if data.get("enrollment_size") is not None else None,
            course_staff_size=int(data["course_staff_size"]) if data.get("course_staff_size") is not None else None,
            calendar_link=data.get("calendar_link", None)
        )

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

    for key, value in data.items():
        if hasattr(course, key):
            if value == "":
                continue  # skip empty updates

            if key in ["enrollment_size", "course_staff_size"]:
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({"error": f"{key} must be an integer"}), 400

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


@course_bp.route("/course/<course_id>/students", methods=["GET"])
def get_students_for_course(course_id):
    students = Student.query.filter_by(course_id=course_id).all()
    if not students:
        return jsonify([]), 200  # Return empty list if no students yet!

    enriched = []
    for s in students:
        person = Person.query.get(s.net_id)
        enriched.append({
            "net_id": s.net_id,
            "course_id": s.course_id,
            "feedback": s.feedback,
            "first_name": person.first_name if person else "",
            "last_name": person.last_name if person else "",
            "yale_email": person.yale_email if person else "",
            "college": person.residential_college if person else "",
            "class_year": person.class_year if person else "",
            "role": "Student"
        })

    return jsonify(enriched), 200
