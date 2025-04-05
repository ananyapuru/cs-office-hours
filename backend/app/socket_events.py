# app/socket_events.py
import requests
from flask_socketio import join_room, emit
from app.models import db, Queue, QueueEntry, Course
from datetime import datetime

# Helper to fetch all queue entries for a course
def fetch_all_entries_for_course(course_id):
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return []
    
    entries = QueueEntry.query.filter_by(queue_id=queue.queue_id).order_by(QueueEntry.time_entered).all()

    entries_data = []
    for entry in entries:
        entries_data.append({
            'queue_entry_id': entry.queue_entry_id,
            'net_id': entry.net_id,
            'first_name': entry.person.first_name,
            'last_name': entry.person.last_name,
            'topic_name': entry.topic_name,
            'status': entry.status,
            'time_entered': entry.time_entered.isoformat() if entry.time_entered else None,
        })
    return entries_data

# Helper to broadcast updated queue to all clients in the room
def broadcast_queue_update(course_id):
    entries = fetch_all_entries_for_course(course_id)
    emit('queue_updated', {'entries': entries}, room=course_id)

# Register all Socket.IO event handlers for queue management
def register_socket_events(socketio):

    @socketio.on('join_room')
    def handle_join_room(data):
        # A client joins a course-specific room
        course_id = data.get('course_id')
        if course_id:
            join_room(course_id)
            emit('joined_room', {'message': f'Joined room for course {course_id}'})

    @socketio.on('student_join_queue')
    def handle_student_join_queue(data):
        # Student attempts to join the queue
        course_id = data.get('course_id')
        net_id = data.get('net_id')
        topic_name = data.get('topic_name')

        queue = Queue.query.filter_by(course_id=course_id).first()

        # Validate queue exists and is active
        if not queue or not queue.is_active:
            emit('error', {'message': 'Queue is not active'})
            return

        # Prevent duplicate active entries
        existing_entry = QueueEntry.query.filter(
            QueueEntry.queue_id == queue.queue_id,
            QueueEntry.net_id == net_id,
            QueueEntry.status.in_(["Pending", "In Progress"])
        ).first()

        if existing_entry:
            emit('error', {'message': 'You are already in the queue!'})
            return

        # Create and save new queue entry
        new_entry = QueueEntry(
            queue_id=queue.queue_id,
            net_id=net_id,
            topic_name=topic_name.strip(),
            status="Pending",
            time_entered=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()

        # Broadcast the updated queue
        broadcast_queue_update(course_id)

    @socketio.on('staff_remove_entry')
    def handle_staff_remove_entry(data):
        # Staff forcibly removes a student from the queue
        course_id = data.get('course_id')
        queue_entry_id = data.get('queue_entry_id')

        entry = QueueEntry.query.get(queue_entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()

        broadcast_queue_update(course_id)

    @socketio.on('student_leave_queue')
    def handle_student_leave_queue(data):
        # Student voluntarily leaves the queue
        course_id = data.get('course_id')
        queue_entry_id = data.get('queue_entry_id')

        if not course_id or not queue_entry_id:
            emit('error', {'message': 'Missing course_id or queue_entry_id'}, room=course_id)
            return

        entry = QueueEntry.query.get(queue_entry_id)
        if not entry:
            emit('error', {'message': 'Queue entry not found'}, room=course_id)
            return

        db.session.delete(entry)
        db.session.commit()

        broadcast_queue_update(course_id)

    @socketio.on('toggle_queue')
    def handle_toggle_queue(data):
        # Student toggles the queue's active status
        course_id = data.get('course_id')
        is_active = data.get('is_active')

        queue = Queue.query.filter_by(course_id=course_id).first()

        if not queue:
            emit('error', {'message': 'Queue not found'})
            return

        queue.is_active = is_active
        db.session.commit()

        # Broadcast the updated active status
        emit('queue_status_updated', {'is_active': is_active}, room=course_id)

    @socketio.on('staff_toggle_queue')
    def handle_staff_toggle_queue(data):
        # Staff toggles the queue's active status (creates if missing)
        course_id = data.get('course_id')
        is_active = data.get('is_active')

        queue = Queue.query.filter_by(course_id=course_id).first()

        if not queue:
            # Create a new queue if none exists
            queue = Queue(course_id=course_id, is_active=is_active)
            db.session.add(queue)
        else:
            # Update existing queue
            queue.is_active = is_active

        db.session.commit()

        # Broadcast the updated active status
        emit('queue_status_updated', {'is_active': is_active}, room=course_id)
