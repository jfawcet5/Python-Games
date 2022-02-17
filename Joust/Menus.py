""" Class definitions for Joust """

import pygame
import sys

from Misc import *

def main_menu(screen, clock, startGameFunction):
    # This function displays the main menu
    screen.fill(BLACK)

    title_font = pygame.font.SysFont("Corbel", 48)
    title_text = title_font.render("Joust", False, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] //2 , SCREEN_SIZE[1] //2))

    counter = 1
    
    while True:
        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_RETURN):
                    # Start the game using the specified function
                    startGameFunction(screen, clock)
                if (ev.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(FPS)
    return None

def gameOver(screen, clock, score, startGameFunction):
    # This function displays the game over menu
    screen.fill(BLACK)

    title_font = pygame.font.SysFont("Corbel", 48)
    title_text = title_font.render("NICE JOUSTING!", False, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] //2 , SCREEN_SIZE[1] //2 - 50))

    score_font = pygame.font.SysFont("Corbel", 48)
    score_text = score_font.render(f"SCORE: {score}", False, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_SIZE[0] //2 , SCREEN_SIZE[1] //2 + 50))
    
    while True:
        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        screen.blit(score_text, score_rect)

        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_RETURN):
                    main_menu(screen, clock, startGameFunction)
                    return
                if (ev.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(FPS)
    return None
