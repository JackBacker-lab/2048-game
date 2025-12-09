import pygame
from game import Game
from renderer import Renderer
import copy


class Controller:
    """
    Interprets player input and requests state changes from Game.
    Does not modify game state directly.
    """

    def __init__(self, game: Game, renderer: Renderer):
        self.game = game
        value, row, col = game.insert_new_tile()
        self.renderer = renderer
        renderer.append_new_tile(value, row, col)

    def process_event(self, event) -> bool:
        """Returns True if the player had won the game, False if he didn't win yet"""
        if not self.game.running:
            return False

        if event.type == pygame.KEYDOWN:
            changed = False
            bias_matrix = []
            move = ""
            prev_grid = copy.deepcopy(self.game.grid)

            if event.key == pygame.K_LEFT:
                changed, bias_matrix = self.game.move_left()
                move = "l"
            elif event.key == pygame.K_RIGHT:
                changed, bias_matrix = self.game.move_right()
                move = "r"
            elif event.key == pygame.K_UP:
                changed, bias_matrix = self.game.move_up()
                move = "u"
            elif event.key == pygame.K_DOWN:
                changed, bias_matrix = self.game.move_down()
                move = "d"

            if changed:
                value, row, col = self.game.insert_new_tile()
                self.renderer.append_new_move(bias_matrix, move, prev_grid)
                self.renderer.append_new_tile(value, row, col)

                # Check Victory / Loss
                if self.game.check_victory():
                    self.game.running = False
                    return True
                elif not self.game.can_move():
                    self.game.running = False
                

        return False

