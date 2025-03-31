from flask import Blueprint, request, jsonify
from app.models import Course, Student, db, Chat, ChatMessage, Person

# Create a Blueprint for the ChatMessage routes
chatmessage_bp = Blueprint("chatmessage", __name__)

# GET: Fetch all chat messages for a specific course (ordered by timestamp)
@chatmessage_bp.route("/chat/course/<course_id>/messages", methods=["GET"])
def get_chat_messages(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return jsonify({"error": f"Chat for course {course_id} not found"}), 404

    messages = ChatMessage.query.filter_by(chat_id=chat.chat_id).order_by(ChatMessage.time_sent).all()

    return jsonify([
        {
            "chat_message_id": m.chat_message_id,
            "chat_id": m.chat_id,
            "net_id": m.net_id,
            "message": m.message,
            "time_sent": m.time_sent
        } for m in messages
    ]), 200

# GET: Fetch all chat messages for a specific course by sender (ordered by timestamp)
@chatmessage_bp.route("/chat/course/<course_id>/person/<net_id>/messages", methods=["GET"])
def get_course_messages_by_person(course_id, net_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return jsonify({"error": f"Chat for course {course_id} not found"}), 404

    person = Person.query.get(net_id)
    if not person:
        return jsonify({"error": f"Student {net_id} not found"}), 404

    # Verify that the student is enrolled in the course.
    enrollment = Student.query.filter_by(net_id=net_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({"error": f"Student {net_id} is not enrolled in course {course_id}"}), 404
    
    messages = ChatMessage.query.filter_by(chat_id=chat.chat_id, net_id=net_id).order_by(ChatMessage.time_sent).all()

    return jsonify([
        {
            "chat_message_id": m.chat_message_id,
            "chat_id": m.chat_id,
            "net_id": m.net_id,
            "message": m.message,
            "time_sent": m.time_sent
        }
        for m in messages
    ]), 200

# POST: Add a chat message to a course's chat
@chatmessage_bp.route("/chat/course/<course_id>/message/add", methods=["POST"])
def add_chat_message(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return jsonify({"error": f"Chat for course {course_id} not found"}), 404

    data = request.json
    required_fields = ["net_id", "message"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Verify that the person exists
    person = Person.query.get(data["net_id"])
    if not person:
        return jsonify({"error": f"Person {data['net_id']} does not exist"}), 404

    new_message = ChatMessage(
        chat_id=chat.chat_id,
        net_id=data["net_id"],
        message=data["message"].strip()
    )

    try:
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"message": f"Chat message added for course {course_id}",
                        "chat_message_id": new_message.chat_message_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE: Clear all chat messages for a course (Admin use)
@chatmessage_bp.route("/chat/course/<course_id>/clear", methods=["DELETE"])
def clear_chat_messages(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": f"Course {course_id} does not exist"}), 404
    chat = Chat.query.filter_by(course_id=course_id).first()
    if not chat:
        return jsonify({"error": f"Chat for course {course_id} not found"}), 404

    messages = ChatMessage.query.filter_by(chat_id=chat.chat_id).all()
    for msg in messages:
        db.session.delete(msg)
    db.session.commit()
    return jsonify({"message": f"All chat messages for course {course_id} have been cleared"}), 200

# DELETE: Delete a specific chat message by its ID (Admin use)
@chatmessage_bp.route("/chat/message/<int:chat_message_id>", methods=["DELETE"])
def delete_chat_message(chat_message_id):
    message = ChatMessage.query.get(chat_message_id)
    if not message:
        return jsonify({"error": f"Chat message {chat_message_id} not found"}), 404
    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": f"Chat message {chat_message_id} has been deleted"}), 200