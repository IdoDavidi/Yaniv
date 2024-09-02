import random
from collections import defaultdict
from enum import Enum
from inputimeout import inputimeout
from player import Player
from card import Card
from deck import Deck
from .user_interface import user_interface
from .const import const
import logging


class turn_Type(Enum):
    DISCARD_SINGLE_CARD = 1
    DISCARD_MULTIPLE_SAME_VALUE = 2
    DISCARD_MULTIPLE_CONSECUTIVE = 3

    @staticmethod
    # this method builds the input message to the user from the turn_Type Enum
    def user_chosen_turn_type():
        prompt_message = "Please choose the type of your turn:\n"
        for turn in turn_Type:
            prompt_message += f"{turn.value}. {turn.name.replace('_', ' ').capitalize()}\n"
        return prompt_message


class Game:

    def __init__(self):
        self.deck = Deck()
        self.discarded_pile = []
        self.players = []
        self.table_score = {}
        self.user = None
        self.initialize()

    def initialize(self):
        self.deck.shuffle()
        self.discarded_pile.append(self.deck.draw())
        num_of_players = self.get_num_of_players()
        self.create_players(num_of_players)
        self.deal_cards()
        for player in self.players:
            self.table_score[player] = 0

    def deal_cards(self):  # 5 rounds, in which every player draws single card to his hand, 5 total.
        for i in range(const.INITIAL_HAND_SIZE):
            for player in self.players:
                player.draw(self.deck)

    def get_num_of_players(self):
        while True:
            try:
                num_of_players = int(input(user_interface.USER_CHOOSES_NUM_OF_PLAYER))
                if const.MIN_AMOUNT_OF_PLAYERS <= num_of_players <= const.MAX_AMOUNT_OF_PLAYERS:
                    return num_of_players
                else:
                    print(user_interface.INVALID_NUM_OF_PLAYERS)
            except ValueError:
                print(const.VALUE_ERROR)

    def create_players(self, num_of_players):
        user_name = (input(user_interface.USER_ENTERS_THEIR_NAME))
        self.user = Player(user_name)
        self.players.append(self.user)
        for i in range(1, num_of_players):
            npc_id = user_interface.NPC_ID.format(id=str(i))
            npc_player = Player(npc_id)
            self.players.append(npc_player)

    def check_for_yaniv(self, player):
        total = sum(card.value for card in player.hand)
        if total <= const.YANIV:
            while True and player == self.user:
                player.show_hand()
                print(f'\n{player.name} has a total hand value of {total}')
                call = input(user_interface.USER_CHOOSE_WHETHER_TO_CALL_YANIV).upper()
                if call == const.YES:
                    print(const.PLAYER_DECLARES_YANIV_MSG.format(player_name=player.name, total_val=total))
                    winner, asaf_flag, asafed = self.check_for_asaf(player, total)
                    self.end_round(winner, asaf_flag, asafed)
                    self.new_round()
                    break
                elif call == const.NO:
                    break
                else:
                    print(const.INVALID_INPUT)
            else:  # player is an NPC
                print(const.PLAYER_DECLARES_YANIV_MSG.format(player_name=player.name, total_val=total))
                player.show_hand()
                winner, asaf_flag, asafed = self.check_for_asaf(player, total)
                self.end_round(winner, asaf_flag, asafed)
                self.new_round()

    # this method checks if other player has lower hand than the player who called Yaniv
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
            print(f'\nFUCKING ASAF! {winner} wins the round with a total hand value of {lowest_score}')
        return winner, asaf_flag, asafed

    def new_round(self):
        for player in self.players:
            player.hand.clear()
        self.deck = Deck()
        self.deck.shuffle()
        self.discarded_pile = [self.deck.draw()]
        self.deal_cards()
        print('\nNew round began')

    def end_round(self, winner, asaf_flag, player_asafed):
        for player in self.players[:]:  # shallow copy of self.players[]
            if player != winner:
                player_total_hand_value = sum(card.value for card in player.hand)
                self.table_score[player] += player_total_hand_value
                if asaf_flag and player == player_asafed:  # player got ASAFed
                    print(f'{player.ame} has been ASAFed, therefore they get extra {const.ASAF_PENALTY_POINTS} points')
                    self.table_score[player] = player_total_hand_value + const.ASAF_PENALTY_POINTS
                else:  # player did not get ASAFed
                    if self.table_score[player] > const.GAME_OVER_POINTS:  # player is out
                        print(f'{player.name} score is {self.table_score[player]}, they are out')
                        self.players.remove(player)
                        self.table_score.pop(player)
                        # finishing the whole game
                        if len(self.players) == 1:  # a single player remained
                            print(const.GAME_FINISHED_MSG.format(winner=self.players[0].name))
                            exit(0)  # games ends
                    elif self.table_score[player] == const.GAME_OVER_POINTS:  # player has exactly 100 point
                        print(
                            f'{player.name} score is exactly {self.table_score[player]}, therefore their score is reduced by half to {const.CUT_BY_HALF}')
                        self.table_score[player] = const.CUT_BY_HALF
                    else:  # player has less than 100 points
                        print(f'{player.name} score is {self.table_score[player]}')
            else:  # winner gets additional 0 points
                print(f'{player.name} score is {self.table_score[player]}')

    def slapdown_option(self, player, card_drew, recent_card_in_discarded_pile):
        if card_drew.rank == recent_card_in_discarded_pile.rank:
            if player == self.user:
                try:
                    print('slapdown is optional')
                    #  limited time for user to slapdown using inputimeout library
                    timeout_val = random.randint(const.SLAPDOWN_MIN_TIME, const.SLAPDOWN_MAX_TIME)
                    slap = inputimeout(user_interface.INSTRUCTIONS_FOR_SLAPDOWN, timeout_val).upper()
                    if slap == const.YES:
                        self.discarded_pile.append(player.hand.pop(-1))  # adding recently drown card to discarded pile
                        print(f"{player.name} SLAPPED THE SHIT OUT OF Y'ALL")
                        player.show_hand()
                    else:
                        print(f'{player.name} gave up the slapdown')
                except Exception:
                    print(f"time's up! slapdown missed...\n")
            else:
                r = random.choice([const.YES, const.NO])  # whether NPC will slap
                if r == const.YES:  # NPC will slap
                    print(f"{player.name} SLAPPED THE SHIT OUT OF Y'ALL")

    # this method discards card from user's hand to the discarded pile and updating user's hand
    def user_discards(self, chosen_card_obj, enum_hand, card_indx, player):
        self.discarded_pile.append(chosen_card_obj)
        player.discard(enum_hand, chosen_card_obj, card_indx)
        enum_hand = player.enumerate_hand()  # re-enumerate to update indices
        return enum_hand

    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    # this method discards first card in user's turn, and return tuple containing discarded card (suit, value)
    def discard_single_card(self, enum_hand, player):
        while True:
            try:
                indx_card_to_discard = int(input(user_interface.PLAYER_CHOOSES_CARD_TO_DISCARD.format(hand=enum_hand)))
                if const.ZERO <= indx_card_to_discard < len(enum_hand):  # Ensure valid index range
                    chosen_card_str = enum_hand[indx_card_to_discard][1]
                    print(f'{player.name} chose to discard: {chosen_card_str}')
                    chosen_card_obj = player.hand[indx_card_to_discard]
                    chosen_suit = chosen_card_obj.suit
                    chosen_value = chosen_card_obj.value
                    enum_hand = self.user_discards(chosen_card_obj, enum_hand, indx_card_to_discard, player)
                    return (chosen_suit, chosen_value, enum_hand)  # for multiple card discard turn types
                else:
                    raise IndexError(const.INDX_ERROR)
            except ValueError:
                print(const.VALUE_ERROR)
            except IndexError as e:
                print(e)

    def discard_multiple_same_value(self, enum_hand, player):
        first_card_flag = True
        while True:
            if first_card_flag:
                _, chosen_value, enum_hand = self.discard_single_card(enum_hand, player)
                first_card_flag = False
                # additional card to discard
            try:
                indx_card_to_discard = int(
                    input(user_interface.PLAYER_CHOOSES_CARD_TO_DISCARD.format(hand=enum_hand)))
                chosen_card_obj = player.hand[indx_card_to_discard]  # retrieving card obj from hand at specific index
                # Ensure valid index range and same value
                if not const.ZERO <= indx_card_to_discard < len(player.hand):
                    raise IndexError(const.INDX_ERROR)
                if not chosen_value == chosen_card_obj.value:
                    raise ValueError(const.WRONG_VALUE_ERROR)
                chosen_card_str = enum_hand[indx_card_to_discard][1]
                print(f'{player.name} chose to discard: {str(chosen_card_obj)}')
                enum_hand = self.user_discards(chosen_card_obj, enum_hand, indx_card_to_discard, player)
                if self.check_done_discarding(player):  # checks if player done discarding
                    break
            except ValueError as e:
                if str(e) == const.WRONG_VALUE_ERROR:
                    print(const.WRONG_VALUE_ERROR)
                else:
                    print(const.VALUE_ERROR)
            except IndexError as e:
                print(e)

    def discard_multiple_consecutive(self, enum_hand, player):
        first_card_flag = True
        card_count = 0
        while True:
            if first_card_flag:
                chosen_suit, chosen_value, _ = self.discard_single_card(enum_hand, player)
                card_count += 1
                first_card_flag = False
            # additional cards selection
            hand = player.enumerate_hand()
            try:
                indx_card_to_discard = int(input(f'Please choose card to discard: {hand}\n'))
                if not 0 <= indx_card_to_discard <= len(hand):
                    raise IndexError(const.INDX_ERROR)
                if not player.hand[indx_card_to_discard].suit == chosen_suit:
                    raise ValueError(const.WRONG_SUIT_ERROR)
                if not player.hand[indx_card_to_discard].value == chosen_value + 1:
                    raise ValueError(const.WRONG_VALUE_ERROR)
                chosen_card_obj = player.hand[indx_card_to_discard]
                chosen_value += 1
                print(f'{player.name} chose to discard: {str(chosen_card_obj)}')
                enum_hand = self.user_discards(chosen_card_obj, enum_hand, indx_card_to_discard, player)
                card_count += 1
                if card_count >= 3:
                    if self.check_done_discarding(player):
                        break
            except ValueError as e:
                if str(e) == const.WRONG_VALUE_ERROR:
                    print(const.WRONG_VALUE_ERROR)
                elif str(e) == const.WRONG_SUIT_ERROR:
                    print()
                else:
                    print(const.VALUE_ERROR)
            except IndexError as e:
                print(e)

    def check_done_discarding(self, player):
        while True:
            player.show_hand()
            done_discarding = input(user_interface.CHECK_DONE_DISCARDING).upper()
            if done_discarding == const.NO or done_discarding == const.YES:
                break
            else:
                print(const.INVALID_INPUT)
        if done_discarding == const.YES:
            return True

    def npc_check_consecutive(self, player):
        check_consecutive_dict = defaultdict(list)
        for card in player.hand:  # Group cards by suit and sort their values
            check_consecutive_dict[card.suit].append(card)
        for suit, cards in check_consecutive_dict.items():
            cards.sort(key=lambda x: x.value)
            for i in range(len(cards) - 2):  # Find consecutive sequences
                if cards[i].value == cards[i + 1].value - 1 == cards[i + 2].value - 2:
                    seq_to_discard = cards[i:i + 3]
                    for j in range(i + 3, len(cards)):  # Extend the sequence if possible
                        if cards[j].value == cards[j - 1].value + 1:
                            seq_to_discard.append(cards[j])
                        else:
                            break
                    for card_to_discard in seq_to_discard:
                        print(f'{player.name} discards: {card_to_discard.value} of {card_to_discard.suit}')
                        self.discarded_pile.append(card_to_discard)
                        player.hand.remove(card_to_discard)
                    return True

    def npc_check_same_value(self, player):
        rank_ascended_sorted_hand = sorted(list(card.value for card in player.hand))
        count_rank_dic = defaultdict(int)
        for rank in rank_ascended_sorted_hand:
            count_rank_dic[rank] += 1
        most_appeared_rank = (max(count_rank_dic.items(), key=lambda item: (item[1], item[0])))
        if most_appeared_rank[1] > 1:
            for card in player.hand[:]:  # creates a shallow copy to iterate over
                if card.value == most_appeared_rank[0]:
                    print(f'{player.name} discards {card}')
                    self.discarded_pile.append(card)
                    player.hand.remove(card)
                    return True

    def npc_single_card_discard(self, player):
        max_card = max(player.hand, key=lambda card: card.value)
        print(f'{player.name} discards {max_card}')
        self.discarded_pile.append(max_card)
        player.hand.remove(max_card)

    def user_turn(self, player):
        def discard_card():
            while True:
                try:
                    player.show_hand()
                    print(f'last discarded card: {last_card_discarded}')
                    turn_type = int(input(turn_Type.user_chosen_turn_type()))
                    if turn_type in [item.value for item in turn_Type]:
                        break  # valid input
                    else:  # invalid input
                        print(const.INVALID_INPUT)
                except ValueError:
                    print(const.INVALID_INPUT)
            # single card discard:
            if turn_type == turn_Type.DISCARD_SINGLE_CARD.value:
                self.discard_single_card(enum_hand, player)
            # discard multiple cards with same rank:
            elif turn_type == turn_Type.DISCARD_MULTIPLE_SAME_VALUE.value:
                self.discard_multiple_same_value(enum_hand, player)
            # discard multiple consecutive cards with the same suit
            elif turn_type == turn_Type.DISCARD_MULTIPLE_CONSECUTIVE.value:
                print('this is a reminder to choose card in ascending order :)')
                self.discard_multiple_consecutive(enum_hand, player)

        def draw_card():
            player.show_hand()
            print(f'Last card discarded: {last_card_discarded}')
            while True:
                try:
                    choose_deck = int(
                        input('Press 1 to draw card from the deck or 2 to draw the last discarded card\n'))
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
                except ValueError:
                    print(const.VALUE_ERROR)

        # actual start  of user turn
        self.check_for_yaniv(player)
        enum_hand = player.enumerate_hand()
        last_card_discarded = self.discarded_pile[-1]
        discard_card()
        draw_card()
        print(f'you finished your turn')
        player.show_hand()

    def npc_turn(self, player):
        def discard_card():
            print(f'\n{player.name} turn starts.')
            # first priority: consecutive cards with the same suit
            if self.npc_check_consecutive(player):
                return
            # second priority: same value cards are discarded
            elif self.npc_check_same_value(player):
                return
            # third priority: single card is discarded
            else:
                self.npc_single_card_discard(player)

        def draw_card():
            recent_card_discarded_this_turn = self.discarded_pile[-1]
            if last_card_discarded.value in list(card.value for card in player.hand):  # NPC has a card with
                # identical rank to the last card in the discarded pile
                print(f'{player.name} chose to draw from discarded pile')
                player.hand.append(last_card_discarded)
                logging.debug(f'{player.name} drew {player.hand[-1]} from discarded pile')
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

        self.check_for_yaniv(player)
        last_card_discarded = self.discarded_pile[-1]
        discard_card()
        draw_card()
        print(f'{player.name} finished their turn')
        player.show_hand()
