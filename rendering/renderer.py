import pygame
from core.game import Game
from rendering.constants import *
from rendering.colors import BG_COLOR
from rendering.tiles import TileManager
from rendering.ui import UI
from rendering.tile_renderer import TileRenderer
from rendering.overlay import Overlay
from rendering.animation_manager import AnimationManager


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
        
        self.anim_manager = AnimationManager()
        self.tile_manager = TileManager(self.game, self.anim_manager)
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        self.prev_grid = [[cell for cell in row] for row in self.game.grid]
        
        self.FONT_BIG = pygame.font.SysFont(FONT_TITLE, FONT_BIG_SIZE)
        self.FONT = pygame.font.SysFont(FONT_TITLE, FONT_SIZE)
        self.FONT_SMALL = pygame.font.SysFont(FONT_TITLE, FONT_SMALL_SIZE)
        
        self.user_interface = UI(self.screen, self.game, self.FONT_SMALL)
        self.tile_renderer = TileRenderer(self.screen, self.anim_manager, self.tile_manager, self.FONT)
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