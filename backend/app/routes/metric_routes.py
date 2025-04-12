# metric_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from ..auth import roles_required
from ..metrics import (
    average_wait_time,
    average_session_duration,
    average_resolution_time_by_staff,
    student_queue_count,
    staff_help_count_by_staff,
    student_staff_interaction_counts,
)
from app.models import Course, Student, ULA, Person  # Import additional models for validations

metrics_bp = Blueprint("metrics", __name__)


def parse_date(date_str):
    """
    Helper: parse an ISO formatted date string into a datetime object.
    Returns None if the string is empty or invalid.
    """
    try:
        return datetime.fromisoformat(date_str).astimezone(timezone.utc) if date_str else None
    except ValueError:
        return None


def validate_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return None, jsonify({"error": f"Course {course_id} not found"}), 404
    return course, None, None


def validate_student(course_id, student_netid):
    # Check that the person exists
    person = Person.query.get(student_netid)
    if not person:
        return None, jsonify({"error": f"Student {student_netid} does not exist"}), 404
    # Check that the student is enrolled in the course
    enrollment = Student.query.filter_by(net_id=student_netid, course_id=course_id).first()
    if not enrollment:
        return None, jsonify({"error": f"Student {student_netid} is not enrolled in course {course_id}"}), 404
    return person, None, None


def validate_staff(course_id, staff_netid):
    # Check that the person exists
    person = Person.query.get(staff_netid)
    if not person:
        return None, jsonify({"error": f"Staff member {staff_netid} does not exist"}), 404
    # Check that the staff is assigned to the course (using ULA as an example)
    assignment = ULA.query.filter_by(net_id=staff_netid, course_id=course_id).first()
    if not assignment:
        return None, jsonify({"error": f"Staff member {staff_netid} is not assigned to course {course_id}"}), 404
    return person, None, None


@metrics_bp.route("/api/metrics/course/<course_id>/average_wait_time", methods=["GET"])
@roles_required(['instructor'])
def get_average_wait_time(course_id):
    """
    Return the average wait time (in seconds) for the course.
    Optional query parameters:
      - start_date, end_date (ISO date strings)
      - student_netid: if provided, returns the wait time for that student only.
        (Validates that the student exists and is enrolled.)
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    student_netid = request.args.get("student_netid")
    if student_netid:
        # Validate student
        _, err_resp, err_code = validate_student(course_id, student_netid)
        if err_resp:
            return err_resp, err_code

    value = average_wait_time(course_id, start_date, end_date, student_netid)
    return jsonify({
        "course_id": course_id,
        "average_wait_time": value,
        "student_netid": student_netid
    }), 200


@metrics_bp.route("/api/metrics/course/<course_id>/average_session_duration", methods=["GET"])
@roles_required(['instructor'])
def get_average_session_duration(course_id):
    """
    Return the average session duration (in seconds) for the course.
    Optional query parameters:
      - start_date, end_date (ISO date strings)
      - student_netid: if provided, returns the duration for that student only.
        (Validates that the student exists and is enrolled.)
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    student_netid = request.args.get("student_netid")
    if student_netid:
        _, err_resp, err_code = validate_student(course_id, student_netid)
        if err_resp:
            return err_resp, err_code

    value = average_session_duration(course_id, start_date, end_date, student_netid)
    return jsonify({
        "course_id": course_id,
        "average_session_duration": value,
        "student_netid": student_netid
    }), 200


@metrics_bp.route("/api/metrics/course/<course_id>/average_resolution_time", methods=["GET"])
@roles_required(['instructor'])
def get_average_resolution_time_by_staff(course_id):
    """
    Return the average resolution time (in seconds) for staff in the course.
    Optional query parameters:
      - start_date, end_date (ISO date strings)
      - staff_netid: if provided, returns a scalar value for that staff member; if omitted, returns a dictionary for all staff.
        (Validates that the staff member exists and is assigned to the course.)
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    staff_netid = request.args.get("staff_netid")
    if staff_netid:
        _, err_resp, err_code = validate_staff(course_id, staff_netid)
        if err_resp:
            return err_resp, err_code

    result = average_resolution_time_by_staff(course_id, start_date, end_date, staff_netid)
    return jsonify({
        "course_id": course_id,
        "average_resolution_time": result,
        "staff_netid": staff_netid
    }), 200


@metrics_bp.route("/api/metrics/course/<course_id>/student_queue_count", methods=["GET"])
@roles_required(['instructor'])
def get_student_queue_count(course_id):
    """
    Return the count of queue entries.
    Optional query parameters:
      - start_date, end_date (ISO date strings)
      - student_netid: if provided, returns the count for that student; otherwise returns a list of counts by student.
        (Validates that the student exists and is enrolled if provided.)
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    student_netid = request.args.get("student_netid")
    if student_netid:
        _, err_resp, err_code = validate_student(course_id, student_netid)
        if err_resp:
            return err_resp, err_code

    result = student_queue_count(course_id, start_date, end_date, student_netid)
    return jsonify({
        "course_id": course_id,
        "student_queue_count": result,
        "student_netid": student_netid
    }), 200


@metrics_bp.route("/api/metrics/course/<course_id>/staff_help_count", methods=["GET"])
@roles_required(['instructor'])
def get_staff_help_count(course_id):
    """
    Return the count of distinct students helped by staff.
    Optional query parameters:
      - start_date, end_date (ISO date strings)
      - staff_netid: if provided, returns the help count for that staff member; otherwise returns a dictionary for all.
        (Validates that the staff member exists and is assigned if provided.)
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    staff_netid = request.args.get("staff_netid")
    if staff_netid:
        _, err_resp, err_code = validate_staff(course_id, staff_netid)
        if err_resp:
            return err_resp, err_code

    result = staff_help_count_by_staff(course_id, start_date, end_date, staff_netid)
    return jsonify({
        "course_id": course_id,
        "staff_help_count": result,
        "staff_netid": staff_netid
    }), 200


@metrics_bp.route("/api/metrics/course/<course_id>/interaction_counts", methods=["GET"])
@roles_required(['instructor'])
def get_interaction_counts(course_id):
    """
    Return the student-staff interaction mappings.
    Optional query parameters:
      - start_date, end_date (ISO date strings, based on time_started)
      - student_netid and/or staff_netid: to filter for a specific student or staff member.
        (If provided, validates existence and enrollment/assignment accordingly.)
    Returns two dictionaries:
      - student_to_staff mapping, and
      - staff_to_student mapping.
    """
    course, err_resp, err_code = validate_course(course_id)
    if not course:
        return err_resp, err_code

    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    student_netid = request.args.get("student_netid")
    staff_netid = request.args.get("staff_netid")
    if student_netid:
        _, err_resp, err_code = validate_student(course_id, student_netid)
        if err_resp:
            return err_resp, err_code
    if staff_netid:
        _, err_resp, err_code = validate_staff(course_id, staff_netid)
        if err_resp:
            return err_resp, err_code

    student_to_staff, staff_to_student = student_staff_interaction_counts(
        course_id,
        student_netid,
        staff_netid,
        start_date,
        end_date
    )
    return jsonify({
        "course_id": course_id,
        "student_to_staff": student_to_staff,
        "staff_to_student": staff_to_student,
        "student_netid": student_netid,
        "staff_netid": staff_netid
    }), 200
