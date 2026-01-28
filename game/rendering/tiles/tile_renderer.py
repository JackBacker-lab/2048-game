import pygame
from pygame.font import Font

from game.rendering import (
    Animation,
    AnimationManager,
)
from game.rendering.colors import (
    TEXT_COLOR_DARK,
    TEXT_COLOR_LIGHT,
    TILE_SHADOW_COLOR,
    colors,
)
from game.rendering.constants import (
    MARGIN,
    SIZE_BLOCK,
    TOP_PANEL_HEIGHT,
)
from game.rendering.tiles.tiles import Tile, TileManager


class TileRenderer:
    def __init__(
            self,
            screen: pygame.Surface,
            anim_manager: AnimationManager,
            tile_manager: TileManager,
            font: Font
        ):
        self.screen = screen
        self.anim_manager = anim_manager
        self.tile_manager = tile_manager
        self.font = font
        self.waiting_for_sync = False


    def render_tiles(self, now: int):
        """Render all tiles on the screen, applying any active animations.

        This method draws each tile with its current animation state, removes finished
        animations, and triggers merge detection once all shift animations are done.
        """
        for tile in self.tile_manager.tiles:
            anim = self.anim_manager.get_next(tile.id)
            self._render_tile(tile, now, anim)

        self.anim_manager.cleanup(now)

        if self.anim_manager.has_shift_animations():
            self.waiting_for_sync = True
            return

        if self.waiting_for_sync:
            self.waiting_for_sync = False
            self.tile_manager.detect_merges()


    def _render_tile(self, tile: Tile, now: int, anim: Animation | None = None):
        """Render a single tile with optional animation effects.

        This method calculates the tile's on-screen rectangle,
        draws its background and shadow, using the appropriate animation state
        if provided, and renders the numeric value.
        """
        if anim is not None:
            pos = anim.get_position(now) or (tile.row, tile.col)
            scale = anim.get_scale(now)
            if scale == 0:
                return
        else:
            pos = (tile.row, tile.col)
            scale = 1.0

        rect = self._get_cell_rect(pos[1], pos[0], scale)

        shadow_offset = 5
        shadow_rect = rect.move(shadow_offset, shadow_offset)
        pygame.draw.rect(
            self.screen,
            TILE_SHADOW_COLOR,
            shadow_rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            colors[tile.value],
            rect,
            border_radius=8
        )

        text_color = TEXT_COLOR_DARK if tile.value <= 4 else TEXT_COLOR_LIGHT
        text = self.font.render(str(tile.value), True, text_color)
        self.screen.blit(text, text.get_rect(center=rect.center))


    @staticmethod
    def _get_cell_rect(x: float, y: float, scale: float):
        """Calculate the rectangle for a tile cell on the screen."""
        base_x = MARGIN + (MARGIN + SIZE_BLOCK) * x
        base_y = MARGIN + TOP_PANEL_HEIGHT + (MARGIN + SIZE_BLOCK) * y
        size = SIZE_BLOCK * scale
        offset = (SIZE_BLOCK - size) / 2
        return pygame.Rect(base_x + offset, base_y + offset, size, size)
