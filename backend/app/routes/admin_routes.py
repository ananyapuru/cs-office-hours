from flask import Blueprint, request, jsonify, session
from app.models import db, Admin, Person, Course
from ..auth import roles_required, login_required

# Create a Blueprint for the Admin routes
admin_bp = Blueprint("admin", __name__)

# GET: Fetch all Admins
@admin_bp.route("/admins", methods=["GET"])
@login_required
def get_all_admins():
    admins = Admin.query.all()
    return jsonify([
        {
            "net_id": a.net_id,
            "course_id": a.course_id
        } for a in admins
    ]), 200

# GET: Fetch Admins by CourseID
@admin_bp.route("/admins/course/<course_id>", methods=["GET"])
@login_required
def get_admins_by_course(course_id):
    admins = Admin.query.filter_by(course_id=course_id).all()
    if not admins:
        return jsonify({"error": f"No Admins found for course {course_id}"}), 404

    return jsonify([
        {
            "net_id": a.net_id,
            "course_id": a.course_id
        } for a in admins
    ]), 200

# GET: Fetch courses Admins are assigned to by NetID
@admin_bp.route("/admins/person", methods=["GET"])
@login_required
def get_admins_by_netid():
    net_id = session.get("CAS_USERNAME")
    if not net_id:
        return jsonify({"error": "Not authenticated"}), 401
    admins = Admin.query.filter_by(net_id=net_id).all()
    if not admins:
        return jsonify({"error": f"No courses found for Admin {net_id}"}), 404

    return jsonify([
        {
            "net_id": a.net_id,
            "course_id": a.course_id
        } for a in admins
    ]), 200

# POST: Assign an Admin to a course
@admin_bp.route("/admin", methods=["POST"])
@login_required
def assign_admin():
    data = request.json

    # Required fields
    required_fields = ["net_id", "course_id"]

    # Ensure required fields exist
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # The person and course must exist before assigning an Admin
    person_exists = Person.query.get(data["net_id"])
    course_exists = Course.query.get(data["course_id"])
    if not person_exists:
        return jsonify({"error": f"Person {data['net_id']} does not exist"}), 404
    if not course_exists:
        return jsonify({"error": f"Course {data['course_id']} does not exist"}), 404
    
    # Check if Admin is already assigned
    if Admin.query.get((data["net_id"], data["course_id"])):
        return jsonify({"error": f"Admin {data['net_id']} is already assigned to course {data['course_id']}"}), 409

    new_admin = Admin(
        net_id=data["net_id"].strip(),
        course_id=data["course_id"].strip(),
    )

    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": f"Admin {new_admin.net_id} assigned to course {new_admin.course_id}"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE: Remove an Admin from a course
@admin_bp.route("/admin/<net_id>/<course_id>", methods=["DELETE"])
@roles_required(['instructor'])
def unassign_admin(net_id, course_id):
    admin = Admin.query.get((net_id, course_id))
    if not admin:
        return jsonify({"error": f"Admin {net_id} is not assigned to course {course_id}"}), 404

    db.session.delete(admin)
    db.session.commit()
    return jsonify({"message": f"Admin {net_id} removed from course {course_id}"}), 200
