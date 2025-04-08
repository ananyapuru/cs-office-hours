import os
import re
from flask import Blueprint, request, jsonify, current_app
from app.models import db, Person, Student, ULA, Admin
from ..auth import roles_required, login_required

# Create a Blueprint for the Person routes
person_bp = Blueprint("person", __name__)

# GET: Fetch All Persons
@person_bp.route("/person", methods = ["GET"])
@roles_required(['instructor'])
def get_all_people():
    people = Person.query.all()
    return jsonify([
        {
            "net_id": p.net_id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "yale_email": p.yale_email,
            "class_year": p.class_year,
            "residential_college": p.residential_college
        } for p in people
    ]), 200

# GET: Fetch a single person by net_id
@person_bp.route("/person/<net_id>", methods = ["GET"])
@login_required
def get_person(net_id):
    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Person with NetID {net_id} was not found"}), 404
    return jsonify({
        "net_id": person.net_id,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "yale_email": person.yale_email,
        "class_year": person.class_year,
        "residential_college": person.residential_college
    }), 200

# POST: Create a new person
@person_bp.route("/person", methods=["POST"])
@login_required
def create_person():
    data = request.json

    # Required fields
    required_fields = ["net_id", "first_name", "last_name", "yale_email", "class_year"]
    
    # Enforce that all the required fields are there in the POST request
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    # Validate that email ends with "@yale.edu"
    if not re.match(r"^[a-zA-Z0-9._%+-]+@yale\.edu$", data["yale_email"]):
        return jsonify({"error": "Invalid Yale email format"}), 400

    # Check if person already exists
    if Person.query.get(data["net_id"]):
        return jsonify({"error": f"Person with NetID: {data['net_id']} already exists"}), 409

    new_person = Person(
        net_id = data["net_id"].strip(),
        first_name = data["first_name"].strip(),
        last_name = data["last_name"].strip(),
        yale_email = data["yale_email"].strip(),
        class_year = int(data["class_year"]),
        residential_college = data.get("residential_college", "").strip() or None  # Optional field
    )
    
    try:
        db.session.add(new_person)
        db.session.commit()
        return jsonify({
            "message": f"Person: {new_person.first_name} {new_person.last_name} (NetID: {new_person.net_id}) was added successfully."
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# PUT: Update an existing person
@person_bp.route("/person/<net_id>", methods=["PUT"])
@login_required
def update_person(net_id):
    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Person with NetID: {net_id} was not found"}), 404

    data = request.json
    required_fields = ["first_name", "last_name", "yale_email", "class_year"]

    for key, value in data.items():
        if hasattr(person, key):
            
            # Prevent updating required columns with empty strings
            if key in required_fields and value == "":
                return jsonify({"error": f"{key} cannot be empty, required field"}), 400
            
            # Ensure updated email is still Yale Email
            if key == "yale_email":
                if not re.match(r"^[a-zA-Z0-9._%+-]+@yale\.edu$", value):
                    return jsonify({"error": "Invalid Yale email format"}), 400
                
            # Ensure that the class year is still an int if updated
            if key == "class_year":
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({"error": "Class year must be a number"}), 400
            
            setattr(person, key, value.strip() if isinstance(value, str) else value)


    db.session.commit()
    return jsonify({"message": f"Person with NetID: {net_id} was updated successfully"}), 200

# PATCH: Update a specific field (Partial Update)
@person_bp.route("/person/<net_id>", methods=["PATCH"])
@login_required
def patch_person(net_id):
    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Person with NetID: {net_id} was not found"}), 404

    data = request.json
    required_fields = ["first_name", "last_name", "yale_email", "class_year"]

    for key, value in data.items():
        if key == "net_id":
            return jsonify({"error": "NetID cannot be changed"}), 400

        if hasattr(person, key):
            # Prevent updating required columns with empty strings
            if key in required_fields and value == "":
                return jsonify({"error": f"{key} cannot be empty, required field"}), 400
            
            # Ensure email is valid if being updated
            if key == "yale_email" and not re.match(r"^[a-zA-Z0-9._%+-]+@yale\.edu$", value):
                return jsonify({"error": "Invalid Yale email format"}), 400

            # Ensure class year is an integer
            if key == "class_year":
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({"error": "Class year must be a number"}), 400

            setattr(person, key, value.strip() if isinstance(value, str) else value)

    db.session.commit()
    return jsonify({"message": f"Person with NetID: {net_id} was updated successfully"}), 200

# DELETE: Remove a person from the database
@person_bp.route("/person/<net_id>", methods=["DELETE"])
@roles_required(['instructor'])
def delete_person(net_id):
    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Person with NetID: {net_id} was not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": f"Person with NetID: {net_id} was deleted successfully"}), 200

# GET: All the roles associated with a person
@person_bp.route("/person/<net_id>/roles", methods=["GET"])
def get_roles(net_id):
    # Check all our DB for roles
    is_student = db.session.query(Student).filter_by(net_id=net_id).first() is not None
    is_ula = db.session.query(ULA).filter_by(net_id=net_id).first() is not None
    is_admin = db.session.query(Admin).filter_by(net_id=net_id).first() is not None

    # Check superusers list from env var
    superuser_netids = os.getenv("SUPERUSER_NETIDS", "")
    superuser_list = [x.strip() for x in superuser_netids.split(",") if x.strip()]
    is_superuser = net_id in superuser_list

    return jsonify({
        "isStudent": is_student,
        "isULA": is_ula,
        "isAdmin": is_admin,
        "isSuperuser": is_superuser
    }), 200

# Yalies API call to populate Persons model is in utils.py