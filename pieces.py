import pygame
from Screen import screen, squares, BOARD_LINE, square_is_valid, Square
import colors
import abc


class Piece(metaclass=abc.ABCMeta):
    def __init__(self, image, square, team):
        self.image = image
        self.square = square
        self.square.current_piece = self
        self.is_white_team = team
        self.move_counter = 0
        self.is_eaten = False

    def color_next_step(self):
        valid_square = self._get_valid_move_squares()
        for square in valid_square:
            square.coloring_square_by_original_color()

    def move(self, next_square: Square):
        valid_squares = self._get_valid_move_squares()
        if next_square in valid_squares:
            # Free current square.
            self.square.current_piece = None
            # Check if next square is taken by other team.
            if next_square.current_piece is not None:
                next_square.current_piece.is_eaten = True
            # Move to next square.
            self.square = next_square
            self.square.current_piece = self

            self.move_counter += 1

    @abc.abstractmethod
    def _get_valid_move_squares(self):
        pass

    def draw(self):
        screen.blit(self.image, self.square.rect.topleft)


class King(Piece):
    WHITE_IMAGE = pygame.image.load('white_king.png')
    BLACK_IMAGE = pygame.image.load('black_king.png')

    def __init__(self, is_white):
        if is_white:
            image = self.WHITE_IMAGE
            square = squares[0][3]
        else:
            image = self.BLACK_IMAGE
            square = squares[7][3]
        super().__init__(image, square, is_white)

    def _get_valid_move_squares(self):
        line = self.square.line_cord
        valid_squares = []
        for line in range(line - 1, line + 2):
            tur = self.square.tur_cord
            for tur in range(tur - 1, tur + 2):
                if square_is_valid(tur, line, self.is_white_team):
                    square = squares[line][tur]
                    valid_squares.append(square)

        return valid_squares


class Pawn(Piece):
    WHITE_IMAGE = pygame.image.load('white_pawn.png')
    BLACK_PAWN = pygame.image.load('black_pawn.png')

    def __init__(self, is_white, place):
        if is_white:
            square = squares[1][place]
            image = self.WHITE_IMAGE
        else:
            square = squares[6][place]
            image = self.BLACK_PAWN
        super().__init__(image, square, is_white)

    def _get_valid_move_squares(self):
        line = self.square.line_cord
        tur = self.square.tur_cord
        valid_moves = []
        # Direction represent one square walk.
        direction = 1 if self.is_white_team else -1
        # Check if nest step is out of board.
        line += direction

        if square_is_valid(tur, line, self.is_white_team):
            next_square = squares[line][tur]

            valid_moves.extend(self.diagonal_eat(next_square))

            if next_square.current_piece is None:
                valid_moves.append(next_square)

                if self.move_counter == 0:
                    line += direction
                    next_square = squares[line][tur]
                    if next_square.current_piece is None:
                        valid_moves.append(next_square)
        return valid_moves

    def diagonal_eat(self, next_square):
        valid_eat_moves = []

        # Left check.
        line = next_square.line_cord
        tur = next_square.tur_cord - 1
        if square_is_valid(tur, line, self.is_white_team):
            current_square = squares[line][tur]
            current_piece = current_square.current_piece
            if current_piece is not None:
                valid_eat_moves.append(current_square)
        # Right check.
        tur += 2
        if square_is_valid(tur, line, self.is_white_team):
            current_square = squares[line][tur]
            current_piece = current_square.current_piece
            if current_piece is not None:
                valid_eat_moves.append(current_square)
        return valid_eat_moves

class Rook(Piece):
    WHITE_IMAGE = pygame.image.load('white_rook.png')
    BLACK_IMAGE = pygame.image.load('black_roock.png')

    def __init__(self, is_white, square):
        if is_white:
            image = self.WHITE_IMAGE
        else:
            image = self.BLACK_IMAGE
        super(Rook, self).__init__(image, square, is_white)

    def _get_valid_move_squares(self):
        valid_moves = _get_vertical_valid_move_squares(self)
        valid_moves.extend(_get_horizontal_valid_move_squares(self))
        return valid_moves


class Bishop(Piece):
    WHITE_IMAGE = pygame.image.load('white_bis.png')
    BLACK_IMAGE = pygame.image.load('black_bis.png')

    def __init__(self, square, is_white):
        image = self.BLACK_IMAGE
        if is_white:
            image = self.WHITE_IMAGE
        super().__init__(image, square, is_white)

    def _get_valid_move_squares(self):
        return _get_diagonal_valid_moves(self)


class Queen(Piece):
    BLACK_IMAGE = pygame.image.load('black_queen.png')
    WHITE_IMAGE = pygame.image.load('white_queen.png')

    def __init__(self, square, is_white):
        image = self.BLACK_IMAGE
        if is_white:
            image = self.WHITE_IMAGE
        super().__init__(image, square, is_white)

    def _get_valid_move_squares(self):
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
    if square_is_valid(next_tur, next_line, piece.is_white_team):
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
        if square_is_valid(this_tur, line, piece.is_white_team):
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
        if square_is_valid(tur, this_line, piece.is_white_team):
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
