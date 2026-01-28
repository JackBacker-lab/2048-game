from unittest.mock import Mock, patch

import pygame
import pytest

from game.core.game import Game
from game.rendering.colors import BG_COLOR
from game.rendering.renderer import Renderer


@pytest.fixture
def mock_game() -> Game:
    game = Mock(spec=Game)
    game.size = 4
    game.grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    return game


@patch("game.rendering.renderer.Overlay")
@patch("game.rendering.renderer.TileRenderer")
@patch("game.rendering.renderer.UI")
@patch("game.rendering.renderer.TileManager")
@patch("game.rendering.renderer.AnimationManager")
@patch("game.rendering.renderer.pygame.font.SysFont")
@patch("game.rendering.renderer.pygame.display.set_mode")
def test_renderer_init(
    mock_set_mode: Mock,
    mock_sysfont: Mock,
    mock_animation_manager_cls: Mock,
    mock_tile_manager_cls: Mock,
    mock_ui_cls: Mock,
    mock_tile_renderer_cls: Mock,
    mock_overlay_cls: Mock,
    mock_game: Game,
):
    # Arrange
    screen_mock = Mock(spec=pygame.Surface)
    mock_set_mode.return_value = screen_mock

    font_big_mock = Mock()
    font_mock = Mock()
    font_small_mock = Mock()

    anim_manager_instance = Mock()
    tile_manager_instance = Mock()
    ui_instance = Mock()
    tile_renderer_instance = Mock()
    overlay_instance = Mock()

    mock_animation_manager_cls.return_value = anim_manager_instance
    mock_tile_manager_cls.return_value = tile_manager_instance
    mock_ui_cls.return_value = ui_instance
    mock_tile_renderer_cls.return_value = tile_renderer_instance
    mock_overlay_cls.return_value = overlay_instance

    # Act
    renderer = Renderer(mock_game)

    # Assert that basic attributes are initialized correctly
    assert renderer.game is mock_game
    assert renderer.grid_size == mock_game.size
    assert renderer.current_time == 0

    # Assert that fonts are initialized
    mock_sysfont.assert_called()
    assert renderer.FONT_BIG is font_big_mock
    assert renderer.FONT is font_mock
    assert renderer.FONT_SMALL is font_small_mock

    mock_set_mode.assert_called_once_with((renderer.WIDTH, renderer.HEIGHT))

    # Assert that all classes are initialized with the correct dependencies
    mock_animation_manager_cls.assert_called_once_with()
    mock_tile_manager_cls.assert_called_once_with(mock_game, anim_manager_instance)
    mock_ui_cls.assert_called_once_with(screen_mock, mock_game, font_small_mock)
    mock_tile_renderer_cls.assert_called_once_with(
        screen_mock, anim_manager_instance, tile_manager_instance, font_mock
    )
    mock_overlay_cls.assert_called_once_with(screen_mock, font_mock, font_small_mock)

    assert renderer.anim_manager is anim_manager_instance
    assert renderer.tile_manager is tile_manager_instance
    assert renderer.user_interface is ui_instance
    assert renderer.tile_renderer is tile_renderer_instance
    assert renderer.overlay is overlay_instance


@patch("game.rendering.renderer.pygame.display.flip")
@patch("game.rendering.renderer.Overlay")
@patch("game.rendering.renderer.TileRenderer")
@patch("game.rendering.renderer.UI")
@patch("game.rendering.renderer.TileManager")
@patch("game.rendering.renderer.AnimationManager")
@patch("game.rendering.renderer.pygame.font.SysFont")
@patch("game.rendering.renderer.pygame.display.set_mode")
def test_renderer_render(
    mock_set_mode: Mock,
    mock_sysfont: Mock,
    mock_animation_manager_cls: Mock,
    mock_tile_manager_cls: Mock,
    mock_ui_cls: Mock,
    mock_tile_renderer_cls: Mock,
    mock_overlay_cls: Mock,
    mock_flip: Mock,
    mock_game: Game,
):
    # Arrange
    mock_screen = Mock(spec=pygame.Surface)
    mock_set_mode.return_value = mock_screen

    font_big_mock = Mock()
    font_mock = Mock()
    font_small_mock = Mock()
    mock_sysfont.side_effect = [font_big_mock, font_mock, font_small_mock]

    anim_manager_instance = Mock()
    tile_manager_instance = Mock()
    ui_instance = Mock()
    tile_renderer_instance = Mock()
    overlay_instance = Mock()

    mock_animation_manager_cls.return_value = anim_manager_instance
    mock_tile_manager_cls.return_value = tile_manager_instance
    mock_ui_cls.return_value = ui_instance
    mock_tile_renderer_cls.return_value = tile_renderer_instance
    mock_overlay_cls.return_value = overlay_instance

    dt_ms = 200

    # Act
    renderer = Renderer(mock_game)
    renderer.render(dt_ms)

    # Assert
    assert renderer.current_time == dt_ms
    mock_screen.fill.assert_called_once_with(BG_COLOR)
    ui_instance.render.assert_called_once_with(renderer.WIDTH, renderer.HEIGHT)
    tile_renderer_instance.render_tiles.assert_called_once_with(renderer.current_time)
    assert mock_flip.assert_called_once_with()
