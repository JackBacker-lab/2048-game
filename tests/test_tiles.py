from typing import Any
from unittest.mock import Mock

import pytest

from game.core.game import Game
from game.core.types import MoveLiteral
from game.rendering.animations.animation_manager import AnimationManager
from game.rendering.animations.animations import AppearAnimation, MergeAnimation
from game.rendering.tiles import Tile
from game.rendering.tiles.tiles import TileManager


@pytest.mark.parametrize(
    "value, row, col, id", [[-1, 0, 1, 2], [0, -1, 2, 3], [0, 1, -2, 3], [0, 1, 2, -3]]
)
def test_invalid_tile_init(value: int, row: int, col: int, id: int):
    with pytest.raises(ValueError):
        Tile(value, row, col, id)


def test_valid_tile_init():
    value, row, col, id = 0, 1, 2, 3
    tile = Tile(value, row, col, id)
    assert tile.value == value
    assert tile.row == row
    assert tile.col == col
    assert tile.id == id


@pytest.mark.parametrize(
    "entity, expected_result",
    [
        [Tile(0, 1, 2, 3), True],
        [Tile(1, 1, 2, 3), False],
        [TileManager(Mock(), Mock()), False],
    ],
    ids=["equal", "not_equal", "not_tile"],
)
def test_tile_eq(entity: Any, expected_result: bool):
    value, row, col, id = 0, 1, 2, 3
    tile = Tile(value, row, col, id)

    assert (tile == entity) is expected_result


def test_tile_eq_not_implemented():
    value, row, col, id = 0, 1, 2, 3
    tile = Tile(value, row, col, id)

    assert tile.__eq__(TileManager(Mock(), Mock())) == NotImplemented


def test_tile_hash():
    value, row, col, tile_id, scale = 2, 1, 3, 10, 1.5
    tile = Tile(value, row, col, tile_id, scale)

    assert hash(tile) == hash((value, row, col, tile_id, scale))


# ==============================
# TileManager
# ==============================
@pytest.fixture
def tile_manager() -> TileManager:
    mock_game = Mock(Game)
    game_size = 4
    mock_game.size = game_size
    mock_anim_manager = Mock(AnimationManager)
    return TileManager(mock_game, mock_anim_manager)


def test_init():
    mock_game = Mock(Game)
    game_size = 4
    mock_game.size = game_size
    mock_anim_manager = Mock(AnimationManager)
    tile_manager = TileManager(mock_game, mock_anim_manager)

    assert tile_manager.game == mock_game
    assert tile_manager.grid_size == game_size
    assert tile_manager.anim_manager == mock_anim_manager
    assert not tile_manager.tiles
    assert tile_manager.next_tile_id == 0


def test_new_tile_id(tile_manager: TileManager):
    next_tile_id = tile_manager.next_tile_id
    tile_id_0 = tile_manager.new_tile_id()
    tile_id_1 = tile_manager.new_tile_id()
    assert next_tile_id == tile_id_0 == tile_id_1 - 1


@pytest.mark.parametrize(
    "tiles, row, col, expected_result",
    [
        [[Tile(2, 1, 2, 3), Tile(2, 2, 1, 0)], 1, 2, [Tile(2, 1, 2, 3)]],
        [
            [Tile(4, 1, 2, 1), Tile(2, 1, 2, 2)],
            1,
            2,
            [Tile(4, 1, 2, 1), Tile(2, 1, 2, 2)],
        ],
    ],
    ids=["diff_positions", "same_positions"],
)
def test_get_tiles_at(
    tile_manager: TileManager,
    tiles: list[Tile],
    row: int,
    col: int,
    expected_result: list[Tile],
):
    tile_manager.tiles = tiles

    assert tile_manager.get_tiles_at(row, col) == expected_result


def test_append_new_tile(tile_manager: TileManager):
    value, row, col = 1, 2, 3
    tile_id = tile_manager.next_tile_id
    tile_manager.anim_manager = Mock(spec=AnimationManager)
    tile_manager.append_new_tile(value, row, col)

    assert Tile(value, row, col, tile_id) in tile_manager.tiles
    assert tile_manager.anim_manager.add.call_count == 1
    called_tile_id, called_anim = tile_manager.anim_manager.add.call_args.args
    assert called_tile_id == tile_id
    assert isinstance(called_anim, AppearAnimation)


@pytest.mark.parametrize(
    "tiles, bias_matrix, move_type, expected_new_tiles",
    [
        # Tile movements to the right (one tile in a row)
        pytest.param(
            [Tile(2, 0, 0, 0), Tile(2, 1, 1, 1)],
            [
                [3, 0, 0, 0],
                [0, 2, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            "r",
            [Tile(2, 0, 3, 0), Tile(2, 1, 3, 1)],
            id="right_move",
        ),
        # Tile movements to the left (two tiles in a row)
        pytest.param(
            [Tile(2, 0, 1, 0), Tile(4, 0, 3, 1)],
            [
                [0, 1, 0, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            "l",
            [Tile(2, 0, 0, 0), Tile(4, 0, 1, 1)],
            id="left_move",
        ),
        # Tile movements to the top
        pytest.param(
            [Tile(8, 3, 1, 0)],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 3, 0, 0],
            ],
            "u",
            [Tile(8, 0, 1, 0)],
            id="upward_move",
        ),
        # Tile movements to the bottom (two tiles shift, one doesn't)
        pytest.param(
            [
                Tile(2, 0, 0, 0),
                Tile(4, 1, 2, 1),
                Tile(8, 2, 3, 2),
            ],
            [
                [2, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            "d",
            [
                Tile(2, 2, 0, 0),
                Tile(4, 2, 2, 1),
                Tile(8, 2, 3, 2),
            ],
            id="downward_move",
        ),
    ],
)
def test_append_new_move_happy_path(
    tiles: list[Tile],
    bias_matrix: list[list[int]],
    move_type: MoveLiteral,
    expected_new_tiles: list[Tile],
    tile_manager: TileManager,
):
    tile_manager.tiles = tiles

    tile_manager.append_new_move(bias_matrix, move_type)

    assert tile_manager.tiles == expected_new_tiles
    for actual, expected in zip(tile_manager.tiles, expected_new_tiles, strict=False):
        assert actual.id == expected.id
        assert actual.value == expected.value


@pytest.mark.parametrize(
    "tiles, bias_matrix, expected_exception",
    [
        # No tile at the position where bias > 0
        pytest.param(
            [Tile(2, 0, 3, 0)],
            [
                [0, 0, 2, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            RuntimeError,
            id="no_tile_at_bias_gt_zero",
        ),
        # 2 tiles at the same position
        pytest.param(
            [Tile(2, 0, 3, 0), Tile(2, 0, 3, 1)],
            [
                [0, 0, 0, 3],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            RuntimeError,
            id="two_tiles_at_the_same_pos",
        ),
    ],
)
def test_append_new_move_error(
    tiles: list[Tile],
    bias_matrix: list[list[int]],
    expected_exception: type[Exception],
    tile_manager: TileManager,
):
    tile_manager.tiles = tiles

    with pytest.raises(expected_exception):
        tile_manager.append_new_move(bias_matrix, "l")


def test_detect_merges_happy_path(tile_manager: TileManager):
    value, row, col, id = 2, 0, 0, 0
    next_tile_id = 2
    tiles = [Tile(value, row, col, id), Tile(value, row, col, id + 1)]
    tile_manager.next_tile_id = next_tile_id
    tile_manager.tiles = tiles
    tile_manager.anim_manager = Mock(spec=AnimationManager)
    tile_manager.detect_merges()

    # assert Tile(value * 2, row, col, id + 2) in tile_manager.tiles
    assert tiles not in tile_manager.tiles
    assert tile_manager.anim_manager.add.call_count == 1
    called_tile_id, called_anim = tile_manager.anim_manager.add.call_args.args
    assert called_tile_id == next_tile_id
    assert isinstance(called_anim, MergeAnimation)


@pytest.mark.parametrize(
    "tiles, expected_exception",
    [
        pytest.param(
            [Tile(2, 0, 0, 0), Tile(2, 0, 0, 1), Tile(2, 0, 0, 2)],
            RuntimeError,
            id="more_than_two_tiles_in_single_cell"
        ),
        pytest.param(
            [Tile(2, 0, 0, 0), Tile(4, 0, 0, 1)],
            RuntimeError,
            id="tiles_with_diff_values"
        )
    ]
)
def test_detect_merges_error(
    tiles: list[Tile],
    expected_exception: type[Exception],
    tile_manager: TileManager
):
    tile_manager.tiles = tiles

    with pytest.raises(expected_exception):
        tile_manager.detect_merges()
