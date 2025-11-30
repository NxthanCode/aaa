document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    let currentUsername = '';
    window.setUsername = function() {
        const usernameInput = document.getElementById('usernameInput');
        const username = usernameInput.value.trim();
        if (username.length < 2) {
            alert('Username must be at least 2 characters long');
            return;
        }
        if (username.length > 20) {
            alert('Username must be less than 20 characters');
            return;
        }
        socket.emit('set_username', { username: username });
    }
    socket.on('username_set', (data) => {
        currentUsername = data.username;
        document.getElementById('usernameModal').style.display = 'none';
        document.getElementById('chatContainer').style.display = 'flex';
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
        document.getElementById('messageInput').focus();
        data.messages.forEach(message => {
            displayMessage(message);
        });
        updateUsersList(data.users);
    });
    socket.on('username_taken', (data) => {
        alert(data.message);
    });
    window.sendMessage = function() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        if (message) {
            socket.emit('send_message', { message: message });
            messageInput.value = '';
        }
    }
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    socket.on('new_message', (data) => {
        displayMessage(data);
    });
    function displayMessage(data) {
        const messagesContainer = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.user_id === socket.id ? 'own' : 'other'}`;
        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${data.username}</strong> • ${data.timestamp}
            </div>
            <div class="message-content">${data.message}</div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    socket.on('user_joined', (data) => {
        updateUsersList(data.users);
        const messagesContainer = document.getElementById('messagesContainer');
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = `${data.username} joined the chat`;
        messagesContainer.appendChild(notification);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
    socket.on('user_left', (data) => {
        updateUsersList(data.users);
        const messagesContainer = document.getElementById('messagesContainer');
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = `${data.username} left the chat`;
        messagesContainer.appendChild(notification);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
    function updateUsersList(users) {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '';
        users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.className = 'user-item';
            userDiv.innerHTML = `
                <div class="user-status"></div>
                <span>${user.username}</span>
            `;
            usersList.appendChild(userDiv);
        });
    }
    document.getElementById('usernameInput').focus();
    document.getElementById('usernameInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            setUsername();
        }
    });
});
