from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
import datetime
import os
import uuid

app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')


socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

active_users = {}
chat_messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    if user_id in active_users:
        username = active_users[user_id]['username']
        del active_users[user_id]
        emit('user_left', {'username': username, 'users': list(active_users.values())}, broadcast=True)
        print(f"User disconnected: {username}")

@socketio.on('set_username')
def handle_set_username(data):
    username = data['username'].strip()
    user_id = request.sid
    
    if any(user['username'].lower() == username.lower() for user in active_users.values()):
        emit('username_taken', {'message': 'Username already taken!'})
        return
    
    active_users[user_id] = {
        'username': username,
        'joined_at': datetime.datetime.now().isoformat(),
        'user_id': user_id
    }
    
    emit('username_set', {
        'username': username,
        'users': list(active_users.values()),
        'messages': chat_messages[-50:]
    })
    
    emit('user_joined', {
        'username': username,
        'users': list(active_users.values())
    }, broadcast=True)
    
    print(f" User joined: {username}")

@socketio.on('send_message')
def handle_send_message(data):
    user_id = request.sid
    if user_id not in active_users:
        return
    
    username = active_users[user_id]['username']
    message_text = data['message'].strip()
    
    if message_text:
        message_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'message': message_text,
            'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
            'user_id': user_id
        }
        
        chat_messages.append(message_data)
        
        if len(chat_messages) > 100:
            chat_messages.pop(0)
        
        emit('new_message', message_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
