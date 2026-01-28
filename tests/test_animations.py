import pytest

from game.rendering.animations.animations import (
    Animation,
    AppearAnimation,
    MergeAnimation,
    ShiftAnimation,
)


# ===========================
# Test Animation class
# ===========================
@pytest.fixture
def animation() -> Animation:
    return Animation(150)


def test_animation_valid_init():
    duration = 100
    animation = Animation(duration)
    assert animation.duration == duration
    assert animation.start_time == 0


def test_animation_invalid_init():
    with pytest.raises(ValueError):
        Animation(0)


def test_animation_start(animation: Animation):
    now = 100
    animation.start(now)
    assert animation.start_time == now


def test_animation_progress_respects_start_time(animation: Animation):
    duration = 150
    # Without start: start_time = 0
    assert animation.progress(0) == 0.0
    assert animation.progress(duration * 10) == 0.0

    # After explicit start at 100 ms
    animation.start(100)
    assert animation.start_time == 100

    # Before start
    assert animation.progress(99) == pytest.approx(-1 / duration, rel=1e-3)  # type: ignore[arg-type]

    # At the beginning
    assert animation.progress(100) == 0.0

    # In the middle
    mid = 100 + duration // 2
    assert 0.0 < animation.progress(mid) < 1.0

    # In the end and after
    end = 100 + duration
    assert animation.progress(end) == 1.0
    assert animation.progress(end + 10) == 1.0


def test_animation_get_scale(animation: Animation):
    result = animation.get_scale(0)
    assert result == 1.0


def test_animation_get_position(animation: Animation):
    result = animation.get_position(0)
    assert result is None


# Test AppearAnimation class
def test_appear_animation_valid_init():
    # Must not throw any exception
    AppearAnimation()


def test_appear_animation_invalid_init():
    with pytest.raises(ValueError):
        AppearAnimation(0)


def test_appear_animation_get_scale_progresses_from_0_to_1():
    duration = 150
    appear_anim = AppearAnimation(duration=duration)

    start_time = 100
    appear_anim.start(start_time)

    assert appear_anim.get_scale(start_time) == 0.0

    mid = start_time + duration // 2
    mid_scale = appear_anim.get_scale(mid)
    assert 0.0 < mid_scale < 1.0

    end = start_time + duration
    assert appear_anim.get_scale(end) == 1.0
    assert appear_anim.get_scale(end + 10) == 1.0


# Test ShiftAnimation class
def test_shift_animation_valid_init():
    from_pos, to_pos = (0, 0), (1, 1)
    shift_anim = ShiftAnimation(from_pos, to_pos)
    assert shift_anim.from_pos == from_pos
    assert shift_anim.to_pos == to_pos


@pytest.mark.parametrize(
    "from_pos, to_pos, duration",
    [
        [(0, -1), (2, 1), 300],
        [(0, 0), (-1, 2), 100],
        [(0, 1), (3, 0), -5]
    ]
)
def test_shift_animation_invalid_init(from_pos: tuple[int, int],
                                      to_pos: tuple[int, int],
                                      duration: int):
    with pytest.raises(ValueError):
        ShiftAnimation(from_pos, to_pos, duration=duration)


def test_shift_animation_get_position():
    duration = 150
    from_pos, to_pos = (0, 0), (1, 1)
    shift_anim = ShiftAnimation(from_pos, to_pos, duration=duration)

    start_time = 100
    shift_anim.start(start_time)

    assert shift_anim.get_position(start_time) == (0, 0)

    mid = start_time + duration // 2
    mid_position = shift_anim.get_position(mid)
    assert (0, 0) < mid_position < (1, 1)

    end = start_time + duration
    assert shift_anim.get_position(end) == (1, 1)
    assert shift_anim.get_position(end + 10) == (1, 1)


# Test MergeAnimation class
def test_merge_animation_valid_init():
    duration = 150
    merge_anim = MergeAnimation(duration)
    assert merge_anim.duration_peak == duration // 2


def test_merge_animation_invalid_init():
    with pytest.raises(ValueError):
        MergeAnimation(-1)


def test_merge_animation_get_scale():
    duration = 150
    merge_anim = MergeAnimation(duration=duration)

    start_time = 100
    merge_anim.start(start_time)

    assert merge_anim.get_scale(start_time - 1) == 1.0
    assert merge_anim.get_scale(start_time) == 1.0

    mid = start_time + duration // 2
    mid_scale = merge_anim.get_scale(mid)
    assert mid_scale == 1.1

    end = start_time + duration
    assert merge_anim.get_scale(end) == 1.0
    assert merge_anim.get_scale(end + 10) == 1.0
