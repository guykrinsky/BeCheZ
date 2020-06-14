from chess_utils import *
from teams import Team
import timer
import pygame
import Screen
import bot

team_got_turn = None
team_doesnt_got_turn = None


def redraw_game_screen(is_white_team_turn, white_team, black_team):
    Screen.draw_bg(is_white_team_turn, white_team, black_team)

    for line in Screen.squares:
        for square in line:
            if square.current_piece is not None:
                square.current_piece.draw()

    pygame.display.flip()


def get_square_clicked():
    mouse_pos = pygame.mouse.get_pos()

    for line in Screen.squares:
        for square in line:
            if square.rect.collidepoint(mouse_pos):
                return square


def move_played(piece_clicked, black_team, white_team):
    global team_got_turn
    global team_doesnt_got_turn
    team_got_turn = team_doesnt_got_turn
    if team_got_turn is white_team:
        team_doesnt_got_turn = black_team
    else:
        team_doesnt_got_turn = white_team

    timer.switch_timers(team_got_turn, team_doesnt_got_turn)

    piece_clicked.move_counter += 1
    pygame.mixer.Sound('pong.wav').play()
    for piece in white_team.pieces:
        if piece.is_eaten:
            white_team.pieces.remove(piece)
    for piece in black_team.pieces:
        if piece.is_eaten:
            black_team.pieces.remove(piece)
    white_team.update_score()
    black_team.update_score()


def game_loop(white_team: Team, black_team: Team):
    black_team.timer.pause()
    running = True
    piece_clicked = None
    global team_got_turn
    global team_doesnt_got_turn
    team_got_turn = white_team
    team_doesnt_got_turn = black_team
    while running:

        if team_got_turn is black_team:
            piece_moved = bot.move(white_team, black_team)
            if piece_moved is None:
                # Bot has nowhere to go, because it's checkmated.
                break
            move_played(piece_moved, team_got_turn, team_doesnt_got_turn)

            # Check if after bot move, you are checkmated.
            if is_checkmated(team_got_turn, team_doesnt_got_turn):
                break
        # else:
        #     piece_moved = bot.move(black_team, white_team)
        #     if piece_moved is None:
        #         # Bot has nowhere to go, because it's checkmated.
        #         break
        #     move_played(piece_moved, team_got_turn, team_doesnt_got_turn)
        #
        #     # Check if after bot move, you are checkmated.
        #     if is_checkmated(team_got_turn, team_doesnt_got_turn):
        #         break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_square = get_square_clicked()

                if clicked_square is None:
                    continue

                if piece_clicked is None:
                    if clicked_square.current_piece is not None and clicked_square.current_piece in team_got_turn.pieces:
                        piece_clicked = clicked_square.current_piece
                        piece_clicked.color_next_step()

                else:
                    if move_turn(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn):
                        move_played(piece_clicked, black_team, white_team)
                        if is_checkmated(team_got_turn, team_doesnt_got_turn):
                            running = False

                    else:
                        pygame.mixer.Sound('error.wav').play()

                    piece_clicked = None

        if white_team.timer.is_game_ended():
            break
        if black_team.timer.is_game_ended():
            break

        redraw_game_screen(team_got_turn is white_team, white_team, black_team)

# def opening_screen():
#     Screen.screen.


def main():

    timer.set_game_length(5)
    Screen.draw_screen()
    white_team = Team()
    black_team = Team()
    place_pieces(white_team, black_team)
    black_team.update_score()
    game_loop(white_team, black_team)


if __name__ == '__main__':
    main()
