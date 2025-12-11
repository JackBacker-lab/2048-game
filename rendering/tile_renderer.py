import pygame
from rendering.constants import *
from rendering.colors import *
from rendering.animations import ShiftAnimation, MergeAnimation, AppearAnimation

class TileRenderer:
    def __init__(self, screen, anim_manager, tile_manager, font):
        self.screen = screen
        self.anim_manager = anim_manager
        self.tile_manager = tile_manager
        self.font = font
        self.waiting_for_sync = False
    

    def render_tiles(self, now):
        """
        Draw all tiles with active animations in the correct order:
        1. Shift animations
        2. Merge animations
        3. Appear animations

        Synchronize tile states with game.grid only after all animations finish.
        """
        shift_tiles = []
        merge_tiles = []
        appear_tiles = []
        idle_tiles = []

        for tile in self.tile_manager.tiles:
            anim = self.anim_manager.get(tile.id)
            if isinstance(anim, ShiftAnimation):
                shift_tiles.append((tile, anim))
            elif isinstance(anim, MergeAnimation):
                merge_tiles.append((tile, anim))
            elif isinstance(anim, AppearAnimation):
                appear_tiles.append((tile, anim))
            else:
                idle_tiles.append((tile, None))

        for tile, anim in shift_tiles + merge_tiles + appear_tiles + idle_tiles:
            self._render_tile(tile, now, anim)

        self.anim_manager.cleanup(now)

        if self.anim_manager.has_shift_animations():
            self.waiting_for_sync = True
            return

        if self.waiting_for_sync and self.tile_manager.pending_merges:
            for (tile_id,) in self.tile_manager.pending_merges:
                anim = MergeAnimation(tile_id)
                self.anim_manager.add(tile_id, anim, now)
            self.tile_manager.pending_merges.clear()
            return

        if self.waiting_for_sync and not self.tile_manager.pending_merges and self.tile_manager.pending_appears:
            for (r, c) in self.tile_manager.pending_appears:
                tile = self.tile_manager.get_tile_at(r, c)
                if tile:
                    anim = AppearAnimation((r, c))
                    self.anim_manager.add(tile.id, anim, now)
            self.tile_manager.pending_appears.clear()
            return

        if self.waiting_for_sync and not self.anim_manager.has_any():
            self.waiting_for_sync = False
            self.tile_manager._sync_tiles_with_game_grid(now)
    
    
    def _render_tile(self, tile, now, anim=None):
        if anim is not None:
            pos = anim.get_position(now) or (tile.row, tile.col)
            scale = anim.get_scale(now)
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
    def _get_cell_rect(x, y, scale):
        base_x = MARGIN + (MARGIN + SIZE_BLOCK) * x
        base_y = MARGIN + TOP_PANEL_HEIGHT + (MARGIN + SIZE_BLOCK) * y
        size = SIZE_BLOCK * scale
        offset = (SIZE_BLOCK - size) / 2
        return pygame.Rect(base_x + offset, base_y + offset, size, size)
