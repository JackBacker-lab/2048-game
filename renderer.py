import pygame
from game import Game
from constants import *

class Renderer:
    """
    Responsible only for drawing the current game state.
    Does not contain game logic.
    """

    def __init__(self, game: Game):
        self.game = game
        self.size = game.size
        
        self.WIDTH = get_width(self.size)
        self.HEIGHT = get_height(self.WIDTH)

        pygame.init()
        self.FONT = pygame.font.SysFont('comicsansms', FONT_SIZE)
        self.TITLE_RECT = pygame.Rect(0, 0, self.WIDTH, PLACE_FOR_TR)

    def create_window(self):
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        return screen

    def render(self, screen):
        screen.fill(BG_COLOR)

        self._draw_header(screen)
        self._draw_grid(screen)
        self._draw_cells(screen)

        pygame.display.flip()
        
    # ----------------------------------------------------------
    # Geometry helpers
    # ----------------------------------------------------------
    def get_cell_rect(self, x, y):
        rect_x = MARGIN + (MARGIN + SIZE_BLOCK) * x
        rect_y = MARGIN + PLACE_FOR_TR + (MARGIN + SIZE_BLOCK) * y
        return pygame.Rect(rect_x, rect_y, SIZE_BLOCK, SIZE_BLOCK)

    # ----------------------------------------------------------
    # Internal rendering components
    # ----------------------------------------------------------
    def _draw_header(self, screen):
        pygame.draw.rect(screen, GREEN, self.TITLE_RECT, 0)
        score = self.game.get_score()
        score_text = self.FONT.render(f"Score: {score}", True, BLUE)
        screen.blit(score_text, (20, 20))

    def _draw_grid(self, screen):
        for i in range(self.size + 1):
            # Vertical
            start_x = MARGIN / 2 + (SIZE_BLOCK + MARGIN) * i
            pygame.draw.line(
                screen, BLACK,
                (start_x, PLACE_FOR_TR),
                (start_x, self.HEIGHT),
                MARGIN
            )
            # Horizontal
            start_y = MARGIN / 2 + PLACE_FOR_TR + (SIZE_BLOCK + MARGIN) * i
            pygame.draw.line(
                screen, BLACK,
                (0, start_y),
                (self.WIDTH, start_y),
                MARGIN
            )

    def _draw_cells(self, screen):
        grid = self.game.grid
        for y in range(self.size):
            for x in range(self.size):
                value = grid[y][x]
                rect = self.get_cell_rect(x, y)
                pygame.draw.rect(screen, colors[value], rect)

                if value != 0:
                    text = self.FONT.render(str(value), True, BLACK)
                    screen.blit(text, text.get_rect(center=rect.center))

    # ----------------------------------------------------------
    # Game Over and Victory screen
    # ----------------------------------------------------------
    def render_game_over(self, screen):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        msg = self.FONT.render("GAME OVER", True, pygame.Color("white"))
        rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        screen.blit(msg, rect)

        pygame.display.flip()
        
    def render_victory(self, screen):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        msg = self.FONT.render("You won!", True, pygame.Color("white"))
        rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        screen.blit(msg, rect)

        pygame.display.flip()