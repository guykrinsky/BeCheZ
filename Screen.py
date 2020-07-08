import pygame
import colors
from teams import Team, get_score_dif
import os

pygame.init()

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 680
MIDDLE_HORIZENTAL = SCREEN_WIDTH / 2
RECT_WIDTH = 200
RECT_HEIGHT = 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
squares = []
PICTURES_PATH = 'pictures'

BOARD_LINE = 8
HEIGHT_OF_SCOREBOARD = 200
SCORE_BOARD = pygame.Surface((screen.get_width(), HEIGHT_OF_SCOREBOARD))
FONT = pygame.font.SysFont('comicsansms', 30)


class ExitGame(Exception):
    pass


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

    def __str__(self):
        return f'(line: {self.line_cord}, tur: {self.tur_cord})'


# Changed
def is_move_to_square_valid(tur, line, team):
    """
    Check if square is in board bounds and not taken by teammate piece.
    """
    if 0 <= line < BOARD_LINE and 0 <= tur < BOARD_LINE:
        # Square is on the board
        check_square_piece = squares[line][tur].current_piece
        if check_square_piece is not None:
            # Check if other piece is on the same team.
            return team is not check_square_piece.team
        # Next move is inside board and empty square.
        return True
    return False


def draw_bg(team_got_turn: Team, team_doesnt_got_turn: Team):
    white_team = team_doesnt_got_turn
    black_team = team_got_turn
    if team_got_turn.is_white_team:
        white_team = team_got_turn
        black_team = team_doesnt_got_turn

    screen.blit(SCORE_BOARD, (0, 0))
    bg_image = pygame.image.load(os.path.join(PICTURES_PATH, 'boardscore_bg.png'))
    SCORE_BOARD.blit(bg_image, (0, 0))

    draw_squares_bg()
    draw_who_turn_is(team_got_turn)
    draw_timers(white_team, black_team)
    draw_score(team_got_turn, team_doesnt_got_turn)


def draw_squares_bg():
    for line in squares:
        for square in line:
            square.draw()


def draw_who_turn_is(team_got_turn):
    if team_got_turn.is_white_team:
        text = FONT.render('White Player Turn', False, colors.WHITE)
    else:
        text = FONT.render('Black Player Turn', False, colors.BLACK)

    SCORE_BOARD.blit(text, (SCORE_BOARD.get_width() / 2 - 80, 0))


def draw_timer(team):
    place = (0, 0) if team.is_white_team else (SCORE_BOARD.get_width() - 55, 0)
    timer = team.timer
    color = colors.WHITE if team.is_white_team else colors.BLACK
    minutes = timer.get_minutes_left()
    seconds = timer.get_seconds_left_to_last_minute()
    if seconds == 60:
        seconds = '00'
    seconds = str(seconds).zfill(2)
    minutes = str(minutes).zfill(2)
    text = FONT.render(f"{minutes}:{seconds}", False, color)
    SCORE_BOARD.blit(text, place)


def draw_timers(white_team, black_team):
    draw_timer(white_team)
    draw_timer(black_team)


def draw_score(team_got_turn, team_doesnt_got_turn):
    white_team = team_got_turn if team_got_turn.is_white_team else team_doesnt_got_turn
    black_team = team_got_turn if not team_got_turn.is_white_team else team_doesnt_got_turn

    white_team.update_score()
    black_team.update_score()

    length = SCREEN_WIDTH - 20
    text = FONT.render("White team score:", False, colors.WHITE)
    SCORE_BOARD.blit(text, (0, SCORE_BOARD.get_height() - 50))

    x_pos = SCREEN_WIDTH - 200
    text = FONT.render("Black team score:", False, colors.WHITE)
    SCORE_BOARD.blit(text, (x_pos, SCORE_BOARD.get_height() - 50))

    pygame.draw.rect(SCORE_BOARD, colors.BLACK, (10, SCORE_BOARD.get_height() - 15, length, 10))
    white_rect_length = length/2 + get_score_dif(white_team, black_team)/10
    pygame.draw.rect(SCORE_BOARD, colors.WHITE, (10, SCORE_BOARD.get_height() - 15, white_rect_length, 10))


def add_squares_to_board():
    SCORE_BOARD.fill(colors.BROWN)
    x = 0
    y = HEIGHT_OF_SCOREBOARD
    for line in range(BOARD_LINE):
        tmp = line % 2
        square_in_line = []
        for tur in range(BOARD_LINE):
            if tur % 2 == tmp:
                color = colors.LIGHT_BROWN
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


def starting_screen():
    screen.fill(colors.WHITE)
    bg_image = pygame.image.load(os.path.join(PICTURES_PATH, 'opening_screen_picture.png'))
    screen.blit(bg_image, (0, 0))
    current_print_height = 150

    one_player_rect = pygame.Rect(MIDDLE_HORIZENTAL - RECT_WIDTH/2, current_print_height, RECT_WIDTH, RECT_HEIGHT)
    pygame.draw.rect(screen, colors.LIGHT_SILVER, one_player_rect)

    text = FONT.render("One Player", False, colors.BLACK)
    screen.blit(text, (one_player_rect.centerx - 50, one_player_rect.centery - 10))
    current_print_height += 200

    tow_player_rect = pygame.Rect(MIDDLE_HORIZENTAL - RECT_WIDTH/2, current_print_height, RECT_WIDTH, RECT_HEIGHT)
    pygame.draw.rect(screen, colors.LIGHT_SILVER, tow_player_rect)

    text = FONT.render("Tow Players", False, colors.BLACK)
    screen.blit(text, (tow_player_rect.centerx - 50, tow_player_rect.centery - 10))
    current_print_height += 100

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise ExitGame

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if one_player_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    return True

                elif tow_player_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    return False
