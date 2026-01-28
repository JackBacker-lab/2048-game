from copy import copy
from itertools import product
from typing import Any, Literal

from game.core.game import Game
from game.rendering.animations import AnimationManager, AppearAnimation, ShiftAnimation
from game.rendering.animations.animations import MergeAnimation


class Tile:
    """Visual representation of a cell: value + position + unique ID."""
    def __init__(self, value: int, row: int, col: int, id: int, scale: float = 1.0):
        if value < 0 or row < 0 or col < 0 or id < 0 or scale < 0:
            raise ValueError("All arguments must be non-negative.")

        self.value = value
        self.row = row
        self.col = col
        self.id = id
        self.scale = scale

    def __eq__(self, other: Any):
        if not isinstance(other, Tile):
            return NotImplemented
        return (
            self.value == other.value
            and self.row == other.row
            and self.col == other.col
            and self.id == other.id
            and self.scale == other.scale
        )

    def __hash__(self):
        return hash((self.value, self.row, self.col, self.id, self.scale))


class TileManager:
    def __init__(self, game: Game, anim_manager: AnimationManager):
        self.game = game
        self.grid_size = game.size
        self.anim_manager = anim_manager

        self.tiles: list[Tile] = []

        self.next_tile_id = 0

    def new_tile_id(self) -> int:
        """Returns a new unique tile ID."""
        self.next_tile_id += 1
        return self.next_tile_id - 1


    def get_tiles_at(self, row: int, col: int) -> list[Tile]:
        """Return the Tile object located at (row, col), or None if empty."""
        return [
            tile for tile in self.tiles if tile.row == row and tile.col == col
        ]

    def append_new_tile(self, value: int, row: int, col: int):
        """Append new logical tile from game.grid to the visual state.

        Add AppearAnimation to the tile.
        """
        tile_id = self.new_tile_id()

        self.anim_manager.add(tile_id, AppearAnimation())

        tile = Tile(value, row, col, tile_id)
        self.tiles.append(tile)


    def append_new_move(
        self,
        bias_matrix: list[list[int]],
        move_type: Literal['l', 'r', 'u', 'd'],
    ) -> None:
        """Append new move and add shift animation for tiles based on bias matrix."""
        new_tiles: list[Tile] = copy(self.tiles)

        MOVE_OFFSET = {
            "l": (0, -1),
            "r": (0, 1),
            "u": (-1, 0),
            "d": (1, 0),
        }
        dr, dc = MOVE_OFFSET[move_type]

        for r, c in product(range(self.grid_size), range(self.grid_size)):
            bias = bias_matrix[r][c]
            if bias == 0:
                continue

            tiles = self.get_tiles_at(r, c)
            if not tiles:
                raise RuntimeError(
                    "Expected a tile at this position because bias > 0, \
                        but none was found."
                )
            if len(tiles) != 1:
                raise RuntimeError(
                    "Expected exactly one tile in a cell \
                        before creating a ShiftAnimation for a new move."
                )

            tile = tiles[0]

            new_r = r + dr * bias
            new_c = c + dc * bias

            anim = ShiftAnimation((r, c), (new_r, new_c))
            self.anim_manager.add(tile.id, anim)

            index = self.tiles.index(tile)
            new_tiles[index] = Tile(tile.value, new_r, new_c, tile.id)

        self.tiles = new_tiles


    def detect_merges(self):
        """Detect merged tiles in the same cell.

        Replace the tiles with a single upgraded tile.
        """
        for r, c in product(range(self.grid_size), range(self.grid_size)):
            tiles = self.get_tiles_at(r, c)
            if len(tiles) > 2:
                raise RuntimeError("A single cell cannot contain more than two tiles.")
            if len(tiles) == 2:
                if tiles[0].value != tiles[1].value:
                    raise RuntimeError(
                        "A single cell cannot contain tiles with different values."
                    )
                value = tiles[0].value
                for tile in tiles:
                    self.tiles.remove(tile)

                tile_id = self.new_tile_id()
                self.tiles.append(Tile(value * 2, r, c, tile_id))
                self.anim_manager.add(tile_id, MergeAnimation())
