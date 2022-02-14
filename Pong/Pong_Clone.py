""" Simple pong clone

"""

import pygame
import sys
import random

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

SCREEN_SIZE = (600, 400)

FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PLAYERSCORE = pygame.event.custom_type() # Player score event
AISCORE = pygame.event.custom_type() # AI score event

UPDATESPEED = pygame.event.custom_type() # Update ball speed event
pygame.time.set_timer(UPDATESPEED, 3000)

# Vector2 class to make some calculations easier/more readable
class vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

        self.vector = [x, y]

        sqrMag = ((self.x**2) + (self.y**2))
        self.magnitude = sqrMag**(1/2)
        return

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return (x, y)

    def __sub__(self, other):
        return vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if (isinstance(other, int)):
            x = self.x * other
            y = self.y * other
            return vector2(x, y)
        elif (isinstance(other, float)):
            x = self.x * other
            y = self.y * other
            return vector2(x, y)
        elif (isinstance(other, self.__class__)):
            print("dot product")
        return 

    def getMagnitude(self):
        sqrMag = ((self.x**2) + (self.y**2))
        return sqrMag**(1/2)

    def normalize(self):
        self.magnitude = self.getMagnitude()
        if (self.magnitude != 0):
            invmag = 1 / self.magnitude
        else:
            invmag = 1
        self.x = self.x * invmag
        self.y = self.y * invmag
        return self.__mul__(invmag)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def update(self, x, y):
        self.x = x
        self.y = y
        self.vector = [x, y]

    def set(self, new):
        self.x = new.x
        self.y = new.y
        return None


class ball:
    def __init__(self):
        self.surf = pygame.Surface((10, 10))
        pygame.draw.circle(self.surf, WHITE, (5, 5), 5, 5)

        self.rect = self.surf.get_rect()
        self.rect.centery = 200
        self.rect.centerx = SCREEN_SIZE[0] // 2
        self.position = vector2(self.rect.centerx, self.rect.centery)
        self.velocity = vector2(-2, 0)
        self.speed = 4

    def update(self):
        # Update velocity based on speed
        magnitude = self.velocity.getMagnitude()
        coefficient = self.speed / magnitude
        self.velocity = self.velocity * coefficient
        self.rect.move_ip(self.velocity.x, self.velocity.y)

        # Check for collision with top wall
        if (self.rect.top <= 0):
            self.rect.top = 1
            self.velocity.y *= -1
            return
        # Check for collision with bottom wall
        if (self.rect.bottom >= SCREEN_SIZE[1]):
            self.rect.bottom = SCREEN_SIZE[1] -1
            self.velocity.y *= -1
            return
        self.position.update(self.rect.centerx, self.rect.centery)

class player:
    def __init__(self):
        self.surf_size = (12, 70)
        self.surf = pygame.Surface(self.surf_size)

        self.paddle_size = [8, 50]

        self.position = vector2(0, 0)

        self.rect = self.surf.get_rect()
        pos = ((self.surf_size[0] - self.paddle_size[0]) // 2, (self.surf_size[1] - self.paddle_size[1]) // 2)
        self.r = pygame.draw.rect(self.surf, WHITE, (pos[0], pos[1], 8, 50))
        self.r.centery = self.rect.centery
        self.rect.center = (SCREEN_SIZE[0] - 20, SCREEN_SIZE[1] / 2)
        return

    def move(self, keys_pressed):
        # Move the player paddle based on keyboard input
        if keys_pressed[K_UP]:
            self.rect.move_ip(0, -8)
        if (keys_pressed[K_DOWN]):
            self.rect.move_ip(0, 8)

        # Restrict movement to keep the paddle on the screen
        if ((self.rect.top + self.r.top) < 0):
            self.rect.top = 0 - self.r.top
        if ((self.rect.bottom - self.r.top) >= SCREEN_SIZE[1]):
            self.rect.top = SCREEN_SIZE[1] - self.r.bottom
        return

    def update(self):
        self.position.update(self.rect.centerx, self.rect.centery)
        return

class AI:
    def __init__(self):
        self.surf_size = (12, 70)
        self.surf = pygame.Surface(self.surf_size)

        self.paddle_size = [8, 50]

        self.position = vector2(0, 0)

        self.rect = self.surf.get_rect()
        pos = ((self.surf_size[0] - self.paddle_size[0]) // 2, (self.surf_size[1] - self.paddle_size[1]) // 2)
        self.r = pygame.draw.rect(self.surf, WHITE, (pos[0], pos[1], 8, 50))
        self.r.centery = self.rect.centery
        self.rect.center = (20, SCREEN_SIZE[1] / 2)

        self.speed = 3.5
        return

    def move(self, ball):
        # Move AI paddle based on position of the ball
        if (ball.rect.centerx <= (SCREEN_SIZE[0] // 2)):
            if (self.rect.centery > ball.rect.centery):
                self.rect.move_ip(0, -1* self.speed)
            if (self.rect.centery < ball.rect.centery):
                self.rect.move_ip(0, self.speed)

    def update(self):
        self.position.update(self.rect.centerx, self.rect.centery)
        return

# Background class manages the dashed lines and score displays
class background:
    def __init__(self):
        self.font = pygame.font.SysFont("Corbel", 75)

        self.playerscore = 0
        self.AIscore = 0

        self.rectangles = []

        y = 0
        while (y < SCREEN_SIZE[1]):
            self.rectangles.append(pygame.Rect(SCREEN_SIZE[0] //2, y, 1, 12))
            y += 20

    def update(self, board):
        # Update scores
        pScoreSurf = self.font.render(str(self.playerscore), True, WHITE)
        aScoreSurf = self.font.render(str(self.AIscore), True, WHITE)

        # Draw dashed lines
        for rectangle in self.rectangles:
            pygame.draw.rect(board, WHITE, rectangle)

        # Draw updated scores
        xpos = (SCREEN_SIZE[0] // 2) - (SCREEN_SIZE[0] // 4)
        board.blit(aScoreSurf, (xpos, 50))
        xpos = (SCREEN_SIZE[0] // 2) + (SCREEN_SIZE[0] // 4)
        board.blit(pScoreSurf, (xpos, 50))

def lerp(a, b, f):
    return (1-f)*a + f*(b)

def collide(ball, player, AI):
    # Check for collision with right wall
    if (ball.rect.right >= SCREEN_SIZE[0]): # AI scored a point
        pygame.event.post(pygame.event.Event(AISCORE))
        return
    # Check for collision with left wall
    if (ball.position.x < AI.rect.left): # Player scored a point
        pygame.event.post(pygame.event.Event(PLAYERSCORE))
        return
    if (ball.rect.right >= player.rect.left):
        if ((ball.rect.top >= player.rect.top) and (ball.rect.bottom <= player.rect.bottom)):
            ball.rect.right = player.rect.left - 1

            # playerpos is the point in world space that is used to calculate the bounce
            # of the ball off the paddle. The x coordinate is the right edge of the screen
            # instead of the center of the paddle to make sure that the ball is given a reasonable
            # velocity in the x coordinate
            playerpos = vector2(SCREEN_SIZE[0], player.position.y)
            paddle2ball = ball.position - playerpos

            paddle2ball.normalize()

            ball.velocity.set(paddle2ball * ball.speed)
            return
    elif (ball.rect.left <= AI.rect.right):
        if ((ball.rect.top >= AI.rect.top) and (ball.rect.bottom <= AI.rect.bottom)): 
            ball.rect.left = AI.rect.right + 1

            AIpos = vector2(0, AI.position.y)
            paddle2ball = ball.position - AIpos

            paddle2ball.normalize()

            ball.velocity.set(paddle2ball * ball.speed)

def main():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    circle = ball()
    player_paddle = player()
    AI_paddle = AI()
    bg = background()

    # List of moving objects
    all_objects = [circle, player_paddle, AI_paddle]

    clock = pygame.time.Clock()
    
    while True: # Game Loop
        # Refresh screen
        screen.fill(BLACK)

        # Check for collisions between ball, player paddle, and AI paddle
        collide(circle, player_paddle, AI_paddle)
        
        for ob in all_objects: # Draw objects to the screen
            screen.blit(ob.surf, ob.rect)

        for ev in pygame.event.get():
            if ev.type == UPDATESPEED: # Update ball speed event
                if (circle.speed <= 15):
                    circle.speed += 1
                    AI_paddle.speed += 0.75

            elif ev.type == PLAYERSCORE: # Player score event
                bg.playerscore += 1
                circle.rect.centerx = (SCREEN_SIZE[0] // 2)
                circle.speed = 5
                AI_paddle.speed = 3.5

            elif ev.type == AISCORE: # AI score event
                bg.AIscore += 1
                circle.rect.centerx = (SCREEN_SIZE[0] // 2)
                circle.speed = 5
                AI_paddle.speed = 3.5
            
            elif ev.type == QUIT: # Pygame quit event
                pygame.quit()
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        bg.update(screen) # Update the background

        # Update objects
        for ob in all_objects:
            ob.update()

        # Update player and AI position
        player_paddle.move(keys_pressed)
        AI_paddle.move(circle)
    
        pygame.display.update()
        clock.tick(FPS)
    return None

main()
