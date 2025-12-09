from animations import Animation, ShiftAnimation

class AnimationManager:
    def __init__(self):
        self.anims = {}  # { tile_id: Animation }

    def add(self, tile_id: int, animation: Animation, now: int):
        animation.start(now)
        self.anims[tile_id] = animation

    def get(self, tile_id):
        return self.anims.get(tile_id)

    def cleanup(self, now):
        finished = [tid for tid, anim in self.anims.items() if anim.progress(now) >= 1.0]
        for tid in finished:
            del self.anims[tid]
            
    def has_shift_animations(self):
        return any(isinstance(anim, ShiftAnimation) for anim in self.anims.values())