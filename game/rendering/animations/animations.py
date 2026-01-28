class Animation:
    """
    Base class for all tile animations.
    Defines common interface: get_position() and get_scale().
    """

    def __init__(self, duration: int):
        if duration < 1:
            raise ValueError("Duration must be greater than zero.")

        self.duration = duration
        self.start_time: int = 0

    def start(self, now: int):
        self.start_time = now

    def progress(self, now: int) -> float:
        if self.start_time == 0:
            return 0

        return min(1.0, (now - self.start_time) / self.duration)

    def get_scale(self, now: int):
        return 1.0

    def get_position(self, now: int) -> tuple[float, float] | None:
        return None


class AppearAnimation(Animation):
    def __init__(self, duration: int = 120):
        if duration < 1:
            raise ValueError("Duration must be greater than zero.")

        super().__init__(duration)

    def get_scale(self, now: int):
        return self.progress(now)


class ShiftAnimation(Animation):
    def __init__(
            self,
            from_pos: tuple[int, int],
            to_pos: tuple[int, int],
            duration: int = 150
        ):
        if duration < 1:
            raise ValueError("Duration must be greater than zero.")
        if any(coord < 0 for pos in (from_pos, to_pos) for coord in pos):
            raise ValueError("Position arguments must be non-negative.")

        super().__init__(duration)
        self.from_pos = from_pos
        self.to_pos = to_pos

    def get_position(self, now: int) -> tuple[float, float]:
        p = self.progress(now)
        y = self.from_pos[0] + (self.to_pos[0] - self.from_pos[0]) * p
        x = self.from_pos[1] + (self.to_pos[1] - self.from_pos[1]) * p
        return (y, x)


class MergeAnimation(Animation):
    def __init__(self, duration: int = 150):
        if duration < 1:
            raise ValueError("Duration must be greater than zero.")

        super().__init__(duration)
        self.duration_peak = duration // 2

        self.scale_up = 1.1
        self.scale_down = 1.0

    def get_scale(self, now: int):
        dt = now - self.start_time
        if dt < 0:
            return 1.0

        if dt < self.duration_peak:
            k = dt / self.duration_peak
            return 1.0 + (self.scale_up - self.scale_down) * k
        elif dt < self.duration:
            k = (dt - self.duration_peak) / (self.duration - self.duration_peak)
            return self.scale_up - (self.scale_up - self.scale_down) * k
        else:
            return self.scale_down

