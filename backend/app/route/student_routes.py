from flask import Blueprint, request, jsonify
from app.models import db, Student

# Create a Blueprint for Student routes
student_bp = Blueprint("student", __name__)

# GET: Fetch all students
@student_bp.route("/student", methods=["GET"])
def get_all_students():
    students = Student.query.all()
    return jsonify([
        {
            "id": s.id,
            "net_id": s.net_id,
            "course_id": s.course_id,
            "feedback": s.feedback
        } for s in students
    ]), 200

# GET: Fetch a single student by ID
@student_bp.route("/student/<int:id>", methods=["GET"])
def get_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"error": f"Student with ID {id} not found"}), 404
    return jsonify({
        "id": student.id,
        "net_id": student.net_id,
        "course_id": student.course_id,
        "feedback": student.feedback
    }), 200

# POST: Create a new student
@student_bp.route("/student", methods=["POST"])
def create_student():
    data = request.json

    required_fields = ["net_id", "course_id"]

    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    new_student = Student(
        net_id=data["net_id"].strip(),
        course_id=data["course_id"].strip(),
        feedback=data.get("feedback", [])
    )

    try:
        db.session.add(new_student)
        db.session.commit()
        return jsonify({"message": f"Student {new_student.id} added successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# PUT: Update an existing student
@student_bp.route("/student/<int:id>", methods=["PUT"])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"error": f"Student with ID {id} not found"}), 404

    data = request.json

    for key, value in data.items():
        if hasattr(student, key):
            setattr(student, key, value.strip() if isinstance(value, str) else value)

    db.session.commit()
    return jsonify({"message": f"Student {id} updated successfully"}), 200

# DELETE: Remove a student
@student_bp.route("/student/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"error": f"Student with ID {id} not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"Student {id} deleted successfully"}), 200
