from game import *

test_mate_board = np.zeros((8, 8), dtype=int)
test_mate_board[1, 1] = -6
test_mate_board[6, 6] = -5
test_mate_board[5, 5] = -1
test_mate_board[7, 7] = 6

test_game = Game(board=test_mate_board)
test_game.sim_game()


for i in range(5):
    game = Game(seed=i)
    game.sim_game()
