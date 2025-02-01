def get_possible_moves(board: np.ndarray, position: (int, int)) -> list[tuple[int, int]]:
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
