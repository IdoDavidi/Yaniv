import Card
from Deck import Deck


class Player:

    def __init__(self, name):
        self.name = name
        self.hand = []

    # this method removes the last card from the deck and adds it to a player's hand
    def draw(self, deck):
        card = deck.draw()
        self.hand.append(card)

    # this method discards a card from player's hand
    def discard(self, card):
        self.hand.remove(card)

    def show_hand(self):
        print([str(card) for card in self.hand])

    def __str__(self):
        player_hand = ', '.join(str(card) for card in self.hand)
        return f"{self.name}: {player_hand}"
