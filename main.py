import numpy as np


board = np.zeros(shape=(8, 8), dtype=int)

# piece guide:
# pieces = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen", 6: "king"}

# init white pieces
board[6] = 1
board[7, 1], board[7, 6] = 2, 2
board[7, 2], board[7, 5] = 3, 3
board[7, 0], board[7, 7] = 4, 4
board[7, 3], board[7, 4] = 5, 6
# init black pieces
board[1] = -1
board[0] = -board[7]

def poll_all_whites(game_board: np.ndarray):







print(f"pawn moves: {get_possible_moves((1,0))}")
print(f"knight moves: {get_possible_moves((0,1))}")
print(f"bishop moves: {get_possible_moves((0,2))}")
print(f"rook moves: {get_possible_moves((0,0))}")
print(f"queen moves: {get_possible_moves((0,3))}")
print(f"king moves: {get_possible_moves((0,4))}")

