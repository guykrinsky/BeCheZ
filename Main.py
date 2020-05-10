import pygame
import Screen
import pieces
import colors

pygame.init()


def redraw_game_screen(board_pieces):
    Screen.draw_bg()
    for piece in board_pieces:
        piece.draw()
    pygame.display.flip()


def add_pawns(board_pieces):
    for place in range(Screen.BOARD_LINE):
        board_pieces.append(pieces.Pawn(True, place))
    for place in range(Screen.BOARD_LINE):
        board_pieces.append(pieces.Pawn(False, place))
    return board_pieces


def place_pieces():
    board_pieces = [pieces.King(False), pieces.King(True)]
    board_pieces.extend([pieces.Rook(True, Screen.squares[0][0]), pieces.Rook(False, Screen.squares[7][0]), pieces.Rook(True, Screen.squares[0][7]), pieces.Rook(False, Screen.squares[7][7])])
    board_pieces = add_pawns(board_pieces)
    return board_pieces


def listen_to_mouse(board_pieces, last_piece_clicked):
    mouse_pos = pygame.mouse.get_pos()
    if last_piece_clicked is None:
        for piece in board_pieces:
            if piece.square.rect.collidepoint(mouse_pos):
                piece.color_next_step()
                last_piece_clicked = piece
    else:
        for line in Screen.squares:
            for square in line:
                if square.rect.collidepoint(mouse_pos):
                    last_piece_clicked.move(square)

                # Reset square color to its original color(black or white).
                if square.color != square.original_color:
                    square.coloring_square_by_original_color()

        last_piece_clicked = None

    return last_piece_clicked


def game_loop(board_pieces):
    running = True
    piece_clicked = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                piece_clicked = listen_to_mouse(board_pieces, piece_clicked)

        for piece in board_pieces:
            if piece.is_eaten:
                board_pieces.remove(piece)

        redraw_game_screen(board_pieces)


def main():
    Screen.draw_screen()
    board_pieces = place_pieces()
    redraw_game_screen(board_pieces)
    game_loop(board_pieces)


if __name__ == '__main__':
    main()
