import jwt
from flask import request, jsonify, current_app, request
from functools import wraps
from flask_socketio import emit

def roles_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # Expect the token in the Authorization header as "Bearer <token>"
            auth_header = request.headers.get('Authorization', None)
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]

            if not token:
                return jsonify({'error': 'HTTP: Token is missing'}), 401

            try:
                payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
                user_roles = payload.get('roles', {})
                course_id = kwargs.get('course_id')
                user_role = user_roles.get(course_id)
                
                if user_role not in required_roles:
                    return jsonify({'error': 'Forbidden: Insufficient role'}), 403
                
                # Attach token data to request
                request.user = {'net_id': payload.get('sub'), 'roles': user_roles}
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator


def socket_roles_required(required_roles, course_id_key='course_id'):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get the socket session (user info stored at connection time)
            user = request.environ.get('user')
            
            # Assume the event's data is passed as the first argument
            data = args[0] if args else {}
            course_id = data.get(course_id_key)
            
            # Check if the user exists and has a role for this course
            if not user or user.get('roles', {}).get(course_id) not in required_roles:
                emit('error', {'message': 'Forbidden: Insufficient role'})
                return  # Do not proceed further
                
            # Proceed to call the original event handler
            return f(*args, **kwargs)
        return decorated
    return decorator

