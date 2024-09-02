from game import Game

if __name__ == '__main__':
    try:
        game = Game()
        while True:
            i = 0
            while i < len(game.players):  # mark1
                if i == 0:
                    # Check if the user is still in the game before taking their turn
                    if game.user in game.players:
                        game.user_turn(game.players[i])  # user
                    else:
                        game.npc_turn(game.players[i])  # NPC, user's is out
                else:
                    game.npc_turn(game.players[i])  # NPC
                i += 1
    except SystemExit:
        print('Game is over')
    except Exception as e:
        print(f'error occurred: {e}')
