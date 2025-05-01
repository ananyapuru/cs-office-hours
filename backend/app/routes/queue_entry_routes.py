from flask import Blueprint, request, jsonify
from app.models import Student, db, Queue, Person, ULA, QueueEntry
from sqlalchemy.sql import func
from ..auth import roles_required

# Create a Blueprint for the Queue routes
queue_entry_bp = Blueprint("queue_entry", __name__)

# GET: Get all the queue entries within a Queue
@queue_entry_bp.route("/queue/course/<course_id>/entries", methods=["GET"])
@roles_required(['instructor', 'ULA'])
def get_all_queue_entries_for_course(course_id):
    """Fetches all queue entries for a course."""
    mode = request.args.get("mode")  # optional query parameter
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    query = QueueEntry.query.filter_by(queue_id=queue.queue_id)
    if mode:
        query = query.filter_by(mode=mode)
    queue_entries = query.order_by(QueueEntry.time_entered).all()

    return jsonify([
        {
            "queue_entry_id": q.queue_entry_id,
            "queue_id": q.queue_id,
            "net_id": q.net_id,
            "ula_net_id": q.ula_net_id,
            "topic_name": q.topic_name,
            "zoom_link": q.zoom_link,
            "status": q.status,
            "mode": q.mode,
            "time_entered": q.time_entered.isoformat() if q.time_entered else None,
            "time_started": q.time_started.isoformat() if q.time_started else None,
            "time_finished": q.time_finished.isoformat() if q.time_finished else None
        } for q in queue_entries
    ]), 200

@queue_entry_bp.route("/queue/course/<course_id>/active-entries", methods=["GET"])
@roles_required(['instructor', 'ULA'])
def get_active_queue_entries_for_course(course_id):
    """Fetches only active queue entries for a course (excludes completed entries)."""
    mode = request.args.get("mode")  # Optional query parameter
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    query = QueueEntry.query.filter_by(queue_id=queue.queue_id)
    # Exclude entries where status is "Completed"
    query = query.filter(QueueEntry.status != "Completed")
    if mode:
        query = query.filter_by(mode=mode)
    queue_entries = query.order_by(QueueEntry.time_entered).all()

    return jsonify([
        {
            "queue_entry_id": q.queue_entry_id,
            "queue_id": q.queue_id,
            "net_id": q.net_id,
            "ula_net_id": q.ula_net_id,
            "topic_name": q.topic_name,
            "zoom_link": q.zoom_link,
            "status": q.status,
            "mode": q.mode,
            "time_entered": q.time_entered.isoformat() if q.time_entered else None,
            "time_started": q.time_started.isoformat() if q.time_started else None,
            "time_finished": q.time_finished.isoformat() if q.time_finished else None
        } for q in queue_entries
    ]), 200


# GET: Fetch queue entries for a student in a specific course
@queue_entry_bp.route("/queue/course/<course_id>/person/<net_id>", methods=["GET"])
@roles_required(['instructor', 'ULA'])
def get_queue_by_student_in_course(course_id, net_id):
    # Verify that the person exists
    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Student {net_id} not found"}), 404

    # Verify that the student is enrolled in the course.
    enrollment = Student.query.filter_by(net_id=net_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404

    # Verify that the queue exists for the course.
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    # Retrieve queue entries for the student.
    queue_entries = QueueEntry.query.filter_by(queue_id=queue.queue_id, net_id=net_id).all()
    
    return jsonify([
        {
            "queue_entry_id": q.queue_entry_id,
            "queue_id": q.queue_id,
            "net_id": q.net_id,
            "ula_net_id": q.ula_net_id,
            "topic_name": q.topic_name,
            "zoom_link": q.zoom_link,
            "status": q.status,
            "mode": q.mode,
            "time_entered": q.time_entered,
            "time_started": q.time_started,
            "time_finished": q.time_finished
        } for q in queue_entries
    ]), 200



# POST: Add a student to the queue
@queue_entry_bp.route("/queue/course/<course_id>/add", methods=["POST"])
@roles_required(['instructor', 'ULA', 'student'])
def add_to_queue(course_id):
    # Ensure Queue Exists
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    data = request.json
    required_fields = ["net_id", "topic_name"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Ensure Student Exists
    person = Person.query.get(data["net_id"])
    if not person:
        return jsonify({"error": f"Student {data['net_id']} does not exist"}), 404
    
    # Ensure student does not have another active queue entry
    existing_entry = QueueEntry.query.filter_by(
        net_id=data["net_id"], queue_id=queue.queue_id
    ).filter(QueueEntry.status.in_(["In Queue", "In Progress"])).first()
    if existing_entry:
        return jsonify({"error": "Student already has an active queue entry"}), 409
    

    new_queue_entry = QueueEntry(
        queue_id = queue.queue_id,
        net_id = data["net_id"],
        ula_net_id = None,
        topic_name = data["topic_name"].strip(),
        zoom_link = data.get("zoom_link", "").strip() or None,
        status = "In Queue",
        mode = data.get("mode", "in-person").strip(),
        # time_entered = func.now(),
        time_entered = datetime.now(timezone.utc),
        time_started = None,
        time_finished = None
    )

    try:
        db.session.add(new_queue_entry)
        db.session.commit()
        return jsonify({"message": f"Student {data['net_id']} added to queue", "queue_entry_id": new_queue_entry.queue_entry_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# PATCH: Complete queue entry (Set to "Completed")
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>/complete", methods=["PATCH"])
@roles_required(['instructor', 'ULA'])
def complete_queue_entry(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404

    if queue_entry.status != "In Progress":
        return jsonify({"error": "Only In Progress queue entries can be completed"}), 400
    
    queue_entry.status = "Completed"
    # queue_entry.time_finished = func.now()
    queue_entry.time_finished = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"message": f"Queue entry {queue_entry_id} marked as completed"}), 200

# PATCH: Assign a ULA to a queue entry and set to in progress
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>/assign", methods=["PATCH"])
@roles_required(['instructor', 'ULA'])
def assign_ula(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404

    if queue_entry.status == "Completed":
        return jsonify({"error": "Cannot modify a completed queue entry"}), 400
    
    data = request.json
    if "ula_net_id" not in data:
        return jsonify({"error": "Missing 'ula_net_id' field"}), 400
    
    ula_exists = Person.query.get(data["ula_net_id"])
    if not ula_exists:
        return jsonify({"error": f"ULA {data['ula_net_id']} does not exist"}), 404

    # Check if the ULA is assigned to the same course
    ula_assigned = ULA.query.filter_by(net_id=data["ula_net_id"], course_id=queue_entry.queue.course_id).first()
    if not ula_assigned:
        return jsonify({"error": f"ULA {data['ula_net_id']} is not assigned to course {queue_entry.course_id}"}), 403
    
    queue_entry.ula_net_id = data["ula_net_id"]
    queue_entry.status = "In Progress"
    # queue_entry.time_started = func.now()
    queue_entry.time_started = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"message": f"ULA {data['ula_net_id']} assigned to queue entry {queue_entry_id}"}), 200

# PATCH: Edit Topic Name
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>/topic", methods=["PATCH"])
@roles_required(['instructor', 'ULA', 'student'])
def update_topic_name(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404
    
    if queue_entry.status == "Completed":
        return jsonify({"error": "Cannot modify a completed queue entry"}), 400

    data = request.json
    if "topic_name" not in data or not isinstance(data["topic_name"], str):
        return jsonify({"error": "Topic name must be a string"}), 400

    queue_entry.topic_name = data["topic_name"].strip()
    db.session.commit()

    return jsonify({"message": f"Topic name updated for queue entry {queue_entry_id}"}), 200

# PATCH: Edit Zoom Link
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>/zoom", methods=["PATCH"])
@roles_required(['instructor', 'ULA', 'student'])
def update_zoom_link(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404
    
    if queue_entry.status == "Completed":
        return jsonify({"error": "Cannot modify a completed queue entry"}), 400
    
    data = request.json
    if "zoom_link" not in data or not isinstance(data["zoom_link"], str):
        return jsonify({"error": "Zoom link must be a string"}), 400

    queue_entry.zoom_link = data["zoom_link"].strip()
    db.session.commit()

    return jsonify({"message": f"Zoom link updated for queue entry {queue_entry_id}"}), 200

# DELETE: Remove Zoom Link (Reset to Empty String / NULL)
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>/zoom", methods=["DELETE"])
@roles_required(['instructor', 'ULA', 'student'])
def delete_zoom_link(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404
    
    if queue_entry.status == "Completed":
        return jsonify({"error": "Cannot modify a completed queue entry"}), 400

    queue_entry.zoom_link = None  # Set Zoom link to NULL
    db.session.commit()

    return jsonify({"message": f"Zoom link removed for queue entry {queue_entry_id}"}), 200

# DELETE: Clear all queue entries for a Queue(Admin use)
@queue_entry_bp.route("/queue/course/<course_id>/clear", methods=["DELETE"])
@roles_required(['instructor', 'ULA'])
def clear_queue_by_course(course_id):
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": f"Queue for course {course_id} not found"}), 404

    queue_entries = QueueEntry.query.filter_by(queue_id=queue.queue_id).all()

    for entry in queue_entries:
        db.session.delete(entry)

    db.session.commit()
    return jsonify({"message": f"All queue entries for queue {queue.queue_id} cleared"}), 200

# DELETE: Remove a queue entry
@queue_entry_bp.route("/queue/entry/<int:queue_entry_id>", methods=["DELETE"])
@roles_required(['instructor' 'ULA', 'student'])
def delete_queue_entry(queue_entry_id):
    queue_entry = QueueEntry.query.get(queue_entry_id)
    if not queue_entry:
        return jsonify({"error": f"Queue entry {queue_entry_id} not found"}), 404

    queue_id = queue_entry.queue_id

    db.session.delete(queue_entry)
    db.session.commit()

    return jsonify({"message": f"Queue entry {queue_entry_id} has been removed"}), 200


### 
###
### FOR TESTING PURPOSES ONLY 
###
###
from datetime import datetime, timezone
# Create a blueprint for test routes.
test_queue_bp = Blueprint("test_queue", __name__)
@test_queue_bp.route("/test/queue/course/<course_id>/add", methods=["POST"])

def test_add_queue_entry(course_id):
    data = request.get_json()
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return jsonify({"error": "Queue not found"}), 404

    try:
        entry = QueueEntry(
            net_id=data["net_id"],
            queue_id=queue.queue_id,
            topic_name=data.get("topic_name"),
            mode=data.get("mode"),
            time_entered = datetime.fromisoformat(data["time_entered"]).astimezone(timezone.utc),
            time_started = datetime.fromisoformat(data["time_started"]).astimezone(timezone.utc),
            time_finished = datetime.fromisoformat(data["time_finished"]).astimezone(timezone.utc),
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({"queue_entry_id": entry.queue_entry_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


