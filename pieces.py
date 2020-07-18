import pygame
from screen import *
import abc
import os

WHITE_PIECES_PATH = os.path.join(PICTURES_PATH, 'white_pieces')
BLACK_PIECES_PATH = os.path.join(PICTURES_PATH, 'black_pieces')


class Piece(metaclass=abc.ABCMeta):
    BASIC_SCORE = 0
    SCORE_EVOLUTION_TABLE = None

    def __init__(self, square, team):
        self.image = self.WHITE_IMAGE if team.is_white_team else self.BLACK_IMAGE
        self.square = square
        self.square.current_piece = self
        self.team = team
        self.is_eaten = False
        self.save_location = None
        self.starting_square = square
        self.move_counter = 0
        if team.is_white_team:
            self.SCORE_EVOLUTION_TABLE = self.SCORE_EVOLUTION_TABLE[::-1]

    def _is_already_moved(self):
        return self.square is self.starting_square

    def color_next_step(self):
        valid_square = self.get_valid_move_squares()
        for square in valid_square:
            square.coloring_square_by_original_color()

    def move(self, next_square: Square):
        # Free current square.
        self.square.current_piece = None
        # Check if next square is taken by other team.
        if next_square.current_piece is not None:
            next_square.current_piece.is_eaten = True

        # Move to next square.
        self.square = next_square
        self.square.current_piece = self
        return

    @abc.abstractmethod
    def get_valid_move_squares(self):
        pass

    def draw(self):
        if not self.is_eaten:
            screen.blit(self.image, self.square.rect)

    @property
    def score(self):
        return self.BASIC_SCORE + self.SCORE_EVOLUTION_TABLE[self.square.line_cord][self.square.tur_cord]

    def __str__(self):
        team = 'white' if self.team.is_white_team else 'black'
        state = 'alive' if not self.is_eaten else 'eaten'
        type_of_piece = type(self).__name__
        return f'{type_of_piece}, position: {self.square}, ' \
               f'{state}, {team} team'


class King(Piece):
    BASIC_SCORE = 2000
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_king.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_king.png'))
    SCORE_EVOLUTION_TABLE = [[-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-20, -30, -30, -40, -40, -30, -30, -20],
                             [-10, -20, -20, -20, -20, -20, -20, -10],
                             [20,   20,   0,  0,  0,   0,   20,   20],
                             [20,   30,  10,  0,  0,  10,   30,   20]]

    def __init__(self, team: Team):
        square = squares[0][3] if team.is_white_team else squares[7][3]
        super().__init__(square, team)

    def get_valid_move_squares(self):
        line = self.square.line_cord
        valid_squares = []
        for line in range(line - 1, line + 2):
            tur = self.square.tur_cord
            for tur in range(tur - 1, tur + 2):
                if is_move_to_square_valid(tur, line, self.team):
                    valid_squares.append(squares[line][tur])

        return valid_squares


class Pawn(Piece):
    BASIC_SCORE = 100
    LINE_OF_WHITE_PAWNS = 1
    LINE_OF_BLACK_PAWNS = 6
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_pawn.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_pawn.png'))
    SCORE_EVOLUTION_TABLE = [[0,   0,   0,   0,   0,   0,  0,   0],
                             [50, 50,  50,  50,  50,  50, 50,  50],
                             [10, 10,  20,  30,  30,  20, 10,  10],
                             [5,   5,  10,  25,  25,  10,  5,   5],
                             [0,   0,   0,  20,  20,   0,  0,   0],
                             [5,  -5, -10,   0,   0, -10, -5,   5],
                             [5,  10,  10, -20, -20,  10, 10,   5],
                             [0,   0,   0,   0,   0,   0,  0,   0]]

    def __init__(self, team: Team, tur=None, square=None):

        if square is None:
            square = squares[Pawn.LINE_OF_WHITE_PAWNS][tur] if team.is_white_team else squares[Pawn.LINE_OF_BLACK_PAWNS][tur]
        super().__init__(square, team)

    def is_reached_to_end(self):
        end = BOARD_LINE-1 if self.team.is_white_team else 0
        return self.square.line_cord == end

    def get_valid_move_squares(self):
        line = self.square.line_cord
        tur = self.square.tur_cord
        valid_moves = []
        # Direction represent one square walk.
        direction = 1 if self.team.is_white_team else -1
        line += direction
        # Check if nest step is out of board.
        if line > 7 or line < 0:
            return valid_moves

        next_square = squares[line][tur]
        valid_moves.extend(self._diagonal_eat(next_square))

        if next_square.current_piece is not None:
            return valid_moves

        valid_moves.append(next_square)
        if self.move_counter == 0:
            line += direction
            next_square = squares[line][tur]
            if next_square.current_piece is None:
                valid_moves.append(next_square)

        return valid_moves

    def _diagonal_eat(self, next_square):
        valid_eat_moves = []

        # Left check.
        line = next_square.line_cord
        tur = next_square.tur_cord - 1
        if is_move_to_square_valid(tur, line, self.team):
            current_square = squares[line][tur]
            if current_square.current_piece is not None:
                valid_eat_moves.append(current_square)
        # Right check.
        tur += 2
        if is_move_to_square_valid(tur, line, self.team):
            current_square = squares[line][tur]
            if current_square.current_piece is not None:
                valid_eat_moves.append(current_square)
        return valid_eat_moves


class Knight(Piece):
    BASIC_SCORE = 320
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_knight.png'))
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_knight.png'))
    SCORE_EVOLUTION_TABLE = [[-50, -40, -30, -30, -30, -30, -40, -50],
                            [-40, -20,   0,   0,   0,   0, -20, -40],
                            [-30,   0,  10,  15,  15,  10,   0, -30],
                            [-30,   5,  15,  20,  20,  15,   5, -30],
                            [-30,   0,  15,  20,  20,  15,   0, -30],
                            [-30,   5,  10,  15,  15,  10,   5, -30],
                            [-40, -20,   0,   5,   5,   0, -20, -40],
                            [-50, -40, -30, -30, -30, -30, -40, -50]]

    def get_valid_move_squares(self):
        valid_moves = []
        self_line = self.square.line_cord
        self_tur = self.square.tur_cord
        team = self.team
        knight_moves = [(1, 2), (1, -2), (2, -1), (2, 1), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]
        for tur_move, line_move in knight_moves:
            if is_move_to_square_valid(self_tur + tur_move, self_line + line_move, team):
                valid_moves.append(squares[self_line+line_move][self_tur+tur_move])
        return valid_moves


class Rook(Piece):
    BASIC_SCORE = 500
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_rook.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_rook.png'))
    SCORE_EVOLUTION_TABLE = [[0,  0,  0,  0,  0,  0,  0,  0],
                             [5, 10, 10, 10, 10, 10, 10,  5],
                             [-5,  0,  0,  0,  0,  0,  0, -5],
                             [-5,  0,  0,  0,  0,  0,  0, -5],
                             [-5,  0,  0,  0,  0,  0,  0, -5],
                             [-5,  0,  0,  0,  0,  0,  0, -5],
                             [-5,  0,  0,  0,  0,  0,  0, -5],
                             [0,  0,  0,  5,  5,  0,  0,  0]]

    def get_valid_move_squares(self):
        return _get_valid_straight_move_squares(self)


class Bishop(Piece):
    BASIC_SCORE = 330
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_bishop.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_bishop.png'))
    SCORE_EVOLUTION_TABLE = [[-20,-10,-10,-10,-10,-10,-10,-20],
                            [-10,  0,  0,  0,  0,  0,  0,-10],
                            [-10,  0,  5, 10, 10,  5,  0,-10],
                            [-10,  5,  5, 10, 10,  5,  5,-10],
                            [-10,  0, 10, 10, 10, 10,  0,-10],
                            [-10, 10, 10, 10, 10, 10, 10,-10],
                            [-10,  5,  0,  0,  0,  0,  5,-10],
                            [-20,-10,-10,-10,-10,-10,-10,-20]]

    def get_valid_move_squares(self):
        return _get_diagonal_valid_moves(self)


class Queen(Piece):
    BASIC_SCORE = 900
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_queen.png'))
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_queen.png'))
    SCORE_EVOLUTION_TABLE = [[-20, -10, -10, -5, -5, -10, -10,  -20],
                             [-10,   0,   0,  0,  0,   0,   0,  -10],
                             [-10,   0,   5,  5,  5,   5,   0,  -10],
                             [ -5,   0,   5,  5,  5,   5,   0,   -5],
                             [  0,   0,   5,  5,  5,   5,   0,   -5],
                             [-10,   5,   5,  5,  5,   5,   0,  -10],
                             [-10,   0,   5,  0,  0,   0,   0,  -10],
                             [-20, -10, -10, -5, -5, -10, -10,  -20]]

    def get_valid_move_squares(self):
        valid_squares = []
        valid_squares.extend(_get_diagonal_valid_moves(self))
        valid_squares.extend(_get_valid_straight_move_squares(self))
        return valid_squares


def _get_diagonal_valid_moves(piece):
    valid_squares = []
    found_right_down = True
    found_left_down = True
    found_right_up = True
    found_left_up = True

    for current_distance in range(1, BOARD_LINE):

        if found_right_down:
            found_right_down = _check_next_diagonal_valid_move(piece, current_distance, current_distance,
                                                                              valid_squares)
        if found_left_down:
            found_left_down = _check_next_diagonal_valid_move(piece, current_distance,
                                                                             current_distance * -1, valid_squares)
        if found_right_up:
            found_right_up = _check_next_diagonal_valid_move(piece, current_distance * -1,
                                                                            current_distance, valid_squares)
        if found_left_up:
            found_left_up = _check_next_diagonal_valid_move(piece, current_distance * -1,
                                                                           current_distance * -1,
                                                                           valid_squares)
    return valid_squares


def _check_next_diagonal_valid_move(piece, line_distance_from_square, tur_distance_from_square, valid_squares):
    next_tur = piece.square.tur_cord + tur_distance_from_square
    next_line = piece.square.line_cord + line_distance_from_square
    if is_move_to_square_valid(next_tur, next_line, piece.team):
        square = squares[next_line][next_tur]
        valid_squares.append(square)
        return square.current_piece is None
    return False


def _get_valid_straight_move_squares(piece):
    valid_moves = _get_straight_valid_move_squares(piece, is_vertical=True)
    valid_moves.extend(_get_straight_valid_move_squares(piece, is_vertical=False))
    return valid_moves


def _get_straight_valid_move_squares(piece, is_vertical):
    piece_tur = piece.square.tur_cord
    piece_line = piece.square.line_cord
    move_on = piece_tur if is_vertical else piece_line
    permanent = piece_line if is_vertical else piece_tur
    valid_moves = []

    for tur_or_line in range(move_on):
        square = squares[permanent][tur_or_line] if is_vertical else squares[tur_or_line][permanent]
        if square.current_piece is None:  # If square is empty we just add him to the row.
            valid_moves.append(square)
            continue
        if square.current_piece.team is piece.team:  # If square taken by teamate piece we have to make a new row.
            valid_moves = []
        else:   # square is taken by enemy.
            # we start a new raw from this square(including).
            valid_moves = [square]
            continue

    # Add squares after piece
    for tur_or_line in range(move_on+1, BOARD_LINE):
        square = squares[permanent][tur_or_line] if is_vertical else squares[tur_or_line][permanent]
        if square.current_piece is None:
            valid_moves.append(square)  # If square is empty we just add him to the row.
            continue

        if square.current_piece.team is piece.team:  # If square taken by teamate piece
            break
        else:
            # square is taken by enemy.
            valid_moves.append(square)
            break
    return valid_moves
