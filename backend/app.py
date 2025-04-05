# backend/app.py
# This block of code is to prevent an error which happens because the flask‑cas‑ng code (or its dependency) is using the name basestring, which was removed in Python 3. 
# In Python 2, basestring was a built‑in type that served as a common base class for str and unicode
import builtins
import os

if not hasattr(builtins, 'basestring'):
    builtins.basestring = str
    
from app import create_app
from app.socket_events import register_socket_events

app, socketio = create_app()
register_socket_events(socketio)

PORT = int(os.getenv('PORT'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002)