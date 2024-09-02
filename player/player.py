class Player:

    def __init__(self, name):
        self.name = name
        self.hand = []

    # this method removes the last card from the deck and adds it to a player's hand
    def draw(self, deck):
        card = deck.draw()
        self.hand.append(card)

    # this method discards a card from player's hand
    def discard(self, enum_hand, card, card_id):
        self.hand.remove(card)
        enum_hand.pop(card_id)

    def show_hand(self):
        print(f'\n{self.name} hand is:')
        print([str(card) for card in self.hand])

    def __str__(self):
        player_hand = ', '.join(str(card) for card in self.hand)
        return f"{self.name}: {player_hand}"

    # this method returns enumeration of player's hand in a tuple
    # (index, card string representation, card object)
    def enumerate_hand(self):
        return [(i, str(card)) for i, card in enumerate(self.hand)]
