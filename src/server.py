from .app import create_app
from .extensions import socketio

app = create_app()

if __name__ == '__main__':
    # Run with socketio to enable eventlet
    socketio.run(app, host='0.0.0.0', port=5000)
