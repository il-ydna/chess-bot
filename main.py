from game import *

test_mate_board = np.zeros((8, 8), dtype=int)
test_mate_board[1, 1] = -6
test_mate_board[6, 6] = -5
test_mate_board[5, 5] = -1
test_mate_board[7, 7] = 6

test_game = Game(board=test_mate_board)
test_game.sim_game()

games_to_sim = 100

start_time = time.perf_counter()
for i in range(games_to_sim):
    game = Game(seed=i)
    game.sim_game()
end_time = time.perf_counter()
elapsed_time_ms = (end_time - start_time) * 1000

print("average ms to run sim:", elapsed_time_ms/games_to_sim)