import pygame
import colors

screen = pygame.display.set_mode((480, 480))
squares = []


class Square:
    WIDTH = 60
    HEIGHT = 60

    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.color = color
        self.orginal_color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

    def coloring_square_by_original_color(self):
        if self.color == self.orginal_color:
            if self.orginal_color == colors.BLACK:
                self.color = colors.DARK_RED
            else:
                self.color = colors.LIGHT_RED
        else:
            self.color = self.orginal_color


def draw_bg():
    for line in squares:
        for square in line:
            square.draw()


def draw_screen():
    x = 0
    y = 0
    for line in range(8):
        tmp = line % 2
        square_in_line = []
        for tur in range(8):
            if tur % 2 == tmp:
                color = colors.WHITE
            else:
                color = colors.BLACK

            square_in_line.append(Square(x, y, color))
            x += Square.WIDTH
        x = 0
        y += Square.HEIGHT
        squares.append(square_in_line)
    draw_bg()
    pygame.display.flip()
