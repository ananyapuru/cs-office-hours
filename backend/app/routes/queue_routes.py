from flask import Blueprint, request, jsonify
from app.models import db, Queue, QueueEntry, Course
from ..auth import roles_required

# Create a Blueprint for the Person routes
queue_bp = Blueprint("queue", __name__)


@queue_bp.route("/queue/course/<course_id>/status", methods=["GET"])
@roles_required(['instructor', 'ULA', 'student'])
def get_queue_status(course_id):
    queue = Queue.query.filter_by(course_id=course_id).first()

    if not queue:
        # Auto-create a queue if missing
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": f"Course {course_id} does not exist"}), 404
        
        queue = Queue(course_id=course_id, is_active=False)
        db.session.add(queue)
        db.session.commit()

    return jsonify({"course_id": course_id, "is_active": queue.is_active}), 200


# PATCH: Enable/Disable queue for a course
@queue_bp.route("/queue/course/<course_id>/toggle", methods=["PATCH"])
@roles_required(['instructor', 'ULA'])
def toggle_queue_status(course_id):
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    data = request.json
    if "is_active" not in data or not isinstance(data["is_active"], bool):
        return jsonify({"error": "Missing or invalid 'is_active' field"}), 400

    queue.is_active = data["is_active"]
    db.session.commit()
    return jsonify({"message": f"Queue for course {course_id} set to {'enabled' if data['is_active'] else 'disabled'}"}), 200

# POST: Create a queue for a course
@queue_bp.route("/queue/course/<course_id>/create", methods=["POST"])
@roles_required(['instructor'])
def create_queue(course_id):
    """Creates a queue for a specific course if it doesn't already exist."""
    course_exists = Course.query.get(course_id)
    if not course_exists:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    
    existing_queue = Queue.query.filter_by(course_id=course_id).first()
    if existing_queue:
        return jsonify({"error": f"Queue for course {course_id} already exists"}), 409

    new_queue = Queue(course_id=course_id, is_active=False)  # Default queue starts as disabled

    db.session.add(new_queue)
    db.session.commit()

    return jsonify({"message": f"Queue created for course {course_id}", "queue_id": new_queue.queue_id}), 201

# DELETE: Remove queue for a course
@queue_bp.route("/queue/course/<course_id>/delete", methods=["DELETE"])
@roles_required(['instructor'])
def delete_queue(course_id):
    """Deletes a queue and all its entries for a specific course."""
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    # Also delete all queue entries associated with this queue
    QueueEntry.query.filter_by(queue_id=queue.queue_id).delete()

    db.session.delete(queue)
    db.session.commit()

    return jsonify({"message": f"Queue for course {course_id} has been deleted"}), 200
