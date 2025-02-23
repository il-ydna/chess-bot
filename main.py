import numpy as np
from movement import *

gboard = np.zeros(shape=(8, 8), dtype=int)
print(gboard)

# piece guide:
pieces = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen", 6: "king", 7: "2pawn"}

# init white pieces
gboard[6] = 1
gboard[7, 1], gboard[7, 6] = 2, 2
gboard[7, 2], gboard[7, 5] = 3, 3
gboard[7, 0], gboard[7, 7] = 4, 4
gboard[7, 3], gboard[7, 4] = 5, 6
# init black pieces
gboard[1] = -1
gboard[0] = -gboard[7]

test_board = np.array([
    [-4, -2, -3, -5, -6, -3, -2, -4],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  1,  1,  1,  1,  1,  1,  1],
    [ 4,  0,  0,  0,  6,  3,  2,  4]
])
untouched = (gboard != 0).astype(int)
untouched[7, 1:4] = 0
print(untouched)
print(test_board)


# print(f"pawn moves:   {get_possible_moves(gboard, (1,0))}")
# print(f"knight moves: {get_possible_moves(gboard, (0,1))}")
# print(f"bishop moves: {get_possible_moves(gboard, (0,2))}")
# print(f"rook moves:   {get_possible_moves(gboard, (0,0))}")
# print(f"queen moves:  {get_possible_moves(gboard, (0,3))}")
# print(f"king moves:   {get_possible_moves(gboard, (0,4))}")

print("WHITE MOVES: ")
w_m = poll_all_whites(test_board, untouched)
print("BLACK MOVES: ")
b_m = poll_all_blacks(test_board, untouched)
print(w_m)
print(b_m)

filter_special_conditions(test_board, w_m, b_m, untouched)

