from unittest.mock import Mock, patch

import pygame
import pytest
from pygame.event import Event

from game import GameState
from game.main import run_single_game, wait_for_restart


def test_run_single_game_victory():
    clock = Mock()
    controller = Mock()
    renderer = Mock()

    controller.process_event.side_effect = [
        GameState.PLAYING,
        GameState.VICTORY,
    ]

    with patch("game.main.pygame.event.get") as mock_get:
        mock_get.return_value = [Event(pygame.KEYDOWN, key=pygame.K_LEFT)]
        state = run_single_game(clock, controller, renderer)

    assert state == GameState.VICTORY
    assert renderer.render.called
    assert controller.process_event.call_count >= 2


def test_run_single_game_quit():
    clock = Mock()
    controller = Mock()
    renderer = Mock()

    controller.process_event.side_effect = [
        GameState.PLAYING,
        GameState.VICTORY,
    ]

    with patch("game.main.pygame.event.get") as mock_get:
        mock_get.return_value = [Event(pygame.QUIT)]
        with pytest.raises(SystemExit):
            run_single_game(clock, controller, renderer)

    assert not renderer.render.called
    assert controller.process_event.call_count == 1


@pytest.mark.parametrize(
    "event",
    [
        [Event(pygame.QUIT)],
        [Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    ],
    ids=["quit", "return"]
)
@patch("game.main.pygame.event.get")
@patch("game.main.pygame.quit")
@patch("game.main.sys.exit", side_effect=SystemExit)
def test_wait_for_restart_quit(
    mock_exit: Mock,
    mock_quit: Mock,
    mock_get: Mock,
    event: Event
):
    # Arrange
    clock = Mock()
    mock_get.return_value = event

    # Act
    with pytest.raises(SystemExit):
        wait_for_restart(clock)

    # Assert
    mock_quit.assert_called_once()
    mock_exit.assert_called_once()


@patch("game.main.pygame.event.get")
def test_wait_for_restart_restart(mock_get: Mock):
    # Arrange
    clock = Mock()
    mock_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)]

    # Act & Assert: program must complete without exceptions
    wait_for_restart(clock)
