import random
from typing import List


class Game:
    """
    Contains only the game logic: interaction with game grid List[List[int]]
    """
    
    def __init__(self, size: int = 4):
        self.size = size
        self.grid: List[List[int]] = [[0] * size for _ in range(size)]
        self.running = True

        # Starting tile
        self.insert_new_tile()

    def insert_new_tile(self):
        """Creates new tile (2 or 4) in random empty cell"""
        empty_cells = [
            (i, j)
            for i in range(self.size)
            for j in range(self.size)
            if self.grid[i][j] == 0
        ]
        x, y = random.choice(empty_cells)
        self.grid[x][y] = 2 if random.random() < 0.75 else 4

    def can_move(self) -> bool:
        """Checks can you do at least one move"""

        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x];

                # If there is any empty cells
                if cell == 0:
                    return True

                # If you can join tiles vertically
                elif x + 1 < self.size and cell == self.grid[y][x + 1]:
                    return True

                # If you can join tiles horizontally
                elif y + 1 < self.size and cell == self.grid[y + 1][x]:
                    return True

        return False

    def check_victory(self) -> bool:
        """Victory is when there is a 2048 on the field"""
        return any(2048 in row for row in self.grid)

    def get_score(self) -> int:
        """Score is max tile on the field"""
        return max(max(row) for row in self.grid)

    # ---------------------------------------------------------
    # Core mechanics
    # ---------------------------------------------------------

    def shift_left(self):
        """
        Executes tile compression, join, repeated compression,
        realizing move left mechanic
        """
        new_grid = []

        for row in self.grid:
            # 1. Remove zeros (compression)
            row = [el for el in row if el != 0]

            # 2. Join neighbour cells
            for i in range(len(row) - 1):
                if row[i] == row[i + 1] != 0:
                    row[i] *= 2
                    row[i + 1] = 0

            # 3. Compress again
            row = [el for el in row if el != 0]

            # 4. Add missing zeros on the right
            while len(row) < self.size:
                row.append(0)

            new_grid.append(row)

        self.grid = new_grid

    # ---------------------------------------------------------
    # Rotations (used for UP/DOWN moves)
    # ---------------------------------------------------------

    def rotate_ccw(self, matrix):
        return [list(row) for row in zip(*matrix)][::-1]

    def rotate_cw(self, matrix):
        return [list(row)[::-1] for row in zip(*matrix)]

    # ---------------------------------------------------------
    # Moves (return True, if grid had changed)
    # ---------------------------------------------------------

    def move_left(self) -> bool:
        old = self.grid
        self.shift_left()
        return old != self.grid

    def move_right(self) -> bool:
        old = self.grid
        self.grid = [row[::-1] for row in self.grid]
        self.shift_left()
        self.grid = [row[::-1] for row in self.grid]
        return old != self.grid

    def move_up(self) -> bool:
        old = self.grid
        self.grid = self.rotate_ccw(self.grid)
        self.shift_left()
        self.grid = self.rotate_cw(self.grid)
        return old != self.grid

    def move_down(self) -> bool:
        old = self.grid
        self.grid = self.rotate_cw(self.grid)
        self.shift_left()
        self.grid = self.rotate_ccw(self.grid)
        return old != self.grid
