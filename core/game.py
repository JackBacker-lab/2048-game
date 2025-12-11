import random
import copy
from typing import List


class Game:
    """
    Encapsulates only the core 2048 game logic.
    Stores and updates the numerical game grid (List[List[int]]).
    """
    
    def __init__(self, size: int = 4):
        """
        :param size: Grid dimension (size x size)
        """
        self.size = size
        self.grid: List[List[int]] = [[0] * size for _ in range(size)]
        self.running = True
        self.should_stop = False

    def insert_new_tile(self) -> tuple[int, int, int]:
        """
        Creates new tile (2 or 4) in random empty cell.
        Returns tuple: (value, row, col)
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
        """True if at least one move is possible."""
        
        # Adjacent equal tiles horizontally or vertically
        for r in range(self.size):
            for c in range(self.size):
                value = self.grid[r][c]
                if value == 0:    # Empty space → move possible
                    return True
                if c + 1 < self.size and value == self.grid[r][c + 1]:
                    return True
                if r + 1 < self.size and value == self.grid[r + 1][c]:
                    return True

        return False

    def check_victory(self) -> bool:
        """True if 2048 tile exists."""
        return any(2048 in row for row in self.grid)

    def get_score(self) -> int:
        """Maximum tile."""
        return max(max(row) for row in self.grid)

    # ---------------------------------------------------------
    # Core mechanics
    # ---------------------------------------------------------

    def _shift_left(self):
        """
        Shift all tiles to the left with merge logic and compute
        the bias (displacement) matrix for animation purposes.

        Returns:
            List[List[int]]: bias matrix,
            List[List[int]]: merge matrix.
        """
        new_grid = []
        bias_matrix = []
        merge_matrix = []

        for row in self.grid:
            # Extract non-zero tiles with original indices
            tiles = [(idx, row[idx]) for idx in range(self.size) if row[idx] != 0]

            # Build merge groups: either a single tile (tuple)
            # or a pair for merging (list of two tuples)
            groups = []
            i = 0
            while i < len(tiles):
                if i < len(tiles) - 1 and tiles[i][1] == tiles[i + 1][1]:
                    groups.append([tiles[i], tiles[i + 1]])  # merge group
                    i += 2
                else:
                    groups.append(tiles[i])                  # single tile
                    i += 1

            # Compute displacement for each original index
            bias_row = [0] * self.size
            merge_row = [0] * self.size
            for new_x, group in enumerate(groups):
                if isinstance(group, tuple):
                    old_x = group[0]
                    bias_row[old_x] = old_x - new_x
                else:
                    merge_row[new_x] = 1
                    for old_x, _ in group:
                        bias_row[old_x] = old_x - new_x

            bias_matrix.append(bias_row)
            merge_matrix.append(merge_row)

            # Merge tile values
            compressed = [v for _, v in tiles]
            result = []
            i = 0
            while i < len(compressed):
                if i < len(compressed) - 1 and compressed[i] == compressed[i + 1]:
                    result.append(compressed[i] * 2)
                    i += 2
                else:
                    result.append(compressed[i])
                    i += 1

            # Fill remaining cells with zeros
            result += [0] * (self.size - len(result))
            new_grid.append(result)


        self.grid = new_grid
        return bias_matrix, merge_matrix


    # ---------------------------------------------------------
    # Matrix rotations (used for UP/DOWN moves)
    # ---------------------------------------------------------

    @staticmethod
    def rotate_ccw(matrix):
        """Rotate matrix 90° CCW."""
        return [list(row) for row in zip(*matrix)][::-1]

    @staticmethod
    def rotate_cw(matrix):
        """Rotate matrix 90° CW."""
        return [list(row)[::-1] for row in zip(*matrix)]

    # ---------------------------------------------------------
    # Moves
    # ---------------------------------------------------------

    def move_left(self):
        """Shift tiles to the left. Returns (changed: bool, bias_matrix: list)."""
        old = copy.deepcopy(self.grid)
        bias_matrix, merge_matrix = self._shift_left()
        changed = old != self.grid
        return changed, bias_matrix, merge_matrix

    def move_right(self):
        """Shift tiles to the right. Returns (changed: bool, bias_matrix: list)."""
        old = copy.deepcopy(self.grid)
        
        self.grid = [row[::-1] for row in self.grid]
        bias_matrix, merge_matrix = self._shift_left()
        self.grid = [row[::-1] for row in self.grid]
        bias_matrix = [row[::-1] for row in bias_matrix]
        merge_matrix = [row[::-1] for row in merge_matrix]
        
        changed = old != self.grid
        return changed, bias_matrix, merge_matrix

    def move_up(self):
        """Shift tiles upward. Returns (changed: bool, bias_matrix: list)."""
        old = copy.deepcopy(self.grid)
        
        self.grid = self.rotate_ccw(self.grid)
        bias_matrix, merge_matrix = self._shift_left()
        self.grid = self.rotate_cw(self.grid)
        bias_matrix = self.rotate_cw(bias_matrix)
        merge_matrix = self.rotate_cw(merge_matrix)
        
        changed = old != self.grid
        return changed, bias_matrix, merge_matrix

    def move_down(self):
        """Shift tiles downward. Returns (changed: bool, bias_matrix: list)."""
        old = copy.deepcopy(self.grid)
        
        self.grid = self.rotate_cw(self.grid)
        bias_matrix, merge_matrix = self._shift_left()
        self.grid = self.rotate_ccw(self.grid)
        bias_matrix = self.rotate_ccw(bias_matrix)
        merge_matrix = self.rotate_ccw(merge_matrix)
        
        changed = old != self.grid
        return changed, bias_matrix, merge_matrix
