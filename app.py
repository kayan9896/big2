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
online={}

def match():
    while len(waitlist) >= 4:
            game_id = len(games)
            game = Poker()
            game.distribute()
            games[game_id] = game
            online[game_id]={}
            for i in range(4):
                usr=waitlist.pop(0)
                assigned[usr]=(game_id,i)
                online[game_id][i]=time.time()

@app.route('/start', methods=['GET'])
def start_game():
    # Add the player to the waitlist
    user_id = uuid.uuid4()
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
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    cards = data.get('cards')

    # Check if the game and player exist
    if game_id not in games or player_id not in games[game_id].players:
        return jsonify({'message': 'Invalid game or player'}), 400

    # Call the play function and return the updated player's cards
    try:
        games[game_id].play(player_id, cards)
        if len(online[game_id])>0:
            while games[game_id].turn not in online[game_id]:
                games[game_id].skip()

        response = {
            'cards': games[game_id].players,
            'last': games[game_id].last[0],
            'turn': games[game_id].turn
        }
        for i in range(4):
            if len(games[game_id].players[i]) ==0:
                # Broadcast gameover message to all players in the game
                socketio.emit('gameover',{'winner':i})  
                  # Remove the finished game 
        socketio.emit('game_state_update', response)      
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@app.route('/skip', methods=['POST'])
def skip_turn():
    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    # Check if the game and player exist
    if game_id not in games or player_id not in games[game_id].players:
        return jsonify({'message': 'Invalid game or player'}), 400

    # Call the skip function and return the updated turn
    games[game_id].skip()
    if len(online[game_id])>0:
        while games[game_id].turn not in online[game_id]:
            games[game_id].skip()

    response = {
            'cards': games[game_id].players,
            'last': games[game_id].last[0],
            'turn': games[game_id].turn
        }
    print(game_id)    
    socketio.emit('game_state_update', response) 
    return jsonify(response), 200

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

import threading

def clean_up_games():
    while True:
        current_time = time.time()
        print(current_time)
        for game_id, game in list(games.items()):
            print(current_time,game.last_active)
            if game.last_active < current_time - 3600:
                del games[game_id]
                del online[game_id]
                print(games)
                print(f"Game {game_id} has been removed due to inactivity.")
        time.sleep(1800)

# Run the clean_up_games function every 30 minutes
cleanup_thread = threading.Thread(target=clean_up_games)
cleanup_thread.daemon = True  # Set as daemon so it exits when the main thread exits
cleanup_thread.start()

heartbeat_interval = 5  # seconds


@socketio.on('heartbeat')
def handle_heartbeat(data):
    player_id = data.get('player_id')
    game_id= data.get('game_id')
    if game_id in online and player_id in online[game_id]:  # Check if player is still in the game
        online[game_id][player_id] = time.time()

from threading import Timer

def check_inactive_players():
    print(' Check for inactive players and handle game switch')
    for game_id in online:
        dlt=[]
        for player_id in online[game_id]:
            if time.time() - online[game_id][player_id] > heartbeat_interval * 2:
                dlt.append(player_id)
        for i in dlt:
            online[game_id].pop(i)
            print(i)
        if len(online[game_id])>0:
            while games[game_id].turn not in online[game_id]:
                games[game_id].skip()

                response = {
                            'cards': games[game_id].players,
                            'last': games[game_id].last[0],
                            'turn': games[game_id].turn
                        }   
                socketio.emit('game_state_update', response)   
                
                
    # Schedule the next check
    t = Timer(heartbeat_interval, check_inactive_players)
    t.daemon = True
    t.start()

check_inactive_players()  # Start the recurring check

@socketio.on('player_left')
def handle_player_left(data):
    game_id = data.get('game_id')
    player_id = data.get('player_id')  

    # Check if the game and player exist
    if game_id in games and player_id in games[game_id].players:
        # Mark the player as left or disconnected (you can implement this state)
        games[game_id].players[player_id]['status'] = 'left'
        print(f"Player {player_id} has left the game.")

        # Check if there are any active players left in the game, if not end the game.
        active_players = [player for player in games[game_id].players if player['status'] != 'left']
        if len(active_players) <= 1:
            # Broadcast gameover message to all remaining players (if any)
            socketio.emit('gameover', {'winner': 'No winner'})
            # Remove the finished game
            del games[game_id]
        else:
            # Continue the game with the next active player's turn
            games[game_id].skip()
            response = {
                'turn': games[game_id].turn
            }
            socketio.emit('game_state_update', response) 


if __name__ == '__main__':
    app.run(debug=True)