# import sys
# from pathlib import Path
# sys.path.append(str(Path(__file__).parent.parent.parent))

from src import *

player1 = Player("Player 1")
player2 = Player("Player 2")
player3 = Player("Player 3")
player4 = Player("Player 4")

game = Game(player1, player2, player3, player4)
game.start_game()