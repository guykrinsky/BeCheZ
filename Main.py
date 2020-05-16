
from chess_utils import *

pygame.init()


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

        redraw_game_screen()


def main():
    Screen.draw_screen()
    board_pieces = place_pieces()
    redraw_game_screen()
    game_loop(board_pieces)


if __name__ == '__main__':
    main()
