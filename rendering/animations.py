from typing import Optional


class Animation:
    """
    Base class for all tile animations.
    Defines common interface: get_position() and get_scale().
    """

    def __init__(self, duration: int):
        self.duration = duration
        self.start_time = None

    def start(self, now):
        self.start_time = now

    def progress(self, now):
        return min(1.0, (now - self.start_time) / self.duration)

    def get_scale(self, now):
        return 1.0

    def get_position(self, now) -> Optional[tuple[int, int]]: 
        return None
    

class AppearAnimation(Animation):
    def __init__(self, pos, duration=120):
        super().__init__(duration)
        self.pos = pos

    def get_scale(self, now):
        return self.progress(now)

    
class ShiftAnimation(Animation):
    def __init__(self, from_pos, to_pos, duration=150):
        super().__init__(duration)
        self.from_pos = from_pos
        self.to_pos = to_pos

    def get_position(self, now) -> tuple[int, int]:
        p = self.progress(now)
        y = self.from_pos[0] + (self.to_pos[0] - self.from_pos[0]) * p
        x = self.from_pos[1] + (self.to_pos[1] - self.from_pos[1]) * p
        return (y, x)

    
class MergeAnimation(Animation):
    def __init__(self, tile_id, duration=150):
        super().__init__(duration)
        self.tile_id = tile_id
        self.duration_peak = duration // 2
        
        self.scale_up = 1.1
        self.scale_down = 1.0

    def get_scale(self, now):
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

