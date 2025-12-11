import pygame
from core.game import Game
from rendering.renderer import Renderer
import copy


class Controller:
    """
    Interprets player input and requests state changes from Game.
    Does not modify game state directly.
    """

    def __init__(self, game: Game, renderer: Renderer):
        self.game = game
        value, row, col = game.insert_new_tile()
        self.tile_manager = renderer.tile_manager
        self.renderer = renderer
        self.tile_manager.append_new_tile(value, row, col, is_first=True)

    def process_event(self, event) -> tuple[bool, bool]:
        """Returns True if the player had won the game, False if he didn't win yet"""
        
        if not self.game.running:
            return False, False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.renderer.user_interface.newgame_rect.collidepoint(event.pos):
                    self.game.should_stop = True
                    return False, True
        if event.type == pygame.KEYDOWN:
            if self.renderer.anim_manager.has_any():
                return False, False 
            changed = False
            bias_matrix = []
            merge_matrix = []
            move = ""
            prev_grid = copy.deepcopy(self.game.grid)
            
            if event.key == pygame.K_LEFT:
                changed, bias_matrix, merge_matrix = self.game.move_left()
                move = "l"
            elif event.key == pygame.K_RIGHT:
                changed, bias_matrix, merge_matrix = self.game.move_right()
                move = "r"
            elif event.key == pygame.K_UP:
                changed, bias_matrix, merge_matrix = self.game.move_up()
                move = "u"
            elif event.key == pygame.K_DOWN:
                changed, bias_matrix, merge_matrix = self.game.move_down()
                move = "d"

            if changed:
                value, row, col = self.game.insert_new_tile()
                self.tile_manager.append_new_move(bias_matrix, move, prev_grid, self.renderer.current_time)
                self.tile_manager.append_new_tile(value, row, col)
                self.tile_manager.append_merge_animation(merge_matrix)

                # Check Victory / Loss
                if self.game.check_victory():
                    self.game.should_stop = True
                    return True, False
                elif not self.game.can_move():
                    self.game.should_stop = True
                

        return False, False

