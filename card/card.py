import dataclasses

@dataclasses.dataclass
class Card:
    card_value = {
        'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
        'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
        'Ten': 10, 'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 1, 'Joker': 0
    }

    suits = ("\u2663", "\u2665", "\u2666", "\u2660")

    ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
             'Ten', 'Jack', 'Queen', 'King', 'Ace', 'Joker')

    royalty = ('Jack', 'Queen', 'King', 'Ace')

    def __init__(self, suit, rank):
        if rank == 'Joker':
            self.suit = None
            self.rank = rank
            self.value = self.card_value[rank]
        else:
            self.suit = suit
            self.rank = rank
            self.value = self.card_value[rank]

    def __str__(self):
        if self.rank == 'Joker':
            return self.rank
        elif self.rank in self.royalty:
            return str(self.rank) + ' ' + self.suit
        else:
            return str(self.value) + ' ' + self.suit

    def __eq__(self, other):
        if self.suit == other.suit and self.rank == other.rank:
            return True
        return False

    @staticmethod
    def from_string_to_card(s):
        if s == 'Joker':
            return Card(None, 0)
        rank, suit = s.split('  ')
        return Card(suit, rank)

    def eq_ranks(self, other):
        if self.rank == other.rank:
            return True
        return False



