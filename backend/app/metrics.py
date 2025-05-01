# metrics.py

from app import db
from app.models import Queue, QueueEntry, Person
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import aliased

def average_wait_time(course_id, start_date=None, end_date=None, student_netid=None):
    """
    Returns the average wait time (in seconds) for queue entries in the given course.
    Wait time is defined as the difference between time_started and time_entered.
    Optionally, if a student_netid is provided, filters the query to that student.
    Also optionally filters by a date range based on time_entered.
    Only entries with a non-null time_started are considered.
    """
    query = (
        db.session.query(
            func.avg(func.extract('epoch', (QueueEntry.time_started - QueueEntry.time_entered)))
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .filter(
            Queue.course_id == course_id,
            QueueEntry.time_started.isnot(None)
        )
    )
    if student_netid:
        query = query.filter(QueueEntry.net_id == student_netid)
    if start_date:
        query = query.filter(QueueEntry.time_entered >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_entered <= end_date)
    return query.scalar()


def average_session_duration(course_id, start_date=None, end_date=None, student_netid=None):
    """
    Returns the average session duration (in seconds) for completed queue entries in the given course.
    Session duration is defined as the difference between time_finished and time_started.
    Optionally, if a student_netid is provided, filters the query to that student.
    Also optionally filters by a date range based on time_started.
    Only entries with a non-null time_finished are considered.
    """
    query = (
        db.session.query(
            func.avg(func.extract('epoch', (QueueEntry.time_finished - QueueEntry.time_started)))
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .filter(
            Queue.course_id == course_id,
            QueueEntry.time_finished.isnot(None)
        )
    )
    if student_netid:
        query = query.filter(QueueEntry.net_id == student_netid)
    if start_date:
        query = query.filter(QueueEntry.time_started >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_started <= end_date)
    return query.scalar()


def average_resolution_time_by_staff(course_id, start_date=None, end_date=None, staff_netid=None):
    """
    Returns the average resolution time (in seconds) for staff members in the given course.
    Resolution time is defined as the difference between time_finished and time_started.
    Optionally, if a staff_netid is provided, returns a scalar value for that staff member;
    otherwise returns a dictionary mapping each staff netid to its average resolution time.
    Optionally filters by a date range based on time_started.
    Only entries with non-null time_started and time_finished are considered.
    """
    query = (
        db.session.query(
            QueueEntry.ula_net_id,
            func.avg(func.extract('epoch', (QueueEntry.time_finished - QueueEntry.time_started))).label('avg_resolution')
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .filter(
            Queue.course_id == course_id,
            QueueEntry.time_started.isnot(None),
            QueueEntry.time_finished.isnot(None)
        )
    )
    if staff_netid:
        query = query.filter(QueueEntry.ula_net_id == staff_netid)
    if start_date:
        query = query.filter(QueueEntry.time_started >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_started <= end_date)
    
    results = query.group_by(QueueEntry.ula_net_id).all()
    
    if staff_netid:
        return results[0][1] if results else None
    else:
        return {netid: avg for netid, avg in results}


def student_queue_count(course_id, start_date=None, end_date=None, student_netid=None):
    """
    Returns the count of how many times student(s) have been in the queue for a given course.
    Optionally, if a student_netid is provided, returns a scalar count for that student;
    otherwise returns a list of tuples (net_id, queue_count) ordered from greatest to least.
    Optionally filters by a date range based on time_entered.
    """
    query = (
        db.session.query(
            QueueEntry.net_id,
            func.count(QueueEntry.queue_entry_id).label('queue_count')
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .filter(Queue.course_id == course_id)
    )
    if student_netid:
        query = query.filter(QueueEntry.net_id == student_netid)
    if start_date:
        query = query.filter(QueueEntry.time_entered >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_entered <= end_date)
    
    query = query.group_by(QueueEntry.net_id).order_by(func.count(QueueEntry.queue_entry_id).desc())
    results = query.all()
    
    if student_netid:
        return results[0][1] if results else 0
    else:
        # Return a list of simple tuples that are JSON serializable.
        return [(row[0], row[1]) for row in results]


def staff_help_count_by_staff(course_id, start_date=None, end_date=None, staff_netid=None):
    """
    Returns the number of distinct students helped by staff member(s) in a given course.
    "Helped" is determined by completed queue entries (time_finished is not null).
    Optionally, if a staff_netid is provided, returns a scalar count for that staff member;
    otherwise returns a dictionary mapping each staff netid to their help count.
    Optionally filters by a date range based on time_started.
    """
    query = (
        db.session.query(
            QueueEntry.ula_net_id,
            func.count(func.distinct(QueueEntry.net_id)).label('student_count')
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .filter(
            Queue.course_id == course_id,
            QueueEntry.time_finished.isnot(None)
        )
    )
    if staff_netid:
        query = query.filter(QueueEntry.ula_net_id == staff_netid)
    if start_date:
        query = query.filter(QueueEntry.time_started >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_started <= end_date)
    
    query = query.group_by(QueueEntry.ula_net_id)
    results = query.all()
    
    if staff_netid:
        return results[0][1] if results else 0
    else:
        return {netid: count for netid, count in results}


def student_staff_interaction_counts(course_id, student_netid=None, staff_netid=None, start_date=None, end_date=None):
    """
    Computes the interaction counts between students and staff, including their first and last names.

    Returns a tuple of two dictionaries:
      - student_to_staff: maps each student netid to a dictionary containing:
            'first_name', 'last_name', and a nested 'staff' dictionary.
            The nested dictionary maps each staff netid to their first_name, last_name,
            and the interaction count (i.e. how many times that staff helped that student).
      - staff_to_student: maps each staff netid to a dictionary containing:
            'first_name', 'last_name', and a nested 'students' dictionary.
            The nested dictionary maps each student netid to their first_name, last_name,
            and the interaction count.
    
    Optional parameters:
      - If student_netid is provided, only include interactions for that student.
      - If staff_netid is provided, only include interactions for that staff member.
      - Date filters (start_date and end_date) are applied based on time_started.
    """

    # Create aliases for the Person model so we can join for both students and staff
    student_alias = aliased(Person)
    staff_alias = aliased(Person)

    query = (
        db.session.query(
            QueueEntry.net_id.label("student_netid"),
            QueueEntry.ula_net_id.label("staff_netid"),
            student_alias.first_name.label("student_first_name"),
            student_alias.last_name.label("student_last_name"),
            staff_alias.first_name.label("staff_first_name"),
            staff_alias.last_name.label("staff_last_name"),
            func.count(QueueEntry.queue_entry_id).label("interaction_count")
        )
        .select_from(QueueEntry)
        .join(Queue, QueueEntry.queue_id == Queue.queue_id)
        .join(student_alias, student_alias.net_id == QueueEntry.net_id)
        .join(staff_alias, staff_alias.net_id == QueueEntry.ula_net_id)
        .filter(
            Queue.course_id == course_id,
            QueueEntry.time_finished.isnot(None),
            QueueEntry.ula_net_id.isnot(None)
        )
    )
    if start_date:
        query = query.filter(QueueEntry.time_started >= start_date)
    if end_date:
        query = query.filter(QueueEntry.time_started <= end_date)
    
    # Group by both the student and staff columns (and names for clarity)
    query = query.group_by(
        QueueEntry.net_id,
        QueueEntry.ula_net_id,
        student_alias.first_name,
        student_alias.last_name,
        staff_alias.first_name,
        staff_alias.last_name
    )
    
    interactions = query.all()
    
    student_to_staff = {}
    staff_to_student = {}
    
    for row in interactions:
        s_netid = row.student_netid
        st_netid = row.staff_netid
        s_first = row.student_first_name
        s_last = row.student_last_name
        st_first = row.staff_first_name
        st_last = row.staff_last_name
        count = row.interaction_count
        
        # Skip unmatched records if filtering by a specific student or staff
        if student_netid and s_netid != student_netid:
            continue
        if staff_netid and st_netid != staff_netid:
            continue
        
        # Build mapping for student -> staff interactions.
        if s_netid not in student_to_staff:
            student_to_staff[s_netid] = {
                "first_name": s_first,
                "last_name": s_last,
                "staff": {}
            }
        student_to_staff[s_netid]["staff"][st_netid] = {
            "first_name": st_first,
            "last_name": st_last,
            "interaction_count": count
        }
        
        # Build mapping for staff -> student interactions.
        if st_netid not in staff_to_student:
            staff_to_student[st_netid] = {
                "first_name": st_first,
                "last_name": st_last,
                "students": {}
            }
        staff_to_student[st_netid]["students"][s_netid] = {
            "first_name": s_first,
            "last_name": s_last,
            "interaction_count": count
        }
    
    return student_to_staff, staff_to_student


# metrics.py

# from app import db
# from app.models import Queue, QueueEntry, Person
# from sqlalchemy import func
# from datetime import datetime
# from sqlalchemy.orm import aliased

# def average_wait_time(course_id, start_date=None, end_date=None, student_netid=None):
#     """
#     Returns the average wait time (in seconds) for queue entries in the given course.
#     Wait time = time_started - time_entered.
#     """
#     # Step 1: Build a base query that selects each entry’s time delta.
#     base = (
#         db.session.query(
#             QueueEntry.queue_entry_id.label("entry_id"),
#             (QueueEntry.time_started - QueueEntry.time_entered).label("delta")
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .filter(
#             Queue.course_id == course_id,
#             QueueEntry.time_started.isnot(None)
#         )
#     )
#     if student_netid:
#         base = base.filter(QueueEntry.net_id == student_netid)
#     if start_date:
#         base = base.filter(QueueEntry.time_entered >= start_date)
#     if end_date:
#         base = base.filter(QueueEntry.time_entered <= end_date)

#     # Group by the primary key so each entry appears only once.
#     base = base.group_by(QueueEntry.queue_entry_id)

#     # Turn it into a subquery that yields distinct (entry_id, delta) pairs.
#     subq = base.subquery()

#     # Step 2: Take the average of the epoch (seconds) of each distinct delta.
#     query = db.session.query(
#         func.avg(func.extract('epoch', subq.c.delta))
#     )
#     return query.scalar()


# def average_session_duration(course_id, start_date=None, end_date=None, student_netid=None):
#     """
#     Returns the average session duration (in seconds) for completed entries: time_finished - time_started.
#     """
#     base = (
#         db.session.query(
#             QueueEntry.queue_entry_id.label("entry_id"),
#             (QueueEntry.time_finished - QueueEntry.time_started).label("delta")
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .filter(
#             Queue.course_id == course_id,
#             QueueEntry.time_finished.isnot(None)
#         )
#     )
#     if student_netid:
#         base = base.filter(QueueEntry.net_id == student_netid)
#     if start_date:
#         base = base.filter(QueueEntry.time_started >= start_date)
#     if end_date:
#         base = base.filter(QueueEntry.time_started <= end_date)

#     base = base.group_by(QueueEntry.queue_entry_id)
#     subq = base.subquery()

#     query = db.session.query(
#         func.avg(func.extract('epoch', subq.c.delta))
#     )
#     return query.scalar()


# def average_resolution_time_by_staff(course_id, start_date=None, end_date=None, staff_netid=None):
#     """
#     Returns the average resolution time (in seconds) for staff in a given course:
#     time_finished - time_started.
    
#     If staff_netid is provided, returns a single float;
#     otherwise returns a dict mapping staff_netid -> average resolution time.
#     """
#     # Subquery that picks each distinct entry with its staff_netid and delta.
#     base = (
#         db.session.query(
#             QueueEntry.queue_entry_id.label("entry_id"),
#             QueueEntry.ula_net_id.label("staff_netid"),
#             (QueueEntry.time_finished - QueueEntry.time_started).label("delta")
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .filter(
#             Queue.course_id == course_id,
#             QueueEntry.time_started.isnot(None),
#             QueueEntry.time_finished.isnot(None)
#         )
#     )
#     if staff_netid:
#         base = base.filter(QueueEntry.ula_net_id == staff_netid)
#     if start_date:
#         base = base.filter(QueueEntry.time_started >= start_date)
#     if end_date:
#         base = base.filter(QueueEntry.time_started <= end_date)

#     # Group by queue_entry_id (and staff) so each queue entry is uniquely counted.
#     base = base.group_by(QueueEntry.queue_entry_id, QueueEntry.ula_net_id)
#     subq = base.subquery()

#     # If staff_netid is specified, compute a single average of the subquery’s deltas.
#     if staff_netid:
#         query = db.session.query(
#             func.avg(func.extract('epoch', subq.c.delta))
#         )
#         result = query.scalar()
#         return result

#     # Otherwise, group by staff to build a dict { staff_netid: average_seconds }
#     rows = (
#         db.session.query(
#             subq.c.staff_netid,
#             func.avg(func.extract('epoch', subq.c.delta))
#         )
#         .group_by(subq.c.staff_netid)
#         .all()
#     )
#     return {r[0]: r[1] for r in rows}


# def student_queue_count(course_id, start_date=None, end_date=None, student_netid=None):
#     """
#     Returns how many times each student has been in the queue for a given course.
#     If student_netid is provided, returns a single integer; otherwise returns a list of (net_id, count).
#     """
#     query = (
#         db.session.query(
#             QueueEntry.net_id,
#             func.count(QueueEntry.queue_entry_id).label('queue_count')
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .filter(Queue.course_id == course_id)
#     )
#     if student_netid:
#         query = query.filter(QueueEntry.net_id == student_netid)
#     if start_date:
#         query = query.filter(QueueEntry.time_entered >= start_date)
#     if end_date:
#         query = query.filter(QueueEntry.time_entered <= end_date)

#     query = query.group_by(QueueEntry.net_id).order_by(func.count(QueueEntry.queue_entry_id).desc())
#     results = query.all()

#     if student_netid:
#         # If no rows match, return 0 instead of failing.
#         return results[0][1] if results else 0
#     else:
#         return [(row[0], row[1]) for row in results]


# def staff_help_count_by_staff(course_id, start_date=None, end_date=None, staff_netid=None):
#     """
#     Returns the number of distinct students helped by staff in a given course.
#     If staff_netid is specified, returns an integer; otherwise a dict { staff_netid: count }.
#     'Helped' is determined by having a non-null time_finished.
#     """
#     query = (
#         db.session.query(
#             QueueEntry.ula_net_id,
#             func.count(func.distinct(QueueEntry.net_id)).label('student_count')
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .filter(
#             Queue.course_id == course_id,
#             QueueEntry.time_finished.isnot(None)
#         )
#     )
#     if staff_netid:
#         query = query.filter(QueueEntry.ula_net_id == staff_netid)
#     if start_date:
#         query = query.filter(QueueEntry.time_started >= start_date)
#     if end_date:
#         query = query.filter(QueueEntry.time_started <= end_date)

#     query = query.group_by(QueueEntry.ula_net_id)
#     results = query.all()

#     if staff_netid:
#         return results[0][1] if results else 0
#     else:
#         return {row[0]: row[1] for row in results}


# def student_staff_interaction_counts(course_id, student_netid=None, staff_netid=None, start_date=None, end_date=None):
#     """
#     Computes student-staff interaction counts for a given course, returning two dictionaries:
#       - student_to_staff
#       - staff_to_student
#     Both map netids to name info & interaction counts.
#     """
#     student_alias = aliased(Person)
#     staff_alias = aliased(Person)

#     base = (
#         db.session.query(
#             QueueEntry.net_id.label("student_netid"),
#             QueueEntry.ula_net_id.label("staff_netid"),
#             student_alias.first_name.label("student_first_name"),
#             student_alias.last_name.label("student_last_name"),
#             staff_alias.first_name.label("staff_first_name"),
#             staff_alias.last_name.label("staff_last_name"),
#             func.count(QueueEntry.queue_entry_id).label("interaction_count")
#         )
#         .join(Queue, QueueEntry.queue_id == Queue.queue_id)
#         .join(student_alias, student_alias.net_id == QueueEntry.net_id)
#         .join(staff_alias, staff_alias.net_id == QueueEntry.ula_net_id)
#         .filter(
#             Queue.course_id == course_id,
#             QueueEntry.time_finished.isnot(None),
#             QueueEntry.ula_net_id.isnot(None)
#         )
#     )
#     if start_date:
#         base = base.filter(QueueEntry.time_started >= start_date)
#     if end_date:
#         base = base.filter(QueueEntry.time_started <= end_date)

#     # Group by both student + staff to get distinct counts
#     base = base.group_by(
#         QueueEntry.net_id,
#         QueueEntry.ula_net_id,
#         student_alias.first_name,
#         student_alias.last_name,
#         staff_alias.first_name,
#         staff_alias.last_name
#     )

#     # We still do the final filter in Python if user asked for a specific netid.
#     interactions = base.all()

#     student_to_staff = {}
#     staff_to_student = {}

#     for row in interactions:
#         s_netid = row.student_netid
#         st_netid = row.staff_netid
#         s_first = row.student_first_name
#         s_last = row.student_last_name
#         st_first = row.staff_first_name
#         st_last = row.staff_last_name
#         count = row.interaction_count

#         # If user wants a specific student or staff, skip rows that don't match.
#         if student_netid and s_netid != student_netid:
#             continue
#         if staff_netid and st_netid != staff_netid:
#             continue

#         # Build student -> staff mapping
#         if s_netid not in student_to_staff:
#             student_to_staff[s_netid] = {
#                 "first_name": s_first,
#                 "last_name": s_last,
#                 "staff": {}
#             }
#         student_to_staff[s_netid]["staff"][st_netid] = {
#             "first_name": st_first,
#             "last_name": st_last,
#             "interaction_count": count
#         }

#         # Build staff -> student mapping
#         if st_netid not in staff_to_student:
#             staff_to_student[st_netid] = {
#                 "first_name": st_first,
#                 "last_name": st_last,
#                 "students": {}
#             }
#         staff_to_student[st_netid]["students"][s_netid] = {
#             "first_name": s_first,
#             "last_name": s_last,
#             "interaction_count": count
#         }

#     return student_to_staff, staff_to_student
