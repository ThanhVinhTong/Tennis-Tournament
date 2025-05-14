# run.py
from app import create_app, db, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        host='127.0.0.1',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True
    )
