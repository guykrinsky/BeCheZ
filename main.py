from chess_utils import *
from teams import Team, get_score_dif
import timer
import pygame
import screen
import bot
import os
import colors

SOUNDS_PATH = 'sounds'

team_got_turn = None
team_doesnt_got_turn = None
turn_number = 0


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
    redraw_game_screen()
    global turn_number
    pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'pong.wav')).play()

    switch_turn(white_team, black_team)

    print(piece_clicked)

    if is_checkmated(team_got_turn, team_doesnt_got_turn):
        screen.draw_winner(team_doesnt_got_turn)
        raise Checkmated

    if is_tie(team_got_turn, team_doesnt_got_turn):
        text = f"Tie"
        text_surface = screen.LARGE_FONT.render(text, False, colors.DARK_GREEN)
        screen.screen.blit(text_surface, (screen.SCREEN_WIDTH/2 - 50, screen.SCREEN_HEIGHT/2 - 30))
        pygame.display.flip()
        raise Tie

    piece_clicked.move_counter += 1
    turn_number += 1

    remove_eaten_pieces(white_team, black_team)
    white_team.update_score()
    black_team.update_score()
    score_dif = get_score_dif(white_team, black_team)
    team_leading = white_team if score_dif > 0 else black_team
    print(f'turn {turn_number}:\n'
          f'team leading is {team_leading} in {score_dif}\n'
          f'keep going!')


def print_board(white_team, black_team):
    print(white_team)
    white_team.print_pieces()
    print(black_team)
    black_team.print_pieces()


def game_loop(white_team: Team, black_team: Team, is_one_player_playing, bot_depth):
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
            update_game_after_move(piece_moved, team_got_turn, team_doesnt_got_turn)

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
                except MoveError:
                    # The move wasn't valid.
                    pygame.mixer.Sound(os.path.join(SOUNDS_PATH, 'error.wav')).play()

                piece_clicked = None

        try:
            team_won = black_team
            white_team.timer.is_out_of_time()
            team_won = white_team
            black_team.timer.is_out_of_time()
        except timer.RunOutOfTime:
            print(team_won)
            screen.draw_winner(team_won)
            redraw_game_screen()
            raise GameEnd

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
        return

    except GameEnd:
        print("Game ended.")
        timer.sleep(10)


if __name__ == '__main__':
    main()
