from flask import Blueprint, request, jsonify
from app.models import db, Chat, ChatMessage, Course, Person
from ..auth import roles_required, login_required

# Create a Blueprint for the Chat routes
chat_bp = Blueprint("chat", __name__)

# POST: Create a chat instance for a course
@chat_bp.route("/chat/course/<course_id>/create", methods=["POST"])
@roles_required(['instructor'])
def create_chat(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    
    existing_chat = Chat.query.filter_by(course_id=course_id).first()
    if existing_chat:
        return jsonify({"error": f"Chat for course {course_id} already exists"}), 409

    new_chat = Chat(course_id=course_id)
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"message": f"Chat created for course {course_id}", "chat_id": new_chat.chat_id}), 201

# DELETE: Delete the chat table instance for a course (Admin use)
@chat_bp.route("/chat/course/<course_id>/delete", methods=["DELETE"])
@roles_required(['instructor'])
def delete_chat(course_id):
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return jsonify({"error": f"Chat for course {course_id} not found"}), 404

    db.session.delete(chat)
    db.session.commit()
    return jsonify({"message": f"Chat for course {course_id} has been deleted"}), 200