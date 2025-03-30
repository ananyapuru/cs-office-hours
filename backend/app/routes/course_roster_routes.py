import os
import pandas as pd
from flask import Blueprint, request, jsonify
from app.models import db, Person, Student, ULA, Admin, Course
from app.utils import fetch_from_yalies

course_roster_bp = Blueprint('course_roster', __name__)

CURRENT_CENTURY = 2000

@course_roster_bp.route('/upload-roster/<course_id>', methods=['POST'])
def upload_roster(course_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV"}), 400

    try:
        df = pd.read_csv(file)

        required_columns = ["Net ID", "First Name", "Last Name", "Email", "Role", "College", "Year"]
        for col in required_columns:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        # Ensure course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": f"Course {course_id} not found"}), 404

        for _, row in df.iterrows():
            net_id = str(row["Net ID"]).strip()
            role = str(row["Role"]).strip().lower()

            # Default to CSV values
            first_name = str(row["First Name"]).strip()
            last_name = str(row["Last Name"]).strip()
            email = str(row["Email"]).strip()
            college = str(row["College"]).strip() or None
            year_raw = row.get("Year", "")
            try:
                class_year = int(year_raw)
                if class_year < CURRENT_CENTURY:
                    class_year += CURRENT_CENTURY
            except:
                class_year = 0

            # If ULA, override by fetching from Yalies
            if "ula" in role:
                yalies_data = fetch_from_yalies(net_id)
                if yalies_data:
                    first_name = yalies_data.get("first_name", first_name)
                    last_name = yalies_data.get("last_name", last_name)
                    email = yalies_data.get("email", email)
                    class_year = yalies_data.get("year", class_year)
                    college = yalies_data.get("college", college)

            # Create Person if not exists
            person = Person.query.get(net_id)
            if not person:
                person = Person(
                    net_id=net_id,
                    first_name=first_name,
                    last_name=last_name,
                    yale_email=email,
                    class_year=class_year,
                    residential_college=college
                )
                db.session.add(person)

            # Add role-specific object if not already present
            if "student" in role:
                if not Student.query.get((net_id, course_id)):
                    db.session.add(Student(net_id=net_id, course_id=course_id, feedback=[]))

            elif "ula" in role or "ta" in role:
                if not ULA.query.get((net_id, course_id)):
                    db.session.add(ULA(net_id=net_id, course_id=course_id))

            elif "admin" in role or "instructor" in role:
                if not Admin.query.get((net_id, course_id)):
                    db.session.add(Admin(net_id=net_id, course_id=course_id))

        db.session.commit()
        return jsonify({"message": "Roster uploaded and processed successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
