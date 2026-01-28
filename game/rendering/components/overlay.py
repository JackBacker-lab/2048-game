import pygame
from pygame.font import Font

from game.rendering.colors import (
    GAMEOVER_CARD_COLOR,
    GAMEOVER_TEXT_COLOR,
    VICTORY_CARD_COLOR,
    VICTORY_TEXT_COLOR,
)


class Overlay:
    def __init__(self, screen: pygame.Surface, font: Font, font_small: Font):
        self.screen = screen
        self.font = font
        self.font_small = font_small


    def _render(self, title: str, subtitle: str,
               card_color: pygame.Color,
               text_color: pygame.Color,
               width: int, height: int):
        """Render a semi-transparent overlay card with a title and subtitle message."""
        overlay_bg = pygame.Surface((width, height))
        overlay_bg.fill(card_color)
        overlay_bg.set_alpha(150)
        self.screen.blit(overlay_bg, (0, 0))

        card_w = int(width * 0.62)
        card_h = int(height * 0.38)
        card_x = (width - card_w) // 2
        card_y = (height - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # Shadow
        shadow = card_rect.inflate(10, 10).move(10, 10)
        shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, 20),
            shadow_surf.get_rect(),
            border_radius=28
        )
        self.screen.blit(shadow_surf, shadow)

        # Card
        pygame.draw.rect(
            self.screen,
            card_color,
            card_rect,
            border_radius=22
        )

        title_text = self.font.render(title, True, text_color)
        title_rect = title_text.get_rect(center=(width // 2,
                                                card_y + card_h * 0.38))
        self.screen.blit(title_text, title_rect)

        subtitle_text = self.font_small.render(subtitle, True, text_color)
        subtitle_rect = subtitle_text.get_rect(center=(width // 2,
                                                    card_y + card_h * 0.68))
        self.screen.blit(subtitle_text, subtitle_rect)

        pygame.display.flip()


    def render_victory(self, width: int, height: int):
        """Render the victory overlay on top of the current screen."""
        self._render(
            title="YOU WON!",
            subtitle="Press R to restart",
            card_color=VICTORY_CARD_COLOR,
            text_color=VICTORY_TEXT_COLOR,
            width=width,
            height=height
        )


    def render_game_over(self, width: int, height: int):
        """Render the game over overlay on top of the current screen."""
        self._render(
            title="GAME OVER",
            subtitle="Press R to try again",
            card_color=GAMEOVER_CARD_COLOR,
            text_color=GAMEOVER_TEXT_COLOR,
            width=width,
            height=height
        )
