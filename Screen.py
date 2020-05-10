import pygame
import colors

screen = pygame.display.set_mode((480, 480))
squares = []

BOARD_LINE = 8


class Square:
    WIDTH = 60
    HEIGHT = 60

    def __init__(self, x, y, color, tur, line):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.color = color
        self.original_color = color
        self.tur_cord = tur
        self.line_cord = line
        self.current_piece = None

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

    def coloring_square_by_original_color(self):
        if self.color == self.original_color:
            if self.original_color == colors.DARK_GREEN:
                self.color = colors.DARK_RED
            else:
                self.color = colors.LIGHT_RED
        else:
            self.color = self.original_color


def square_is_valid(tur, line, is_white_team):
    """
    Check if square is in board bounds and not taken by teammate piece.
    """
    if 0 <= line < BOARD_LINE:
        if 0 <= tur < BOARD_LINE:
            check_square_piece = squares[line][tur].current_piece
            if check_square_piece is not None:
                # Check if other piece is on the same team.
                return is_white_team != check_square_piece.is_white_team
            # Next move is inside board and empty square.
            return True
    return False


def draw_bg():
    for line in squares:
        for square in line:
            square.draw()


def draw_screen():
    x = 0
    y = 0
    for line in range(BOARD_LINE):
        tmp = line % 2
        square_in_line = []
        for tur in range(BOARD_LINE):
            if tur % 2 == tmp:
                color = colors.WHITE
            else:
                color = colors.DARK_GREEN

            square_in_line.append(Square(x, y, color, tur, line))
            x += Square.WIDTH
        x = 0
        y += Square.HEIGHT
        squares.append(square_in_line)
    draw_bg()
    pygame.display.flip()
