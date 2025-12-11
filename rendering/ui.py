import pygame
from rendering.colors import *
from rendering.constants import *

class UI:
    def __init__(self, screen, game, font_small):
        self.screen = screen
        self.game = game
        self.font_small = font_small
        self.newgame_rect = pygame.Rect(PANEL_PADDING, PANEL_PADDING_TOP, BOX_WIDTH, int(TOP_PANEL_HEIGHT * 0.35))

    def render(self, width, height):
        pygame.draw.rect(
            self.screen,
            PANEL_BG,
            pygame.Rect(0 + MARGIN / 2, 0 + MARGIN / 2, width - MARGIN, TOP_PANEL_HEIGHT - MARGIN),
            border_radius=BORDER_RADIUS
        )

        score_rect = pygame.Rect(
            width - BOX_WIDTH - PANEL_PADDING,
            PANEL_PADDING_TOP * 0.8,
            BOX_WIDTH,
            BOX_HEIGHT
        )

        pygame.draw.rect(
            self.screen,
            SCORE_BG,
            score_rect,
            border_radius=BORDER_RADIUS
        )

        score = self.game.get_score()
        score_title = self.font_small.render("SCORE", True, SCORE_TEXT_COLOR)
        score_value = self.font_small.render(str(score), True, SCORE_TEXT_COLOR)

        self.screen.blit(score_title, score_title.get_rect(center=(score_rect.centerx, score_rect.y + 15)))
        self.screen.blit(score_value, score_value.get_rect(center=(score_rect.centerx, score_rect.y + 42)))

        best_rect = pygame.Rect(
            width - 2 * BOX_WIDTH - 2 * PANEL_PADDING,
            PANEL_PADDING_TOP * 0.8,
            BOX_WIDTH,
            BOX_HEIGHT
        )

        pygame.draw.rect(
            self.screen,
            SCORE_BG,
            best_rect,
            border_radius=BORDER_RADIUS
        )

        best_title = self.font_small.render("BEST", True, SCORE_TEXT_COLOR)
        best_value = self.font_small.render(str(score), True, SCORE_TEXT_COLOR)

        self.screen.blit(best_title, best_title.get_rect(center=(best_rect.centerx, best_rect.y + 15)))
        self.screen.blit(best_value, best_value.get_rect(center=(best_rect.centerx, best_rect.y + 42)))
        
        self._render_newgame_button(width)
        self._render_grid_background(width, height)

    def _render_newgame_button(self, width):
        button_width = int(width * 0.3)
        button_height = int(TOP_PANEL_HEIGHT * 0.35)

        x = PANEL_PADDING
        y = PANEL_PADDING_TOP

        self.newgame_rect = pygame.Rect(x, y, button_width, button_height)

        mouse = pygame.mouse.get_pos()
        hover = self.newgame_rect.collidepoint(mouse)
        bg = NEWGAME_BG_HOVER if hover else NEWGAME_BG

        shadow_rect = self.newgame_rect.move(3, 3)
        pygame.draw.rect(self.screen, SCORE_SHADOW, shadow_rect, border_radius=10)

        pygame.draw.rect(self.screen, bg, self.newgame_rect, border_radius=10)

        text = self.font_small.render("NEW GAME", True, NEWGAME_TEXT)
        self.screen.blit(text, text.get_rect(center=self.newgame_rect.center))
        
    
    def _render_grid_background(self, width, height):
        pygame.draw.rect(
            self.screen,
            GRID_BG_COLOR,
            pygame.Rect(
                MARGIN / 2,
                TOP_PANEL_HEIGHT + MARGIN / 2,
                width - MARGIN,
                height - TOP_PANEL_HEIGHT - MARGIN
            ),
            border_radius=BORDER_RADIUS
        )