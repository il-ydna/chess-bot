import numpy as np


pieces = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen", 6: "king", 7: "2pawn"}

def get_possible_moves(board: np.ndarray, position: (int, int), ut_pieces: np.ndarray) -> list[tuple[int, int]]:
    untouched = ut_pieces[position]

    def move_on_opponent(p_type, d_r, d_c):
        return p_type * board[d_r, d_c] < 0

    def move_on_teammate(p_type, d_r, d_c):
        return p_type * board[d_r, d_c] > 0

    def move_to_empty(p_type, d_r, d_c):
        return p_type * board[d_r, d_c] != 0

    def move_in_bounds(d_r, d_c):
        return (0 <= d_r <= 7) and (0 <= d_c <= 7)
    # each tuple represents a direction. useful for implementing movement
    corners = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    sides = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    curr_r = position[0]
    curr_c = position[1]
    from_coords = (curr_r, curr_c)
    piece_type = board[position]
    possible_moves = []
    # pawn
    if abs(piece_type) == 1:
        # general one-step move
        possible_moves.append((curr_r - int(piece_type), curr_c))
        # two-step move
        if untouched:
            possible_moves.append((curr_r - int(2 * piece_type), curr_c))

        # diagonal capture
        l_diag = (curr_r - piece_type, curr_c - 1)
        r_diag = (curr_r - piece_type, curr_c + 1)
        if move_in_bounds(*l_diag) and move_on_opponent(piece_type, *l_diag):
            possible_moves.append(l_diag)
        if move_in_bounds(*r_diag) and move_on_opponent(piece_type, *r_diag):
            possible_moves.append(r_diag)

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

    for i in range(len(possible_moves)):
        possible_moves[i] = (from_coords, possible_moves[i])

    return possible_moves


def execute_move(board, mov_from, mov_to):
    # castling handler
    if (abs(mov_from[0]) == 8):
        print("castle available! wow")
    board[mov_to] = board[mov_from]
    board[mov_from] = 0


def check_for_check(board, ut_pieces, is_black):
    w_king = np.argwhere(board == 6)[0]
    b_king = np.argwhere(board == -6)[0]

    print()
    if is_black:
        moves = poll_all_whites(board, ut_pieces)
    else:
        moves = poll_all_blacks(board, ut_pieces)
    for m in moves:
        if m == tuple(b_king.tolist()) and is_black:
            return True
        if m == tuple(w_king.tolist()) and not is_black:
            return True
    return False


def filter_special_conditions(board, w_moves, b_moves, ut_pieces):
    # check

    # if black is in check
    if check_for_check(board,ut_pieces,True):
        for i in range(len(b_moves)):
            # create a temp board where you try each move
            temp_board = board.copy()
            # see if you're still in check
            execute_move(temp_board, b_moves[i][0], b_moves[i][1])
            if not check_for_check(temp_board, ut_pieces, True):
                b_moves.pop(i)
                i-=1

    if check_for_check(board,ut_pieces,False):
        for i in range(len(w_moves)):
            temp_board = board.copy()
            execute_move(temp_board, w_moves[i][0], w_moves[i][1])
            if not check_for_check(temp_board, ut_pieces, True):
                w_moves.pop(i)
                i-=1

    # mate
    if len(w_moves) == 0:
        print("black wins")
    if len(b_moves) == 0:
        print("white wins")

    # castling
    # hacky castling nomenclature:
    # in the from coordinate tuple
    # +/-8 will represent castle scenarios
    # +1 means right castle, -1 means left castle
    # white castle
    if check_for_check(board, ut_pieces, True):
        # if the king's untouched
        if ut_pieces[7,4] != 0:
            # check left
            if ut_pieces[7,0] != 0 and np.all(board[7, 1:4] == 0):
                w_moves.append((8, -1), (0,0))
            # check right
            if ut_pieces[7,7] != 0 and np.all(board[7, 5:8] == 0):
                w_moves.append((8, 1), (0,0))

    # black castle
    if check_for_check(board, ut_pieces, False):
        # if the king's untouched
        if ut_pieces[0, 4] != 0:
            # check left
            if ut_pieces[0, 0] != 0 and np.all(board[0, 1:4] == 0):
                b_moves.append((-8, -1), (0, 0))
            # check right
            if ut_pieces[0, 7] != 0 and np.all(board[0, 5:8] == 0):
                b_moves.append((-8, 1), (0, 0))

    print(w_moves)
    print(b_moves)


def poll_all_whites(board: np.ndarray, ut_pieces: np.ndarray):
    white_moves = []
    w_pieces = np.argwhere(board > 0)
    for p in w_pieces:
        p_moves = get_possible_moves(board, tuple(p), ut_pieces)
        # print(f"{pieces[board[tuple(p)]]} from {tuple(p)}, to {p_moves}")
        # appends (from, to) coordinates
        for move in p_moves:
            white_moves.extend((tuple(p), move))
    return white_moves


def poll_all_blacks(board: np.ndarray, ut_pieces: np.ndarray):
    black_moves = []
    b_pieces = np.argwhere(board < 0)
    for p in b_pieces:
        p_moves = get_possible_moves(board, tuple(p), ut_pieces)
        # print(f"{pieces[-board[tuple(p)]]} from {tuple(p)}, to {p_moves}")
        for move in p_moves:
            black_moves.extend((tuple(p), move))
    return black_moves


