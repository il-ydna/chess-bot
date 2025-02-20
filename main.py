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

untouched = (gboard != 0).astype(int)





# print(f"pawn moves:   {get_possible_moves(gboard, (1,0))}")
# print(f"knight moves: {get_possible_moves(gboard, (0,1))}")
# print(f"bishop moves: {get_possible_moves(gboard, (0,2))}")
# print(f"rook moves:   {get_possible_moves(gboard, (0,0))}")
# print(f"queen moves:  {get_possible_moves(gboard, (0,3))}")
# print(f"king moves:   {get_possible_moves(gboard, (0,4))}")

print("WHITE MOVES: ")
w_m = poll_all_whites(gboard, untouched)
print("BLACK MOVES: ")
b_m = poll_all_blacks(gboard, untouched)
print(w_m)
print(b_m)

filter_special_conditions(gboard, w_m, b_m, untouched)

