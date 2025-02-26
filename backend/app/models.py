from app import db
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy import Index, func



class Person(db.Model):
    __tablename__ = "person"

    # Primary Key: NetID
    net_id = db.Column(db.String, primary_key = True)

    # Columns
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String, nullable = False)
    yale_email = db.Column(db.String, nullable = False, unique = True)
    class_year = db.Column(db.Integer, nullable = False)
    residential_college = db.Column(db.String, nullable = True)

    # Relations (1: Many, 1 Person can have multiple student, ULA, Admin/Instructor instances)
    students = db.relationship("Student", backref = "person", lazy = True)
    ulas = db.relationship("ULA", backref = "person", lazy = True)
    admins = db.relationship("Admin", backref = "person", lazy = True)

class Course(db.Model):
    __tablename__ = "course"

    # Primary Key: CourseID -> Concatenation of course dept, code, academic year, and academic semester: CPSC_323_AY24-25_S25
    course_id = db.Column(db.String, primary_key = True)  

    # Columns
    academic_year = db.Column(db.String, nullable = False)
    academic_term = db.Column(db.String, nullable = False)
    enrollment_size = db.Column(db.Integer, nullable = False)
    course_staff_size = db.Column(db.Integer, nullable = False)

    # Relations (Students, ULAs, Admins have a Many:1 relationship with Course table, many students all map to the same course)
    students = db.relationship("Student", backref = "course", lazy = True)
    ulas = db.relationship("ULA", backref = "course", lazy = True)
    admins = db.relationship("Admin", backref = "course", lazy = True)

class Student(db.Model):
    __tablename__ = "student"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> Students; Many: 1: Students -> Course)
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), primary_key = True) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), primary_key = True)

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable = True, server_default = "{}") # Feedback array that contains lists of messages

    # Enforce that no duplicate students can be enrolled in the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name = "unique_student_course"),)

class ULA(db.Model):
    __tablename__ = "ula"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> ULAs; Many: 1: ULAs -> Course)
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), primary_key = True) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), primary_key = True)

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable = True, server_default = "{}") # Feedback array that contains lists of messages
    zoom_link = db.Column(db.String, nullable = True) 

    # Enforce that no duplicate ULAs can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name = "unique_ula_course"),)

class Admin(db.Model):
    __tablename__ = "admin"

    # Primary Key: Composite Primary Key (NetID, CourseID)
    # Relations (1: Many: Person -> Admin; Many: 1: Admin -> Course)
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), primary_key = True) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), primary_key = True)

    # Enforce that no duplicate Admins / Instructors can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name = "unique_admin_course"),)

class Queue(db.Model):
    __tablename__ = "queue"

    # Primary Key: Each course gets exactly ONE queue instance
    queue_id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)

    # Foreign key: Connect back to Course
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), unique = True, nullable = False) 

    # Queue Status
    is_active = db.Column(db.Boolean, nullable = False, server_default = "false")  # Whether the queue is open

    # Relationships
    course = db.relationship("Course", backref = db.backref("queue", uselist = False)) # 1:1 with Course
    entries = db.relationship("QueueEntry", backref = "queue", lazy = "dynamic") # 1:Many with Entries, Dynamic Loading

class QueueEntry(db.Model):
    __tablename__ = "queue_entry"

    # Primary Key: Unique ID for each queue entry
    queue_entry_id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    # Foreign Keys / Relations: (1:1 Course to Queue)
    queue_id = db.Column(db.Integer, db.ForeignKey("queue.queue_id"), nullable = False)  # Queue entries are associated with
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), nullable = False)  # Student in queue
    ula_net_id = db.Column(db.String, db.ForeignKey("person.net_id"), nullable = True)  # ULA assigned to help, can be null when pending

    # Queue Position (determined dynamically)
    position = db.Column(db.Integer, nullable = False)

    # Required Topic Name
    topic_name = db.Column(db.String, nullable = False)  # Description of the problem

    # Optional Zoom Link (for remote office hours)
    zoom_link = db.Column(db.String, nullable = True)

    # Status Enum: Pending → In Progress → Completed
    status = db.Column(
        ENUM("Pending", "In Progress", "Completed", name = "queue_status_enum"),
        nullable = False,
        server_default = "Pending"
    )

    # Timing Metrics
    time_entered = db.Column(db.DateTime, nullable=False, server_default=func.now())  # When student joined queue
    time_started = db.Column(db.DateTime, nullable = True)  # When ULA started helping
    time_finished = db.Column(db.DateTime, nullable = True)  # When ULA finished helping

    # Relationships (Eager Loading for performance)
    person = db.relationship("Person", foreign_keys = [net_id], backref = "queue_entries", lazy = "dynamic")
    ula = db.relationship("Person", foreign_keys = [ula_net_id], backref = "assigned_queue_tasks", lazy = "dynamic")
    queue = db.relationship("Queue", backref = "entries")

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