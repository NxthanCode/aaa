const socket = io();
let currentUser = null;
let isHost = false;
let currentTheme = 'light';
let userAvatars = {};
let questionTimer = null;
let currentQuestionIndex = 0;
socket.on('connect', () => {
    console.log('connected');
});
socket.on('username_set', (data) => {
    currentUser = data.username;
    isHost = data.is_host;
    showScreen('lobby-screen');
    updateUserList(data.users);
    updateGameState(data.game_state);
    const hostControls = document.getElementById('host-controls');
    const waitingMessage = document.getElementById('waiting-message');
    const hostGameControls = document.getElementById('host-game-controls');
    const hostResetControls = document.getElementById('host-reset-controls');
    if (isHost) {
        if (hostControls) hostControls.style.display = 'block';
        if (waitingMessage) waitingMessage.style.display = 'none';
        if (hostGameControls) hostGameControls.style.display = 'block';
        if (hostResetControls) hostResetControls.style.display = 'block';
    } else {
        if (hostControls) hostControls.style.display = 'none';
        if (waitingMessage) waitingMessage.style.display = 'block';
        if (hostGameControls) hostGameControls.style.display = 'none';
        if (hostResetControls) hostResetControls.style.display = 'none';
    }
});
socket.on('username_taken', (data) => {
    alert(data.message);
});
socket.on('user_joined', (data) => {
    updateUserList(data.users);
    updateGameState(data.game_state);
});
socket.on('user_left', (data) => {
    updateUserList(data.users);
    updateGameState(data.game_state);
});
socket.on('game_settings_updated', (data) => {
    updateGameState(data.game_state);
});
socket.on('game_started', (data) => {
    updateGameState(data.game_state);
    showScreen('game-screen');
    currentQuestionIndex = 0;
    displayQuestion(data.first_question, currentQuestionIndex);
    startQuestionTimer(data.game_state.time_per_question);
});
socket.on('question_timer_start', (data) => {
    currentQuestionIndex = data.question_index;
    startQuestionTimer(data.time_per_question);
});
socket.on('next_question', (data) => {
    updateGameState(data.game_state);
    currentQuestionIndex = data.game_state.current_question;
    displayQuestion(data.question, currentQuestionIndex);
    document.getElementById('answer-feedback').innerHTML = '';
    resetOptions();
    startQuestionTimer(data.game_state.time_per_question);
});
socket.on('scores_updated', (data) => {
    updateLiveScores(data.player_scores, data.players_answered);
});
socket.on('question_results', (data) => {
    showQuestionResults(data.correct_answer, data.player_scores);
});
socket.on('game_over', (data) => {
    updateGameState(data.game_state);
    showScreen('results-screen');
    displayResults(data.scores);
    clearTimeout(questionTimer);
});
socket.on('game_reset', (data) => {
    updateGameState(data.game_state);
    showScreen('lobby-screen');
    clearTimeout(questionTimer);
});
socket.on('new_host', (data) => {
    if (currentUser === data.username) {
        isHost = true;
        document.getElementById('host-controls').style.display = 'block';
        document.getElementById('host-game-controls').style.display = 'block';
        document.getElementById('host-reset-controls').style.display = 'block';
        document.getElementById('waiting-message').style.display = 'none';
        alert('you r now the host');
    }
});
function setUsername() {
    const usernameInput = document.getElementById('username-input');
    const username = usernameInput.value.trim();
    if (username.length < 2) {
        alert('enter a username with at least 2 characters');
        return;
    }
    if (username.length > 20) {
        alert('username must be less than 20 characters');
        return;
    }
    socket.emit('set_username', { username: username });
}
function updateGameSettings() {
    if (!isHost) return;
    
    const questionCount = document.getElementById('question-count').value;
    const theme = document.getElementById('theme-select').value;
    
    console.log(`Updating settings: ${questionCount} questions, ${theme} theme`);
    
    socket.emit('update_game_settings', {
        question_count: parseInt(questionCount),  // FIX: Ensure it's integer
        theme: theme
    });
}
function startGame() {
    if (!isHost) return;
    socket.emit('start_game');
}
function nextQuestion() {
    if (!isHost) return;
    socket.emit('next_question');
}
function resetGame() {
    if (!isHost) return;
    socket.emit('reset_game');
}
function submitAnswer(questionIndex, answerIndex) {
    socket.emit('submit_answer', {
        question_index: questionIndex,
        answer_index: answerIndex
    });
}
function returnToLobby() {
    showScreen('lobby-screen');
}
function startQuestionTimer(timePerQuestion) {
    clearTimeout(questionTimer);
    const timerElement = document.getElementById('timer');
    if (!timerElement) {
        const gameInfo = document.getElementById('game-info');
        const timerDiv = document.createElement('div');
        timerDiv.className = 'info-item';
        timerDiv.id = 'timer-container';
        timerDiv.innerHTML = `
            <i class="fas fa-clock"></i>
            Time: <span id="timer">${timePerQuestion}</span>s
        `;
        gameInfo.appendChild(timerDiv);
    }
    let timeLeft = timePerQuestion;
    updateTimerDisplay(timeLeft);
    questionTimer = setInterval(() => {
        timeLeft--;
        updateTimerDisplay(timeLeft);
        if (timeLeft <= 0) {
            clearInterval(questionTimer);
            document.getElementById('timer').textContent = '0';
        }
    }, 1000);
}
function updateTimerDisplay(timeLeft) {
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = timeLeft;
        if (timeLeft <= 10) {
            timerElement.style.color = '#ff4444';
            timerElement.style.fontWeight = 'bold';
        } else if (timeLeft <= 20) {
            timerElement.style.color = '#ffaa00';
        } else {
            timerElement.style.color = '';
        }
    }
}
function showScreen(screenId) {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}
function updateUserList(users) {
    const userList = document.getElementById('user-list');
    userList.innerHTML = '<h3><i class="fas fa-user-friends"></i> Players (' + users.length + ')</h3>';
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        const avatar = generateUserAvatar(user.username);
        userItem.innerHTML = `
            <div class="user-avatar">${avatar}</div>
            <div class="user-info">
                <span class="user-name">${user.username}</span>
                ${user.is_host ? '<span class="host-badge"><i class="fas fa-crown"></i> HOST</span>' : ''}
            </div>
        `;
        userList.appendChild(userItem);
    });
}
function generateUserAvatar(username) {
    if (!userAvatars[username]) {
        const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f'];
        const color = colors[username.length % colors.length];
        const letter = username.charAt(0).toUpperCase();
        userAvatars[username] = {
            letter: letter,
            color: color
        };
    }
    return userAvatars[username].letter;
}
function updateGameState(gameState) {
    currentTheme = gameState.theme;
    document.body.className = currentTheme + '-theme';
    if (isHost) {
        document.getElementById('question-count').value = gameState.question_count;
        document.getElementById('theme-select').value = gameState.theme;
    }
    document.getElementById('current-question').textContent = gameState.current_question + 1;
    document.getElementById('total-questions').textContent = gameState.question_count;
}
function updateLiveScores(scores, playersAnswered) {
    const liveScoresElement = document.getElementById('live-scores');
    if (!liveScoresElement) {
        const gameInfo = document.getElementById('game-info');
        const scoresDiv = document.createElement('div');
        scoresDiv.id = 'live-scores';
        scoresDiv.className = 'live-scores';
        gameInfo.appendChild(scoresDiv);
    }
    const sortedScores = scores.sort((a, b) => b.score - a.score);
    document.getElementById('live-scores').innerHTML = `
        <div class="scores-header">
            <i class="fas fa-chart-line"></i>
            Live Scores (${playersAnswered}/${Object.keys(userAvatars).length} answered)
        </div>
        <div class="scores-list">
            ${sortedScores.map(score => `
                <div class="score-line ${score.username === currentUser ? 'current-user' : ''}">
                    <span class="score-name">${score.username}</span>
                    <span class="score-points">${score.score} pts</span>
                </div>
            `).join('')}
        </div>
    `;
}
function displayQuestion(question, questionIndex) {
    if (!question) {
        console.error('No question provided');
        return;
    }
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    if (!questionText || !optionsContainer) {
        console.error('Question elements not found');
        return;
    }
    questionText.textContent = question.question;
    optionsContainer.innerHTML = '';
    const optionLetters = ['A', 'B', 'C', 'D'];
    if (!question.options || !Array.isArray(question.options)) {
        console.error('Question has no options array');
        return;
    }
    question.options.forEach((option, index) => {
        const optionElement = document.createElement('div');
        optionElement.className = 'option';
        optionElement.innerHTML = `
            <span class="option-letter">${optionLetters[index]}</span>
            <span class="option-text">${option}</span>
        `;
        optionElement.onclick = () => {
            if (optionElement.classList.contains('disabled')) return;
            const allOptions = document.querySelectorAll('.option');
            allOptions.forEach(opt => {
                opt.classList.add('disabled');
            });
            optionElement.classList.add('selected');
            submitAnswer(questionIndex, index);
        };
        optionsContainer.appendChild(optionElement);
    });
}
function resetOptions() {
    document.querySelectorAll('.option').forEach(option => {
        option.classList.remove('selected', 'correct', 'incorrect', 'disabled');
    });
}
function showQuestionResults(correctAnswer, playerScores) {
    const options = document.querySelectorAll('.option');
    options[correctAnswer].classList.add('correct');
    const feedback = document.getElementById('answer-feedback');
    const selectedOption = document.querySelector('.option.selected');
    if (selectedOption) {
        if (Array.from(options).indexOf(selectedOption) === correctAnswer) {
            feedback.innerHTML = '<i class="fas fa-check-circle"></i> correct';
            feedback.className = 'answer-feedback correct-feedback';
        } else {
            feedback.innerHTML = '<i class="fas fa-times-circle"></i> incorrect';
            feedback.className = 'answer-feedback incorrect-feedback';
        }
    } else {
        feedback.innerHTML = '<i class="fas fa-clock"></i> time\'s up!';
        feedback.className = 'answer-feedback time-up-feedback';
    }
    updateLiveScores(playerScores, Object.keys(userAvatars).length);
}
function displayResults(scores) {
    const scoreBoard = document.getElementById('score-board');
    scoreBoard.innerHTML = '<h3><i class="fas fa-chart-bar"></i> Final Leaderboard</h3>';
    const sortedScores = scores.sort((a, b) => b.score - a.score);
    sortedScores.forEach((score, index) => {
        const scoreItem = document.createElement('div');
        scoreItem.className = `score-item ${index === 0 ? 'winner' : ''} ${score.username === currentUser ? 'current-user' : ''}`;
        const avatar = generateUserAvatar(score.username);
        scoreItem.innerHTML = `
            <div class="user-avatar">${avatar}</div>
            <div class="score-details">
                <span class="user-name">
                    ${score.username}
                    ${index === 0 ? '<i class="fas fa-trophy trophy-icon"></i>' : ''}
                </span>
                <span class="score-value">
                    ${score.score} / ${document.getElementById('total-questions').textContent}
                    ${index < 3 ? `<span class="rank-badge">#${index + 1}</span>` : ''}
                </span>
            </div>
        `;
        scoreBoard.appendChild(scoreItem);
    });
}
document.getElementById('username-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        setUsername();
    }
});
document.getElementById('theme-select').addEventListener('change', function() {
    if (isHost) {
        updateGameSettings();
    }
});
document.getElementById('question-count').addEventListener('change', function() {
    if (isHost) {
        updateGameSettings();
    }
});
