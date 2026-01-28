import pygame
from pygame.font import Font

from game.core.game import Game
from game.rendering.colors import (
    GRID_BG_COLOR,
    NEWGAME_BG,
    NEWGAME_BG_HOVER,
    NEWGAME_TEXT,
    PANEL_BG,
    SCORE_BG,
    SCORE_SHADOW,
    SCORE_TEXT_COLOR,
)
from game.rendering.constants import (
    BORDER_RADIUS,
    BOX_HEIGHT,
    BOX_WIDTH,
    MARGIN,
    PANEL_PADDING,
    PANEL_PADDING_TOP,
    TOP_PANEL_HEIGHT,
)


class UI:
    def __init__(self, screen: pygame.Surface, game: Game, font_small: Font):
        self.screen = screen
        self.game = game
        self.font_small = font_small
        self.newgame_rect = pygame.Rect(
            PANEL_PADDING,
            PANEL_PADDING_TOP,
            BOX_WIDTH,
            TOP_PANEL_HEIGHT * 0.35
        )

    def render(self, width: int, height: int):
        self._render_background(width)

        score = self.game.get_score()
        score_rect = pygame.Rect(
            width - (BOX_WIDTH + PANEL_PADDING),
            PANEL_PADDING_TOP,
            BOX_WIDTH,
            BOX_HEIGHT
        )

        self._render_score_button("SCORE", score, score_rect)

        best_score_rect = pygame.Rect(
            width - 2 * (BOX_WIDTH + PANEL_PADDING),
            PANEL_PADDING_TOP,
            BOX_WIDTH,
            BOX_HEIGHT
        )

        self._render_score_button("BEST", score, best_score_rect)

        self._render_newgame_button(width)
        self._render_grid_background(width, height)

    def _render_score_button(self, title_text: str, score: int, rect: pygame.Rect):
        pygame.draw.rect(
            self.screen,
            SCORE_BG,
            rect,
            border_radius=BORDER_RADIUS
        )

        score_title = self.font_small.render(title_text, True, SCORE_TEXT_COLOR)
        score_value = self.font_small.render(str(score), True, SCORE_TEXT_COLOR)

        self.screen.blit(
            score_title, score_title.get_rect(center=(rect.centerx, rect.y + 15))
        )
        self.screen.blit(
            score_value, score_value.get_rect(center=(rect.centerx, rect.y + 42))
        )

    def _render_newgame_button(self, width: int):
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


    def _render_background(self, width: int):
        pygame.draw.rect(
            self.screen,
            PANEL_BG,
            pygame.Rect(
                0 + MARGIN / 2,
                0 + MARGIN / 2,
                width - MARGIN,
                TOP_PANEL_HEIGHT - MARGIN
            ),
            border_radius=BORDER_RADIUS
        )

    def _render_grid_background(self, width: int, height: int):
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
