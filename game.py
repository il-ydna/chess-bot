import numpy as np

pieces = {1: "pawn  ", 2: "knight", 3: "bishop", 4: "rook  ", 5: "queen ", 6: "king  ", 7: "2pawn "}
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

    def __init__(self, board=default_board):
        self.board = board

        # true means white, false black
        self.turn = True

        # 1 means untouched, 0 means piece has been moved
        self.untouched = (self.board != 0).astype(int)

        # needs to hold to, from, and (eventually) score
        self.white_moves = np.zeros(shape=(0, 4))
        self.black_moves = np.zeros(shape=(0, 4))

    def move_on_opponent(self, piece: Piece, dest):
        return piece.side * self.board[dest] < 0

    def move_on_teammate(self, piece: Piece, dest):
        return piece.side * self.board[dest] > 0

    def move_in_bounds(self, dest):
        return (0 <= dest[0] <= 7) and (0 <= dest[1] <= 7)

    def get_possible_moves(self, piece: Piece):
        # pawn
        if piece.ptype == 1:
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
        self.turn = True
        w_pieces = np.argwhere(self.board > 0)
        for p in w_pieces:
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            self.get_possible_moves(curr_piece)

    def poll_blacks(self):
        self.turn = False
        b_pieces = np.argwhere(self.board < 0)
        for p in b_pieces:
            curr_piece = self.Piece(self.board, tuple(p), self.untouched)
            print(curr_piece)
            self.get_possible_moves(curr_piece)

    def add_move(self, piece: Piece, move):
        if self.turn:
            self.white_moves = np.vstack((np.array([[*move, piece.ptype * piece.side, 0]]), self.white_moves))
        else:
            self.black_moves = np.vstack((np.array([[*move, piece.ptype * piece.side, 0]]), self.black_moves))

    def black_in_check(self):
        for move in self.white_moves:
            if self.board[move[0], move[1]] == -6:
                return True
        return False

    def white_in_check(self):
        for move in self.black_moves:
            if self.board[move[0], move[1]] == 6:
                return True
        return False

    # movement funcs
    def get_pawn_moves(self, piece: Piece):
        # one-step move
        potential_move = (int(piece.curr_r - (piece.ptype * piece.side)), piece.curr_c)
        if self.board[potential_move] == 0:
            self.add_move(piece, potential_move)
        # two-step move
        potential_move = (piece.curr_r - int(2 * piece.ptype * piece.side), piece.curr_c)
        if piece.untouched and self.move_in_bounds(potential_move):
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
        if self.move_in_bounds(l_diag) and self.board[l_side] == (-7 * piece.side):
            self.add_move(piece, (l_diag[0] - 8 * piece.side, l_diag[1]))
        if self.move_in_bounds(r_diag) and self.board[r_side] == (-7 * piece.side):
            self.add_move(piece, (r_diag[0] - 8 * piece.side, r_diag[1]))

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

                dest_r += sides[i][0]
                dest_c += sides[i][1]

                # if the next move up is blocked by a piece, end this diagonal
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

