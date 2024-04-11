from django.http import JsonResponse
from big2 import Poker

game = Poker()

def start_game(request):
    game.distribute()
    return JsonResponse({'message': 'Game started.'})

def make_move(request):
    player = int(request.GET.get('player'))
    cards = eval(request.GET.get('cards'))  # Assume cards are passed as a list of tuples

    try:
        game.play(player, cards)
        return JsonResponse({'message': 'Move successful.'})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

def check_validity(request):
    player = int(request.GET.get('player'))
    cards = eval(request.GET.get('cards'))  # Assume cards are passed as a list of tuples

    is_valid = game.valid(player, cards)
    return JsonResponse({'valid': is_valid})
