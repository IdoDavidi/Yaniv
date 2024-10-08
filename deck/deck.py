from card import Card
import random


class Deck:

    def __init__(self):
        self.deck = []
        for suit in Card.suits:
            for rank in Card.ranks:
                if rank != 'Joker':  # Exclude jokers from standard cards
                    self.deck.append(Card(suit, rank))
        self.deck.append(Card(None, 'Joker'))
        self.deck.append(Card(None, 'Joker'))

    def shuffle(self):
        random.shuffle(self.deck)

    # this method removes the card from the top of the deck and returns it
    def draw(self):
        return self.deck.pop(0)

    def __str__(self):
        res = ''
        count = 0
        for card in self.deck:
            res += (card.__str__() + '\n')
            count += 1
        print(count)
        return res


if __name__ == '__main__':
    deck = Deck()
    print(deck)