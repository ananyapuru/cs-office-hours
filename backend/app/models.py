from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY


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
    queue_status = db.Column(db.Boolean, nullable = False) # Flag indicating whether queue is enabled or not

    # Relations (Students, ULAs, Admins have a Many:1 relationship with Course table, many students all map to the same course)
    students = db.relationship("Student", backref = "course", lazy = True)
    ulas = db.relationship("ULA", backref = "course", lazy = True)
    admins = db.relationship("Admin", backref = "course", lazy = True)

class Student(db.Model):
    __tablename__ = "student"

    # Primary Key: Default Int
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable = True, server_default = "{}") # Feedback array that contains lists of messages

    # Relations (1: Many: Person -> Students; Many: 1: Students -> Course)
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), nullable = False) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), nullable = False)

    # Enforce that no duplicate students can be enrolled in the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name="unique_student_course"),)

class ULA(db.Model):
    __tablename__ = "ula"

    # Primary Key: Default Int
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    # Columns
    feedback = db.Column(ARRAY(db.String), nullable = True, server_default = "{}") # Feedback array that contains lists of messages
    zoom_link = db.Column(db.String, nullable = True) 

    # Relations (1: Many: Person -> ULAs; Many: 1: ULAs -> Course)
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), nullable = False) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), nullable = False)

    # Enforce that no duplicate ULAs can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name = "unique_ula_course"),)

class Admin(db.Model):
    __tablename__ = "admin"

    # Primary Key: Default Int
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    # Columns / Relations
    net_id = db.Column(db.String, db.ForeignKey("person.net_id"), nullable = False) # Foreign Keys to Relate back to Person and Course Tables
    course_id = db.Column(db.String, db.ForeignKey("course.course_id"), nullable = False)

    # Enforce that no duplicate Admins / Instructors can be hired for the same course
    __table_args__ = (db.UniqueConstraint("net_id", "course_id", name = "unique_admin_course"),)



