import pygame
from Screen import screen, squares
import colors
import abc


class Piece(metaclass=abc.ABCMeta):
    def __init__(self, image, square, team):
        self.image = image
        self.square = square
        self.team_is_white = team

    def move(self, square):
        if square in self.get_valid_move_squares():
            self.square = square

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
        super().__init__(image, square, False)

    def get_valid_move_squares(self):
        line = int(self.square.rect.top / 60)
        valid_squares = []
        for line in range(line - 1, line + 2):
            tur = int(self.square.rect.left / 60)
            if line > 7:
                break
            for tur in range(tur - 1, tur + 2):
                if tur > 7:
                    break

                valid_squares.append(squares[line][tur])
                squares[line][tur].coloring_square_by_original_color()

        valid_squares.remove(self.square)
        return valid_squares
