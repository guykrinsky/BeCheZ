import pygame
from Screen import screen, squares, BOARD_LINE, square_is_valid
import colors
import abc


class Piece(metaclass=abc.ABCMeta):
    def __init__(self, image, square, team):
        self.image = image
        self.square = square
        self.square.empty = False
        self.team_is_white = team
        self.move_counter = 0

    def color_next_step(self):
        valid_square = self.get_valid_move_squares()
        for square in valid_square:
            square.coloring_square_by_original_color()

    def move(self, square):
        valid_squares = self.get_valid_move_squares()
        if square in valid_squares:
            # Free current square.
            self.square.empty = True
            # Move to next square.
            self.square = square
            self.square.empty = False
            self.move_counter += 1

    @abc.abstractmethod
    def get_valid_move_squares(self):
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

    def get_valid_move_squares(self):
        line = self.square.line_cord
        valid_squares = []
        for line in range(line - 1, line + 2):
            tur = self.square.tur_cord
            for tur in range(tur - 1, tur + 2):
                if square_is_valid(tur, line):
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

    def get_valid_move_squares(self):
        line = self.square.line_cord
        tur = self.square.tur_cord
        return_square = []
        # Direction represent one square walk.
        direction = 1 if self.team_is_white else -1
        # Check if nest step is out of board.
        line += direction
        if square_is_valid(tur, line):
            square = squares[line][tur]
            return_square.append(square)
            if self.move_counter == 0:
                line += direction
                if square_is_valid(tur, line):
                    square = squares[line][tur]
                    return_square.append(square)
        return return_square


# class Rook(Piece):
#     WHITE_IMAGE = pygame.image.load('rook_white.png')
#     BLACK_IMAGE = pygame.image.load('rook_black.png')
#     def __init__(self, is_white):


