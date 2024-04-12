import random

class Poker:
    def __init__(self):
        self.players = {0: [], 1: [], 2: [], 3: []}
        self.turn = 0
        self.last = None

    def distribute(self):
        cards = [(i, j) for i in range(3, 16) for j in range(1, 5)]
        random.shuffle(cards)
        for i in range(4):
            self.players[i] = cards[i*13:(i+1)*13]
        for player, cards in self.players.items():
            if (3, 4) in cards:
                self.turn = player
                break

    def skip(self):
        self.turn = (self.turn + 1) % 4

    def play(self, player, cards):
        if player != self.turn:
            raise ValueError("It's not your turn")
        if not all(card in self.players[player] for card in cards):
            raise ValueError("You don't have these cards")
        s=set(self.players[player])
        s -= set(cards)
        self.players[player]=list(s)
        self.last = (cards,player)
        self.turn = (self.turn + 1) % 4


    def valid(self, player, cards):
        if not self.last:
            return self.is_valid_combination(cards) and (3,4) in cards
        if self.last and self.last[1] == player:
            return self.is_valid_combination(cards)
        else:
            return self.is_valid_combination(cards) and self.compare_combinations(self.last, cards)

    def is_valid_combination(self, cards):
        if len(cards) == 1:
            return True
        elif len(cards) == 2:
            return cards[0][0] == cards[1][0]
        elif len(cards) == 5:
            return self.is_straight(cards) or self.is_flush(cards) or self.is_full_house(cards) or self.is_king_kong(cards) or self.is_straight_flush(cards)
        else:
            return False

    def is_straight(self, cards):
        return all(cards[i][0] == cards[i+1][0] + 1 for i in range(4))

    def is_flush(self, cards):
        return all(card[1] == cards[0][1] for card in cards)

    def is_full_house(self, cards):
        return len(set(card[0] for card in cards)) == 2 and any(cards.count(card) == 3 for card in cards)

    def is_king_kong(self, cards):
        return len(set(card[0] for card in cards)) == 2 and any(cards.count(card) == 4 for card in cards)

    def is_straight_flush(self, cards):
        return self.is_straight(cards) and self.is_flush(cards)

    def compare_combinations(self, last, cards):
        if len(last) == 1:
            return cards[0][0] > last[0][0] or (cards[0][0] == last[0][0] and cards[0][1] < last[0][1])
        elif len(last) == 2:
            return cards[0][0] > last[0][0] or (cards[0][0] == last[0][0] and cards[0][1] < last[0][1])
        elif len(last) == 5:
            if self.is_straight(last):
                return self.is_straight(cards) and cards[-1][0] > last[-1][0]
            elif self.is_flush(last):
                return self.is_flush(cards) and cards[-1][0] > last[-1][0]
            elif self.is_full_house(last):
                return self.is_full_house(cards) and cards[0][0] > last[0][0]
            elif self.is_king_kong(last):
                return self.is_king_kong(cards) and cards[0][0] > last[0][0]
            elif self.is_straight_flush(last):
                return self.is_straight_flush(cards) and cards[-1][0] > last[-1][0]
            else:
                return False
        else:
            return False
# Test the game
game = Poker()
game.distribute()
print(game.valid(game.turn,[(3,4),(2,3)]))

