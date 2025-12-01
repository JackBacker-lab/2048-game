import pygame
from game import Game


class Controller:
    """
    Interprets player input and requests state changes from Game.
    Does not modify game state directly.
    """

    def __init__(self, game: Game):
        self.game = game

    def process_event(self, event) -> bool:
        """Returns True if the player had won the game, False if he didn't win yet"""
        if not self.game.running:
            return False

        if event.type == pygame.KEYDOWN:
            changed = False

            if event.key == pygame.K_LEFT:
                changed = self.game.move_left()
            elif event.key == pygame.K_RIGHT:
                changed = self.game.move_right()
            elif event.key == pygame.K_UP:
                changed = self.game.move_up()
            elif event.key == pygame.K_DOWN:
                changed = self.game.move_down()

            if changed:
                self.game.insert_new_tile()

                # Victory
                if self.game.check_victory():
                    self.game.running = False
                    return True

                # Loss
                if not self.game.can_move():
                    self.game.running = False

        return False

