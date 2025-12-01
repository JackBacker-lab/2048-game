"""
Main entry point for the 2048 Game.
Architecture:
- Game: game logic
- Renderer: drawing UI
- Controller: player input
"""

import pygame
import sys

from game import Game
from renderer import Renderer
from controller import Controller


FPS = 60


def main():
    pygame.init()
    clock = pygame.time.Clock()

    # Core modules
    game = Game(size=4)
    renderer = Renderer(game)
    controller = Controller(game)

    screen = renderer.create_window()
    pygame.display.set_caption("2048")

    did_user_win = False
    # Main loop
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            did_user_win = controller.process_event(event)

        renderer.render(screen)
        pygame.display.update()

        clock.tick(FPS)

    # Game over or victory screen
    if did_user_win:
        renderer.render_victory(screen)
    else:
        renderer.render_game_over(screen)
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()


if __name__ == "__main__":
    main()
