from chess_utils import *
from teams import Team
import timer
import pygame
import Screen
import bot


def redraw_game_screen(team_got_turn, white_team_timer, black_team_timer):
    Screen.draw_bg(team_got_turn, white_team_timer, black_team_timer)

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


def game_loop(white_team: Team, black_team: Team):
    black_team.timer.pause()
    running = True
    piece_clicked = None
    team_got_turn = white_team
    team_doesnt_got_turn = black_team
    while running:
        # if team_got_turn is black_team:
        #     if is_checkmated(white_team, black_team, team_got_turn):
        #         running = False
        #         break
        #     bot.move(white_team, black_team)
        #     team_got_turn = white_team
        #     timer.set_timer(team_got_turn, white_team, black_team)
        #     for piece in white_team.pieces:
        #         if piece.is_eaten:
        #             white_team.pieces.remove(piece)
        #     for piece in black_team.pieces:
        #         if piece.is_eaten:
        #             black_team.pieces.remove(piece)
        #     white_team.update_score()
        #     black_team.update_score()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_square = get_square_clicked()

                if clicked_square is None:
                    break

                if piece_clicked is None:
                    if clicked_square.current_piece is not None and clicked_square.current_piece in team_got_turn.pieces:
                        piece_clicked = clicked_square.current_piece
                        piece_clicked.color_next_step()

                else:
                    if move_turn(piece_clicked, clicked_square, team_got_turn, team_doesnt_got_turn):
                        team_got_turn = team_doesnt_got_turn
                        if team_got_turn is white_team:
                            team_doesnt_got_turn = black_team
                        else:
                            team_doesnt_got_turn = white_team
                        piece_clicked.move_counter += 1
                        pygame.mixer.Sound('pong.wav').play()
                        timer.set_timer(team_got_turn, white_team, black_team)
                        for piece in white_team.pieces:
                            if piece.is_eaten:
                                white_team.pieces.remove(piece)
                        for piece in black_team.pieces:
                            if piece.is_eaten:
                                black_team.pieces.remove(piece)
                        white_team.update_score()
                        black_team.update_score()
                    else:
                        pygame.mixer.Sound('error.wav').play()

                    piece_clicked = None

                if is_checkmated(team_got_turn, team_doesnt_got_turn):
                    running = False

        if white_team.timer.is_game_ended():
            break
        if black_team.timer.is_game_ended():
            break

        redraw_game_screen(team_got_turn, white_team.timer, black_team.timer)


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
