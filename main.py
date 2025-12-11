"""
Main entry point for the 2048 Game.
Architecture:
- Game: game logic
- Renderer: drawing UI
- Controller: player input
"""

import pygame
import sys

from core.game import Game
from rendering.renderer import Renderer
from input.controller import Controller


FPS = 60


def main():
    pygame.init()
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()

    while True:
        game = Game(size=4)
        renderer = Renderer(game)
        controller = Controller(game, renderer)

        did_user_win = False
        did_user_restart = False
        waiting_for_restart = True

        while game.running:
            dt = clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                result, did_user_restart = controller.process_event(event)
                if result:
                    did_user_win = True

            renderer.render(dt)

            if game.should_stop:
                if not renderer.tile_manager.anim_manager.has_any():
                    game.running = False

        if did_user_win:
            renderer.overlay.render_victory(renderer.WIDTH, renderer.HEIGHT)
        elif not did_user_win and not did_user_restart:
            renderer.overlay.render_game_over(renderer.WIDTH, renderer.HEIGHT)
        else:
            waiting_for_restart = False

        pygame.display.update()
        
        while waiting_for_restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                        waiting_for_restart = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            clock.tick(30)


if __name__ == "__main__":
    main()
