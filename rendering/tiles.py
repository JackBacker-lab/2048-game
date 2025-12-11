from rendering.animations import AppearAnimation, ShiftAnimation

class Tile:
    """Visual representation of a cell: value + position + unique ID."""   
    def __init__(self, value, row, col, id):
        self.value = value
        self.row = row
        self.col = col
        self.id = id


class TileManager:
    def __init__(self, game, anim_manager):
        self.game = game
        self.grid_size = game.size
        self.anim_manager = anim_manager
        self.tiles = []
        self.tile_ids = [[0]*self.grid_size for _ in range(self.grid_size)]
        self.next_tile_id = 1
        self.pending_merges = []
        self.pending_appears = []

    def _new_tile_id(self):
        """Returns a new unique tile ID."""
        self.next_tile_id += 1
        return self.next_tile_id - 1
    
    def get_tile_at(self, row: int, col: int):
        """Return the Tile object located at (row, col), or None if empty."""
        for tile in self.tiles:
            if tile.row == row and tile.col == col:
                return tile
        return None
    
    def append_new_tile(self, value, row, col, is_first: bool = False):
        """
        Adds a new tile created by the game logic (e.g. after a move)
        """
        tile_id = self._new_tile_id()
        self.tile_ids[row][col] = tile_id
        
        if is_first:
            tile = Tile(value, row, col, tile_id) 
            self.tiles.append(tile)

        self.pending_appears.append((row, col))

        
    def append_new_move(self, bias_matrix, move_type, prev_grid, now):
        """
        Initializes tiles for the new move:
        - builds tiles from the previous grid
        - applies shift animations according to bias_matrix
        - prepares updated tile ID mapping
        """
        self.prev_grid = prev_grid
        self.tiles = []
        new_tile_ids = [[0]*self.grid_size for _ in range(self.grid_size)]
        
        DIR_OFFSET = {
            "l": (0, -1),
            "r": (0, 1),
            "u": (-1, 0),
            "d": (1, 0),
        }

        for y in range(self.grid_size):
            for x in range(self.grid_size):
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
                self.anim_manager.add(tile_id, anim, now)
                
        self.tile_ids = new_tile_ids
        
        
    def append_merge_animation(self, merge_matrix):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if merge_matrix[r][c] == 1:
                    tile = self.get_tile_at(r, c)
                    if tile:
                        self.pending_merges.append((tile.id,))
    

    def _sync_tiles_with_game_grid(self, now):
        """
        Reconstructs tile list based on game.grid after all shift animations end.
        Ensures a consistent one-tile-per-cell mapping.
        Adds appear animation for newly created tiles.
        """
        self.tile_ids = [[0]*self.grid_size for _ in range(self.grid_size)]
        new_tiles = []

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                val = self.game.grid[r][c]
                if val == 0:
                    continue

                tile = next((t for t in self.tiles if t.row == r and t.col == c), None)

                if tile:
                    tile.value = val
                else:
                    tile = Tile(val, r, c, self._new_tile_id())
                    self.anim_manager.add(tile.id, AppearAnimation((r, c)), now)

                new_tiles.append(tile)
                self.tile_ids[r][c] = tile.id

        self.tiles = new_tiles
