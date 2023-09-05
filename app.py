from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = '1234'  # Change this to a secure secret key

socketio = SocketIO(app, cors_allowed_origins="*")

# User model
class User:
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin

# Group model
class Group:
    def __init__(self, name):
        self.name = name
        self.members = set()

# Database for storing user and group data (for demonstration purposes)
users = {"kavya": User("kavya", "priya", is_admin=True)}
groups = {}

@app.route('/')
def index():
    return render_template('index.html')

# ... (Your login, logout, user management APIs as shown earlier)

# Group Management and Messaging
@socketio.on('create_group')
def create_group(data):
    group_name = data['groupName']
    if group_name not in groups:
        groups[group_name] = Group(group_name)
        emit('message', f'Group "{group_name}" created', broadcast=True)
        emit('available_groups', {'groups': list(groups.keys())}, broadcast=True)
    else:
        emit('message', f'Group "{group_name}" already exists', broadcast=True)

@socketio.on('delete_group')
def delete_group(data):
    group_name = data['groupName']
    if group_name in groups:
        del groups[group_name]
        emit('message', f'Group "{group_name}" deleted', broadcast=True)
        emit('available_groups', {'groups': list(groups.keys())}, broadcast=True)
    else:
        emit('message', f'Group "{group_name}" not found', broadcast=True)

# Admin API: Add User to Group
@socketio.on('add_user_to_group')
def add_user_to_group(data):
    group_name = data['groupName']
    username = data['username']

    if group_name in groups and username in users:
        group = groups[group_name]
        group.members.add(username)
        emit('message', f'User "{username}" added to group "{group_name}"', room=group_name)
    elif group_name not in groups:
        emit('message', f'Group "{group_name}" not found', broadcast=True)
    else:
        emit('message', f'User "{username}" not found', room=group_name)

# Admin API: Remove User from Group
@socketio.on('remove_user_from_group')
def remove_user_from_group(data):
    group_name = data['groupName']
    username = data['username']

    if group_name in groups:
        group = groups[group_name]
        if username in group.members:
            group.members.remove(username)
            emit('message', f'User "{username}" removed from group "{group_name}"', room=group_name)
        else:
            emit('message', f'User "{username}" is not in group "{group_name}"', room=group_name)
    else:
        emit('message', f'Group "{group_name}" not found', broadcast=True)

@socketio.on('send_group_message')
def send_group_message(data):
    group_name = data['groupName']
    username = data['username']
    message = data['message']
    if group_name in groups and username in groups[group_name].members:
        emit('message', f'{username}: {message}', room=group_name)
    elif group_name not in groups:
        emit('message', f'Group "{group_name}" not found', broadcast=True)
    else:
        emit('message', f'User "{username}" is not in group "{group_name}"', room=group_name)

@socketio.on('connect')
def handle_connect():
    print('User connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('User disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
