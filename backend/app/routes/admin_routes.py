from flask import Blueprint, request, jsonify, session
from app.models import db, Admin, Person, Course
from app.utils import fetch_from_yalies
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
    data = request.json or {}
    net_id = data.get("net_id", "").strip()
    course_id = data.get("course_id", "").strip()

    # Validate input
    if not net_id or not course_id:
        return jsonify({"error": "net_id and course_id are required"}), 400

    # Ensure course exists
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404

    # Ensure person exists (or fetch/create via Yalies)
    person = Person.query.get(net_id)
    if not person:
        yalies_data = fetch_from_yalies(net_id)
        if not yalies_data:
            return jsonify({"error": f"Person with NetID {net_id} not found via Yalies API"}), 404

        try:
            person = Person(
                net_id=net_id,
                first_name=yalies_data.get("first_name", ""),
                last_name=yalies_data.get("last_name", ""),
                yale_email=yalies_data.get("email", f"{net_id}@yale.edu"),
                class_year=yalies_data.get("year", 0),
                residential_college=yalies_data.get("college", None)
            )
            db.session.add(person)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create Person: {str(e)}"}), 500

    # Check if Admin is already assigned
    if Admin.query.get((net_id, course_id)):
        return jsonify({"error": f"Admin {net_id} is already assigned to course {course_id}"}), 409

    # Create the Admin record
    new_admin = Admin(net_id=net_id, course_id=course_id)
    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({
            "message": f"Admin {new_admin.net_id} assigned to course {new_admin.course_id}"
        }), 201
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
