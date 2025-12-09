import pygame
from game import Game
from constants import *
from animation_manager import AnimationManager
from animations import AppearAnimation, ShiftAnimation


class Tile:
    """Visual representation of a cell: value + position + unique ID."""   
    def __init__(self, value, row, col, id):
        self.value = value
        self.row = row
        self.col = col
        self.id = id


class Renderer:
    """
    Renders the game board and manages tile animations.
    Does not modify the game logic or the game grid.
    """

    def __init__(self, game: Game):
        self.game = game
        self.size = game.size
        
        self.current_time = 0
        
        self.WIDTH = get_width(self.size)
        self.HEIGHT = get_height(self.WIDTH)
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        self.FONT = pygame.font.SysFont('comicsansms', FONT_SIZE)
        self.TITLE_RECT = pygame.Rect(0, 0, self.WIDTH, PLACE_FOR_TR)
        
        self.prev_grid = [[cell for cell in row] for row in self.game.grid]
        
        self.anim_manager = AnimationManager()
        
        self.tiles: list[Tile] = []
        self.tile_ids = [[0]*self.size for _ in range(self.size)]
        self.next_tile_id = 1
        
        
    def render(self, dt_ms: int):
        """
        Renders a single frame.
        Updates animation time, draws header, grid and tiles.
        """
        self.current_time += dt_ms
        
        self.screen.fill(BG_COLOR)

        self._draw_header()
        self._draw_grid()
        self._draw_cells()

        pygame.display.flip()
        
    
    def _new_tile_id(self):
        """Returns a new unique tile ID."""
        self.next_tile_id += 1
        return self.next_tile_id - 1

        
    def append_new_tile(self, value, row, col):
        """
        Adds a new tile created by the game logic (e.g. after a move),
        attaches appear animation.
        """
        tile_id = self._new_tile_id()
        self.tile_ids[row][col] = tile_id

        tile = Tile(value, row, col, tile_id)
        self.tiles.append(tile)

        self.anim_manager.add(tile_id, AppearAnimation((row, col)), self.current_time)

        
    def append_new_move(self, bias_matrix, move_type, prev_grid):
        """
        Initializes tiles for the new move:
        - builds tiles from the previous grid
        - applies shift animations according to bias_matrix
        - prepares updated tile ID mapping
        """
        self.prev_grid = prev_grid
        self.tiles = []
        new_tile_ids = [[0]*self.size for _ in range(self.size)]
        
        DIR_OFFSET = {
            "l": (0, -1),
            "r": (0, 1),
            "u": (-1, 0),
            "d": (1, 0),
        }

        for y in range(self.size):
            for x in range(self.size):
                val = prev_grid[y][x]
                if val == 0:
                    continue

                bias = bias_matrix[y][x]
                if bias == 0:
                    tile_id = self.tile_ids[y][x]
                    self.tiles.append(Tile(val, y, x, tile_id))
                    continue

                dy, dx = DIR_OFFSET[move_type]
                new_y = y + dy * bias
                new_x = x + dx * bias

                tile_id = self.tile_ids[y][x]
                new_tile_ids[new_y][new_x] = tile_id
                
                tile = Tile(val, new_y, new_x, tile_id)
                self.tiles.append(tile)

                anim = ShiftAnimation((y, x), (new_y, new_x))
                self.anim_manager.add(tile_id, anim, self.current_time)
                
        self.tile_ids = new_tile_ids
        
    # ----------------------------------------------------------
    # Geometry helpers
    # ----------------------------------------------------------
    def _get_cell_rect(self, x, y, scale):
        base_x = MARGIN + (MARGIN + SIZE_BLOCK) * x
        base_y = MARGIN + PLACE_FOR_TR + (MARGIN + SIZE_BLOCK) * y

        size = SIZE_BLOCK * scale
        offset = (SIZE_BLOCK - size) / 2

        rect_x = base_x + offset
        rect_y = base_y + offset

        return pygame.Rect(rect_x, rect_y, size, size)


    # ----------------------------------------------------------
    # Internal rendering components
    # ----------------------------------------------------------
    def _draw_header(self):
        pygame.draw.rect(self.screen, GREEN, self.TITLE_RECT, 0)
        score = self.game.get_score()
        score_text = self.FONT.render(f"Score: {score}", True, BLUE)
        self.screen.blit(score_text, (20, 20))

    def _draw_grid(self):
        for i in range(self.size + 1):
            start_x = MARGIN / 2 + (SIZE_BLOCK + MARGIN) * i
            pygame.draw.line(
                self.screen, BLACK,
                (start_x, PLACE_FOR_TR),
                (start_x, self.HEIGHT),
                MARGIN
            )
            start_y = MARGIN / 2 + PLACE_FOR_TR + (SIZE_BLOCK + MARGIN) * i
            pygame.draw.line(
                self.screen, BLACK,
                (0, start_y),
                (self.WIDTH, start_y),
                MARGIN
            )

    def _draw_cells(self):
        """
        Draws all tiles with active animations.
        When shift animations finish, synchronizes tile states with game.grid.
        """
        for tile in self.tiles:
            anim = self.anim_manager.get(tile.id)
            if anim:
                if isinstance(anim, ShiftAnimation):
                    pos = anim.interpolate(self.current_time)
                    scale = 1.0
                elif isinstance(anim, AppearAnimation):
                    pos = (tile.row, tile.col)
                    scale = anim.scale(self.current_time)
                else:
                    pos = (tile.row, tile.col)
                    scale = 1.0
            else:
                pos = (tile.row, tile.col)
                scale = 1.0

            rect = self._get_cell_rect(pos[1], pos[0], scale)
            pygame.draw.rect(self.screen, colors[tile.value], rect)
            text = self.FONT.render(str(tile.value), True, BLACK)
            self.screen.blit(text, text.get_rect(center=rect.center))

        self.anim_manager.cleanup(self.current_time)

        if not self.anim_manager.has_shift_animations():
            self._sync_tiles_with_game_grid()


    def _sync_tiles_with_game_grid(self):
        """
        Reconstructs tile list based on game.grid after all shift animations end.
        Ensures a consistent one-tile-per-cell mapping.
        Adds appear animation for newly created tiles.
        """
        self.tile_ids = [[0]*self.size for _ in range(self.size)]
        new_tiles = []

        for r in range(self.size):
            for c in range(self.size):
                val = self.game.grid[r][c]
                if val == 0:
                    continue

                tile = next((t for t in self.tiles if t.row == r and t.col == c), None)

                if tile:
                    tile.value = val
                else:
                    tile = Tile(val, r, c, self._new_tile_id())
                    self.anim_manager.add(tile.id, AppearAnimation((r, c)), self.current_time)

                new_tiles.append(tile)
                self.tile_ids[r][c] = tile.id

        self.tiles = new_tiles
        

    # ----------------------------------------------------------
    # Game Over and Victory screen
    # ----------------------------------------------------------
    def render_game_over(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        msg = self.FONT.render("GAME OVER", True, pygame.Color("white"))
        rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(msg, rect)

        pygame.display.flip()
        
    def render_victory(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        msg = self.FONT.render("You won!", True, pygame.Color("white"))
        rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(msg, rect)

        pygame.display.flip()