import pygame
import colors

pygame.init()

screen = pygame.display.set_mode((480, 600))
squares = []

BOARD_LINE = 8
HEIGHT_OF_SCOREBOARD = 120
SCORE_BOARD = pygame.Surface((screen.get_width(), HEIGHT_OF_SCOREBOARD))
FONT = pygame.font.SysFont('comicsansms', 30)


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


def draw_bg(is_white_team_turn):
    screen.blit(SCORE_BOARD, (0, 0))
    pygame.draw.rect(SCORE_BOARD, colors.BROWN, (0, 0, SCORE_BOARD.get_width(), SCORE_BOARD.get_height()))
    for line in squares:
        for square in line:
            square.draw()

    if is_white_team_turn:
        text = FONT.render('Turn is white', False, colors.WHITE)
        color = colors.WHITE
    else:
        text = FONT.render('Turn is black.', False, colors.BLACK)
        color = colors.BLACK

    SCORE_BOARD.blit(text, (SCORE_BOARD.get_width()/2-60, 0))


def draw_screen():
    SCORE_BOARD.fill(colors.BROWN)
    x = 0
    y = HEIGHT_OF_SCOREBOARD
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
    pygame.display.flip()


def color_all_square_to_original_color():
    for line in squares:
        for square in line:
            if square.color != square.original_color:
                square.coloring_square_by_original_color()