from enum import Enum


class GameState(Enum):
    PLAYING = 0
    VICTORY = 1
    GAME_OVER = 2
    RESTARTING = 3
