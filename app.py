from app import create_app
from flask_socketio import SocketIO
from app.game import register_socketio_events
import eventlet

eventlet.monkey_patch()

app = create_app()
socketio = SocketIO(app)
register_socketio_events(socketio)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
