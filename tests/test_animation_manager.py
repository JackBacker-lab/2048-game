from unittest.mock import Mock, patch

import pytest

from game.rendering import (
    Animation,
    AnimationManager,
    AppearAnimation,
    MergeAnimation,
    ShiftAnimation,
)


@pytest.fixture
def anim_manager() -> AnimationManager:
    return AnimationManager()


@pytest.fixture
def tile_id() -> int:
    return 0

@pytest.fixture
def now() -> int:
    return 0


@pytest.fixture
def mock_animation() -> Mock:
    animation = Mock(spec=Animation)
    animation.start = Mock()
    return animation


def test_init(anim_manager: AnimationManager):
    assert not anim_manager.anims, \
        "Dict anims must be empty at the initialization"


@patch("game.rendering.AnimationManager.start_certain_anims")
def test_start_no_anims(start_certain_anims_mock: Mock, anim_manager: AnimationManager):
    anim_manager.start(100)
    assert start_certain_anims_mock.call_count == 0


@patch("game.rendering.AnimationManager.start_certain_anims")
def test_start_with_anims(mock_sca: Mock, anim_manager: AnimationManager):
    now = 0
    appear_anim = AppearAnimation()
    anim_manager.anims = {0: [appear_anim]}
    anim_manager.start(now)
    mock_sca.assert_called_once_with(AppearAnimation, now)


@patch("game.rendering.Animation.start")
def test_start_certain_anims(mock_start: Mock, anim_manager: AnimationManager):
    now = 0
    appear_anim = AppearAnimation()
    anim_manager.anims = {0: [appear_anim]}

    anim_manager.start_certain_anims(AppearAnimation, now)

    mock_start.assert_called_once_with(now)


def test_add(anim_manager: AnimationManager, mock_animation: Mock, tile_id: int):
    anim_manager.add(tile_id, mock_animation)

    assert anim_manager.anims.get(tile_id) == [mock_animation], \
        "Animation must be added to the dict."


def test_get_next(anim_manager: AnimationManager,
             tile_id: int, now: int):
    first_anim = AppearAnimation()
    second_anim = MergeAnimation()
    anim_manager.add(tile_id, first_anim)
    anim_manager.add(tile_id, second_anim)

    assert anim_manager.get_next(tile_id) == first_anim


def test_cleanup(anim_manager: AnimationManager, mock_animation: Mock,
             tile_id: int, now: int):
    # Arrange
    anim_manager.add(tile_id, mock_animation)
    anims = anim_manager.anims

    # Act [anim.progress() >= 1.0]
    mock_animation.progress.return_value = 1.0
    mock_animation.start_time = 100
    anim_manager.cleanup(now)

    # Assert [anim.progress() >= 1.0]
    assert not anim_manager.anims, "Animations dict must be cleared if progress >= 0"

    # Act [anim.progress() < 1.0]
    mock_animation.progress.return_value = 0.99
    anim_manager.cleanup(now)

    # Assert [anim.progress() < 1.0]
    assert anim_manager.anims == anims, \
        "Animations dict must not be changed if progress < 0"


def test_has_shift_animations(
    anim_manager: AnimationManager,
    tile_id: int,
):
    anim_manager.add(tile_id, ShiftAnimation((0, 0), (1, 1)))

    assert anim_manager.has_shift_animations()


def test_has_any(
    anim_manager: AnimationManager,
    tile_id: int,
    mock_animation: Mock,
):
    anim_manager.add(tile_id, mock_animation)

    assert anim_manager.has_any()
