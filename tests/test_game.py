import pytest

from game import Game


@pytest.fixture
def game() -> Game:
    """Base 4x4 game grid for testing."""
    return Game(size=4)


@pytest.fixture
def game_2x2() -> Game:
    """Smaller 2x2 game grid for testing scalability."""
    return Game(size=2)


@pytest.fixture
def game_full_grid() -> Game:
    """Base 4x4 game grid with all cells filled (no empty cells)"""
    game = Game(size=4)
    game.grid = [
        [2, 4, 8, 16],
        [32, 64, 128, 256],
        [512, 1024, 2, 4],
        [8, 16, 32, 64]
    ]
    return game


#===============================
# Insert new tile tests
#===============================

def test_insert_new_tile_basic(game: Game):
    initial_empty_cells = sum(row.count(0) for row in game.grid)

    value, row, col = game.insert_new_tile()

    assert value in (2, 4), "Inserted tile must be either 2 or 4"
    assert game.grid[row][col] == value, \
        "Tile value must be correctly placed in the grid"
    new_empty_cells = sum(row.count(0) for row in game.grid)
    assert new_empty_cells == initial_empty_cells - 1, \
        "Number of empty cells should decrease by 1"



def test_insert_new_tile_smaller_grid(game_2x2: Game):
    _, row, col = game_2x2.insert_new_tile()

    assert 0 <= row < 2, "Row value must be within bounds of 2x2 grid"
    assert 0 <= col < 2, "Column value must be within bounds of 2x2 grid"


#===============================
# Can move tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_result",
    [
        pytest.param(
            [
                [0, 4, 2, 4],
                [8, 2, 4, 2],
                [2, 4, 2, 4],
                [4, 2, 4, 2]
            ],
            True,
            id="empty_space"
        ),
        pytest.param(
            [
                [4, 4, 2, 4],
                [8, 2, 4, 2],
                [2, 4, 2, 4],
                [4, 2, 4, 2]
            ],
            True,
            id="neighboring_equal_tiles_horizontally"
        ),
        pytest.param(
            [
                [4, 8, 2, 4],
                [4, 2, 4, 2],
                [2, 4, 2, 4],
                [4, 2, 4, 2]
            ],
            True,
            id="neighboring_equal_tiles_vertically"
        ),
        pytest.param(
            [
                [4, 8, 2, 4],
                [16, 2, 4, 2],
                [2, 4, 2, 4],
                [4, 2, 4, 2]
            ],
            False,
            id="no_moves_available"
        ),
    ]
)
def test_can_move(game: Game, grid: list[list[int]], expected_result: bool):
    game.grid = grid

    result = game.can_move()

    assert result == expected_result


#===============================
# Check victory tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_result",
    [
        pytest.param(
            [
                [4096, 4, 512, 4],
                [8, 2, 4, 2],
                [2, 1024, 2, 4],
                [256, 2, 4, 8192]
            ],
            False,
            id="no_2048_tile"
        ),
        pytest.param(
            [
                [4, 4096, 2, 4],
                [8, 2, 8192, 2],
                [1024, 4, 2, 4],
                [4, 2, 4, 2048]
            ],
            True,
            id="2048_tile_exists"
        ),
    ]
)
def test_check_victory(game: Game, grid: list[list[int]], expected_result: bool):
    game.grid = grid

    result = game.check_victory()

    assert result == expected_result


#===============================
# Get score tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_result",
    [
        pytest.param(
            [
                [4096, 4, 512, 4],
                [8, 2, 4, 2],
                [2, 1024, 2, 4],
                [256, 2, 4, 8192]
            ],
            8192,
            id="score_one_max"
        ),
        pytest.param(
            [
                [1024, 4, 1024, 4],
                [8, 2, 4, 2],
                [2, 1024, 2, 4],
                [256, 2, 4, 1024]
            ],
            1024,
            id="score_several_max"
        ),
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            0,
            id="empty_grid"
        ),
    ]
)
def test_get_score(game: Game, grid: list[list[int]], expected_result: int):
    game.grid = grid

    result = game.get_score()

    assert result == expected_result


#===============================
# Move left tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_bias_matrix, expected_changed",
    [
        # No changes expected
        pytest.param(
            [
                [2, 4, 8, 16],
                [2, 4, 8, 16],
                [2, 4, 8, 16],
                [2, 4, 8, 16]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="no_changes"
        ),
        # Shifts only, no merges
        pytest.param(
            [
                [2, 0, 4, 0],
                [0, 8, 0, 16],
                [32, 0, 0, 64],
                [0, 0, 0, 128]
            ],
            [
                [0, 0, 1, 0],
                [0, 1, 0, 2],
                [0, 0, 0, 2],
                [0, 0, 0, 3]
            ],
            True,
            id="shifts_only"
        ),
        # Several possible merges
        pytest.param(
            [
                [2, 2, 2, 2],
                [2, 2, 4, 4],
                [2, 2, 2, 4],
                [0, 2, 2, 2]
            ],
            [
                [0, 1, 1, 2],
                [0, 1, 1, 2],
                [0, 1, 1, 1],
                [0, 1, 2, 2]
            ],
            True,
            id="possible_merges"
        ),
        # Big numbers
        pytest.param(
            [
                [1024, 1024, 2048, 2048],
                [4096, 4096, 8192, 8192],
                [0, 16384, 32768, 32768],
                [0, 0, 131072, 131072]
            ],
            [
                [0, 1, 1, 2],
                [0, 1, 1, 2],
                [0, 1, 1, 2],
                [0, 0, 2, 3]
            ],
            True,
            id="big_numbers"
        ),
        # Empty grid
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="empty_grid"
        ),
        # Multiple consecutive merges: 2,2,4,4 → 4,8
        pytest.param(
            [
                [2, 2, 4, 4],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 1, 1, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="multiple_consecutive_merges"
        ),
        # Single tile (edge case)
        pytest.param(
            [
                [0, 0, 0, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 3],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="single_tile"
        ),
        # Asymmetric distribution with complex merges
        pytest.param(
            [
                [2, 0, 2, 0],
                [0, 4, 4, 0],
                [8, 0, 0, 8],
                [0, 0, 16, 0]
            ],
            [
                [0, 0, 2, 0],
                [0, 1, 2, 0],
                [0, 0, 0, 3],
                [0, 0, 2, 0]
            ],
            True,
            id="asymmetric_distribution"
        ),
    ]
)
def test_move_left(
    game: Game,
    grid: list[list[int]],
    expected_bias_matrix: list[list[int]],
    expected_changed: bool
):
    game.grid = grid

    changed, bias_matrix, move_type = game.move_left()

    assert changed == expected_changed
    assert bias_matrix == expected_bias_matrix
    assert move_type == 'l'


#===============================
# Move right tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_bias_matrix, expected_changed",
    [
        # No changes expected
        pytest.param(
            [
                [16, 8, 4, 2],
                [16, 8, 4, 2],
                [16, 8, 4, 2],
                [16, 8, 4, 2]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="no_changes"
        ),
        # Shifts only, no merges
        pytest.param(
            [
                [0, 4, 0, 2],
                [16, 0, 8, 0],
                [64, 0, 0, 32],
                [128, 0, 0, 0]
            ],
            [
                [0, 1, 0, 0],
                [2, 0, 1, 0],
                [2, 0, 0, 0],
                [3, 0, 0, 0]
            ],
            True,
            id="shifts_only"
        ),
        # Several merges
        pytest.param(
            [
                [2, 2, 2, 2],
                [4, 4, 2, 2],
                [4, 2, 2, 2],
                [2, 2, 0, 2]
            ],
            [
                [2, 1, 1, 0],
                [2, 1, 1, 0],
                [1, 1, 1, 0],
                [2, 2, 0, 0]
            ],
            True,
            id="several_merges"
        ),
        # Multiple consecutive merges: 4,4,2,2 → 8,4
        pytest.param(
            [
                [4, 4, 2, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [2, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="multiple_consecutive_merges"
        ),
        # Single tile at left edge
        pytest.param(
            [
                [2, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [3, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="single_tile"
        ),
        # Big numbers
        pytest.param(
            [
                [2048, 2048, 1024, 1024],
                [8192, 8192, 4096, 4096],
                [32768, 0, 16384, 16384],
                [131072, 0, 0, 131072]
            ],
            [
                [2, 1, 1, 0],
                [2, 1, 1, 0],
                [2, 0, 1, 0],
                [3, 0, 0, 0]
            ],
            True,
            id="big_numbers"
        ),
        # Empty grid
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="empty_grid"
        ),
    ]
)
def test_move_right(
    game: Game,
    grid: list[list[int]],
    expected_bias_matrix: list[list[int]],
    expected_changed: bool
):
    game.grid = grid

    changed, bias_matrix, move_type = game.move_right()

    assert changed == expected_changed
    assert bias_matrix == expected_bias_matrix
    assert move_type == 'r'


#===============================
# Move up tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_bias_matrix, expected_changed",
    [
        # No changes expected
        pytest.param(
            [
                [2, 2, 2, 2],
                [4, 4, 4, 4],
                [8, 8, 8, 8],
                [16, 16, 16, 16]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="no_changes"
        ),
        # Shifts only (no merges)
        pytest.param(
            [
                [2, 0, 32, 0],
                [0, 8, 0, 4],
                [0, 0, 0, 16],
                [4, 0, 64, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 0, 1],
                [0, 0, 0, 1],
                [2, 0, 2, 0]
            ],
            True,
            id="shifts_only"
        ),
        # Several merges in columns
        pytest.param(
            [
                [2, 2, 2, 2],
                [2, 2, 4, 4],
                [2, 2, 2, 4],
                [0, 2, 2, 2]
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 1],
                [0, 2, 1, 1]
            ],
            True,
            id="several_merges"
        ),
        # Multiple consecutive merges in column: 2,2,4,4 → 4,8
        pytest.param(
            [
                [2, 0, 0, 0],
                [2, 0, 0, 0],
                [4, 0, 0, 0],
                [4, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [2, 0, 0, 0]
            ],
            True,
            id="multiple_consecutive_merges"
        ),
        # Single tile at bottom
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [2, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [3, 0, 0, 0]
            ],
            True,
            id="single_tile"
        ),
        # Big numbers
        pytest.param(
            [
                [1024, 4096, 0, 2048],
                [1024, 4096, 16384, 2048],
                [2048, 8192, 32768, 8192],
                [2048, 8192, 32768, 131072]
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [2, 2, 2, 1]
            ],
            True,
            id="big_numbers"
        ),
        # Asymmetric distribution with complex merges
        pytest.param(
            [
                [2, 0, 0, 8],
                [0, 0, 4, 0],
                [2, 0, 4, 0],
                [0, 16, 0, 8]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 1, 0],
                [2, 0, 2, 0],
                [0, 3, 0, 3]
            ],
            True,
            id="asymmetric_distribution"
        ),
        # Empty grid
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="empty_grid"
        ),
    ]
)
def test_move_up(
    game: Game,
    grid: list[list[int]],
    expected_bias_matrix: list[list[int]],
    expected_changed: bool
):
    game.grid = grid

    changed, bias_matrix, move_type = game.move_up()

    assert changed == expected_changed
    assert bias_matrix == expected_bias_matrix
    assert move_type == 'u'


#===============================
# Move down tests
#===============================

@pytest.mark.parametrize(
    "grid, expected_bias_matrix, expected_changed",
    [
        # No changes expected
        pytest.param(
            [
                [16, 16, 16, 16],
                [8, 8, 8, 8],
                [4, 4, 4, 4],
                [2, 2, 2, 2]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="no_changes"
        ),
        # Shifts only (no merges)
        pytest.param(
            [
                [4, 8, 64, 16],
                [0, 0, 0, 4],
                [2, 0, 32, 0],
                [0, 0, 0, 0]
            ],
            [
                [2, 3, 2, 2],
                [0, 0, 0, 2],
                [1, 0, 1, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="shifts_only"
        ),
        # Several merges in columns
        pytest.param(
            [
                [0, 2, 2, 2],
                [2, 2, 2, 4],
                [2, 2, 4, 4],
                [2, 2, 2, 2]
            ],
            [
                [0, 2, 1, 1],
                [1, 1, 0, 1],
                [1, 1, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="several_merges"
        ),
        # Multiple consecutive merges in column: 4,4,2,2 → 8,4
        pytest.param(
            [
                [4, 0, 0, 0],
                [4, 0, 0, 0],
                [2, 0, 0, 0],
                [2, 0, 0, 0]
            ],
            [
                [2, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="multiple_consecutive_merges"
        ),
        # Single tile at top
        pytest.param(
            [
                [2, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [3, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="single_tile"
        ),
        # Big numbers
        pytest.param(
            [
                [2048, 2048, 0, 1024],
                [2048, 2048, 16384, 1024],
                [8192, 4096, 32768, 8192],
                [8192, 4096, 32768, 4096]
            ],
            [
                [2, 2, 0, 1],
                [1, 1, 1, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0]
            ],
            True,
            id="big_numbers"
        ),
        # Empty grid
        pytest.param(
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            False,
            id="empty_grid"
        ),
    ]
)
def test_move_down(
    game: Game,
    grid: list[list[int]],
    expected_bias_matrix: list[list[int]],
    expected_changed: bool
):
    game.grid = grid

    changed, bias_matrix, move_type = game.move_down()

    assert changed == expected_changed
    assert bias_matrix == expected_bias_matrix
    assert move_type == 'd'
