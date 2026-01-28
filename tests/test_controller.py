from unittest.mock import Mock

import pygame
import pytest

from game import Controller, Game, GameState
from game.rendering import UI, AnimationManager, Renderer, TileManager


@pytest.fixture
def mock_game() -> Mock:
    empty_grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    game = Mock(spec=Game)
    game.size = 4
    game.insert_new_tile.return_value = (2, 0, 0)
    game.grid = empty_grid
    return game


@pytest.fixture
def mock_ui() -> Mock:
    ui = Mock(spec=UI)
    ui.newgame_rect = Mock()
    ui.newgame_rect.collidepoint.return_value = True
    return ui


@pytest.fixture
def mock_tile_manager() -> Mock:
    tile_manager = Mock(spec=TileManager)
    tile_manager.append_new_tile = Mock()
    tile_manager.append_new_move = Mock()
    tile_manager.append_merge_animations = Mock()
    return tile_manager


@pytest.fixture
def mock_animation_manager() -> Mock:
    anim_manager = Mock(spec=AnimationManager)
    anim_manager.has_any.return_value = False
    return anim_manager


@pytest.fixture
def mock_renderer(mock_game: Mock, mock_ui: Mock, mock_tile_manager: Mock,
                  mock_animation_manager: Mock) -> Mock:
    renderer = Mock(spec=Renderer)
    renderer.game = mock_game
    renderer.user_interface = mock_ui
    renderer.tile_manager = mock_tile_manager
    renderer.anim_manager = mock_animation_manager
    renderer.current_time = 0
    return renderer


@pytest.fixture
def mock_event_restart_click() -> Mock:
    mock_event = Mock(spec=pygame.event.Event)
    mock_event.type = pygame.MOUSEBUTTONDOWN
    mock_event.button = 1
    mock_event.pos = (50, 50)
    return mock_event


@pytest.fixture
def mock_event_key_down_left() -> Mock:
    mock_event = Mock(spec=pygame.event.Event)
    mock_event.type = pygame.KEYDOWN
    mock_event.key = pygame.K_LEFT
    return mock_event


@pytest.fixture
def mock_event_key_down_right() -> Mock:
    mock_event = Mock(spec=pygame.event.Event)
    mock_event.type = pygame.KEYDOWN
    mock_event.key = pygame.K_RIGHT
    return mock_event


@pytest.fixture
def mock_event_key_down_up() -> Mock:
    mock_event = Mock(spec=pygame.event.Event)
    mock_event.type = pygame.KEYDOWN
    mock_event.key = pygame.K_UP
    return mock_event


@pytest.fixture
def mock_event_key_down_down() -> Mock:
    mock_event = Mock(spec=pygame.event.Event)
    mock_event.type = pygame.KEYDOWN
    mock_event.key = pygame.K_DOWN
    return mock_event


def test_init(mock_game: Mock, mock_renderer: Mock):
    """Test Controller initialization."""
    controller = Controller(mock_game, mock_renderer)

    assert controller.game == mock_game
    assert controller.tile_manager == mock_renderer.tile_manager
    assert controller.renderer == mock_renderer
    assert controller.is_waiting_to_declare_victory is False
    assert controller.is_waiting_to_declare_game_over is False
    assert mock_game.insert_new_tile.call_count == 1
    assert mock_renderer.game.insert_new_tile.call_count == 1
    mock_renderer.tile_manager.append_new_tile.assert_called_once_with(
        2, 0, 0
    )


def test_process_event_while_animating(mock_game: Mock, mock_renderer: Mock):
    """Test that while animations are running, state remains PLAYING."""
    controller = Controller(mock_game, mock_renderer)
    mock_renderer.anim_manager.has_any.return_value = True

    state = controller.process_event(None)
    assert state == GameState.PLAYING, \
        "While animations are running, state should remain PLAYING."


def test_process_event_declare_victory(mock_game: Mock, mock_renderer: Mock):
    """Test that waiting to declare victory sets the state to VICTORY."""
    controller = Controller(mock_game, mock_renderer)
    controller.is_waiting_to_declare_victory = True

    state = controller.process_event(None)
    assert state == GameState.VICTORY, \
        "If waiting to declare victory, state should be VICTORY."


def test_process_event_declare_game_over(mock_game: Mock, mock_renderer: Mock):
    """Test that waiting to declare game over sets the state to GAME_OVER."""
    controller = Controller(mock_game, mock_renderer)
    controller.is_waiting_to_declare_game_over = True

    state = controller.process_event(None)
    assert state == GameState.GAME_OVER, \
        "If waiting to declare game over, state should be GAME_OVER."


def test_process_event_no_event(mock_game: Mock, mock_renderer: Mock):
    controller = Controller(mock_game, mock_renderer)
    state = controller.process_event(None)
    assert state == GameState.PLAYING, "No event should keep game in PLAYING state."


def test_process_event_restart_click(mock_game: Mock, mock_renderer: Mock,
                                     mock_event_restart_click: Mock):
    controller = Controller(mock_game, mock_renderer)
    state = controller.process_event(mock_event_restart_click)
    assert state == GameState.RESTARTING, \
        "Clicking restart should set state to RESTARTING."


@pytest.mark.parametrize(
    "event_fixture, move_method_name",
    [
        ("mock_event_key_down_left", "move_left"),
        ("mock_event_key_down_right", "move_right"),
        ("mock_event_key_down_up", "move_up"),
        ("mock_event_key_down_down", "move_down"),
    ],
    ids=["left", "right", "up", "down"]
)
def test_process_event_key_move_no_change(
    mock_game: Mock,
    mock_renderer: Mock,
    request: pytest.FixtureRequest,
    event_fixture: str,
    move_method_name: str,
):
    """Test that key press with no grid changes returns PLAYING state."""
    event = request.getfixturevalue(event_fixture)
    controller = Controller(mock_game, mock_renderer)

    move_method = getattr(mock_game, move_method_name)
    move_method.return_value = False, [], []

    state = controller.process_event(event)
    assert state == GameState.PLAYING


@pytest.mark.parametrize(
    "event_fixture, move_method_name, move_str",
    [
        ("mock_event_key_down_left", "move_left", "l"),
        ("mock_event_key_down_right", "move_right", "r"),
        ("mock_event_key_down_up", "move_up", "u"),
        ("mock_event_key_down_down", "move_down", "d"),
    ],
    ids=["left", "right", "up", "down"]
)
def test_process_event_key_move_with_change(
    mock_game: Mock,
    mock_renderer: Mock,
    request: pytest.FixtureRequest,
    event_fixture: str,
    move_method_name: str,
    move_str: str
):
    """Test that key press with grid changes processes move correctly."""
    event = request.getfixturevalue(event_fixture)
    controller = Controller(mock_game, mock_renderer)
    mock_game.insert_new_tile.reset_mock()

    # Setup move method and other dependencies
    bias_matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]

    move_method = getattr(mock_game, move_method_name)
    move_method.return_value = True, bias_matrix, move_str
    mock_game.check_victory.return_value = False
    mock_game.can_move.return_value = True

    # Execute
    state = controller.process_event(event)

    # Verify
    mock_renderer.tile_manager.append_new_move.assert_called_with(
        bias_matrix, move_str
    )
    mock_game.insert_new_tile.assert_called_once()
    mock_renderer.tile_manager.append_new_tile.assert_called_with(2, 0, 0)
    mock_game.check_victory.assert_called_once()
    mock_game.can_move.assert_called_once()
    assert state == GameState.PLAYING


def test_process_event_key_move_victory(
    mock_game: Mock,
    mock_renderer: Mock,
    mock_event_key_down_left: Mock
):
    """Test that achieving victory sets the appropriate flag."""
    controller = Controller(mock_game, mock_renderer)

    # Setup move method and other dependencies
    prev_grid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    bias_matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    merge_matrix = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]

    mock_game.move_left.return_value = True, bias_matrix, merge_matrix
    mock_game.check_victory.return_value = True
    mock_game.grid = prev_grid
    mock_renderer.current_time = 0

    # Execute
    state = controller.process_event(mock_event_key_down_left)

    # Verify
    assert controller.is_waiting_to_declare_victory is True
    assert state == GameState.PLAYING


def test_process_event_key_move_game_over(
    mock_game: Mock,
    mock_renderer: Mock,
    mock_event_key_down_left: Mock
):
    """Test that game over sets the appropriate flag."""
    controller = Controller(mock_game, mock_renderer)

    # Setup move method and other dependencies
    prev_grid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    bias_matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    merge_matrix = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]

    mock_game.move_left.return_value = True, bias_matrix, merge_matrix
    mock_game.check_victory.return_value = False
    mock_game.can_move.return_value = False
    mock_game.grid = prev_grid
    mock_renderer.current_time = 0

    # Execute
    state = controller.process_event(mock_event_key_down_left)

    # Verify
    assert controller.is_waiting_to_declare_game_over is True
    assert state == GameState.PLAYING


def test_process_event_other_keydown_event(
    mock_game: Mock,
    mock_renderer: Mock,
):
    controller = Controller(mock_game, mock_renderer)
    mock_event = Mock(pygame.event.Event)
    mock_event.type = pygame.KEYDOWN
    mock_event.key = pygame.K_ESCAPE

    state = controller.process_event(mock_event)
    assert state == GameState.PLAYING


def test_process_event_other_event(
    mock_game: Mock,
    mock_renderer: Mock,
):
    controller = Controller(mock_game, mock_renderer)
    mock_event = Mock(pygame.event.Event)
    mock_event.type = pygame.MOUSEBUTTONDOWN
    mock_event.button = 2

    state = controller.process_event(mock_event)
    assert state == GameState.PLAYING
