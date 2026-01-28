"""
Main entry point for the 2048 Game.
Architecture:
- Game: game logic
- Renderer: drawing UI
- Controller: player input
"""

import sys

import pygame

from game import Controller, Game, GameState, Renderer

FPS = 60


def main():
    pygame.init()
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()

    while True:
        game = Game(size=3)
        renderer = Renderer(game)
        controller = Controller(game, renderer)

        game_state = run_single_game(clock, controller, renderer)

        if game_state == GameState.RESTARTING:
            continue
        elif game_state == GameState.VICTORY:
            renderer.overlay.render_victory(renderer.WIDTH, renderer.HEIGHT)
        elif game_state == GameState.GAME_OVER:
            renderer.overlay.render_game_over(renderer.WIDTH, renderer.HEIGHT)

        wait_for_restart(clock)


def run_single_game(
    clock: pygame.time.Clock, controller: Controller, renderer: Renderer
) -> GameState:
    game_state = GameState.PLAYING

    while game_state == GameState.PLAYING:
        dt = clock.tick(FPS)

        # Check if controller is waiting to declare victory / game over
        # every frame
        game_state = controller.process_event(None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game_state = controller.process_event(event)

        renderer.render(dt)

    return game_state


def wait_for_restart(clock: pygame.time.Clock) -> None:
    waiting_for_restart = True
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
