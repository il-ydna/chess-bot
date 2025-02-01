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


def get_possible_moves(position: (int, int)) -> list[tuple[int, int]]:
    # each tuple represents a direction. useful for implementing movement
    corners = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    sides = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    curr_r = position[0]
    curr_c = position[1]
    piece_type = board[position]
    possible_moves = []
    # pawn
    if abs(piece_type) == 1:
        # general one-step move
        possible_moves.append((curr_r - int(piece_type), curr_c))
        # two-step move
        if piece_type == -curr_r:
            possible_moves.append((curr_r - int(2 * piece_type), curr_c))
        # TODO: implement en passant

    # knight
    if abs(piece_type) == 2:
        # this implementation of knight movement works trust me
        # first do the long row-wise moves
        move_r, move_c = 2, 1
        for i in range(8):
            # halfway thru the loop swap to long col-wise moves
            if i == 4:
                move_r, move_c = 1, 2
            dest_r, dest_c = curr_r, curr_c
            # use the directions list to "spin" the horse moves
            dest_r += move_r * corners[i % 4][0]
            dest_c += move_c * corners[i % 4][1]

            # check move legality
            if (move_in_bounds(dest_r, dest_c)
                    and not move_on_teammate(piece_type, dest_r, dest_c)):
                possible_moves.append((dest_r, dest_c))

    # bishop/queen(slants)
    if abs(piece_type) == 3 or abs(piece_type) == 5:
        for i in range(4):
            # loop thru the 4 corner directions
            dest_r, dest_c = curr_r, curr_c
            dest_r += corners[i][0]
            dest_c += corners[i][1]
            # check move legality
            while (move_in_bounds(dest_r, dest_c)
                   and not move_on_teammate(piece_type, dest_r, dest_c)):
                # goes through if the dest spot is open or opponent
                possible_moves.append((dest_r, dest_c))

                dest_r += corners[i][0]
                dest_c += corners[i][1]

                # if the next move up is blocked by a piece, end this diagonal
                if piece_type * board[dest_r, dest_c] != 0:
                    break

    # rook/queen(straight)
    if abs(piece_type) == 4 or abs(piece_type) == 5:
        for i in range(4):
            dest_r, dest_c = curr_r, curr_c
            dest_r += sides[i][0]
            dest_c += sides[i][1]
            while (move_in_bounds(dest_r, dest_c)
                    and not move_on_teammate(piece_type, dest_r, dest_c)):
                # goes through if the dest spot is open or opponent
                possible_moves.append((dest_r, dest_c))

                dest_r += sides[i][0]
                dest_c += sides[i][1]

                # if the next move up is blocked by a piece, end this diagonal
                if piece_type * board[dest_r, dest_c] != 0:
                    break
    # king
    if abs(piece_type) == 6:
        # straights
        for i in range(4):
            dest_r, dest_c = curr_r, curr_c
            dest_r += sides[i][0]
            dest_c += sides[i][1]
            if (move_in_bounds(dest_r, dest_c)
                    and not move_on_teammate(piece_type, dest_r, dest_c)):
                possible_moves.append((dest_r, dest_c))

        # slants
        for i in range(4):
            dest_r, dest_c = curr_r, curr_c
            dest_r += corners[i][0]
            dest_c += corners[i][1]
            if (move_in_bounds(dest_r, dest_c)
                    and not move_on_teammate(piece_type, dest_r, dest_c)):
                possible_moves.append((dest_r, dest_c))

    return possible_moves


def move_on_opponent(piece_type, dest_r, dest_c):
    return piece_type * board[dest_r, dest_c] < 0


def move_on_teammate(piece_type, dest_r, dest_c):
    return piece_type * board[dest_r, dest_c] > 0


def move_to_empty(piece_type, dest_r, dest_c):
    return piece_type * board[dest_r, dest_c] != 0


def move_in_bounds(dest_r, dest_c):
    return (0 <= dest_r <= 7) and (0 <= dest_c <= 7)


print(f"pawn moves: {get_possible_moves((1,0))}")
print(f"knight moves: {get_possible_moves((0,1))}")
print(f"bishop moves: {get_possible_moves((0,2))}")
print(f"rook moves: {get_possible_moves((0,0))}")
print(f"queen moves: {get_possible_moves((0,3))}")
print(f"king moves: {get_possible_moves((0,4))}")

