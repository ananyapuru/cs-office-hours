from app import db
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy import Index, func

##########################################
#               Person                 #
##########################################
class Person(db.Model):
    __tablename__ = "person"

    # Primary Key: NetID
    net_id = db.Column(db.String, primary_key=True)

    # Columns
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    yale_email = db.Column(db.String, nullable=False, unique=True)
    class_year = db.Column(db.Integer, nullable=False)
    residential_college = db.Column(db.String, nullable=True)

    # Relations (1: Many, 1 Person can have multiple student, ULA, Admin/Instructor instances)
    # Updated to use back_populates and cascade deletes to prevent dependency issues.
    students = db.relationship(
        "Student",
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    ulas = db.relationship(
        "ULA",
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    admins = db.relationship(
        "Admin",
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Relationships for Queue Entries:
    # - When the Person is the student in the queue
    # - When the Person is the assigned ULA for a queue entry

    queue_entries = db.relationship(
        "QueueEntry",
        foreign_keys="[QueueEntry.net_id]",
        back_populates="person",
        lazy="dynamic",
        passive_deletes=True
    )
    assigned_queue_tasks = db.relationship(
        "QueueEntry",
        foreign_keys="[QueueEntry.ula_net_id]",
        back_populates="ula",
        lazy="dynamic",
        passive_deletes=True
    )

    # Relationships for Chat Messages:
    # - When a person sends a message in the chat
    chat_messages = db.relationship(
        "ChatMessage",
        foreign_keys="[ChatMessage.net_id]",
        back_populates="person",
        lazy="dynamic",
        passive_deletes=True
    )

##########################################
#               Course                 #
##########################################
class Course(db.Model):
    __tablename__ = "course"

    # Primary Key: CourseID -> Concatenation of course dept, code, academic year, and academic semester: CPSC_323_AY24-25_S25
    course_id = db.Column(db.String, primary_key=True)

    # Columns
    academic_year = db.Column(db.String, nullable=False)
    academic_term = db.Column(db.String, nullable=False)
    enrollment_size = db.Column(db.Integer, nullable=True)
    course_staff_size = db.Column(db.Integer, nullable=True)

    # Relations (Students, ULAs, Admins have a Many:1 relationship with Course table, many students all map to the same course)
    students = db.relationship(
        "Student",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    ulas = db.relationship(
        "ULA",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    admins = db.relationship(
        "Admin",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # 1:1 relationship with Queue (each course has exactly one queue)
    # Using lazy="selectin" for efficient batch loading.
    queue = db.relationship(
        "Queue",
        back_populates="course",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    # 1:1 relationship with Chat (each course gets exactly one chat table)
    chat = db.relationship(
        "Chat",
        back_populates="course",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

##########################################
#              Student                 #
##########################################
class Student(db.Model):
    __tablename__ = "student"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> Students; Many: 1: Students -> Course)
    net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="CASCADE"),
        primary_key=True
    )  # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(
        db.String,
        db.ForeignKey("course.course_id", ondelete="CASCADE"),
        primary_key=True
    )

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable=True, server_default="{}")  # Feedback array that contains lists of messages

    # Enforce that no duplicate students can be enrolled in the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name="unique_student_course"),)

    # Relationships
    # Using lazy="joined" as these are frequently needed when a Student is queried.
    person = db.relationship("Person", back_populates="students", lazy="joined")
    course = db.relationship("Course", back_populates="students", lazy="joined")

##########################################
#                ULA                   #
##########################################
class ULA(db.Model):
    __tablename__ = "ula"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> ULAs; Many: 1: ULAs -> Course)
    net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="CASCADE"),
        primary_key=True
    )  # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(
        db.String,
        db.ForeignKey("course.course_id", ondelete="CASCADE"),
        primary_key=True
    )

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable=True, server_default="{}")  # Feedback array that contains lists of messages
    zoom_link = db.Column(db.String, nullable=True)

    # Enforce that no duplicate ULAs can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name="unique_ula_course"),)

    # Relationships
    # Using lazy="joined" as ULA information is critical when managing course staff.
    person = db.relationship("Person", back_populates="ulas", lazy="joined")
    course = db.relationship("Course", back_populates="ulas", lazy="joined")

##########################################
#               Admin                  #
##########################################
class Admin(db.Model):
    __tablename__ = "admin"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> Admin; Many: 1: Admin -> Course)
    net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="CASCADE"),
        primary_key=True
    )  # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(
        db.String,
        db.ForeignKey("course.course_id", ondelete="CASCADE"),
        primary_key=True
    )

    # Enforce that no duplicate Admins / Instructors can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name="unique_admin_course"),)

    # Relationships
    person = db.relationship("Person", back_populates="admins", lazy="joined")
    course = db.relationship("Course", back_populates="admins", lazy="joined")

##########################################
#               Queue                  #
##########################################
class Queue(db.Model):
    __tablename__ = "queue"

    # Primary Key: Each course gets exactly ONE queue instance
    queue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign key: Connect back to Course
    course_id = db.Column(
        db.String,
        db.ForeignKey("course.course_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Queue Status
    is_active = db.Column(db.Boolean, nullable=False, server_default="false")  # Whether the queue is open

    # Relationships
    # Using lazy="joined" for course as it is a 1:1 relationship and using lazy="dynamic" for entries since
    # there may be a ton of queue entries and we want to filter them efficiently.
    course = db.relationship("Course", back_populates="queue", lazy="joined")
    entries = db.relationship(
        "QueueEntry",
        back_populates="queue",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="dynamic"
    )

##########################################
#             QueueEntry               #
##########################################
class QueueEntry(db.Model):
    __tablename__ = "queue_entry"

    # Primary Key: Unique ID for each queue entry
    queue_entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys / Relations: (1:many Queue: Entries)
    queue_id = db.Column(
        db.Integer,
        db.ForeignKey("queue.queue_id", ondelete="CASCADE"),
        nullable=False
    )  # Queue entries are associated with
    net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="CASCADE"),
        nullable=False
    )  # Student in queue
    ula_net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="SET NULL"),
        nullable=True
    )  # ULA assigned to help, can be null when pending

    # Queue Position (determined dynamically)
    position = db.Column(db.Integer, nullable=True)

    # Required Topic Name
    topic_name = db.Column(db.String, nullable=False)  # Description of the problem

    # Optional Zoom Link (for remote office hours)
    zoom_link = db.Column(db.String, nullable=True)

    # Status Enum: Pending → In Progress → Completed
    status = db.Column(
        ENUM("Pending", "In Progress", "Completed", name="queue_status_enum"),
        nullable=False,
        server_default="Pending"
    )

    # Timing Metrics
    time_entered = db.Column(db.DateTime, nullable=False, server_default=func.now())  # When student joined queue
    time_started = db.Column(db.DateTime, nullable=True)  # When ULA started helping
    time_finished = db.Column(db.DateTime, nullable=True)  # When ULA finished helping

    # Relationships (Eager Loading for performance)
    # Using lazy="joined" here since when fetching queue entries, we often need the associated person and ULA details.
    person = db.relationship(
        "Person",
        foreign_keys=[net_id],
        back_populates="queue_entries",
        lazy="joined"
    )
    ula = db.relationship(
        "Person",
        foreign_keys=[ula_net_id],
        back_populates="assigned_queue_tasks",
        lazy="joined"
    )
    queue = db.relationship("Queue", back_populates="entries")

    # Unique Constraint: Prevent multiple active entries by only allowing one "Pending" or "In Progress" entry at a time
    __table_args__ = (
        Index(
            "unique_active_queue_entry",
            "net_id",
            "queue_id",
            unique=True,
            postgresql_where=db.text("status IN ('Pending', 'In Progress')")
        ),
    )

    @staticmethod
    def get_next_position(queue_id):
        """Returns the next available position in the queue for a given course, excluding completed entries."""
        last_position = (
            db.session.query(db.func.max(QueueEntry.position))
            .filter(QueueEntry.queue_id == queue_id, QueueEntry.status.in_(["Pending", "In Progress"]))
            .scalar()
        )
        return (last_position or 0) + 1  # If no active entries, start from 1

##########################################
#               Chat                  #
##########################################
class Chat(db.Model):
    __tablename__ = "chat"

    # Primary Key: Each course gets exactly ONE Chat Table instance
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign key: Connect back to Course
    course_id = db.Column(
        db.String,
        db.ForeignKey("course.course_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Relationships
    # Using lazy="joined" for course as it is a 1:1 relationship and using lazy="dynamic" for messages since
    # there may be a ton of messages and we want to filter them efficiently.
    course = db.relationship("Course", back_populates="chat", lazy="joined")
    messages = db.relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="dynamic"
    )

##########################################
#             ChatMessage             #
##########################################
class ChatMessage(db.Model):
    __tablename__ = "chat_message"

    # Primary Key: Unique ID for each chat message
    chat_message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys / Relations: (1:1 Chat: Messages)
    chat_id = db.Column(
        db.Integer,
        db.ForeignKey("chat.chat_id", ondelete="CASCADE"),
        nullable=False
    ) 

    # FK linking Person Table (who sent the message?)
    net_id = db.Column(
        db.String,
        db.ForeignKey("person.net_id", ondelete="CASCADE"),
        nullable=False
    ) 

    # Message
    message = db.Column(db.Text, nullable = False)

    # When message was sent
    time_sent = db.Column(db.DateTime, nullable=False, server_default=func.now()) 


    # Relationships (Eager Loading for performance)
    # Using lazy="joined" here since when fetching chat messages, we often need the associated person details
    person = db.relationship(
        "Person",
        foreign_keys=[net_id],
        back_populates="chat_messages",
        lazy="joined"
    )
    chat = db.relationship("Chat", back_populates="messages")
