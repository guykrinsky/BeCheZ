import pygame
from Screen import screen, squares, BOARD_LINE, square_is_valid, Square
import abc
import os

WHITE_PIECES_PATH = os.path.join('pictures', 'white_pieces')
BLACK_PIECES_PATH = os.path.join('pictures', 'black_pieces')


class Piece(metaclass=abc.ABCMeta):
    SCORE = 0

    def __init__(self, image, square, team):
        self.image = image
        self.square = square
        self.square.current_piece = self
        self.IS_IN_WHITE_TEAM = team
        self.is_eaten = False
        self.save_location = None
        self.starting_square = square
        self.move_counter = 0

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
        self.update_score()

    @abc.abstractmethod
    def get_valid_move_squares(self):
        pass

    def draw(self):
        screen.blit(self.image, self.square.rect)

    def update_score(self):
        pass


class King(Piece):
    SCORE = 0
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_king.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_king.png'))

    def __init__(self, is_white):
        if is_white:
            image = self.WHITE_IMAGE
            square = squares[0][3]
        else:
            image = self.BLACK_IMAGE
            square = squares[7][3]
        super().__init__(image, square, is_white)

    def get_valid_move_squares(self):
        line = self.square.line_cord
        valid_squares = []
        for line in range(line - 1, line + 2):
            tur = self.square.tur_cord
            for tur in range(tur - 1, tur + 2):
                if square_is_valid(tur, line, self.IS_IN_WHITE_TEAM):
                    square = squares[line][tur]
                    valid_squares.append(square)

        return valid_squares


class Pawn(Piece):
    SCORE = 10
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_pawn.png'))
    BLACK_PAWN = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_pawn.png'))

    def __init__(self, is_white, place):
        if is_white:
            square = squares[1][place]
            image = self.WHITE_IMAGE
        else:
            square = squares[6][place]
            image = self.BLACK_PAWN
        super().__init__(image, square, is_white)

    def is_reached_to_end(self):
        if self.IS_IN_WHITE_TEAM:
            return self.square.line_cord == BOARD_LINE-1
        return self.square.line_cord == 0

    def get_valid_move_squares(self):
        line = self.square.line_cord
        tur = self.square.tur_cord
        valid_moves = []
        # Direction represent one square walk.
        direction = 1 if self.IS_IN_WHITE_TEAM else -1
        # Check if nest step is out of board.
        line += direction

        next_square = squares[line][tur]

        valid_moves.extend(self._diagonal_eat(next_square))

        if next_square.current_piece is None:
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
        if square_is_valid(tur, line, self.IS_IN_WHITE_TEAM):
            current_square = squares[line][tur]
            if current_square.current_piece is not None:
                valid_eat_moves.append(current_square)
        # Right check.
        tur += 2
        if square_is_valid(tur, line, self.IS_IN_WHITE_TEAM):
            current_square = squares[line][tur]
            if current_square.current_piece is not None:
                valid_eat_moves.append(current_square)
        return valid_eat_moves

    def update_score(self):
        self.SCORE = 10
        if 3 <= self.square.line_cord <= 5:
            self.SCORE = 11


class Knight(Piece):
    SCORE = 32
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_knight.png'))
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_knight.png'))

    def __init__(self, square, is_white):
        image = self.BLACK_IMAGE
        if is_white:
            image = self.WHITE_IMAGE
        super().__init__(image, square, is_white)

    def get_valid_move_squares(self):
        valid_moves = []
        self_line = self.square.line_cord
        self_tur = self.square.tur_cord
        team = self.IS_IN_WHITE_TEAM
        knight_moves = [(1, 2), (1, -2), (2, -1), (2, 1), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]
        for tur_move, line_move in knight_moves:
            if square_is_valid(self_tur + tur_move, self_line + line_move, team):
                valid_moves.append(squares[self_line+line_move][self_tur+tur_move])
        return valid_moves

    def update_score(self):
        self.SCORE = 25
        if 3 <= self.square.tur_cord <= 5:
            self.SCORE = 35


class Rook(Piece):
    SCORE = 50
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_rook.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_roock.png'))

    def __init__(self, is_white, square):
        if is_white:
            image = self.WHITE_IMAGE
        else:
            image = self.BLACK_IMAGE
        super(Rook, self).__init__(image, square, is_white)

    def get_valid_move_squares(self):
        valid_moves = _get_vertical_valid_move_squares(self)
        valid_moves.extend(_get_horizontal_valid_move_squares(self))
        return valid_moves


class Bishop(Piece):
    SCORE = 33
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_bis.png'))
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_bis.png'))

    def __init__(self, square, is_white):
        image = self.BLACK_IMAGE
        if is_white:
            image = self.WHITE_IMAGE
        super().__init__(image, square, is_white)

    def get_valid_move_squares(self):
        return _get_diagonal_valid_moves(self)

    def update_score(self):
        self.SCORE = 30
        if 3 <= self.square.tur_cord <= 5:
            self.SCORE = 35


class Queen(Piece):
    SCORE = 90
    BLACK_IMAGE = pygame.image.load(os.path.join(BLACK_PIECES_PATH, 'black_queen.png'))
    WHITE_IMAGE = pygame.image.load(os.path.join(WHITE_PIECES_PATH, 'white_queen.png'))

    def __init__(self, square, is_white):
        image = self.BLACK_IMAGE
        if is_white:
            image = self.WHITE_IMAGE
        super().__init__(image, square, is_white)

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
            valid_squares, found_right_down = _check_next_diagonal_valid_move(piece, current_distance, current_distance,
                                                                              valid_squares)
        if found_left_down:
            valid_squares, found_left_down = _check_next_diagonal_valid_move(piece, current_distance,
                                                                             current_distance * -1, valid_squares)
        if found_right_up:
            valid_squares, found_right_up = _check_next_diagonal_valid_move(piece, current_distance * -1,
                                                                            current_distance, valid_squares)
        if found_left_up:
            valid_squares, found_left_up = _check_next_diagonal_valid_move(piece, current_distance * -1,
                                                                           current_distance * -1,
                                                                           valid_squares)
    return valid_squares


def _check_next_diagonal_valid_move(piece, line_distance_from_square, tur_distance_from_square, valid_squares):
    next_tur = piece.square.tur_cord + tur_distance_from_square
    next_line = piece.square.line_cord + line_distance_from_square
    if square_is_valid(next_tur, next_line, piece.IS_IN_WHITE_TEAM):
        square = squares[next_line][next_tur]
        valid_squares.append(square)
        return valid_squares, square.current_piece is None
    return valid_squares, False


def _get_valid_straight_move_squares(piece):
    valid_moves = _get_vertical_valid_move_squares(piece)
    valid_moves.extend(_get_horizontal_valid_move_squares(piece))
    return valid_moves


def _get_horizontal_valid_move_squares(piece):
    this_tur = piece.square.tur_cord

    valid_moves = []

    for line in range(BOARD_LINE):
        if square_is_valid(this_tur, line, piece.IS_IN_WHITE_TEAM):
            square = squares[line][this_tur]
            # If square is empty we just add him to the row.
            valid_moves.append(square)
            if square.current_piece is not None:
                # If square is taken by enemy and including piece(this rook), this is the valid squares.
                if piece.square in valid_moves:
                    break
                # Other we start a new raw from this square(including).
                else:
                    valid_moves = [square]
            continue

        # Because piece.team equals to piece.team he isn't valid but we need to add him to return square.
        if squares[line][this_tur].current_piece == piece:
            valid_moves.append(piece.square)

        # If the row of squares touch teammate square and including piece(this piece), this is the valid squares.
        elif piece.square in valid_moves:
            break

        # Other we have to make a new row.
        else:
            valid_moves = []

    valid_moves.remove(piece.square)
    return valid_moves


def _get_vertical_valid_move_squares(piece):
    # Check squares left  and right then root.

    this_line = piece.square.line_cord
    valid_moves = []

    for tur in range(BOARD_LINE):
        if square_is_valid(tur, this_line, piece.IS_IN_WHITE_TEAM):
            square = squares[this_line][tur]
            valid_moves.append(square)
            if square.current_piece is not None:
                if piece.square in valid_moves:
                    break
                else:
                    valid_moves = [square]
            continue

        if squares[this_line][tur].current_piece == piece:
            valid_moves.append(piece.square)

        elif piece.square in valid_moves:
            break
        else:
            valid_moves = []

    valid_moves.remove(piece.square)
    return valid_moves
