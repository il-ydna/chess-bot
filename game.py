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
          5: "queen ", 6: "king  ", 7: "2pawn ", 8: "leppawn",
          9: "reppawn", 10: "pawntoknight", 11: "pawntobish",
          12: "pawntorook", 13: "pawntoqueen"}
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

test_mate_board = np.zeros((8, 8), dtype=int)
test_mate_board[1, 1] = -6
test_mate_board[6, 6] = -5
test_mate_board[5, 5] = -1
test_mate_board[7, 7] = 6


class Game:
    class Piece:
        def __init__(self, board, position, untouched):
            self.ptype = abs(int(board[position]))
            self.side = self.ptype/int(board[position])
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

        # needs to hold to, from, and (eventually) score
        # structured as:
        # (from row, from col, to row, to col, piece type, score)
        self.white_moves = np.zeros(shape=(0, 6))
        self.black_moves = np.zeros(shape=(0, 6))

    @measure_runtime
    def sim_game(self):
        self.poll_whites()
        self.poll_blacks()
        while self.game_running:
            self.execute_move()

    def move_on_opponent(self, piece: Piece, dest):
        return piece.side * self.board[dest] < 0

    def move_on_teammate(self, piece: Piece, dest):
        return piece.side * self.board[dest] > 0

    def move_in_bounds(self, dest):
        return (0 <= dest[0] <= 7) and (0 <= dest[1] <= 7)

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
        self.white_moves = np.zeros(shape=(0, 6))
        w_pieces = np.argwhere(self.board > 0)
        for p in w_pieces:
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            self.get_possible_moves(curr_piece)
        self.white_moves = self.white_moves[np.argsort(self.white_moves[:, -1])][::-1]

    def poll_blacks(self):
        self.black_moves = np.zeros(shape=(0, 6))
        b_pieces = np.argwhere(self.board < 0)
        for p in b_pieces:
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            self.get_possible_moves(curr_piece)
        self.black_moves = self.black_moves[np.argsort(self.black_moves[:, -1])][::-1]

    def add_move(self, piece: Piece, move):
        piece_score = random.random()
        if piece.side > 0:
            self.white_moves = np.vstack(
                (np.array([[*piece.position, *move, piece.ptype * piece.side, piece_score]]), self.white_moves))
        else:
            self.black_moves = np.vstack(
                (np.array([[*piece.position, *move, piece.ptype * piece.side, piece_score]]), self.black_moves))

    def black_in_check(self):
        self.poll_whites()
        for move in self.white_moves:
            if self.board[int(move[2]), int(move[3])] == -6:
                return True
        return False

    def white_in_check(self):
        self.poll_blacks()
        for move in self.black_moves:
            if self.board[int(move[2]), int(move[3])] == 6:
                return True
        return False

    def execute_move(self):
        # create a backup board
        backup_board = self.board.copy()

        # go thru the best moves
        if self.turn == 'white':
            available_moves = self.white_moves.copy()
        else:
            available_moves = self.black_moves.copy()
        i = 0
        while available_moves.shape[0] > 0:
            # print(f"{self.turn}'s turn")
            # print(available_moves)
            move = available_moves[0]
            piece_type = abs(move[4])
            piece_side = move[4]/abs(move[4])
            pos_from = (int(move[0]), int(move[1]))
            pos_to = (int(move[2]), int(move[3]))

            # can't eat kings
            if abs(self.board[pos_to]) == 6:
                available_moves = np.delete(available_moves, 0, axis=0)
            # set up en passant
            elif piece_type == 1 and abs(pos_from[0] - pos_to[0]) == 2:
                self.board[pos_from] = 0
                self.board[pos_to] = 7 * piece_side
            elif piece_type == 7:
                self.board[pos_from] = 0
                self.board[pos_to] = 1 * piece_side
            # execute en passant (left)
            elif piece_type == 8:
                self.board[pos_from] = 0
                self.board[pos_to] = 1 * piece_side
                # extract the victim's position
                v_row = pos_from[0]
                v_col = pos_from[1] - 1
                self.board[v_row, v_col] = 0
            # execute en passant (right)
            elif piece_type == 9:
                self.board[pos_from] = 0
                self.board[pos_to] = 1 * piece_side
                # extract the victim's position
                v_row = pos_from[0]
                v_col = pos_from[1] + 1
                self.board[v_row, v_col] = 0
            # promotion
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
            # other
            else:
                self.board[pos_from] = 0
                self.board[pos_to] = piece_type * piece_side

            # check if the move puts yourself in check
            if self.turn == 'white' and self.white_in_check():
                # print('invalid white move')
                available_moves = np.delete(available_moves, 0, axis=0)
                self.board = backup_board.copy()
            elif self.turn == 'black' and self.black_in_check():
                # print('invalid black move')
                available_moves = np.delete(available_moves, 0, axis=0)
                self.board = backup_board.copy()
            else:
                # change the turn, stop looking for new moves
                self.untouched[pos_from] = 0
                if self.turn == 'black':
                    self.turn = 'white'
                else:
                    self.turn = 'black'
                break

        # print(f"moving a {'white' if move[4] > 0 else 'black'} {pieces[abs(move[4])]} "
        #       f"from {int(move[0]), int(move[1])} to {int(move[2]), int(move[3])}")
        # print(self.board)

        if np.isin(self.board, [0, -6, 6]).all():
            print("stalemate :/")
            self.game_running = False
        if available_moves.shape[0] == 0:
            print(self.turn, " has been checkmated :(")
            self.game_running = False

    # movement funcs
    def get_pawn_moves(self, piece: Piece):
        # one-step move
        potential_move = (int(piece.curr_r - (piece.ptype * piece.side)), piece.curr_c)
        if self.move_in_bounds(potential_move) and self.board[potential_move] == 0:
            # promotion
            if (potential_move[0] == 7 and piece.side == -1) or (potential_move[0] == 0 and piece.side == 1):
                for i in range(10, 14):
                    piece.ptype = i
                    self.add_move(piece, potential_move)
            else:
                self.add_move(piece, potential_move)

        # two-step move
        potential_move = (piece.curr_r - int(2 * piece.ptype * piece.side), piece.curr_c)
        if piece.untouched and self.move_in_bounds(potential_move) and self.board[potential_move] == 0:
            self.add_move(piece, potential_move)

        # diagonal capture
        l_diag = (int(piece.curr_r - piece.side), piece.curr_c - 1)
        r_diag = (int(piece.curr_r - piece.side), piece.curr_c + 1)
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

            # check move legality
            if (self.move_in_bounds((dest_r, dest_c))
                    and not self.move_on_teammate(piece, (dest_r, dest_c))):
                self.add_move(piece, (dest_r, dest_c))

    def get_slant_moves(self, piece: Piece):
        for i in range(4):
            # loop through the 4 corner directions
            dest_r, dest_c = piece.curr_r, piece.curr_c
            dest_r += corners[i][0]
            dest_c += corners[i][1]
            # check move legality
            while (self.move_in_bounds((dest_r, dest_c))
                   and not self.move_on_teammate(piece, (dest_r, dest_c))):
                # goes through if the dest spot is open or opponent
                self.add_move(piece, (dest_r, dest_c))

                dest_r += corners[i][0]
                dest_c += corners[i][1]

                # if the next move in the diag is blocked or past the edge, end the diagonal
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

                # if ate a piece, end
                if self.move_on_opponent(piece, (dest_r, dest_c)):
                    break

                dest_r += sides[i][0]
                dest_c += sides[i][1]

                # if the next move up is blocked by a piece, end this straight
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

        if self.untouched[back_line, 4] != 0:
            # check left
            if self.untouched[back_line, 0] != 0 and np.all(self.board[back_line, 1:4] == 0):
                self.add_move(piece, (back_line, 0))
            # check right
            if self.untouched[back_line, 7] != 0 and np.all(self.board[7, 5:8] == 0):
                self.add_move(piece, (back_line, 7))
