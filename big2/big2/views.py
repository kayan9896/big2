from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .big2 import Poker
import json
import time
import random
import uuid

# Global variable to store the list of players waiting for a game
waitlist = []

# Global variable to store the current games in progress
games = {}
assigned={}

@csrf_exempt
def start_game(request):
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
            return JsonResponse(response)
    waitlist.remove(user_id)
    return JsonResponse({'message': 'Timeout waiting for another player'})
    
def match():
    while len(waitlist) >= 4:
            game_id = len(games)
            game = Poker()
            game.distribute()
            games[game_id] = game
            for i in range(4):
                usr=waitlist.pop(0)
                assigned[usr]=(game_id,i)


def assign_players(game_id, players):
    for i, player in enumerate(players):
        games[game_id].players[i] = set([(i, j) for i in range(3, 16) for j in range(1, 5)])

@csrf_exempt
def play(request):
    data = json.loads(request.body)
    game_id = data['game_id']
    player_id = data['player_id']
    cards = data['cards']
    games[game_id].play(player_id, cards)
    return JsonResponse({'cards': list(games[game_id].players[player_id])})

@csrf_exempt
def skip(request):
    game_id = json.loads(request.body)['game_id']
    games[game_id].skip()
    return JsonResponse({'turn': games[game_id].turn})

@csrf_exempt
def valid(request):
    data = json.loads(request.body)
    game_id = data['game_id']
    player_id = data['player_id']
    cards = data['cards']
    return JsonResponse({'valid': games[game_id].valid(player_id, cards)})