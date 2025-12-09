class Animation:
    def __init__(self, duration: int):
        self.duration = duration
        self.start_time = None

    def start(self, now):
        self.start_time = now

    def progress(self, now):
        return min(1.0, (now - self.start_time) / self.duration)
    

class AppearAnimation(Animation):
    def __init__(self, pos, duration=170):
        super().__init__(duration)
        self.pos = pos

    def scale(self, now):
        return self.progress(now)
    
    
class ShiftAnimation(Animation):
    def __init__(self, from_pos, to_pos, duration=130):
        super().__init__(duration)
        self.from_pos = from_pos
        self.to_pos = to_pos

    def interpolate(self, now):
        p = self.progress(now)
        y = self.from_pos[0] + (self.to_pos[0] - self.from_pos[0]) * p
        x = self.from_pos[1] + (self.to_pos[1] - self.from_pos[1]) * p
        return (y, x)