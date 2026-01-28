from game.rendering.animations.animations import (
    Animation,
    AppearAnimation,
    MergeAnimation,
    ShiftAnimation,
)

_ANIM_ORDER = (ShiftAnimation, MergeAnimation, AppearAnimation)


class AnimationManager:
    def __init__(self):
        """Initialize the animation manager with an empty animation registry."""
        # { tile_id: [Animation, ...] }
        self.anims: dict[int, list[Animation]] = {}


    def start(self, now: int) -> None:
        """Start the next group of queued animations.

        This method picks one animation type in strict logical order
        (Shift -> Merge -> Appear) and starts all animations of that type
        that have not been started yet.
        """
        if not self.anims:
            return

        for anim_type in _ANIM_ORDER:
            if any(
                isinstance(anim, anim_type)
                for anims in self.anims.values()
                for anim in anims
            ):
                self.start_certain_anims(anim_type, now)
                break


    def start_certain_anims(
        self,
        anim_type: type[Animation],
        now: int,
    ) -> None:
        """Start all animations of a certain Animation type if not started yet."""
        for anims in self.anims.values():
            for anim in anims:
                if isinstance(anim, anim_type) and anim.start_time == 0:
                    anim.start(now)


    def add(self, tile_id: int, animation: Animation) -> None:
        """Add a new animation for the specified tile."""
        if tile_id not in self.anims:
            self.anims[tile_id] = []
        self.anims[tile_id].append(animation)


    def get_next(self, tile_id: int) -> Animation | None:
        """Return the next queued animation for the given tile, if any."""
        anims = self.anims.get(tile_id)
        return anims[0] if anims else None


    def cleanup(self, now: int) -> None:
        """Remove finished animations."""
        to_delete_tile_ids: list[int] = []
        for tid, anims in self.anims.items():
            if remaining := [anim for anim in anims if anim.start_time == 0 or
                             anim.progress(now) < 1.0]:
                self.anims[tid] = remaining
            else:
                to_delete_tile_ids.append(tid)

        for tid in to_delete_tile_ids:
            del self.anims[tid]


    def has_shift_animations(self) -> bool:
        return any(
            isinstance(anim, ShiftAnimation)
            for anims in self.anims.values()
            for anim in anims
        )


    def has_any(self) -> bool:
        """Return True if there is at least one animation registered."""
        return bool(self.anims)
