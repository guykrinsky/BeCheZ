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
        return_square = []
        # Direction represent one square walk.
        direction = 1 if self.is_white_team else -1
        # Check if nest step is out of board.
        line += direction
        if square_is_valid(tur, line, self.is_white_team):
            square = squares[line][tur]
            return_square.append(square)
            if self.move_counter == 0:
                line += direction
                if square_is_valid(tur, line, self.is_white_team):
                    square = squares[line][tur]
                    return_square.append(square)
        return return_square


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

        return_squares = self._get_horizintal_valid_move_squares()
        return_squares.extend(self._get_vertical_valid_move_squares())
        return return_squares

    def _get_horizintal_valid_move_squares(self):
        # Check squares left  and right then root.

        this_line = self.square.line_cord
        return_squares = []

        for tur in range(BOARD_LINE):
            if square_is_valid(tur, this_line, self.is_white_team):
                square = squares[this_line][tur]
                return_squares.append(square)
                if square.current_piece is not None:
                    if self.square in return_squares:
                        break
                    else:
                        return_squares = [square]
                continue

            if squares[this_line][tur].current_piece == self:
                return_squares.append(self.square)

            elif self.square in return_squares:
                break
            else:
                return_squares = []

        return_squares.remove(self.square)

        return return_squares

    def _get_vertical_valid_move_squares(self):
        this_tur = self.square.tur_cord

        valid_moves = []

        for line in range(BOARD_LINE):
            if square_is_valid(this_tur, line, self.is_white_team):
                square = squares[line][this_tur]
                # If square is empty we just add him to the row.
                valid_moves.append(square)
                if square.current_piece is not None:
                    # If square is taken by enemy and including self(this rook), this is the valid squares.
                    if self.square in valid_moves:
                        break
                    # Other we start a new raw from this square(including).
                    else:
                        valid_moves = [square]
                continue

            # Because self.team equals to self.team he isn't valid but we need to add him to return square.
            if squares[line][this_tur].current_piece == self:
                valid_moves.append(self.square)

            # If the row of squares touch teammate square and including self(this rook), this is the valid squares.
            elif self.square in valid_moves:
                break

            # Other we have to make a new row.
            else:
                valid_moves = []

        valid_moves.remove(self.square)
        return valid_moves
