import pygame
import colors
from teams import *
import os
import exceptions
import logging

pygame.init()

SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h - 50
HEIGHT_OF_SCOREBOARD = 200

SPACE_FROM_SCOREBOARD = 50
BOARD_SIDE = SCREEN_HEIGHT - HEIGHT_OF_SCOREBOARD - SPACE_FROM_SCOREBOARD * 2

MIDDLE_HORIZONTAL = SCREEN_WIDTH / 2
RECT_WIDTH = 200
RECT_HEIGHT = 100

NUMBER_OF_SMALL_RECTS = 4
SMALL_RECT_WIDTH = SCREEN_WIDTH/(NUMBER_OF_SMALL_RECTS*4)
SMALL_RECT_HEIGHT = SCREEN_HEIGHT/(NUMBER_OF_SMALL_RECTS*2)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

squares = []
PICTURES_PATH = 'pictures'

NUMBER_OF_SQUARES = 8
SCORE_BOARD = pygame.Surface((SCREEN_WIDTH, HEIGHT_OF_SCOREBOARD))

REGULAR_FONT = pygame.font.SysFont('comicsansms', 30)
LARGE_FONT = pygame.font.Font('freesansbold.ttf', 80)

SPACE_BETWEEN_BOARD_AND_EATEN_PIECES = 100

GAME_LENGTH_OPTION = (1, 3, 5, 10)

LIGHT_SQUARE_COLOR = colors.LIGHT_BLUE
DARK_SQUARE_COLOR = colors.DARK_BLUE


class Square:
    SIDE = BOARD_SIDE/NUMBER_OF_SQUARES

    def __init__(self, x, y, color, tur, line):
        self.rect = pygame.Rect(x, y, self.SIDE, self.SIDE)
        self.color = color
        self.original_color = color
        self.tur_cord = tur
        self.line_cord = line
        self.id = str(line) + str(tur)
        self.x_mid = x + Square.SIDE/2
        self.y_mid = y + Square.SIDE/2
        self.current_piece = None

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.current_piece is not None:
            self.current_piece.draw()

    def coloring_square_by_original_color(self):
        if self.color == self.original_color:
            if self.original_color == DARK_SQUARE_COLOR:
                self.color = colors.DARK_RED
            else:
                self.color = colors.LIGHT_RED
        else:
            self.color = self.original_color

    def __str__(self):
        return f'(line: {self.line_cord}, tur: {self.tur_cord})'


def add_squares_to_board():
    # at the begging of the game, draw and init the squares.

    bg_image = pygame.image.load(os.path.join(PICTURES_PATH, 'main_background.jpg'))
    screen.blit(bg_image, (0, HEIGHT_OF_SCOREBOARD))

    x = SPACE_FROM_SCOREBOARD
    y = HEIGHT_OF_SCOREBOARD + SPACE_FROM_SCOREBOARD
    for line in range(NUMBER_OF_SQUARES):
        tmp = line % 2
        line_of_squars = []
        for tur in range(NUMBER_OF_SQUARES):
            if tur % 2 == tmp:
                color = LIGHT_SQUARE_COLOR
            else:
                color = DARK_SQUARE_COLOR

            current_square = Square(x, y, color, tur, line)
            line_of_squars.append(current_square)

            x += Square.SIDE

        squares.append(line_of_squars)
        x = SPACE_FROM_SCOREBOARD
        y += Square.SIDE

    pygame.display.flip()


def is_move_to_square_valid(tur, line, team):
    if 0 <= line < NUMBER_OF_SQUARES and 0 <= tur < NUMBER_OF_SQUARES:
        # Square is on the board
        check_square_piece = squares[line][tur].current_piece
        if check_square_piece is not None:
            # Check if other piece is on the same team.
            return team is not check_square_piece.team
        # Next move is inside board and empty square.
        return True
    return False


def draw_bg(team_got_turn: Team, team_doesnt_got_turn: Team):
    draw_scoreboard(team_got_turn, team_doesnt_got_turn)
    draw_board()


def draw_scoreboard(team_got_turn: Team, team_doesnt_got_turn: Team):

    white_team, black_team = get_teams_colors(team_got_turn, team_doesnt_got_turn)
    screen.blit(SCORE_BOARD, (0, 0))
    # I switched to just clear color and not an image as the background of the scoreboard.
    # draw bg image of score board. this way the last "scoreboard" is erased.
    SCORE_BOARD.fill(colors.DARK_BLUE)
    # bg_image = pygame.image.load(os.path.join(PICTURES_PATH, 'boardscore_bg.png'))
    # SCORE_BOARD.blit(bg_image, (0, 0))

    draw_who_turn_is(team_got_turn)
    draw_timers(white_team, black_team)
    draw_score(team_got_turn, team_doesnt_got_turn)


def draw_board():
    for line in squares:
        for square in line:
            square.draw()


def draw_who_turn_is(team_got_turn):
    if team_got_turn.is_white_team:
        text = LARGE_FONT.render('White Player Turn', False, colors.WHITE)
    else:
        text = LARGE_FONT.render('Black Player Turn', False, colors.BLACK)

    SCORE_BOARD.blit(text, (MIDDLE_HORIZONTAL - text.get_width()/2, 0))


def draw_timer(team):
    timer = team.timer
    color = colors.WHITE if team.is_white_team else colors.BLACK
    minutes = timer.get_minutes_left()
    seconds = timer.get_seconds_left_to_last_minute()

    seconds = '00' if seconds == 60 else str(seconds).zfill(2)
    minutes = str(minutes).zfill(2)
    text = REGULAR_FONT.render(f"{minutes}:{seconds}", False, color)
    place = (10, 0) if team.is_white_team else (SCORE_BOARD.get_width() - text.get_width(), 0)
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
    text = REGULAR_FONT.render("White team score:", False, colors.WHITE)
    SCORE_BOARD.blit(text, (0, SCORE_BOARD.get_height() - 15 - text.get_height()))

    text = REGULAR_FONT.render("Black team score:", False, colors.WHITE)
    SCORE_BOARD.blit(text, (SCREEN_WIDTH - text.get_width() - 10, SCORE_BOARD.get_height() - 15 - text.get_height()))

    pygame.draw.rect(SCORE_BOARD, colors.BLACK, (10, SCORE_BOARD.get_height() - 15, length, 10))
    white_rect_length = length / 2 + get_score_difference(white_team, black_team) / 10
    pygame.draw.rect(SCORE_BOARD, colors.WHITE, (10, SCORE_BOARD.get_height() - 15, white_rect_length, 10))


def color_all_square_to_original_color():
    for line in squares:
        for square in line:
            if square.color != square.original_color:
                square.coloring_square_by_original_color()


def draw_eaten_pieces(white_team: Team, black_team: Team):
    width, height = int(SCREEN_WIDTH - BOARD_SIDE - (SPACE_BETWEEN_BOARD_AND_EATEN_PIECES * 2)),\
                    int(white_team.pieces[0].image.get_height() + 5)
    rect = pygame.Rect(BOARD_SIDE + SPACE_BETWEEN_BOARD_AND_EATEN_PIECES,
                       SCORE_BOARD.get_height() + (SPACE_FROM_SCOREBOARD*2), width, height)
    pygame.draw.rect(screen, colors.DARK_BLUE, rect)
    x = BOARD_SIDE + SPACE_BETWEEN_BOARD_AND_EATEN_PIECES
    size = int(min(width / 16, white_team.pieces[0].image.get_height()))
    for eaten_piece in white_team.eaten_pieces:
        image = pygame.transform.scale(eaten_piece.image, (size, size))
        screen.blit(image, (x, rect.top))
        x += size

    rect = pygame.Rect(BOARD_SIDE + SPACE_BETWEEN_BOARD_AND_EATEN_PIECES,
                       SCREEN_HEIGHT - (SPACE_FROM_SCOREBOARD*2) - height, width, height)
    pygame.draw.rect(screen, colors.WHITE, rect)
    x = BOARD_SIDE + SPACE_BETWEEN_BOARD_AND_EATEN_PIECES
    for eaten_piece in black_team.eaten_pieces:
        image = pygame.transform.scale(eaten_piece.image, (size, size))
        screen.blit(image, (x, rect.top))
        x += size


def draw_winner(team_won):
    text = f"Team won is {team_won}"
    logging.info(text)
    text_surface = LARGE_FONT.render(text, False, colors.LIGHT_BLUE)
    screen.blit(text_surface, (MIDDLE_HORIZONTAL - text_surface.get_width()/2, SCREEN_HEIGHT / 2 - text_surface.get_height()/2))
    pygame.display.flip()


def draw_tie():
    text = f"Tie"
    text_surface = LARGE_FONT.render(text, False, colors.DARK_GREEN)
    screen.blit(text_surface, (SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 - 30))
    pygame.display.flip()