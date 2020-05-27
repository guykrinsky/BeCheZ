from timer import Timer
from chess_utils import *
import teams
import timer


def redraw_game_screen(is_white_team_turn, white_team_timer, black_team_timer):
    Screen.draw_bg(is_white_team_turn, white_team_timer, black_team_timer)

    for line in Screen.squares:
        for square in line:
            if square.current_piece is not None:
                square.current_piece.draw()

    pygame.display.flip()


def listen_to_mouse():
    mouse_pos = pygame.mouse.get_pos()

    for line in Screen.squares:
        for square in line:
            if square.rect.collidepoint(mouse_pos):
                return square


def set_timer(is_white_team_turn, white_timer, black_timer):
    if is_white_team_turn:
        white_timer.resume()
        black_timer.pause()
    else:
        black_timer.resume()
        white_timer.pause()


def game_loop(white_team: teams.Team, black_team: teams.Team):

    black_team.timer.pause()
    running = True
    piece_clicked = None
    is_white_team_turn = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = listen_to_mouse()

                if square is None:
                    break

                if piece_clicked is None:
                    if square.current_piece is not None and square.current_piece.is_white_team == is_white_team_turn:
                        piece_clicked = square.current_piece
                        piece_clicked.color_next_step()

                else:
                    if move_turn(piece_clicked, square, is_white_team_turn, white_team, black_team):
                        is_white_team_turn = not is_white_team_turn
                        piece_clicked.move_counter += 1
                        pygame.mixer.Sound('pong.wav').play()
                        set_timer(is_white_team_turn, white_team.timer, black_team.timer)
                    else:
                        pygame.mixer.Sound('error.wav').play()

                    piece_clicked = None

                if is_checkmated(white_team, black_team, is_white_team_turn):
                    running = False

        if white_team.timer.is_game_ended():
            break
        if black_team.timer.is_game_ended():
            break

        for piece in white_team.pieces:
            if piece.is_eaten:
                white_team.pieces.remove(piece)
        for piece in black_team.pieces:
            if piece.is_eaten:
                black_team.pieces.remove(piece)

        redraw_game_screen(is_white_team_turn, white_team.timer, black_team.timer)


def main():
    timer.set_game_length(1)
    Screen.draw_screen()
    white_team = teams.Team(True)
    black_team = teams.Team(False)
    place_pieces(white_team, black_team)
    game_loop(white_team, black_team)


if __name__ == '__main__':
    main()
