import pygame
import colors
from teams import Team

pygame.init()

screen = pygame.display.set_mode((480, 600))
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
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
            if self.original_color == colors.DARK_BROWN:
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
                return is_white_team != check_square_piece.IS_IN_WHITE_TEAM
            # Next move is inside board and empty square.
            return True
    return False


def draw_bg(is_white_team_turn, white_team: Team, black_team: Team):
    white_timer = white_team.timer
    black_timer = black_team.timer
    screen.blit(SCORE_BOARD, (0, 0))
    pygame.draw.rect(SCORE_BOARD, colors.BROWN, (0, 0, SCORE_BOARD.get_width(), SCORE_BOARD.get_height()))

    draw_squares_bg()
    draw_who_turn_is(is_white_team_turn)
    draw_timer(white_timer, black_timer)
    draw_score(white_team, black_team)


def draw_squares_bg():
    for line in squares:
        for square in line:
            square.draw()


def draw_who_turn_is(is_white_team_turn):
    if is_white_team_turn:
        text = FONT.render('White Player Turn', False, colors.WHITE)
    else:
        text = FONT.render('Black Player Turn', False, colors.BLACK)

    SCORE_BOARD.blit(text, (SCORE_BOARD.get_width() / 2 - 80, 0))


def draw_timer(white_timer, black_timer):
    minutes = white_timer.get_minutes_left()
    seconds = white_timer.get_seconds_left_to_last_minute()
    if seconds == 60:
        seconds = '00'
    seconds = str(seconds).zfill(2)
    minutes = str(minutes).zfill(2)
    text = FONT.render(f"{minutes}:{seconds}", False, colors.WHITE)
    SCORE_BOARD.blit(text, (0, 0))
    minutes = black_timer.get_minutes_left()
    seconds = black_timer.get_seconds_left_to_last_minute()
    if seconds == 60:
        seconds = '00'
    seconds = str(seconds).zfill(2)
    minutes = str(minutes).zfill(2)
    text = FONT.render(f"{minutes}:{seconds}", False, colors.BLACK)
    SCORE_BOARD.blit(text, (SCORE_BOARD.get_width() - 55, 0))


def draw_score(white_team, black_team):
    white_team.update_score()
    black_team.update_score()

    start_team_score = 200
    length = white_team.score / 2
    text = FONT.render("White team score:", False, colors.WHITE)
    SCORE_BOARD.blit(text, (0, SCORE_BOARD.get_height() - 50))
    pygame.draw.rect(SCORE_BOARD, colors.BLACK, (0, SCORE_BOARD.get_height() - 15, start_team_score, 10))
    pygame.draw.rect(SCORE_BOARD, colors.WHITE, (0, SCORE_BOARD.get_height() - 15, length, 10))

    length = black_team.score / 2
    x_pos = SCORE_BOARD.get_width() - start_team_score
    text = FONT.render("Black team score:", False, colors.BLACK)
    SCORE_BOARD.blit(text, (x_pos, SCORE_BOARD.get_height() - 50))
    pygame.draw.rect(SCORE_BOARD, colors.WHITE, (x_pos, SCORE_BOARD.get_height() - 15, start_team_score, 10))
    pygame.draw.rect(SCORE_BOARD, colors.BLACK, (x_pos, SCORE_BOARD.get_height() - 15, length, 10))


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
                color = colors.DARK_BROWN

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


MIDDLE_HORIZENTAL = SCREEN_WIDTH/2
RECT_WIDTH = 200
RECT_HEIGHT = 100


def starting_screen():
    screen.fill(colors.WHITE)

    current_print_height = 10

    text = FONT.render("Welcome to chess", False, colors.DARK_RED)
    screen.blit(text, (MIDDLE_HORIZENTAL - 90, current_print_height))
    current_print_height += 100

    one_player_rect = pygame.Rect(MIDDLE_HORIZENTAL - RECT_WIDTH/2, current_print_height, RECT_WIDTH, RECT_HEIGHT)
    pygame.draw.rect(screen, colors.DARK_RED, one_player_rect)

    text = FONT.render("One Player", False, colors.WHITE)
    screen.blit(text, (one_player_rect.centerx - 50, one_player_rect.centery - 10))
    current_print_height += 200

    tow_player_rect = pygame.Rect(MIDDLE_HORIZENTAL - RECT_WIDTH/2, current_print_height, RECT_WIDTH, RECT_HEIGHT)
    pygame.draw.rect(screen, colors.DARK_RED, tow_player_rect)

    text = FONT.render("Tow Players", False, colors.WHITE)
    screen.blit(text, (tow_player_rect.centerx - 50, tow_player_rect.centery - 10))
    current_print_height += 100

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if one_player_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    return True

                elif tow_player_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    return False
