# app/socket_events.py
import requests
import jwt
from flask_socketio import join_room, emit, disconnect
from flask import request, current_app
from app.models import db, Queue, QueueEntry, Course, Chat, ChatMessage
from datetime import datetime
from .auth import socket_roles_required

# Helper to fetch all queue entries for a course
def fetch_all_entries_for_course(course_id):
    queue = Queue.query.filter_by(course_id=course_id).first()
    if not queue:
        return []
    
    # Only return entries that are not marked as "Completed"
    entries = QueueEntry.query.filter(
        QueueEntry.queue_id == queue.queue_id,
        QueueEntry.status != "Completed"
    ).order_by(QueueEntry.time_entered).all()

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

# Helper to fetch all the chat messages for a course
def fetch_chat_messages_for_course(course_id):
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return []

    messages = ChatMessage.query.filter_by(chat_id=chat.chat_id).order_by(ChatMessage.time_sent).all()
    return [{
        'chat_message_id': m.chat_message_id,
        'net_id': m.net_id,
        'first_name': m.person.first_name,
        'last_name': m.person.last_name,
        'message': m.message,
        'time_sent': m.time_sent.isoformat()
    } for m in messages]


# Helper to broadcast updated queue to all clients in the room
def broadcast_queue_update(course_id):
    entries = fetch_all_entries_for_course(course_id)
    emit('queue_updated', {'entries': entries}, room=course_id)

# Helper to broadcast updated chat to all clients in the room
def broadcast_chat_update(course_id):
    messages = fetch_chat_messages_for_course(course_id)
    emit('chat_updated', {'messages': messages}, room=course_id)


# Register all Socket.IO event handlers for queue management
def register_socket_events(socketio):

    @socketio.on('connect')
    def on_connect():
        # 1) Extract token
        token = request.args.get('token')
        if not token:
            emit('error', {'message': 'Missing token'})
            return disconnect()

        # 2) Decode & verify
        try:
            payload = jwt.decode(
                token,
                current_app.secret_key,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            emit('error', {'message': 'Token expired'})
            return disconnect()
        except jwt.InvalidTokenError:
            emit('error', {'message': 'Invalid token'})
            return disconnect()

        # 3) Stash user info
        # We encoded: { netid, roles: {...}, exp }
        request.environ['user'] = {
            'net_id': payload.get('netid'),
            'roles': payload.get('roles', {})
        }
        
    @socketio.on('join_room')
    @socket_roles_required(required_roles=['student','ULA','instructor'])
    def handle_join_room(data):
        # A client joins a course-specific room
        course_id = data.get('course_id')
        if course_id:
            join_room(course_id)
            emit('joined_room', {'message': f'Joined room for course {course_id}'})

    @socketio.on('student_join_queue')
    @socket_roles_required(required_roles=['student'])
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
            QueueEntry.status.in_(["In Queue", "In Progress"])
        ).first()

        if existing_entry:
            emit('error', {'message': 'You are already in the queue!'})
            return

        # Create and save new queue entry
        new_entry = QueueEntry(
            queue_id=queue.queue_id,
            net_id=net_id,
            topic_name=topic_name.strip(),
            status="In Queue",
            time_entered=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()

        # Broadcast the updated queue
        broadcast_queue_update(course_id)

    @socketio.on('staff_remove_entry')
    @socket_roles_required(required_roles=['instructor', 'ULA'])
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
    @socket_roles_required(required_roles=['student'])
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
    @socket_roles_required(required_roles=['student'])
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
    @socket_roles_required(required_roles=['instructor', 'ULA'])
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

    @socketio.on('staff_clear_queue')
    @socket_roles_required(required_roles=['instructor', 'ULA'])
    def handle_staff_clear_queue(data):
        course_id = data.get('course_id')
        # Find the queue for the course
        queue = Queue.query.filter_by(course_id=course_id).first()
        if not queue:
            emit('error', {'message': 'Queue not found'}, room=course_id)
            return

        # Delete all entries associated with the queue
        QueueEntry.query.filter_by(queue_id=queue.queue_id).delete()
        db.session.commit()

        # Broadcast the updated (now empty) queue
        broadcast_queue_update(course_id)

    @socketio.on('staff_update_entry')
    @socket_roles_required(required_roles=['instructor', 'ULA'])
    def handle_staff_update_entry(data):
        course_id = data.get('course_id')
        queue_entry_id = data.get('queue_entry_id')
        new_status = data.get('new_status')
        staff_net_id = data.get('staff_net_id')  # Staff member making the update

        # Fetch the queue entry by its ID
        entry = QueueEntry.query.get(queue_entry_id)
        if not entry:
            emit('error', {'message': 'Queue entry not found'}, room=course_id)
            return

        # Update the entry status
        entry.status = new_status
        entry.ula_net_id = staff_net_id
        db.session.commit()

        # Broadcast the updated queue
        broadcast_queue_update(course_id)




    ### CHAT
    @socketio.on('send_chat_message')
    @socket_roles_required(required_roles=['student', 'ULA', 'instructor'])
    def handle_send_chat_message(data):
        course_id = data.get('course_id')
        message_text = data.get('message')

        if not course_id or not message_text:
            emit('error', {'message': 'Missing course ID or message'})
            return

        user = request.environ.get('user', {})
        net_id = user.get('net_id')

        chat = Chat.query.filter_by(course_id=course_id).first()
        if not chat:
            # Create a new chat instance for the course
            chat = Chat(course_id=course_id)
            db.session.add(chat)
            db.session.commit()

        message = ChatMessage(
            chat_id=chat.chat_id,
            net_id=net_id,
            message=message_text.strip()
        )
        db.session.add(message)
        db.session.commit()

        broadcast_chat_update(course_id)


    @socketio.on('get_chat_history')
    @socket_roles_required(required_roles=['student', 'ULA', 'instructor'])
    def handle_get_chat_history(data):
        course_id = data.get('course_id')
        if not course_id:
            emit('error', {'message': 'Missing course ID'})
            return

        messages = fetch_chat_messages_for_course(course_id)
        emit('chat_updated', {'messages': messages})
