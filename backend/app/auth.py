import jwt
from flask import request, jsonify, current_app, request
from functools import wraps
from flask_socketio import emit

def roles_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get('Authorization', '')
            parts = auth.split()
            if len(parts)!=2 or parts[0].lower()!='bearer':
                return jsonify(error='Token missing'), 401
            token = parts[1]

            try:
                payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify(error='Token expired'), 401
            except jwt.InvalidTokenError:
                return jsonify(error='Invalid token'), 401

            # 1) correct netid key
            netid = payload.get('netid')
            # 2) your roles map now holds lists
            roles_map = payload.get('roles', {})
            course_id = kwargs.get('course_id')
            if not course_id:
                data = request.get_json(silent=True) or {}
                course_id = data.get('course_id')
            # get the list of roles (or empty list)
            user_roles_for_course = roles_map.get(course_id, [])

            # check intersection
            if not any(r in required_roles for r in user_roles_for_course):
                return jsonify(error=f'Forbidden: Insufficient role, needed {required_roles}'), 403

            # stash the user
            request.user = {'net_id': netid, 'roles': roles_map}
            return f(*args, **kwargs)
        return decorated
    return decorator


def socket_roles_required(required_roles, course_id_key='course_id'):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = request.environ.get('user', {})
            roles_map = user.get('roles', {})
            data = args[0] if args else {}
            course_id = data.get(course_id_key)

            # get the array (or empty)
            user_roles_for_course = roles_map.get(course_id, [])

            # if no overlap, forbidden
            if not any(r in required_roles for r in user_roles_for_course):
                emit('error', {'message': 'Forbidden: Insufficient role'})
                return

            return f(*args, **kwargs)
        return decorated
    return decorator

# Only check if netid is in the token (for routes that don't need a specific per role check)
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        parts = auth.split()
        if len(parts)!=2 or parts[0].lower()!='bearer':
            return jsonify(error='Token missing'), 401
        token = parts[1]
        try:
            payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify(error='Token expired'), 401
        except jwt.InvalidTokenError:
            return jsonify(error='Invalid token'), 401

        request.user = payload.get('netid')
        return f(*args, **kwargs)
    return decorated



