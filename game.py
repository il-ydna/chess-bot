import numpy as np
import random
import time
from functools import wraps


def measure_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time_ms = (end_time - start_time) * 1000
        print(f"{elapsed_time_ms:.4f} ms")
        return result

    return wrapper


pieces = {1: "pawn  ", 2: "knight", 3: "bishop", 4: "rook  ",
          5: "queen ", 6: "king  ", 7: "2pawn ", 8: "l_ep_pawn",
          9: "r_ep_pawn", 10: "pawn_to_knight", 11: "pawn_to_bish",
          12: "pawn_to_rook", 13: "pawn_to_queen"}
corners = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
sides = [(1, 0), (-1, 0), (0, 1), (0, -1)]

default_board = np.zeros(shape=(8, 8), dtype=int)
# init white pieces
default_board[6] = 1
default_board[7, 1], default_board[7, 6] = 2, 2
default_board[7, 2], default_board[7, 5] = 3, 3
default_board[7, 0], default_board[7, 7] = 4, 4
default_board[7, 3], default_board[7, 4] = 5, 6
# init black pieces
default_board[1] = -1
default_board[0] = -default_board[7]


class Game:
    # piece class is used to more cleanly code movement
    class Piece:
        def __init__(self, board, position, untouched):
            self.ptype = abs(int(board[position]))
            self.side = self.ptype / int(board[position])
            self.position = position
            self.untouched = untouched[position]
            self.curr_r = position[0]
            self.curr_c = position[1]

        def __repr__(self):
            return f"{'white' if self.side > 0 else 'black'} {pieces[self.ptype]} at {tuple(map(int, self.position))}"

    def __init__(self, board=default_board, seed=17):

        self.board = board
        self.turn = 'white'
        self.game_running = True
        # 1 means untouched, 0 means piece has been moved
        self.untouched = (self.board != 0).astype(int)

        self.white_ep_used = False
        self.black_ep_used = False

        random.seed(seed)

        # moves structured as:
        # (from row, from col, to row, to col, signed piece type, score)
        self.white_moves = np.zeros(shape=(0, 6))
        self.black_moves = np.zeros(shape=(0, 6))

    # @measure_runtime
    def sim_game(self):
        self.poll_whites()
        self.poll_blacks()
        while self.game_running:
            self.execute_move()

    # movement helper funcs
    def move_on_opponent(self, piece: Piece, dest):
        return piece.side * self.board[dest] < 0

    def move_on_teammate(self, piece: Piece, dest):
        return piece.side * self.board[dest] > 0

    def move_in_bounds(self, dest):
        return (0 <= dest[0] <= 7) and (0 <= dest[1] <= 7)

    # function that routes whatever piece is passed in to its proper handler(s)
    def get_possible_moves(self, piece: Piece):
        # pawn
        if piece.ptype == 1 or piece.ptype == 7:
            self.get_pawn_moves(piece)
        # knight
        if piece.ptype == 2:
            self.get_knight_moves(piece)
        # slants (bishop & queen)
        if piece.ptype == 3 or piece.ptype == 5:
            self.get_slant_moves(piece)
        # straights (rook & queen)
        if piece.ptype == 4 or piece.ptype == 5:
            self.get_straight_moves(piece)
        # king
        if piece.ptype == 6:
            self.get_king_moves(piece)

    def poll_whites(self):
        # clears all moves
        self.white_moves = np.zeros(shape=(0, 6))
        # find all whites
        w_pieces = np.argwhere(self.board > 0)
        for p in w_pieces:
            # creates a new piece object to be passed into the handlers
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            self.get_possible_moves(curr_piece)

    def poll_blacks(self):
        # clear moves
        self.black_moves = np.zeros(shape=(0, 6))
        # find blacks
        b_pieces = np.argwhere(self.board < 0)
        for p in b_pieces:
            # new piece object
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            self.get_possible_moves(curr_piece)

    # helper func used in handlers
    def add_move(self, piece: Piece, move):
        # TODO: create move scoring system
        piece_score = random.random()

        # stack moves onto their appropriate moves matrix
        if piece.side > 0:
            self.white_moves = np.vstack(
                (np.array([[*piece.position, *move, piece.ptype * piece.side, piece_score]]), self.white_moves))
        else:
            self.black_moves = np.vstack(
                (np.array([[*piece.position, *move, piece.ptype * piece.side, piece_score]]), self.black_moves))

    def black_in_check(self):
        # re poll all white moves
        self.poll_whites()
        # see if black king under attack
        for move in self.white_moves:
            if self.board[int(move[2]), int(move[3])] == -6:
                return True
        return False

    def white_in_check(self):
        # re poll blacks
        self.poll_blacks()
        # see if white king is under attack
        for move in self.black_moves:
            if self.board[int(move[2]), int(move[3])] == 6:
                return True
        return False

    def execute_move(self):
        # create a backup board. We will restore the board to this if a potential move is invalid
        backup_board = self.board.copy()

        # store a copy of all the available moves
        if self.turn == 'white':
            available_moves = self.white_moves.copy()
        else:
            available_moves = self.black_moves.copy()

        # sort by score
        available_moves = available_moves[np.argsort(available_moves[:, -1])][::-1]

        # print(available_moves)

        # iter thru all sorted moves, starting at the top
        # invalid moves will get popped until we find the highest valid move

        while available_moves.shape[0] > 0:
            move = available_moves[0]
            piece_type = abs(move[4])
            piece_side = move[4] / abs(move[4])
            pos_from = (int(move[0]), int(move[1]))
            pos_to = (int(move[2]), int(move[3]))

            # can't eat kings
            if abs(self.board[pos_to]) == 6:
                # pop!
                available_moves = np.delete(available_moves, 0, axis=0)
            # pawns that just moved 2 spots are marked as '7' to enable en passant
            elif piece_type == 1 and abs(pos_from[0] - pos_to[0]) == 2:
                self.board[pos_from] = 0
                self.board[pos_to] = 7 * piece_side
            # execute en passant (left) if ptype is 8
            elif piece_type == 8:
                self.board[pos_from] = 0
                self.board[pos_to] = 1 * piece_side
                # get the victim's position
                v_row = pos_from[0]
                v_col = pos_from[1] - 1
                # eat the victim
                self.board[v_row, v_col] = 0
            # execute en passant (right) if ptype is 9
            elif piece_type == 9:
                self.board[pos_from] = 0
                self.board[pos_to] = 1 * piece_side
                # get the victim's position
                v_row = pos_from[0]
                v_col = pos_from[1] + 1
                # eat the victim
                self.board[v_row, v_col] = 0
            # if the move was a promotion
            elif piece_type >= 10:
                self.board[pos_from] = 0
                self.board[pos_to] = (piece_type - 8) * piece_side

            # execute castle
            elif piece_type == 6 and abs(pos_from[1] - pos_to[1]) > 1:
                # check for pre-move check
                if (piece_side > 0 and not self.white_in_check()) \
                        or (piece_side < 0 and not self.black_in_check()):
                    self.board[pos_from] = 4 * piece_side
                    self.board[pos_to] = 6 * piece_side
            # regular move
            else:
                self.board[pos_from] = 0
                self.board[pos_to] = piece_type * piece_side

            # check if the move puts yourself in check or is a second attempt at en passant
            if self.turn == 'white' and (self.white_in_check() or
                                         (self.white_ep_used and (piece_type == 8 or piece_type == 9))):
                # if move is indeed invalid, pop it and restore the board
                available_moves = np.delete(available_moves, 0, axis=0)
                self.board = backup_board.copy()
            elif self.turn == 'black' and (self.black_in_check() or
                                           (self.black_ep_used and (piece_type == 8 or piece_type == 9))):
                # invalid -> pop move and restore board
                available_moves = np.delete(available_moves, 0, axis=0)
                self.board = backup_board.copy()

            # successful move!
            else:
                # mark the piece as touched
                self.untouched[pos_from] = 0

                # use up the single en passant available if applicable
                if piece_type == 8 or piece_type == 9:
                    if piece_side == -1:
                        self.black_ep_used = True
                    else:
                        self.white_ep_used = True

                # black successfully moved, flipping back to white
                if self.turn == 'black':
                    self.turn = 'white'
                    # if there's a 2-move white we've now forfeited our chance to en passant it
                    # since we chose a different move
                    self.board[self.board == 7] = 1
                else:
                    self.turn = 'black'
                    self.board[self.board == -7] = -1
                break

        # printing new board & the move made
        # print(f"moving a {'white' if move[4] > 0 else 'black'} {pieces[abs(move[4])]} "
        #       f"from {int(move[0]), int(move[1])} to {int(move[2]), int(move[3])}")
        # print(self.board)

        # if only kings left, stalemate
        if np.isin(self.board, [0, -6, 6]).all():
            # print("stalemate :/")
            pass
            self.game_running = False
        # if all possible moves have been popped
        if available_moves.shape[0] == 0:
            # stalemate if not in check
            if self.turn == 'white' and not self.white_in_check() \
                    or self.turn == 'black' and not self.black_in_check():
                # print("stalemate :/")
                pass
            # checkmate!
            else:
                pass
                # print(self.turn, " has been checkmated :(")
            self.game_running = False

    # movement funcs
    def get_pawn_moves(self, piece: Piece):
        # one-step move
        potential_move = (int(piece.curr_r - (piece.ptype * piece.side)), piece.curr_c)
        if self.move_in_bounds(potential_move) and self.board[potential_move] == 0:
            # if your one-step lands you on the last row
            if (potential_move[0] == 7 and piece.side == -1) or (potential_move[0] == 0 and piece.side == 1):
                # 4 potential moves (knight, bishop, rook, queen)
                for i in range(10, 14):
                    piece.ptype = i
                    self.add_move(piece, potential_move)
            else:
                self.add_move(piece, potential_move)

        # two-step move
        potential_move = (piece.curr_r - int(2 * piece.ptype * piece.side), piece.curr_c)
        spot_in_front = (piece.curr_r - int(piece.ptype * piece.side), piece.curr_c)
        # untouched, in bounds, 2 spots in front must be empty
        if piece.untouched and self.move_in_bounds(potential_move) \
                and self.board[potential_move] == 0 and self.board[spot_in_front] == 0:
            self.add_move(piece, potential_move)

        # diagonal capture
        l_diag = (int(piece.curr_r - piece.side), piece.curr_c - 1)
        r_diag = (int(piece.curr_r - piece.side), piece.curr_c + 1)
        # bounds check, opp check
        if self.move_in_bounds(l_diag) and self.move_on_opponent(piece, l_diag):
            self.add_move(piece, l_diag)
        if self.move_in_bounds(r_diag) and self.move_on_opponent(piece, r_diag):
            self.add_move(piece, r_diag)

        # en passant
        l_side = (piece.curr_r, piece.curr_c - 1)
        r_side = (piece.curr_r, piece.curr_c + 1)
        # diag must be in bounds and empty, neighbor must be a 2-move pawn
        if self.move_in_bounds(l_diag) and self.board[l_side] == (-7 * piece.side) and self.board[*l_diag] == 0:
            piece.ptype = 8
            self.add_move(piece, (l_diag[0], l_diag[1]))
        if self.move_in_bounds(r_diag) and self.board[r_side] == (-7 * piece.side) and self.board[*l_diag] == 0:
            piece.ptype = 9
            self.add_move(piece, (r_diag[0], r_diag[1]))

    def get_knight_moves(self, piece: Piece):
        # this implementation of knight movement works trust me
        # first do the long row-wise moves
        move_r, move_c = 2, 1
        for i in range(8):
            # halfway thru the loop swap to long col-wise moves
            if i == 4:
                move_r, move_c = 1, 2
            dest_r, dest_c = piece.curr_r, piece.curr_c
            # use the directions list to "spin" the horse moves
            dest_r += move_r * corners[i % 4][0]
            dest_c += move_c * corners[i % 4][1]

            # check move legality (bounds & not on teammate)
            if (self.move_in_bounds((dest_r, dest_c))
                    and not self.move_on_teammate(piece, (dest_r, dest_c))):
                self.add_move(piece, (dest_r, dest_c))

    def get_slant_moves(self, piece: Piece):
        for i in range(4):
            # loop through the 4 corner directions
            dest_r, dest_c = piece.curr_r, piece.curr_c
            dest_r += corners[i][0]
            dest_c += corners[i][1]
            # check move legality (bounds, teammate)
            while (self.move_in_bounds((dest_r, dest_c))
                   and not self.move_on_teammate(piece, (dest_r, dest_c))):
                # goes through if the dest spot is open or opponent
                self.add_move(piece, (dest_r, dest_c))

                # if reached an enemy, end the slant
                if self.move_on_opponent(piece, (dest_r, dest_c)):
                    break

                dest_r += corners[i][0]
                dest_c += corners[i][1]

                # if the next move in the slant is out of bounds or blocked, end the slant
                if not self.move_in_bounds((dest_r, dest_c)) or self.board[dest_r, dest_c] != 0:
                    break

    def get_straight_moves(self, piece: Piece):
        for i in range(4):
            dest_r, dest_c = piece.curr_r, piece.curr_c
            dest_r += sides[i][0]
            dest_c += sides[i][1]
            while (self.move_in_bounds((dest_r, dest_c))
                   and not self.move_on_teammate(piece, (dest_r, dest_c))):
                # goes through if the dest spot is open or opponent
                self.add_move(piece, (dest_r, dest_c))

                # if reached an enemy, end the straight
                if self.move_on_opponent(piece, (dest_r, dest_c)):
                    break

                dest_r += sides[i][0]
                dest_c += sides[i][1]

                # if the next move up is out of bounds or blocked by a piece, end this straight
                if not self.move_in_bounds((dest_r, dest_c)) or self.board[dest_r, dest_c] != 0:
                    break

    def get_king_moves(self, piece: Piece):
        # straights
        for i in range(4):
            dest_r, dest_c = piece.curr_r, piece.curr_c
            dest_r += sides[i][0]
            dest_c += sides[i][1]
            if (self.move_in_bounds((dest_r, dest_c))
                    and not self.move_on_teammate(piece, (dest_r, dest_c))):
                self.add_move(piece, (dest_r, dest_c))

        # slants
        for i in range(4):
            dest_r, dest_c = piece.curr_r, piece.curr_c
            dest_r += corners[i][0]
            dest_c += corners[i][1]
            if (self.move_in_bounds((dest_r, dest_c))
                    and not self.move_on_teammate(piece, (dest_r, dest_c))):
                self.add_move(piece, (dest_r, dest_c))

        # castle
        # black or white?
        if piece.side == -1:
            back_line = 0
        else:
            back_line = 7

        # untouched king?
        if self.untouched[back_line, 4] != 0:
            # untouched left rook/empty lane?
            if self.untouched[back_line, 0] != 0 and np.all(self.board[back_line, 1:4] == 0):
                self.add_move(piece, (back_line, 0))
            # check right
            if self.untouched[back_line, 7] != 0 and np.all(self.board[7, 5:8] == 0):
                self.add_move(piece, (back_line, 7))
