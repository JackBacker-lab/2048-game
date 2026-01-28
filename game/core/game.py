import copy
import itertools
import random

from game.core.types import MoveLiteral


class Game:
    """
    Encapsulates only the core 2048 game logic.
    Stores and updates the numerical game grid (list[list[int]]).
    """
    def __init__(self, size: int = 4):
        """
        :param size: Grid dimension (size x size)
        """
        self.size = size
        self.grid: list[list[int]] = [[0] * size for _ in range(size)]

    def insert_new_tile(self) -> tuple[int, int, int]:
        """Create new tile (2 or 4) in random empty cell.

        Return the value and coordinates of the inserted tile as (value, row, col).
        """
        empty_cells = [
            (i, j)
            for i in range(self.size)
            for j in range(self.size)
            if self.grid[i][j] == 0
        ]
        y, x = random.choice(empty_cells)
        self.grid[y][x] = 2 if random.random() < 0.9 else 4
        return (self.grid[y][x], y, x)

    def can_move(self) -> bool:
        """Return True if at least one move is possible.

        A move is possible if there is an empty cell
        or two adjacent tiles with the same value.
        """
        for r, c in itertools.product(range(self.size), range(self.size)):
            value = self.grid[r][c]
            if value == 0:
                return True
            if c + 1 < self.size and value == self.grid[r][c + 1]:
                return True
            if r + 1 < self.size and value == self.grid[r + 1][c]:
                return True

        return False

    def check_victory(self) -> bool:
        """Return True if the victory condition is reached.

        Victory is achieved when at least one tile with value 2048 exists in the grid.
        """
        return any(2048 in row for row in self.grid)

    def get_score(self) -> int:
        """Return the current game score.

        The score is defined as the maximum tile value currently present on the grid.
        """
        return max(max(row) for row in self.grid)


    def move_left(self) -> tuple[bool, list[list[int]], MoveLiteral]:
        """Shift tiles to the left.

        Return changed, bias_matrix and move type.
        """
        old = copy.deepcopy(self.grid)
        bias_matrix = self._shift_left()
        changed = old != self.grid
        return changed, bias_matrix, "l"


    def move_right(self) -> tuple[bool, list[list[int]], MoveLiteral]:
        """Shift tiles to the right.

        Return changed, bias_matrix and move type.
        """
        old = copy.deepcopy(self.grid)

        self.grid = [row[::-1] for row in self.grid]
        bias_matrix = self._shift_left()
        self.grid = [row[::-1] for row in self.grid]
        bias_matrix = [row[::-1] for row in bias_matrix]

        changed = old != self.grid
        return changed, bias_matrix, "r"


    def move_up(self) -> tuple[bool, list[list[int]], MoveLiteral]:
        """Shift tiles upward.

        Return changed, bias_matrix and move type.
        """
        old = copy.deepcopy(self.grid)

        self.grid = self._rotate_ccw(self.grid)
        bias_matrix = self._shift_left()
        self.grid = self._rotate_cw(self.grid)
        bias_matrix = self._rotate_cw(bias_matrix)

        changed = old != self.grid
        return changed, bias_matrix, "u"


    def move_down(self) -> tuple[bool, list[list[int]], MoveLiteral]:
        """Shift tiles downward.

        Return changed, bias_matrix and move type.
        """
        old = copy.deepcopy(self.grid)

        self.grid = self._rotate_cw(self.grid)
        bias_matrix = self._shift_left()
        self.grid = self._rotate_ccw(self.grid)
        bias_matrix = self._rotate_ccw(bias_matrix)

        changed = old != self.grid
        return changed, bias_matrix, "d"


    @staticmethod
    def _rotate_ccw(matrix: list[list[int]]):
        """Rotate matrix 90° CCW."""
        return [list(row) for row in zip(*matrix, strict=True)][::-1]


    @staticmethod
    def _rotate_cw(matrix: list[list[int]]):
        """Rotate matrix 90° CW."""
        return [list(row)[::-1] for row in zip(*matrix, strict=True)]


    def _shift_left(self) -> list[list[int]]:
        """Shift all tiles to the left with merge logic.

        Retrieve and return bias matrix.
        """
        new_grid: list[list[int]] = []

        for row in self.grid:
            # Extract non-zero tiles with original indices
            tiles: list[tuple[int, int]] = [
                (idx, row[idx]) for idx in range(self.size) if row[idx] != 0
            ]

            # Merge tile values
            compressed = [v for _, v in tiles]
            new_row: list[int] = []
            i = 0
            while i < len(compressed):
                if i < len(compressed) - 1 and compressed[i] == compressed[i + 1]:
                    new_row.append(compressed[i] * 2)
                    i += 2
                else:
                    new_row.append(compressed[i])
                    i += 1

            # Fill remaining cells with zeros
            new_row += [0] * (self.size - len(new_row))
            new_grid.append(new_row)


        bias_matrix = self._get_bias_matrix()
        self.grid = new_grid

        return bias_matrix


    def _build_merge_groups(self, tiles: list[tuple[int, int]]
    ) -> list[list[tuple[int, int]] | tuple[int, int]]:
        """Build merge groups for a single row of tiles.

        Each group is either a single tile (tuple)
        or a pair of tiles to be merged (list of two tuples).

        Example:
            [(0, 2), (1, 2), (2, 4)] -> [[(0, 2), (1, 2)], (2, 4)]
        """
        merge_groups: list[list[tuple[int, int]] | tuple[int, int]] = []
        i = 0
        while i < len(tiles):
            if i < len(tiles) - 1 and tiles[i][1] == tiles[i + 1][1]:
                merge_groups.append([tiles[i], tiles[i + 1]])
                i += 2
            else:
                merge_groups.append(tiles[i])
                i += 1

        return merge_groups


    def _get_bias_matrix(self) -> list[list[int]]:
        """Compute the bias matrix for the current grid state.

        The bias matrix stores how many cells each tile moves during a left shift.
        """
        bias_matrix: list[list[int]] = []
        for row in self.grid:
            # Extract non-zero tiles with original indices
            tiles: list[tuple[int, int]] = [
                (idx, row[idx]) for idx in range(self.size) if row[idx] != 0
            ]

            merge_groups = self._build_merge_groups(tiles)

            # Compute displacement for each original index
            bias_row = [0] * self.size
            for new_col, group in enumerate(merge_groups):
                if isinstance(group, tuple):
                    old_col = group[0]
                    bias_row[old_col] = old_col - new_col
                else:
                    for old_col, _ in group:
                        bias_row[old_col] = old_col - new_col

            bias_matrix.append(bias_row)

        return bias_matrix
