import random
from collections import defaultdict

from inputimeout import inputimeout

from Card import Card
from Deck import Deck
import Constants
from Player import Player


class Game:

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.discarded_pile = [self.deck.draw()]
        self.players = []
        self.table_score = {}
        self.user = None
        self.initialize()

    def initialize(self):
        num_of_players = self.get_num_of_players()
        self.create_players(num_of_players)
        self.deal_cards()
        for player in self.players:
            self.table_score[player] = 0

    def deal_cards(self):  # 5 rounds, in which every player draws single card to his hand, 5 total.
        for i in range(Constants.INITIAL_HAND_SIZE):
            for player in self.players:
                player.draw(self.deck)

    def get_num_of_players(self) -> int:
        while True:
            num_of_players = int(input(
                f'Please pick number of players between {Constants.MIN_AMOUNT_OF_PLAYERS} and'
                f' {Constants.MAX_AMOUNT_OF_PLAYERS}\n'))
            if Constants.MIN_AMOUNT_OF_PLAYERS <= num_of_players <= Constants.MAX_AMOUNT_OF_PLAYERS:
                return num_of_players
            else:
                print(
                    f'must be a number between {Constants.MIN_AMOUNT_OF_PLAYERS} and {Constants.MAX_AMOUNT_OF_PLAYERS}')

    def create_players(self, num_of_players):
        user_name = (input('Please enter your name\n'))
        self.user = Player(user_name)
        self.players.append(self.user)
        for i in range(1, num_of_players):
            npc_id = f'NPC{i}'
            npc_player = Player(npc_id)
            self.players.append(npc_player)

    def check_for_yaniv(self, player):
        total = sum(card.value for card in player.hand)
        if total <= Constants.YANIV:
            while True and player == self.user:
                print(f'\n{player.name} has a total hand value of {total} with:')
                player.show_hand()
                call = input('Do you wish to call YANIV? Y/N\n').upper()
                if call == 'Y':
                    print(f'\nYANIV! \tSUCK IT! \n{player.name} has total hand value of {total}')
                    winner, asaf_flag, asafed = self.check_for_asaf(player, total)
                    self.end_round(winner, asaf_flag, asafed)
                    self.new_round()
                    print('\nNew round began')
                    return True
                elif call == 'N':
                    break
                else:
                    print('Invalid input')
            else:  # player is an NPC
                print(f'\n{player.name} calls YANIV! SUCK IT! {player.name} has total hand value of {total} with:')
                player.show_hand()
                winner, asaf_flag, asafed = self.check_for_asaf(player, total)
                self.end_round(winner, asaf_flag, asafed)
                self.new_round()
                return True

    def check_for_asaf(self, yaniv_caller, yaniv_caller_hand_score):
        lowest_score = yaniv_caller_hand_score
        winner = yaniv_caller
        asaf_flag = False
        asafed = None
        for player in self.players:
            if player != yaniv_caller:
                player_hand_score = sum(card.value for card in player.hand)
                if player_hand_score <= lowest_score:
                    lowest_score = player_hand_score
                    winner = player
        if winner != yaniv_caller:
            asaf_flag = True
            asafed = yaniv_caller
            print(f'\nFUCKING ASAF! {winner.name} wins the round with a total hand value of {lowest_score}')
        return winner, asaf_flag, asafed

    def new_round(self):
        for player in self.players:
            player.hand.clear()
        self.deck = Deck()
        self.deck.shuffle()
        self.discarded_pile = [self.deck.draw()]
        self.deal_cards()

    def end_round(self, winner, asaf_flag, player_asafed):
        for player in self.players[:]:  # shallow copy of self.players[]
            if player != winner:
                player_total_hand_value = sum(card.value for card in player.hand)
                self.table_score[player] += player_total_hand_value
                if asaf_flag and player == player_asafed:  # player got ASAFed
                    print(f'{player.name} has been ASAFed, therefore they get extra {Constants.ASAF_FINE} points')
                    self.table_score[player] = player_total_hand_value + Constants.ASAF_FINE
                    print(f'{player.name} score is {self.table_score[player]}')
                else:  # player did not get ASAFed
                    if self.table_score[player] > Constants.GAME_OVER:  # player is out
                        print(f'{player.name} score is {self.table_score[player]}, they are out')
                        self.players.remove(player)
                        self.table_score.pop(player)
                        # finishing the whole game
                        if len(self.players) == 1:
                            print(
                                f'\nCongrats {self.players[0].name}, you are the winner! I salute you, fame and riches'
                                f' coming your way')
                            exit(0)  # should end the game here
                    elif self.table_score[player] == Constants.GAME_OVER:  # player has exactly 100 point
                        print(
                            f'{player.name} score is exactly {self.table_score[player]}, therefore their score is cut '
                            f'by half to {Constants.CUT_BY_HALF}')
                        self.table_score[player] = Constants.CUT_BY_HALF
                    else:  # player has less than 100 points
                        print(f'{player.name} score is {self.table_score[player]}')
            else:
                print(f'{player.name} score is {self.table_score[player]}')

    def slapdown_option(self, player, card_drew, recent_card_in_discarded_pile):
        if card_drew.eq_ranks(recent_card_in_discarded_pile):
            if player == self.user:
                try:
                    print('\nslapdown is optional')
                    #  limited time for user to slapdown
                    timeout_val = random.randint(Constants.SLAPDOWN_MIN_TIME, Constants.SLAPDOWN_MAX_TIME)
                    slap = int(inputimeout('press 0 and then Enter to SLAPDOWN THE SHIT OUT OF THEM\n',
                                           timeout_val))
                    if slap == 0:
                        self.discarded_pile.append(player.hand.pop(-1))
                        print(f"{player.name} SLAPPED THE SHIT OUT OF Y'ALL")
                        print(f'{player.name} current hand:')
                        player.show_hand()
                    else:
                        print(f'{player.name} gave up the slapdown')
                except Exception:
                    print(f"time's up! slapdown missed...\n")
            else:
                r = random.randint(1, 2)  # whether NPC will slap
                if r == 1:  # NPC will slap
                    print(f"\nSLAPDWOON!! \t {player.name} SLAPPED THE SHIT OUT OF Y'ALL")

    def user_turn(self, player):

        last_card_discarded = self.discarded_pile[-1]

        def discard_card():

            def appending_card_to_discarded_pile_and_removing_card_from_player_hand(card, card_id):
                self.discarded_pile.append(card)
                player.discard(card)
                hand.pop(card_id)

            def check_done_discarding():
                while True:
                    print('your current hand is:')
                    player.show_hand()
                    done_discarding = input('are you done discarding cards? Y/N\n').upper()
                    if done_discarding == 'N' or done_discarding == 'Y':
                        break
                    else:
                        print('Invalid input')
                if done_discarding == 'Y':
                    return True

            def enumerate_hand(player_hand):
                return list(enumerate([str(card) for card in player_hand]))  # display of player's hand where each card
                # has id starting

            # actual start  of user turn
            hand = enumerate_hand(player.hand)

            while True:
                print(f'\n{player.name} initial hand is:')
                player.show_hand()
                print(f'last discarded card: {last_card_discarded}')
                turn_type = int(input('Please choose the type of your turn: \n'
                                      '1.discard single card \n2.discard multiple cards with the same rank \n'
                                      '3.discard multiple consecutive cards with the same suit \n'))
                if 1 <= turn_type <= 3:
                    break
                else:
                    print('invalid choice')

            if turn_type == 1:  # single card discard:
                while True:
                    id_card_to_discard = int(input(f'Please choose a card to discard: {hand}\n'))
                    if 0 <= id_card_to_discard <= len(hand):
                        chosen_card = hand[id_card_to_discard][1]
                        print(f'{player.name} chose to discard: {chosen_card}')
                        chosen_card_obj = Card.from_string_to_card(chosen_card)
                        appending_card_to_discarded_pile_and_removing_card_from_player_hand(chosen_card_obj,
                                                                                            id_card_to_discard)
                        break
                    else:
                        print('Invalid choice')

            elif turn_type == 2:  # discard multiple cards with same rank
                first_card_flag = True
                done_flag = False
                while True:
                    if done_flag:
                        break
                    hand = enumerate_hand(player.hand)
                    id_card_to_discard = int(input(f'Please choose card to discard: {hand}\n'))
                    if 0 <= id_card_to_discard <= len(hand):
                        chosen_card = hand[id_card_to_discard][1]
                        print(f'you chose to discard: {chosen_card}')
                        chosen_card_obj = Card.from_string_to_card(chosen_card)
                        if first_card_flag:  # first card picked
                            first_card_flag = False
                            chosen_rank = chosen_card_obj.rank
                            appending_card_to_discarded_pile_and_removing_card_from_player_hand(chosen_card_obj,
                                                                                                id_card_to_discard)
                        else:  # not the first card picked
                            if chosen_card_obj.rank != chosen_rank:
                                print('Invalid choice, cards must be of the same rank')
                            else:
                                appending_card_to_discarded_pile_and_removing_card_from_player_hand(chosen_card_obj,
                                                                                                    id_card_to_discard)
                                while True:
                                    if check_done_discarding():
                                        done_flag = True
                                        break
                                    else:
                                        done_flag = False
                                        break
                    else:
                        print('Invalid choice')

            elif turn_type == 3:  # discard multiple consecutive cards with the same suit
                print('this is a reminder to choose card in ascending order :)')
                first_card_flag = True
                card_count = 0
                last_card_chosen = None
                while True:
                    hand = enumerate_hand(player.hand)
                    id_card_to_discard = int(input(f'Please choose card to discard: {hand}\n'))
                    if 0 <= id_card_to_discard <= len(hand):
                        chosen_card = hand[id_card_to_discard][1]
                        chosen_card_obj = Card.from_string_to_card(chosen_card)
                        if first_card_flag:  # first card picked
                            first_card_flag = False
                            chosen_suit = chosen_card_obj.suit
                            card_count += 1
                            last_card_chosen = chosen_card_obj
                            appending_card_to_discarded_pile_and_removing_card_from_player_hand(chosen_card_obj,
                                                                                                id_card_to_discard)
                        else:  # not the first card picked
                            if (chosen_card_obj.suit != chosen_suit or
                                    chosen_card_obj.value != last_card_chosen.value + 1):
                                print('Invalid choice, cards must be consecutive in the same suit')
                            else:
                                card_count += 1
                                last_card_chosen = chosen_card_obj
                                appending_card_to_discarded_pile_and_removing_card_from_player_hand(chosen_card_obj,
                                                                                                    id_card_to_discard)
                                if card_count >= 3:
                                    if check_done_discarding():
                                        break
                    else:
                        print('Invalid choice')

        def draw_card():
            print(f'{player.name} current hand is:')
            player.show_hand()
            print(f'Last card discarded: {last_card_discarded}')
            while True:
                choose_deck = int(input('Press 1 to draw card from the deck or 2 to draw the last discarded card\n'))
                if choose_deck == 1:
                    player.draw(self.deck)
                    print(f'you drew: {player.hand[-1]} from deck')
                    #  slapdown option
                    self.slapdown_option(player, player.hand[-1], self.discarded_pile[-1])
                    break
                elif choose_deck == 2:
                    card_drew = last_card_discarded
                    self.discarded_pile.remove(card_drew)
                    player.hand.append(card_drew)
                    print(f'you drew: {player.hand[-1]} from discarded pile')
                    break
                else:
                    print('Invalid input')

        new_round_flag = self.check_for_yaniv(player)
        if new_round_flag:
            last_card_discarded = self.discarded_pile[-1]
        discard_card()
        draw_card()
        print(f'you finished your turn, your hand: ')
        player.show_hand()

    def npc_turn(self, player):

        last_card_discarded = self.discarded_pile[-1]

        def discard_card():

            print(f'\n{player.name} turn starts.')
            # first option: multiple cards with same rank
            rank_ascended_sorted_hand = sorted(list(card.value for card in player.hand))
            count_rank_dic = defaultdict(int)
            for rank in rank_ascended_sorted_hand:
                count_rank_dic[rank] += 1
            most_appeared_rank = (max(count_rank_dic.items(), key=lambda item: (item[1], item[0])))

            # second option: consecutive cards with the same suit
            consecutive_suit = ''
            check_consecutive_dict = defaultdict(list)
            seq_to_discard = []
            for card in player.hand:
                check_consecutive_dict[card.suit].append(card.value)
            for suit in check_consecutive_dict:
                check_consecutive_dict[suit].sort()
                values = check_consecutive_dict[suit]
                if len(values) >= 3:
                    for i in range(len(values) - 2):
                        if values[i + 1] == values[i] + 1 and values[i + 2] == values[i] + 2:
                            seq_to_discard = [values[i], values[i + 1], values[i + 2]]
                            if i + 3 < len(values) and values[i + 3] == values[i] + 3:
                                seq_to_discard.append(values[i + 3])
                                if i + 4 < len(values) and values[i + 4] == values[i] + 4:
                                    seq_to_discard.append(values[i + 4])
                    consecutive_suit = suit
            # 3 or more consecutive cards with same suit are discarded
            if len(seq_to_discard) >= most_appeared_rank[1]:
                for i in range(len(seq_to_discard)):
                    print(f'{player.name} discards: {seq_to_discard[i]} of {consecutive_suit}')
                    card_obj_to_discard = Card(consecutive_suit, Card.card_value.get(seq_to_discard[i]))
                    for card in player.hand:
                        if card == card_obj_to_discard:
                            self.discarded_pile.append(card)
                            player.hand.remove(card)

            # same rank cards are discarded
            elif most_appeared_rank[1] > 1:
                for card in player.hand[:]:  # creates a shallow copy to iterate over
                    if card.value == most_appeared_rank[0]:
                        print(f'{player.name} discards {card}')
                        self.discarded_pile.append(card)
                        player.hand.remove(card)

            # a single card is discarded
            else:
                max_card = max(player.hand, key=lambda card: card.value)
                print(f'{player.name} discards {max_card}')
                self.discarded_pile.append(max_card)
                player.hand.remove(max_card)

        def draw_card():
            recent_card_discarded_this_turn = self.discarded_pile[-1]
            if last_card_discarded.value in list(card.value for card in player.hand):  # NPC has a card with
                # identical rank to the last card in the discarded pile
                print(f'{player.name} chose to draw from discarded pile')
                player.hand.append(last_card_discarded)
                print(f'{player.name} drew {player.hand[-1]} from discarded pile')
                self.discarded_pile.remove(last_card_discarded)

            else:  # random draw from 1: deck or 2: discarded pile
                r = random.randint(1, 2)
                if r == 1:
                    print(f'{player.name} chose to draw from deck')
                    player.draw(self.deck)
                    self.slapdown_option(player, player.hand[-1], recent_card_discarded_this_turn)
                else:
                    print(f'{player.name} chose to draw from discarded pile')
                    player.hand.append(last_card_discarded)
                    self.discarded_pile.remove(last_card_discarded)

        new_round_flag = self.check_for_yaniv(player)
        if new_round_flag:
            last_card_discarded = self.discarded_pile[-1]
        discard_card()
        draw_card()

