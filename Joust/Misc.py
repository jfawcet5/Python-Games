""" Miscellaneous definitions that are used throughout the project """

# Size of screen
SCREEN_SIZE = (600,600)

# Framerate for game
FPS = 60

# Pygame constants
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_x,
    K_ESCAPE,
    K_RETURN,
    KEYUP,
    KEYDOWN,
    QUIT,
)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 80)
YELLOW = (180, 180, 10)
BRIGHT_YELLOW = (255, 255, 0)

# Platform images
PLATFORM1 = "Art/Platform1.png"     # Top center platform
PLATFORM23 = "Art/Platform2-3.png"  # Top right and top left platforms
PLATFORM4 = "Art/Platform4.png"     # Middle left platform
PLATFORM5 = "Art/Platform5.png"     # Middle center platform
PLATFORM6 = "Art/Platform6.png"     # Middle right platform 1
PLATFORM7 = "Art/Platform7.png"     # Middle right platform 2
PLATFORM8 = "Art/TestPlat.png" 

# Player images
PLAYER_IDLE_GROUND = "Art/Player_Idle_g.png"
PLAYER_IDLE_AIR = "Art/Player_Idle_a.png"
PLAYER_FLAP = "Art/Player_Flap.png"
PLAYER_RESPAWN = ["Art/Player_Respawn1.png", "Art/Player_Respawn2.png", "Art/Player_Respawn3.png"]
PLAYER_WALK = ["Art/Player_Walk1.png", "Art/Player_Walk2.png", "Art/Player_Walk3.png", "Art/Player_Walk4.png"]
PLAYER_SLIDE = "Art/Player_Slide.png"

# Egg image
EGG = "Art/Egg.png"

# Bird image
BIRD_IDLE_G = "Art/Bird_Idle_G.png"
BIRD_IDLE_A = "Art/Bird_Idle_A.png"
BIRD_FLAP = "Art/Bird_Flap.png"

# Bounder images
BOUNDER_IDLE_A = "Art/Bounder_Idle_A.png"
BOUNDER_IDLE_G = "Art/Bounder_Idle_G.png"
BOUNDER_FLAP = "Art/Bounder_Flap.png"
RED_JOUSTER = "Art/Bounder_J.png"

# Hunter images
HUNTER_IDLE_A = "Art/Hunter_Idle_A.png"
HUNTER_IDLE_G = "Art/Hunter_Idle_G.png"
HUNTER_FLAP = "Art/Hunter_Flap.png"
GREY_JOUSTER = "Art/Hunter_J.png"

# Shadow lord images
SHADOWLORD_IDLE_A = "Art/Shadow_Lord_Idle_A.png"
SHADOWLORD_IDLE_G = "Art/Shadow_Lord_Idle_G.png"
SHADOWLORD_FLAP = "Art/Shadow_Lord_Flap.png"
BLUE_JOUSTER = "Art/Shadow_Lord_J.png"

# Mount icon
MOUNT_ICON = "Art/MountIcon.png"

# enemy spawns per wave. 0 = bounder, 1 = hunter, 2 = shadow lord
waveSpawns = [[0, 0, 0],               # Wave 1
              [0, 0, 0, 0],            # Wave 2
              [0, 0, 0, 0, 0, 0],      # Wave 3
              [0, 0, 0, 1, 1],         # Wave 4
              [],                      # Wave 5
              [0, 0, 0, 1, 1, 1],      # Wave 6
              [0, 0, 1, 1, 1, 1],      # Wave 7
              [],                      # Wave 8
              [1, 1, 1, 1, 1, 1],      # Wave 9
              [],                      # Wave 10
              [0, 0, 0, 1, 1, 1, 1, 1],# Wave 11
              [0, 0, 1, 1, 1, 1, 1, 1],# Wave 12
              [],                      # Wave 13
              [1, 1, 1, 1, 1, 1, 1, 1],# Wave 14
              [],                      # Wave 15
              [1, 1, 1, 1, 1, 2],      # Wave 16
              [1, 1, 1, 1, 1, 2],      # Wave 17
              [],                      # Wave 18
              [1, 1, 1, 1, 2, 2],      # Wave 19
              [],                      # Wave 20
              [1, 1, 1, 2, 2, 2],      # Wave 21
              [1, 1, 2, 2, 2, 2],      # Wave 22
              [],                      # Wave 23
              []                       # Wave 24
             ]

# Active platforms per wave
platforms = [[0, 1, 2, 3, 4, 5, 6, 7, 8], # Wave 1
             [0, 1, 2, 3, 4, 5, 6, 7, 8], # Wave 2
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 3
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 4
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 5
             [1, 2, 3, 4, 5, 6, 8],       # Wave 6
             [3, 4, 5, 6, 8],             # Wave 7
             [3, 4, 5, 6, 8],             # Wave 8
             [3, 5, 6, 8],                # Wave 9
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 10
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 11
             [0, 1, 2, 3, 5, 6, 8],       # Wave 12
             [3, 5, 6, 8],                # Wave 13
             [3, 5, 6, 8],                # Wave 14
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 15
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 16
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 17
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 18
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 19
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 20
             [0, 3, 4, 5, 6, 8],          # Wave 21
             [0, 3, 4, 5, 6, 8],          # Wave 22
             [0, 3, 5, 6, 8],             # Wave 23
             [0, 3, 5, 6, 8],             # Wave 24
             [0, 1, 2, 3, 4, 5, 6, 8],    # Wave 25
             [3, 5, 6, 8],                # Wave 26
             [3, 5, 6, 8],                # Wave 27
             [3, 5, 6, 8],                # Wave 28
             [3, 5, 6, 8],                # Wave 29
             [0, 1, 2, 3, 4, 5, 6, 8]     # Wave 25
            ]

# 2 dimensional vector class 
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

        self.vector = [x, y]

        sqrMag = ((self.x**2) + (self.y**2))
        self.magnitude = sqrMag**(1/2)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x, y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if (isinstance(other, int)):
            x = self.x * other
            y = self.y * other
            return Vector2(x, y)
        elif (isinstance(other, float)):
            x = self.x * other
            y = self.y * other
            return Vector2(x, y)
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

    def dot(self, v):
        return (self.x * v.x) + (self.y * v.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def update(self, x, y):
        self.x = x
        self.y = y
        return None
