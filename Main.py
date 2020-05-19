
from chess_utils import *

pygame.init()


def redraw_game_screen(is_white_team_turn):
    Screen.draw_bg(is_white_team_turn)

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


def move_turn(piece_clicked, clicked_square, is_white_team_turn, board_pieces):
    Screen.color_all_square_to_original_color()

    if piece_clicked.is_white_team is not is_white_team_turn:
        return False

    # check_castling.
    if isinstance(piece_clicked, pieces.King) and isinstance(clicked_square.current_piece, pieces.Rook):
        return check_castling(piece_clicked, clicked_square, is_white_team_turn, board_pieces)

    if clicked_square not in piece_clicked.get_valid_move_squares():
        return False

    if is_check_after_move(clicked_square, is_white_team_turn, piece_clicked, board_pieces):
        return False

    piece_clicked.move(clicked_square)
    return True


def game_loop(board_pieces):
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
                    if move_turn(piece_clicked, square, is_white_team_turn, board_pieces):
                        is_white_team_turn = not is_white_team_turn
                        piece_clicked.move_counter += 1
                        pygame.mixer.Sound('pong.wav').play()
                    else:
                        pygame.mixer.Sound('error.wav').play()
                    piece_clicked = None

                if is_checkmated(board_pieces, is_white_team_turn):
                    running = False

        for piece in board_pieces:
            if piece.is_eaten:
                board_pieces.remove(piece)

        redraw_game_screen(is_white_team_turn)


def main():

    Screen.draw_screen()
    board_pieces = place_pieces()
    redraw_game_screen(True)
    game_loop(board_pieces)


if __name__ == '__main__':
    main()
