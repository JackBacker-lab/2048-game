import pygame

# Window dimensions
SIZE_BLOCK = 110
MARGIN = 10

def get_width(size: int = 4):
    return size * SIZE_BLOCK + (size + 1) * MARGIN

def get_height(WIDTH: int):
    return WIDTH + PLACE_FOR_TR

PLACE_FOR_TR = 110
FONT_SIZE = 48

# Colors
BLACK = pygame.Color(0, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
BG_COLOR = pygame.Color(71, 74, 67)

colors = {
    0: pygame.Color("grey"),
    2: pygame.Color("#ffff96"),
    4: pygame.Color("#ffff64"),
    8: pygame.Color("#ffff00"),
    16: pygame.Color("#ffc800"),
    32: pygame.Color("#ff9500"),
    64: pygame.Color("#ff6600"),
    128: pygame.Color("#ff3300"),
    256: pygame.Color("#ff0000"),
    512: pygame.Color("#00ffff"),
    1024: pygame.Color("#0000ff"),
    2048: pygame.Color("#9500ff"),
}