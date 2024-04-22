import random
import time

class Poker:
    def __init__(self):
        self.players = {0: [], 1: [], 2: [], 3: []}
        self.turn = 0
        self.last = None
        self.last_active=None

    def distribute(self):
        cards = [(i, j) for i in range(3, 16) for j in range(1, 5)]
        random.shuffle(cards)
        for i in range(4):
            self.players[i] = sorted(cards[i*13:(i+1)*13],key=lambda c: (c[0],-c[1]))
        for player, cards in self.players.items():
            if cards[0]==(3,4):
                self.turn = player
                self.last=(None,player)
                break
        self.last_active=time.time()

    def skip(self):
        self.turn = (self.turn + 1) % 4

    def play(self, player, c):
        cards=[self.players[player][i] for i in c]
        if player != self.turn:
            raise ValueError("It's not your turn")
        if not all(card in self.players[player] for card in cards):
            raise ValueError("You don't have these cards")
        tmp=[]
        for i in range(len(self.players[player])):
            if i not in c: tmp.append(self.players[player][i])
        self.players[player]=tmp
        self.last = (cards,player)
        self.turn = (self.turn + 1) % 4
        self.last_active=time.time()


    def valid(self, player, c):
        if not c: return -1
        cards=[self.players[player][i] for i in c]
        if not self.last[0]:
            if self.turn==self.last[1]:
                if (3,4) in cards: return self.is_valid_combination(cards)
            else: return self.is_valid_combination(cards)
            return -1
        if self.last[1] == player:
            return self.is_valid_combination(cards)
        else:
            if len(cards)==len(self.last[0]):
                rk=self.is_valid_combination(cards)
                if rk>0: 
                    return self.compare_combinations(self.last[0], cards,rk)
        return -1

    def is_valid_combination(self, cards):
        if len(cards) == 1:
            return 1
        elif len(cards) == 2:
            if cards[0][0] == cards[1][0]: return 2
            return -1
        elif len(cards) == 3:
            if cards[0][0] == cards[1][0] and cards[1][0] == cards[2][0]: return 3
            return -1
        elif len(cards) == 5:
            if self.is_straight(cards): return 4 
            if self.is_flush(cards): return 5 
            if self.is_full_house(cards): return 6 
            if self.is_king_kong(cards): return 7
            if self.is_straight_flush(cards): return 8
        return -1

    def is_straight(self, cards):
        return all(cards[i][0] == cards[i+1][0] - 1 for i in range(4))

    def is_flush(self, cards):
        return all(card[1] == cards[0][1] for card in cards)

    def is_full_house(self, cards):
        return (cards[2][0]==cards[0][0] and cards[3][0]==cards[4][0]) or (cards[2][0]==cards[4][0] and cards[0][0]==cards[1][0])

    def is_king_kong(self, cards):
        return (cards[3][0]==cards[1][0])

    def is_straight_flush(self, cards):
        return self.is_straight(cards) and self.is_flush(cards)

    def compare_combinations(self, last, cards, rk):
        if len(last) == 1:
            return 1 if self.compare_last_one(last,cards) else -1
        elif len(last) == 2:
            return 2 if self.compare_last_one(last,cards) else -1
        elif len(last) == 3:
            return 3 if self.compare_last_one(last,cards) else -1
        elif len(last) == 5:
            if self.is_straight(last):
                if rk>4: return rk
                return 4 if self.compare_last_one(last,cards) else -1
            elif self.is_flush(last):
                if rk>5: return rk
                if rk<5: return -1
                return 5 if self.compare_last_one(last,cards) else -1
            elif self.is_full_house(last):
                if rk>6: return rk
                if rk<6: return -1
                return 6 if cards[2][0] > last[2][0] else -1
            elif self.is_king_kong(last):
                if rk>7: return rk
                if rk<7: return -1
                return 7 if cards[2][0] > last[2][0] else -1
            elif self.is_straight_flush(last):
                if rk<8: return -1
                return 8 if self.compare_last_one(last,cards) else -1
        else:
            return -1

    def compare_last_one(self,last,cards):
        return cards[-1][0] > last[-1][0] or (cards[-1][0] == last[-1][0] and cards[-1][1] < last[-1][1])
# Test the game
game = Poker()
game.distribute()
print(game.valid(game.turn,[1,2]))

