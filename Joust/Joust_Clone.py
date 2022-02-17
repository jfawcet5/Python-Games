""" Implementation of Joust in Python with Pygame


    Future Development:
        - Pteradactyl
        - Lava Troll
        - Enemy walking animation
        - More waves
"""

from Waves import *
from Menus import *
from Misc import *
from Environment import Platform

pygame.init()

# ============================================================== Main Menu ==============================================================   

def main():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    main_menu(screen, clock, gameLoop)
    return

if __name__ == "__main__":
    main()
