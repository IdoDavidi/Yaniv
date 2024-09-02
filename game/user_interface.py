from .const import const


class user_interface:
    USER_CHOOSES_NUM_OF_PLAYER = f'Please pick number of players between {const.MIN_AMOUNT_OF_PLAYERS} and {const.MAX_AMOUNT_OF_PLAYERS}\n'
    INVALID_NUM_OF_PLAYERS = f'must be a number between {const.MIN_AMOUNT_OF_PLAYERS} and {const.MAX_AMOUNT_OF_PLAYERS}'
    USER_ENTERS_THEIR_NAME = 'Please enter your name\n'
    NPC_ID = 'NPC{id}'
    USER_CHOOSE_WHETHER_TO_CALL_YANIV = 'Do you wish to call YANIV? Y/N\n'
    INSTRUCTIONS_FOR_SLAPDOWN = 'press y and then Enter to SLAPDOWN THE SHIT OUT OF THEM\n'
    CHECK_DONE_DISCARDING = 'are you done discarding cards? Y/N\n'
    PLAYER_CHOOSES_CARD_TO_DISCARD = 'Please choose a card to discard: {hand}\n'
