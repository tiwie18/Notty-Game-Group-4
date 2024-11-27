from pickle import GLOBAL

import pygame
from pygame.locals import *
import random
from enum import Enum
import os
import scripts.configs as configs
from scripts.ui_base import *
from scripts.screen_base import *
from scripts.screens import *
import scripts.global_variables as global_variables
import scripts.math_util as math_util


# Main game loop
def main():
    # Initialize pygame
    pygame.init()

    # Set the window dimensions
    screen = pygame.display.set_mode((configs.WINDOW_WIDTH, configs.WINDOW_HEIGHT))
    pygame.display.set_caption('Card Game Funt4stic Te4m')

    # Start with the home screen
    global_variables.current_screen = StartScreen()
    global_variables.game_over = False

    while not global_variables.game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                global_variables.game_over = True
            if event.type == MOUSEBUTTONUP:
                global_variables.current_screen.mouseup(event)
            if event.type == KEYDOWN:
                global_variables.current_screen.keydown(event)

        # Update game state
        global_variables.current_screen.update()

        # Draw everything
        global_variables.current_screen.draw(screen)

        # Update the screen
        pygame.display.flip()

        # Delay to limit frame rate
        pygame.time.delay(30)

    pygame.quit()

if __name__ == "__main__":
    main()
