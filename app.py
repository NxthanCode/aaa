from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
import datetime
import random

app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = 'dev-secret-key-123'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

active_users = {}
game_state = {
    'status': 'lobby',
    'host': None,
    'question_count': 5,
    'theme': 'light',
    'current_question': 0,
    'questions': [],
    'scores': {},
    'player_answers': {},
    'question_start_time': None,
    'time_per_question': 30
}

ALL_QUIZ_QUESTIONS = [
    { 'question': 'What is the capital of Italy?', 'options': ['Rome', 'Milan', 'Naples', 'Turin'], 'correct': 0 },
    { 'question': 'Which planet is closest to the Sun?', 'options': ['Venus', 'Mercury', 'Earth', 'Mars'], 'correct': 1 },
    { 'question': 'How many continents does Earth have?', 'options': ['5', '6', '7', '8'], 'correct': 2 },
    { 'question': 'What is the largest ocean on Earth?', 'options': ['Atlantic', 'Indian', 'Pacific', 'Arctic'], 'correct': 2 },
    { 'question': 'Which animal is known as the King of the Jungle?', 'options': ['Tiger', 'Lion', 'Leopard', 'Panther'], 'correct': 1 },
    { 'question': 'Which gas do plants absorb?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen'], 'correct': 2 },
    { 'question': 'How many degrees are in a circle?', 'options': ['180', '270', '360', '540'], 'correct': 2 },
    { 'question': 'Which country is famous for the pyramids?', 'options': ['India', 'Egypt', 'Mexico', 'Peru'], 'correct': 1 },
    { 'question': 'What is the largest mammal?', 'options': ['Elephant', 'Blue Whale', 'Hippo', 'Giraffe'], 'correct': 1 },
    { 'question': 'Which is the longest river in the world?', 'options': ['Amazon', 'Nile', 'Yangtze', 'Danube'], 'correct': 0 },
    { 'question': 'Which metal is used in batteries?', 'options': ['Copper', 'Lithium', 'Iron', 'Gold'], 'correct': 1 },
    { 'question': 'What is H2O?', 'options': ['Water', 'Oxygen', 'Hydrogen', 'Salt'], 'correct': 0 },
    { 'question': 'How many legs does a spider have?', 'options': ['6', '8', '10', '12'], 'correct': 1 },
    { 'question': 'Which country invented pizza?', 'options': ['France', 'Italy', 'USA', 'Germany'], 'correct': 1 },
    { 'question': 'Which planet has rings?', 'options': ['Venus', 'Earth', 'Saturn', 'Mars'], 'correct': 2 },
    { 'question': 'What is the hardest natural substance?', 'options': ['Gold', 'Iron', 'Diamond', 'Quartz'], 'correct': 2 },
    { 'question': 'Which organ pumps blood?', 'options': ['Liver', 'Heart', 'Lungs', 'Kidneys'], 'correct': 1 },
    { 'question': 'Which number is the Roman numeral X?', 'options': ['5', '10', '15', '20'], 'correct': 1 },
    { 'question': 'What is the smallest planet?', 'options': ['Mars', 'Mercury', 'Venus', 'Pluto'], 'correct': 1 },
    { 'question': 'How many days are in a leap year?', 'options': ['365', '366', '367', '364'], 'correct': 1 },
    { 'question': 'What color are bananas when ripe?', 'options': ['Green', 'Yellow', 'Brown', 'Orange'], 'correct': 1 },
    { 'question': 'Which planet is known as the Red Planet?', 'options': ['Mars', 'Venus', 'Jupiter', 'Saturn'], 'correct': 0 },
    { 'question': 'Which tool is used to measure temperature?', 'options': ['Barometer', 'Thermometer', 'Hygrometer', 'Speedometer'], 'correct': 1 },
    { 'question': 'How many minutes are in 2 hours?', 'options': ['90', '100', '120', '150'], 'correct': 2 },
    { 'question': 'Which animal cannot fly?', 'options': ['Eagle', 'Penguin', 'Sparrow', 'Falcon'], 'correct': 1 },
    { 'question': 'Which shape has three sides?', 'options': ['Square', 'Triangle', 'Circle', 'Hexagon'], 'correct': 1 },
    { 'question': 'Which of these is a fruit?', 'options': ['Carrot', 'Potato', 'Apple', 'Spinach'], 'correct': 2 },
    { 'question': 'What do bees produce?', 'options': ['Milk', 'Silk', 'Honey', 'Oil'], 'correct': 2 },
    { 'question': 'Which month has 28 days?', 'options': ['February', 'April', 'June', 'August'], 'correct': 0 },
    { 'question': 'What is a baby cat called?', 'options': ['Puppy', 'Kitten', 'Calf', 'Cub'], 'correct': 1 },
    { 'question': 'Which direction does the sun rise?', 'options': ['North', 'South', 'East', 'West'], 'correct': 2 },
    { 'question': 'Which organ helps you breathe?', 'options': ['Heart', 'Liver', 'Lungs', 'Stomach'], 'correct': 2 },
    { 'question': 'What is the freezing point of water?', 'options': ['0°C', '10°C', '50°C', '-10°C'], 'correct': 0 },
    { 'question': 'Which planet is the largest?', 'options': ['Earth', 'Venus', 'Jupiter', 'Saturn'], 'correct': 2 },
    { 'question': 'Which country is the largest by area?', 'options': ['USA', 'Russia', 'China', 'Canada'], 'correct': 1 },
    { 'question': 'Which animal is the fastest?', 'options': ['Cheetah', 'Horse', 'Lion', 'Dog'], 'correct': 0 },
    { 'question': 'What is the largest continent?', 'options': ['Africa', 'Europe', 'Asia', 'Australia'], 'correct': 2 },
    { 'question': 'Which food is high in vitamin C?', 'options': ['Banana', 'Orange', 'Bread', 'Rice'], 'correct': 1 },
    { 'question': 'What is a group of wolves called?', 'options': ['Pack', 'Herd', 'Flock', 'Swarm'], 'correct': 0 },
    { 'question': 'Which season comes after spring?', 'options': ['Winter', 'Summer', 'Autumn', 'Fall'], 'correct': 1 },
    { 'question': 'What is the capital of Japan?', 'options': ['Seoul', 'Beijing', 'Tokyo', 'Bangkok'], 'correct': 2 },
    { 'question': 'Which animal lives in Australia?', 'options': ['Panda', 'Kangaroo', 'Tiger', 'Lion'], 'correct': 1 },
    { 'question': 'How many colors are in a rainbow?', 'options': ['5', '6', '7', '8'], 'correct': 2 },
    { 'question': 'Which fruit has seeds on the outside?', 'options': ['Apple', 'Strawberry', 'Pear', 'Orange'], 'correct': 1 },
    { 'question': 'What do cows drink?', 'options': ['Milk', 'Water', 'Juice', 'Tea'], 'correct': 1 },
    { 'question': 'What is the capital of Spain?', 'options': ['Barcelona', 'Madrid', 'Valencia', 'Seville'], 'correct': 1 },
    { 'question': 'Which desert is the largest?', 'options': ['Sahara', 'Gobi', 'Kalahari', 'Atacama'], 'correct': 0 },
    { 'question': 'Which country uses the yen?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 1 },
    { 'question': 'What is Earth’s natural satellite?', 'options': ['Europa', 'Titan', 'Moon', 'Phobos'], 'correct': 2 },
    { 'question': 'Which part of the plant carries out photosynthesis?', 'options': ['Roots', 'Stem', 'Leaves', 'Flowers'], 'correct': 2 },
    { 'question': 'Which shape has 4 equal sides?', 'options': ['Rectangle', 'Square', 'Triangle', 'Circle'], 'correct': 1 },
    { 'question': 'Which is a primary color?', 'options': ['Green', 'Purple', 'Red', 'Teal'], 'correct': 2 },
    { 'question': 'What is the capital of Germany?', 'options': ['Munich', 'Berlin', 'Hamburg', 'Frankfurt'], 'correct': 1 },
    { 'question': 'Where do polar bears live?', 'options': ['Antarctica', 'Arctic', 'Australia', 'Africa'], 'correct': 1 },
    { 'question': 'What is the tallest mountain?', 'options': ['K2', 'Everest', 'Mont Blanc', 'Denali'], 'correct': 1 },
    { 'question': 'What is the main language in Brazil?', 'options': ['Spanish', 'Portuguese', 'English', 'French'], 'correct': 1 },
    { 'question': 'Which liquid do humans need to survive?', 'options': ['Milk', 'Water', 'Oil', 'Soda'], 'correct': 1 },
    { 'question': 'Which sport uses a bat?', 'options': ['Football', 'Cricket', 'Tennis', 'Swimming'], 'correct': 1 },
    { 'question': 'Which bird cannot fly?', 'options': ['Eagle', 'Ostrich', 'Crow', 'Parrot'], 'correct': 1 },
    { 'question': 'How many continents touch the Pacific Ocean?', 'options': ['2', '3', '4', '5'], 'correct': 2 },
    { 'question': 'Which is the smallest continent?', 'options': ['Europe', 'Australia', 'South America', 'Africa'], 'correct': 1 },
    { 'question': 'Which animal lays eggs?', 'options': ['Dog', 'Cat', 'Chicken', 'Cow'], 'correct': 2 },
    { 'question': 'What is the capital of Canada?', 'options': ['Toronto', 'Ottawa', 'Vancouver', 'Montreal'], 'correct': 1 },
    { 'question': 'How many teeth does an adult have?', 'options': ['20', '24', '28', '32'], 'correct': 3 },
    { 'question': 'Which fruit is yellow?', 'options': ['Strawberry', 'Banana', 'Grape', 'Plum'], 'correct': 1 },
    { 'question': 'Which continent is Egypt in?', 'options': ['Asia', 'Europe', 'Africa', 'South America'], 'correct': 2 },
    { 'question': 'Which organ helps digestion?', 'options': ['Heart', 'Stomach', 'Lungs', 'Brain'], 'correct': 1 },
    { 'question': 'Which animal says "Moo"?', 'options': ['Sheep', 'Cow', 'Dog', 'Goat'], 'correct': 1 },
    { 'question': 'What is 5 × 5?', 'options': ['20', '25', '30', '35'], 'correct': 1 },
    { 'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'India', 'Thailand'], 'correct': 1 },
    { 'question': 'What shape is a stop sign?', 'options': ['Hexagon', 'Octagon', 'Pentagon', 'Triangle'], 'correct': 1 },
    { 'question': 'Which insect makes honey?', 'options': ['Butterfly', 'Bee', 'Ant', 'Fly'], 'correct': 1 },
    { 'question': 'Which is the biggest animal on land?', 'options': ['Elephant', 'Hippo', 'Rhino', 'Giraffe'], 'correct': 0 },
    { 'question': 'What do plants release?', 'options': ['CO₂', 'Oxygen', 'Nitrogen', 'Helium'], 'correct': 1 },
    { 'question': 'Which ocean is the smallest?', 'options': ['Pacific', 'Atlantic', 'Indian', 'Arctic'], 'correct': 3 },
    { 'question': 'Which animal is known for black-and-white stripes?', 'options': ['Tiger', 'Zebra', 'Skunk', 'Panda'], 'correct': 1 },
    { 'question': 'Which country has the Eiffel Tower?', 'options': ['Italy', 'France', 'Germany', 'Spain'], 'correct': 1 },
    { 'question': 'How many weeks are in a year?', 'options': ['48', '50', '52', '54'], 'correct': 2 },
    { 'question': 'What is the capital of the UK?', 'options': ['Manchester', 'Birmingham', 'London', 'Liverpool'], 'correct': 2 },
    { 'question': 'Which planet is known for its big red spot?', 'options': ['Mars', 'Jupiter', 'Uranus', 'Neptune'], 'correct': 1 }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    if user_id in active_users:
        username = active_users[user_id]['username']
        del active_users[user_id]
        if game_state['host'] == user_id:
            if active_users:
                new_host_id = next(iter(active_users))
                game_state['host'] = new_host_id
                emit('new_host', {'username': active_users[new_host_id]['username']}, broadcast=True)
            else:
                reset_game()
        emit('user_left', {
            'username': username,
            'users': list(active_users.values()),
            'game_state': game_state
        }, broadcast=True)

@socketio.on('set_username')
def handle_set_username(data):
    username = data['username'].strip()
    user_id = request.sid
    if any(u['username'].lower() == username.lower() for u in active_users.values()):
        emit('username_taken')
        return
    is_host = len(active_users) == 0
    if is_host:
        game_state['host'] = user_id
    active_users[user_id] = {
        'username': username,
        'joined_at': datetime.datetime.now().isoformat(),
        'user_id': user_id,
        'is_host': is_host
    }
    game_state['scores'][user_id] = 0
    emit('username_set', {
        'username': username,
        'users': list(active_users.values()),
        'game_state': game_state,
        'is_host': is_host
    })
    emit('user_joined', {
        'username': username,
        'users': list(active_users.values()),
        'game_state': game_state
    }, broadcast=True)

@socketio.on('update_game_settings')
def handle_update_settings(data):
    if request.sid != game_state['host']:
        return
    game_state['question_count'] = int(data.get('question_count', 5))
    game_state['theme'] = data.get('theme', 'light')
    emit('game_settings_updated', {'game_state': game_state}, broadcast=True)

@socketio.on('start_game')
def handle_start_game():
    if request.sid != game_state['host']:
        return

    to_select = min(game_state['question_count'], len(ALL_QUIZ_QUESTIONS))
    selected = random.sample(ALL_QUIZ_QUESTIONS, to_select)

    game_state.update({
        'questions': selected,
        'current_question': 0,
        'status': 'playing',
        'player_answers': {},
        'scores': {uid: 0 for uid in active_users}
    })

    emit('game_started', {
        'game_state': game_state,
        'first_question': selected[0] if selected else None
    }, broadcast=True)
    start_question_timer()

def start_question_timer():
    game_state['question_start_time'] = datetime.datetime.now().isoformat()
    game_state['player_answers'] = {}
    emit('question_timer_start', {
        'time_per_question': game_state['time_per_question'],
        'question_index': game_state['current_question']
    }, broadcast=True)
    socketio.start_background_task(automatic_next_question)

def automatic_next_question():
    socketio.sleep(game_state['time_per_question'])
    if game_state['status'] == 'playing':
        calculate_question_scores()
        emit('question_results', {
            'game_state': game_state,
            'correct_answer': game_state['questions'][game_state['current_question']]['correct'],
            'player_scores': get_current_scores()
        }, broadcast=True)
        socketio.sleep(3)
        if game_state['status'] == 'playing':
            next_question()

def calculate_question_scores():
    idx = game_state['current_question']
    correct = game_state['questions'][idx]['correct']
    for uid, answers in game_state['player_answers'].items():
        if idx in answers and answers[idx] == correct:
            game_state['scores'][uid] += 1

@socketio.on('submit_answer')
def handle_submit_answer(data):
    user_id = request.sid
    q_idx = data.get('question_index')
    a_idx = data.get('answer_index')
    if user_id not in active_users or q_idx != game_state['current_question']:
        return
    if user_id not in game_state['player_answers']:
        game_state['player_answers'][user_id] = {}
    game_state['player_answers'][user_id][q_idx] = a_idx
    emit('scores_updated', {
        'player_scores': get_current_scores(),
        'players_answered': len(game_state['player_answers'])
    }, broadcast=True)

@socketio.on('next_question')
def handle_next_question():
    if request.sid != game_state['host']:
        return
    calculate_question_scores()
    next_question()

def next_question():
    game_state['current_question'] += 1
    if game_state['current_question'] < len(game_state['questions']):
        start_question_timer()
        emit('next_question', {
            'game_state': game_state,
            'question': game_state['questions'][game_state['current_question']]
        }, broadcast=True)
    else:
        game_state['status'] = 'results'
        emit('game_over', {
            'game_state': game_state,
            'scores': get_scores_with_usernames()
        }, broadcast=True)

def get_current_scores():
    return [{'username': active_users[uid]['username'], 'score': game_state['scores'][uid], 'user_id': uid} for uid in active_users]

def get_scores_with_usernames():
    return [{'username': active_users[uid]['username'], 'score': game_state['scores'][uid]} for uid in active_users]

def reset_game():
    game_state.update({
        'status': 'lobby',
        'host': None,
        'question_count': 5,
        'theme': 'light',
        'current_question': 0,
        'questions': [],
        'scores': {},
        'player_answers': {},
        'question_start_time': None
    })

@socketio.on('reset_game')
def handle_reset_game():
    if request.sid != game_state['host']:
        return
    reset_game()
    emit('game_reset', {'game_state': game_state}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
