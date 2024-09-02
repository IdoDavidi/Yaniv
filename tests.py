import builtins
import unittest
from game import Game, const, turn_Type
from player import Player
from unittest.mock import patch, MagicMock
from game import user_interface
from card import Card


class MyTestCase(unittest.TestCase):

    @patch('game.Game.__init__', lambda self: None)  # Patch __init__ so it doesn't execute
    def setUp(self):
        # Initialize game without running __init__
        self.game = Game()

        # Manually set the attributes that would be set in __init__
        self.game.players = []
        self.game.discarded_pile = []

        self.player = Player(name="NPC1")
        self.game.players.append(self.player)

        # Assign a hand with a consecutive sequence
        self.player.hand = [
            Card(suit='♣', rank='Six'),
            Card(suit='♣', rank='Seven'),
            Card(suit='♣', rank='Eight'),
            Card(suit='♠', rank='Three'),
            Card(suit='♠', rank='Ten'),
        ]

    def test_npc_check_consecutive(self):
        # Run the npc_check_consecutive method
        result = self.game.npc_check_consecutive(self.player)

        # Assertions to check if the consecutive cards were discarded
        self.assertTrue(result)
        self.assertEqual(len(self.player.hand), 2)  # 3 cards should be discarded
        self.assertNotIn(Card(suit='♣', rank='Six'), self.player.hand)
        self.assertNotIn(Card(suit='♣', rank='Seven'), self.player.hand)
        self.assertNotIn(Card(suit='♣', rank='Eight'), self.player.hand)
        self.assertEqual(len(self.game.discarded_pile), 3)  # 3 cards should be in the discarded pile

    def enumerate_hand(player_hand):
        # display of player's hand where each card has an id
        return [(i, str(card), card) for i, card in enumerate(player_hand)]

    @patch('builtins.input', side_effect=[str(i) for i in range(5)])
    def test_user_chosen_turn_type(self, mock_input):
        for i in range(5):
            x = int(input(user_interface.user_chosen_turn_type()))
            self.assertEqual(x, i)

    @patch('game.Game.initialize')
    @patch('builtins.input', side_effect=[str(i) for i in range(9)])
    def test_get_num_of_players(self, mock_input):
        # with patch.object(Game, 'initialize', return_value=None):  # Patch the initialize method
        game = Game()
        for i in range(9):
            with patch('builtins.input', return_value=str(i)):
                if i < const.MIN_AMOUNT_OF_PLAYERS or i > const.MAX_AMOUNT_OF_PLAYERS:
                    with self.assertRaises(ValueError):
                        game.get_num_of_players()
                else:
                    result = game.get_num_of_players()
                    self.assertEqual(result, i)

    @patch('game.Game.initialize')
    @patch('builtins.input', side_effect=['User', 'NPC1', 'NPC2'])
    def test_create_players(self, mock_initialize, mock_input):
        num_of_players = 3
        game = Game()
        game.create_players(num_of_players)

        # Check if the first player is the user
        self.assertEqual(game.players[0].name, 'User')

        # Check if the correct number of players were created
        self.assertEqual(len(game.players), num_of_players)

        # Check if NPCs were created correctly
        self.assertEqual(game.players[1].name, 'NPC1')
        self.assertEqual(game.players[2].name, 'NPC2')


if __name__ == '__main__':
    unittest.main()
