from flask import Flask, request, jsonify
import random
import time
from big2 import Poker
import uuid

from flask_cors import CORS
from flask_socketio import SocketIO, emit 
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# Global variable to store the list of players waiting for a game
waitlist = []

# Global variable to store the current games in progress
games = {}
assigned={}

def match():
    while len(waitlist) >= 4:
            game_id = str(uuid.uuid4())
            game = Poker()
            game.distribute()
            games[game_id] = game
            for i in range(4):
                usr=waitlist.pop(0)
                assigned[usr]=(game_id,i)

@app.route('/start', methods=['GET'])
def start_game():
    # Add the player to the waitlist
    user_id = str(uuid.uuid4())
    waitlist.append(user_id)
    t=5
    while t>0:
        time.sleep(6)
        t-=1
        match()
        print(games)
        print(assigned)
        if user_id in assigned:
            # Return the game details to the players
            response = {
                'user_id':user_id,
                'game_id': assigned[user_id][0],
                'player_id': assigned[user_id][1],
                'turn': games[assigned[user_id][0]].turn,
                'cards': games[assigned[user_id][0]].players
            }
            return jsonify(response), 200
    waitlist.remove(user_id)
    return jsonify({'message': 'Timeout waiting for another player'}), 500

@app.route('/play', methods=['POST'])
def play_card():
    data = request.get_json()
    if not data:
        return error_response('Invalid request data', 400)
    
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    cards = data.get('cards')
    
    if not all([game_id, player_id is not None, cards]):
        return error_response('Missing required fields', 400)
    
    if game_id not in games:
        return error_response('Game not found', 404)
    
    if player_id not in games[game_id].players:
        return error_response('Player not found in this game', 404)

    if games[game_id].is_turn_expired():
        games[game_id].skip()
        emit_game_state(game_id)
        return error_response('Turn time expired', 400)

    try:
        games[game_id].play(player_id, cards)
        
        for i in range(4):
            if len(games[game_id].players[i]) == 0:
                socketio.emit('gameover', {'winner': i}, room=str(game_id))
        
        emit_game_state(game_id)      
        return jsonify({'message': 'Play successful'}), 200
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        app.logger.error(f'Unexpected error in play_card: {str(e)}')
        return error_response('Internal server error', 500)

@app.route('/skip', methods=['POST'])
def skip_turn():
    data = request.get_json()
    is_valid, error_msg = validate_request_data(data, ['game_id', 'player_id'])
    if not is_valid:
        return error_response(error_msg, 400)
    
    game_id = data['game_id']
    player_id = data['player_id']
    
    if game_id not in games:
        return error_response('Game not found', 404)
    
    if player_id not in games[game_id].players:
        return error_response('Player not found in this game', 404)

    current_time = time.time()
    if current_time > games[game_id].turn_start_time + games[game_id].turn_duration:
        games[game_id].skip()

    try:
        games[game_id].skip()
        emit_game_state(game_id)
        logger.info(f'Player {player_id} skipped turn in game {game_id}')
        return jsonify({'message': 'Turn skipped'}), 200
    except Exception as e:
        logger.error(f'Error in skip_turn: {str(e)}')
        return error_response('Internal server error', 500)

@app.route('/valid', methods=['POST'])
def check_validity():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    cards = data.get('cards')

    # Check if the game and player exist
    if game_id not in games or player_id not in games[game_id].players:
        return jsonify({'message': 'Invalid game or player'}), 400

    # Call the valid function and return the result
    result = True if games[game_id].valid(player_id, cards) >0 else False
    response = {
        'valid': result
    }
    return jsonify(response), 200

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    # Check if the game and player exist
    if game_id not in games or player_id not in games[game_id].players:
        return jsonify({'message': 'Invalid game or player'}), 400

    # Call the play function and return the updated player's cards
    try:
        response = {
            'cards': games[game_id].players,
            'last': games[game_id].last[0] if games[game_id].last else None,
            'turn': games[game_id].turn
        }
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


connected_clients = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    connected_clients[request.sid] = user_id
    if user_id in assigned:
        game_id, _ = assigned[user_id]
        socketio.server.enter_room(request.sid, str(game_id))
        print(f"User {user_id} joined room {game_id}")
        emit_game_state(game_id)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = connected_clients.pop(request.sid, None)
    if user_id and user_id in assigned:
        game_id, player_id = assigned[user_id]
        socketio.server.leave_room(request.sid, str(game_id))
        print(f"User {user_id} left room {game_id}")
        # Mark the player as disconnected
        games[game_id].quit.add(player_id) 
        del assigned[user_id]

        # Skip the player's turn and proceed with the next available player
        if games[game_id].turn==player_id: games[game_id].skip()
        response = {
            'cards': games[game_id].players,
            'last': games[game_id].last[0] if games[game_id].last else None,
            'turn': games[game_id].turn
        }
        socketio.emit('game_state_update', response)
        

import threading

def emit_game_state(game_id):
    game = games[game_id]
    response = {
        'cards': game.players,
        'last': game.last[0] if game.last else None,
        'turn': game.turn,
        'turnStartTime': game.turn_start_time,
        'turnDuration': game.turn_duration,
        'room':game_id
    }
    socketio.emit('game_state_update', response, room=game_id)

def manage_game_turns():
    while True:
        current_time = time.time()
        for game_id, game in list(games.items()):
            if current_time - game.turn_start_time > game.turn_duration:
                game.skip()
                emit_game_state(game_id)
        time.sleep(1)  # Check every second

# Start the background thread
turn_manager_thread = threading.Thread(target=manage_game_turns)
turn_manager_thread.daemon = True
turn_manager_thread.start()


def clean_up_games():
    while True:
        current_time = time.time()
        print(current_time)
        for game_id, game in list(games.items()):
            print(current_time,game.last_active)
            if game.last_active < current_time - 600:
                del games[game_id]
                print(games)
                print(f"Game {game_id} has been removed due to inactivity.")
        time.sleep(300)


# Run the clean_up_games function every 30 minutes
cleanup_thread = threading.Thread(target=clean_up_games)
cleanup_thread.daemon = True  # Set as daemon so it exits when the main thread exits
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True)