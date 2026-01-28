import pygame

from game.core.game import Game
from game.rendering.animations import AnimationManager
from game.rendering.colors import BG_COLOR
from game.rendering.components.overlay import Overlay
from game.rendering.components.ui import UI
from game.rendering.constants import (
    FONT_BIG_SIZE,
    FONT_SIZE,
    FONT_SMALL_SIZE,
    FONT_TITLE,
    get_height,
    get_width,
)
from game.rendering.tiles import TileManager, TileRenderer


class Renderer:
    """
    Renders the game board and manages tile animations.
    Does not modify the game logic or the game grid.
    """

    def __init__(self, game: Game):
        self.game = game
        self.grid_size = game.size

        self.current_time = 0

        self.WIDTH = get_width(self.grid_size)
        self.HEIGHT = get_height(self.WIDTH)

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.FONT_BIG = pygame.font.SysFont(FONT_TITLE, FONT_BIG_SIZE)
        self.FONT = pygame.font.SysFont(FONT_TITLE, FONT_SIZE)
        self.FONT_SMALL = pygame.font.SysFont(FONT_TITLE, FONT_SMALL_SIZE)

        self.anim_manager = AnimationManager()
        self.tile_manager = TileManager(self.game, self.anim_manager)
        self.user_interface = UI(self.screen, self.game, self.FONT_SMALL)
        self.tile_renderer = TileRenderer(
            self.screen,
            self.anim_manager,
            self.tile_manager,
            self.FONT
        )
        self.overlay = Overlay(self.screen, self.FONT, self.FONT_SMALL)


    def render(self, dt_ms: int):
        """
        Renders a single frame.
        Updates animation time, draws header, grid and tiles.
        """
        self.current_time += dt_ms

        self.screen.fill(BG_COLOR)

        self.user_interface.render(self.WIDTH, self.HEIGHT)
        self.tile_renderer.render_tiles(self.current_time)

        pygame.display.flip()
