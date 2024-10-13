from app import create_app
from flask_socketio import SocketIO
from app.game import register_socketio_events

app = create_app()
socketio = SocketIO(app)
register_socketio_events(socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True)
