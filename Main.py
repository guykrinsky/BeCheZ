from timer import Timer
from chess_utils import *


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


def game_loop(board_pieces):
    running = True
    piece_clicked = None
    is_white_team_turn = True
    black_timer = Timer()
    black_timer.pause()
    white_timer = Timer()
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
                    if move_turn(piece_clicked, square, is_white_team_turn, board_pieces):
                        is_white_team_turn = not is_white_team_turn
                        piece_clicked.move_counter += 1
                        pygame.mixer.Sound('pong.wav').play()
                        set_timer(is_white_team_turn, white_timer, black_timer)
                    else:
                        pygame.mixer.Sound('error.wav').play()

                    piece_clicked = None

                if is_checkmated(board_pieces, is_white_team_turn):
                    running = False

        if white_timer.get_seconds() > 360:
            break
        if black_timer.get_seconds() > 360:
            break

        for piece in board_pieces:
            if piece.is_eaten:
                board_pieces.remove(piece)

        redraw_game_screen(is_white_team_turn, white_timer, black_timer)


def main():

    Screen.draw_screen()
    board_pieces = place_pieces()
    game_loop(board_pieces)


if __name__ == '__main__':
    main()
