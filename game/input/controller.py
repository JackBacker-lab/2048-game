import pygame
from pygame.event import Event

from game.core.game import Game
from game.core.states import GameState
from game.core.types import MoveLiteral
from game.rendering.renderer import Renderer


class Controller:
    """Interprets player input and requests state changes from Game."""

    def __init__(self, game: Game, renderer: Renderer):
        self.game = game
        self.tile_manager = renderer.tile_manager
        self.renderer = renderer
        value, row, col = game.insert_new_tile()
        self.tile_manager.append_new_tile(value, row, col)

        self.is_waiting_to_declare_victory = False
        self.is_waiting_to_declare_game_over = False


    def process_event(self, event: Event | None) -> GameState:
        """Process a single pygame event and return the current game state."""
        # Wait until all animations finish before declaring victory/game over.
        if self.renderer.anim_manager.has_any():
            self.renderer.anim_manager.start(self.renderer.current_time)
            return GameState.PLAYING

        # Resolve a pending victory or game over once animations have completed.
        if self.is_waiting_to_declare_victory:
            self.is_waiting_to_declare_victory = False
            return GameState.VICTORY
        elif self.is_waiting_to_declare_game_over:
            self.is_waiting_to_declare_game_over = False
            return GameState.GAME_OVER

        # If there is no event (per-frame call from the main loop), keep playing.
        if event is None:
            return GameState.PLAYING

        # Restart the game when the user clicks the "New Game" button.
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.renderer.user_interface.newgame_rect.collidepoint(event.pos)
        ):
            return GameState.RESTARTING

        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)

        return GameState.PLAYING


    def _handle_keydown(self, event: Event) -> GameState:
        """Handle a key press event and update the game state accordingly."""
        results = self._get_game_move_results(event)
        if results is None:
            return GameState.PLAYING

        changed, bias_matrix, move = results
        if not changed:
            return GameState.PLAYING

        self.tile_manager.append_new_move(bias_matrix, move)

        # Check Victory after new move
        if self.game.check_victory():
            self.is_waiting_to_declare_victory = True
            return GameState.PLAYING

        value, row, col = self.game.insert_new_tile()
        self.tile_manager.append_new_tile(value, row, col)

        # Check Game Over after new tile insertion
        if not self.game.can_move():
            self.is_waiting_to_declare_game_over = True

        return GameState.PLAYING


    def _get_game_move_results(self, event: pygame.event.Event
) -> tuple[bool, list[list[int]], MoveLiteral] | None:
        if event.key == pygame.K_LEFT:
            return self.game.move_left()
        elif event.key == pygame.K_RIGHT:
            return self.game.move_right()
        elif event.key == pygame.K_UP:
            return self.game.move_up()
        elif event.key == pygame.K_DOWN:
            return self.game.move_down()
        else:
            return None
