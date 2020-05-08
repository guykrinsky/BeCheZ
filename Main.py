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

def main():
    running = True
    Screen.draw_screen()
    board_pieces = [pieces.King(False), pieces.King(True)]
    redraw_game_screen(board_pieces)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for char in board_pieces:
                    if char.square.rect.collidepoint(mouse_pos):
                        char.square.coloring_square_by_original_color()
                        char.get_valid_move_squares()
                        redraw_game_screen(board_pieces)
                redraw_game_screen(board_pieces)


if __name__ == '__main__':
    main()