""" Class definitions for Joust """
import pygame
import sys
import random

from Misc import *
from Agents import Bounder, Hunter, ShadowLord, EBJ

# Class to display and manage platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, position, size, image=None):
        super(Platform, self).__init__()
        if (image is None):
            self.surf = pygame.Surface(size)
            self.surf.fill((140, 60, 10))
        else:
            self.surf = pygame.image.load(image).convert()
            self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=position)

        self.isSpawnLocation = False
        self.spawnPos = ()

    def setSpawn(self, location):
        self.spawnPos = location
        self.isSpawnLocation = True

# Container for an object that is temporarily rendered to the screen
# to display points where eggs are destroyed
class PointDisplay:
    def __init__(self, position, points, bonusPoints):
        self.font = pygame.font.SysFont("Courier New", 14, bold=False)

        self.points_text = self.font.render(f"{points}", False, YELLOW)
        self.points_rect = self.points_text.get_rect(center=(position))
        
        self.bonus_text = self.font.render(f"{bonusPoints}", False, GREEN)
        self.bonus_rect = self.bonus_text.get_rect(center=(position[0], position[1] -15))

        self.counter = 0
        self.duration = FPS * 1.5

    def render(self, screen):
        screen.blit(self.points_text, self.points_rect)
        screen.blit(self.bonus_text, self.bonus_rect)

    def update(self):
        if (self.counter >= self.duration):
            return 1
        self.counter += 1
        return 0

# Class to manage the displaying of points on the screen
class PointManager:
    def __init__(self):
        self.pointDisplays = []
        self.pointsPerEgg = 250
        self.bonusPointsPerEgg = 500

    def add(self, pointDisplay):
        # Add a new point display
        self.pointDisplays.append(pointDisplay)
        self.pointsPerEgg = min(self.pointsPerEgg + 250, 1000)
        return None

    def render(self, screen):
        # Render all point displays
        for display in self.pointDisplays:
            display.render(screen)

    def reset(self):
        # Losing a mount causes egg value to be reset to base value
        self.pointsPerEgg = 250

    def update(self):
        # Update point displays
        for display in self.pointDisplays:
            retval = display.update()
            if (retval == 1):
                self.pointDisplays.remove(display)
        return None

# Container to hold an object that displays a mount icon on the screen
class MountIcon:
    def __init__(self, position):
        self.surf = pygame.image.load(MOUNT_ICON).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)

        self.rect = self.surf.get_rect(topleft=(position))

# Class to manage and render the total points and remaining mounts
class MainDisplay:
    def __init__(self, mountDisplayPosition, points=0):
        self.font = pygame.font.SysFont("QuickType 2", 26, bold=False)

        self.textposition = (mountDisplayPosition[0] - 3, mountDisplayPosition[1] + 2)

        self.points_text = self.font.render(f"{points}", False, BRIGHT_YELLOW)
        self.points_rect = self.points_text.get_rect(topright=(self.textposition))

        self.remainingMounts = 4

        self.mountIcons = []
        for i in range(5): # Max # of mounts is 5
            icon = MountIcon(mountDisplayPosition)
            self.mountIcons.append(icon)
            mountDisplayPosition = (mountDisplayPosition[0] + 10, mountDisplayPosition[1])
        return None

    def render(self, screen):
        # Render mounts and points
        for i in range(self.remainingMounts):
            curIcon = self.mountIcons[i]
            screen.blit(curIcon.surf, curIcon.rect)

        screen.blit(self.points_text, self.points_rect)

    def update(self, points, mounts):
        # Update points and mounts
        self.points_text = self.font.render(f"{points}", False, BRIGHT_YELLOW)
        self.points_rect = self.points_text.get_rect(topright=(self.textposition))

        self.remainingMounts = mounts
        return None

# Class to manage the lava
class Lava(pygame.sprite.Sprite):
    def __init__(self):
        super(Lava, self).__init__()
        self.surf = pygame.Surface((SCREEN_SIZE[0], 70))
        self.surf.fill((200, 120, 10))
        self.rect1 = self.surf.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 30))

        self.rect = pygame.Rect(0, SCREEN_SIZE[1], SCREEN_SIZE[0], 1)
        self.color = (200, 120, 10)

        self.maxHeight = 40

        self.counter = 0

        self.moveCounter = 0
        self.lavaMoveSpeed = FPS // 3

    def moveUp(self):
        # Increases the height of the lava
        if self.moveCounter == 0:
            if (self.rect.top > SCREEN_SIZE[1] - self.maxHeight):
                newtop = self.rect.top - 4
                newHeight = self.rect.height + 4
                self.rect.update(0, newtop, self.rect.width, newHeight)

        self.moveCounter = (self.moveCounter + 1) % self.lavaMoveSpeed

    def update(self, waveNum):
        # Updates the height of the lava based on current wave
        if waveNum == 2:
            self.maxHeight = 55
        elif waveNum == 3:
            self.maxHeight = 75

        self.moveUp()
        return None

# Stores and manages everything related to the game loop
class Env:
    def __init__(self, listOfPlatforms, Player, Screen, Clock):
        self.platformList = listOfPlatforms
        self.activePlatforms = listOfPlatforms

        self.player = Player
        self.screen = Screen
        self.clock = Clock

        self.enemyGroup = pygame.sprite.Group()
        self.eggGroup = pygame.sprite.Group()

        self.pointManager = PointManager()

        Plat9 = listOfPlatforms[8]
        self.mainDisplay = MainDisplay((Plat9.rect.left + 106, Plat9.rect.top + 15))

        self.lava = Lava()

        self.wave = 1

    def updatePlatforms(self, indices):
        # Update active platforms
        temp = []
        for index in indices:
            temp.append(self.platformList[index])

        self.activePlatforms = temp
        return None

    def get(self):
        # Get all of the objects related to the gameplay
        values = self.screen, self.clock, self.player, self.enemyGroup, self.eggGroup, self.pointManager, self.mainDisplay
        return values

    def addEnemy(self, eType, position):
        # Add an enemy of a particular type
        temp = None
        if eType == 2:
            temp = ShadowLord(position)
        elif eType == 1:
            temp = Hunter(position)
        else:
            temp = Bounder(position)

        if temp is not None:
            self.enemyGroup.add(temp)
        return None

    def getSpawnLocations(self):
        # Retrieve active spawn locations
        loc = []
        for plat in self.activePlatforms:
            if plat.isSpawnLocation:
                loc.append(plat.spawnPos)
        return loc

    def render(self):
        # Render each of the platforms and lava
        self.screen.fill(self.lava.color, self.lava.rect)

        for plat in self.activePlatforms:
            self.screen.blit(plat.surf, plat.rect)

        self.mainDisplay.render(self.screen)

        self.pointManager.render(self.screen)

    def update(self):
        # Update the env

        self.pointManager.update()
        self.mainDisplay.update(self.player.points, self.player.lives)

        self.lava.update(self.wave)
