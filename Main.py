from Game import Game

if __name__ == '__main__':
    try:
        game = Game()
        while True:
            for i in range(len(game.players)):
                if i == 0:
                    game.user_turn(game.players[i])  # user
                else:
                    game.npc_turn(game.players[i])  # NPC
    except SystemExit:
        print('Game is over')
    except Exception as e:
        print(f'error occurred: {e}')




    '''
    לטפל במקרים של input שגוי של ה user
    מחסנית גמורה
    הדפסות של NPC ו DEBUGGING
    '''