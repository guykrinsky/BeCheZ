from chess_utils import *
from teams import Team, get_score_dif
import timer
import pygame
import screen
import bot
import os

SOUNDS_PATH = 'sounds'

team_got_turn = None
team_doesnt_got_turn = None


def redraw_game_screen():
    screen.draw_bg(team_got_turn, team_doesnt_got_turn)

    for line in screen.squares:
        for square in line:
            if square.current_piece is not None:
                square.current_piece.draw()

    pygame.display.flip()


def get_square_clicked():
    mouse_pos = pygame.mouse.get_pos()

    for line in screen.squares:
        for square in line:
            if square.rect.collidepoint(mouse_pos):
                return square


def switch_turn(white_team, black_team):
    global team_got_turn
    global team_doesnt_got_turn
    team_got_turn = team_doesnt_got_turn
    if team_got_turn is white_team:
        team_doesnt_got_turn = black_team
    else:
        team_doesnt_got_turn = white_team

    timer.switch_timers(team_got_turn, team_doesnt_got_turn)


def remove_eaten_pieces(white_team, black_team):
    for piece in white_team.pieces + black_team.pieces:
        piece_team = white_team if piece.team.is_white_team else black_team
        if piece.is_eaten:
            piece_team.pieces.remove(piece)


def update_game_after_move(piece_clicked, black_team, white_team):
    pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'pong.wav')).play()

    switch_turn(white_team, black_team)

    piece_clicked.move_counter += 1

    remove_eaten_pieces(white_team, black_team)
    white_team.update_score()
    black_team.update_score()
    score_dif = get_score_dif(white_team, black_team)
    print(f'score diffence is {score_dif}')


def print_board(white_team, black_team):
    print(white_team)
    white_team.print_pieces()
    print(black_team)
    black_team.print_pieces()


def game_loop(white_team: Team, black_team: Team, is_one_player_playing, bot_depth):
    print_board(white_team, black_team)
    black_team.timer.pause()
    running = True
    piece_clicked = None
    global team_got_turn
    global team_doesnt_got_turn
    team_got_turn = white_team
    team_doesnt_got_turn = black_team
    while running:

        if team_got_turn is black_team and is_one_player_playing:
            piece_moved = bot.move(white_team, black_team, bot_depth)
            if piece_moved is None:
                # Bot has nowhere to go, because it's checkmated.
                print(f'Team won is {team_doesnt_got_turn}')
                break
            update_game_after_move(piece_moved, team_got_turn, team_doesnt_got_turn)

            # Check if after bot move, you are checkmated.
            if is_checkmated(team_got_turn, team_doesnt_got_turn):
                print(f'Team won is {team_doesnt_got_turn}')
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise screen.ExitGame

            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_square = get_square_clicked()

                if clicked_square is None:
                    continue

                if piece_clicked is None:
                    piece_clicked = clicked_square.current_piece
                    if piece_clicked in team_got_turn.pieces:
                        piece_clicked.color_next_step()
                    continue

                # If user already clicked on a piece,
                # we try to move the piece to the square the user clicked on.
                try:
                    try_to_move(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn)
                    # Move is valid.
                    update_game_after_move(piece_clicked, black_team, white_team)
                    if is_checkmated(team_got_turn, team_doesnt_got_turn):
                        print(f'Team won is {team_doesnt_got_turn}')
                        running = False
                except MoveError:
                    # The move wasn't valid.
                    pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'error.wav')).play()

                piece_clicked = None

        if white_team.timer.is_game_ended():
            break
        if black_team.timer.is_game_ended():
            break

        redraw_game_screen()


def main():
    try:
        is_one_player, game_length, bot_depth = screen.starting_screen()
        timer.set_game_length(game_length)
        screen.add_squares_to_board()
        white_team = Team(True)
        black_team = Team(False)
        place_pieces(white_team, black_team)
        game_loop(white_team, black_team, is_one_player, bot_depth)

    except screen.ExitGame:
        pass


if __name__ == '__main__':
    main()
