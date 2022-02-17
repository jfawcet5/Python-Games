""" Function definitions for the different types of waves """

import pygame
import random
import sys

from Environment import Env, PointManager, PointDisplay, Platform
from Menus import main_menu, gameOver

from Agents import Player, EBJ

from Misc import *

def killAllEnemies(env):
    for e in env.enemyGroup:
        env.enemyGroup.remove(e)

    for e in env.eggGroup:
        env.eggGroup.remove(e)

    return None

def getRandomLocationOnPlatform(platform):
    # Generate a random position on a specified platform
    ypos = platform.rect.top - 6
    xpos = random.randint(platform.rect.left + 10, platform.rect.right - 10)
    if (xpos > SCREEN_SIZE[0]):
        xpos  = SCREEN_SIZE[0] - 10
    elif (xpos < 0):
        xpos = 10
    return (xpos, ypos)


def collision(env, platformGroup):
    """ This function is responsible for handling collisions between all moving game objects
    """
    screen, clock, player, enemies, eggGroup, pointManager, mainDisplay = env.get()

    # Check enemy collisions
    for e1 in enemies:
        if (e1.alive == 1): # If enemy is alive
            if (player.state != 5): # If player in not invincible (respawning)
                if e1.rect.colliderect(player.rect): # Enemy collision with player
                    dist = Vector2(e1.rect.centerx - player.rect.centerx, e1.rect.centery - player.rect.centery) * (1/12)
                    
                    if (dist.y < 0): # Enemy is above player
                        e1.velocity.y = dist.y
                        e1.velocity.x *= -1
                        player.die(env.getSpawnLocations())
                        pointManager.reset()
                        
                    elif (dist.y > 0): # Player is above enemy
                        player.velocity = dist * -1
                        if (e1.type == 0):
                            player.points += 500
                        elif (e1.type == 1):
                            player.points += 750
                        elif (e1.type == 2):
                            player.points += 1500
                        e1.die()
                        newEgg = EBJ(e1.rect.center, e1.velocity, e1.type, platformGroup)
                        eggGroup.add(newEgg)
                        enemies.remove(e1)
                        
                    else: # Enemy and Player are at the same height
                        e1.velocity = dist
                        e1.velocity.x *= 1.5
                        player.velocity = dist * -1
            # Check collisions between other enemies
            for e2 in enemies:
                if (e2 != e1):
                    if (e1.rect.colliderect(e2.rect)):
                        dist = Vector2(e1.rect.centerx - e2.rect.centerx, e1.rect.centery - e2.rect.centery)
                        if e1.velocity.x * e2.velocity.x > 0: # If enemies are moving in the same direction
                            if e1.velocity.x > 0: # Both enemies moving to the right
                                # Left most enemy will change direction
                                if dist.x > 0:
                                    e2.rect.right = e1.rect.left - 1
                                    e1.rect.left = e2.rect.right + 1
                                    e2.velocity.x *= -1
                                else:
                                    e1.rect.right = e2.rect.left - 1
                                    e2.rect.left = e1.rect.right + 1
                                    e1.velocity.x *= -1
                            else: # Both enemies moving to the left
                                # Right most enemy will change direction
                                if dist.x > 0:
                                    e2.rect.right = e1.rect.left - 1
                                    e1.rect.left = e2.rect.right + 1
                                    e1.velocity.x *= -1
                                else:
                                    e1.rect.right = e2.rect.left - 1
                                    e2.rect.left = e1.rect.right + 1
                                    e2.velocity.x *= -1
                        else: # Head on collision
                            # Both enemies change direction
                            if dist.x > 0:
                                e2.rect.right = e1.rect.left - 1
                                e1.rect.left = e2.rect.right + 1
                            else:
                                e1.rect.right = e2.rect.left - 1
                                e2.rect.left = e1.rect.right + 1
                            e1.velocity.x *= -1
                            e2.velocity.x *= -1
                        e2.velocity.y = 0
                        e1.velocity.y = 0
                        pass

    # Check egg collisions
    for e in eggGroup:
        if e.egg.rect.colliderect(player.rect): # Egg collision with player
            # award player points
            pointsToAdd = pointManager.pointsPerEgg
            bonus = ''
            if (not player.grounded):
                bonus = pointManager.bonusPointsPerEgg
                pointsToAdd += bonus

            player.points += pointsToAdd
            points = pointManager.pointsPerEgg
            displayPosition = (e.egg.rect.centerx, e.egg.rect.top)
            d = PointDisplay((displayPosition), points, bonus)
            pointManager.add(d)
            e.destroy()

        if (e.egg.rect.colliderect(env.lava.rect)): # Egg collision with lava
            eggGroup.remove(e)

    # Player collision with lava
    if (player.rect.colliderect(env.lava.rect)):
        player.die(env.getSpawnLocations())

    return None

def renderFrame(env, platformGroup):
    """ This function renders all of the appropriate objects to the screen during the
        current frame. All of the objects passed in as parameters will be drawn to the screen
        in the following order: platforms, text displays (score/lives/etc.), Eggs/Bird/Jousters,
        Enemies, player
    """
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()

    env.render()

    for egg in eggGroup: # Render Egg/Birds/Jousters
            egg.render(screen)

    for enemy in enemyGroup: # Render enemies
            screen.blit(enemy.surf, enemy.rect)

    screen.blit(player.surf, player.rect) # Render the player
    return None

def updateFrame(env, platformGroup, pressedKeys):
    """ This function is used to update all of the game objects during the current frame. 
    """
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()
    player.update(pressedKeys, platformGroup) # Update the player

    if player.lives < 0:
        gameOver(screen, clock, player.points, gameLoop)

    for egg in eggGroup: # Update each Egg/Bird/Jouster
        retVal = egg.update(platformGroup, player)
        if (retVal == 1):
            enemy = egg.spawn()
            enemyGroup.add(enemy)
            eggGroup.remove(egg)

        elif (retVal == 2):
            eggGroup.remove(egg)

    for e in enemyGroup: # Update each enemy
        e.update(platformGroup, player)

    collision(env, platformGroup) # Collisions between player and enemies

    env.update()
    return None

def displayCurrentWave(env, wave):
    """ This function runs a simple game loop for 3 seconds while displaying
        the current wave number. 
    """
    # Displays current wave for 3 seconds
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()

    platformGroup = pygame.sprite.Group()
    for plat in env.activePlatforms:
        platformGroup.add(plat)

    timer = 0
    threeSeconds = FPS * 3

    display_font = pygame.font.SysFont("Courier New", 24, bold=False)
    current_wave_text = display_font.render(f"WAVE {wave}", False, WHITE)
    current_wave_rect = current_wave_text.get_rect(center=((SCREEN_SIZE[0] //2) - 20, (SCREEN_SIZE[1] //2) - 70))

    bonus_string1 = ""
    bonus_string2 = ""

    if (wave % 5 == 0):
        # Egg wave
        bonus_string1 = "EGG WAVE"
    elif ((wave - 2) % 5 == 0):
        # survival wave
        bonus_string1 = "SURVIVAL WAVE"
    elif ((wave > 7) and(wave - 3) % 5 == 0):
        pass
    else:
        # generic wave
        if (wave == 1):
            bonus_string1 = "PREPARE TO JOUST"
            bonus_string2 = "BUZZARD BAIT!"
    
    bonus_text1 = display_font.render(bonus_string1, False, WHITE)
    bonus_rect1 = bonus_text1.get_rect(center=((SCREEN_SIZE[0] //2) - 20, (SCREEN_SIZE[1] //2) - 30))

    bonus_text2 = display_font.render(bonus_string2, False, WHITE)
    bonus_rect2 = bonus_text2.get_rect(center=((SCREEN_SIZE[0] //2) - 20, (SCREEN_SIZE[1] //2) + 10))

    while True:
        screen.fill(BLACK)

        if (timer >= threeSeconds):
            return None

        screen.blit(current_wave_text, current_wave_rect)
        screen.blit(bonus_text1, bonus_rect1)
        screen.blit(bonus_text2, bonus_rect2)

        # Input handling below this line
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_SPACE):
                    player.flap()
                if (ev.key == K_ESCAPE):
                    return -1
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed() # Store player inputs

        # Updates below this line
        player.update(pressed, platformGroup) # Update the player

        pointManager.update()
        mainDisplay.update(player.points, player.lives)

        renderFrame(env, platformGroup)
        
        pygame.display.update()
        clock.tick(FPS)

        timer += 1

def genericWave(env, wave):
    """ The genericWave() function specifies the behavior of the game loop for any
        non-special waves.

        During a generic wave, a specified number of enemies will spawn (as described by
        the 'waveSpawns' list at the top of this file), and the wave will not end until all
        of the enemy jousters have been unseated with their eggs destroyed. 
    """
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()
    pointManager.reset()

    displayCurrentWave(env, wave)

    env.updatePlatforms(platforms[wave - 1])
    platformGroup = pygame.sprite.Group()
    for plat in env.activePlatforms:
        platformGroup.add(plat)

    spawn_locations = env.getSpawnLocations()
    numSpawns = len(spawn_locations) - 1

    # First thing to do is spawn enemies. We will spawn 1 enemy every X frames until we reach the appropriate
    # number of enemies for the current wave. After all of the enemies have been spawned, we check if the number
    # of enemies remaining hits 0, after which the function will return.

    enemySpawns = waveSpawns[wave - 1]
    
    numberOfEnemies = len(enemySpawns)
    numSpawned = 0

    counter = FPS

    while True:
        env.screen.fill(BLACK)

        # Input handling below this line
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_SPACE):
                    player.flap()
                if (ev.key == K_ESCAPE):
                    return -1
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed() # Store player inputs

        if (numSpawned < numberOfEnemies):
            counter += 1
            if (counter > (FPS * 3)):
                # Spawn enemy
                eType = enemySpawns[numSpawned]
                spawnPos = spawn_locations[random.randint(0, numSpawns)]
                env.addEnemy(eType, spawnPos)
                numSpawned += 1
                counter = 0
        else:
            # If no more enemies/eggs then the wave is over and we exit this function
            if (len(eggGroup) + len(enemyGroup) == 0):
                return 0

        # Updates go below this line
        updateFrame(env, platformGroup, pressed)

        # Rendering goes below this line
        renderFrame(env, platformGroup)

        pygame.display.update()
        env.clock.tick(FPS)
    return None


def survivalWave(env, wave):
    """ The survivalWave() function specifies the behavior of the game loop for the
        survival wave. 

        A survival wave is the same as a generic wave, except the player receives a
        bonus of 3000 points if they are able to complete the wave without losing a
        mount
    """
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()
    pointManager.reset()

    displayCurrentWave(env, wave)

    env.updatePlatforms(platforms[wave - 1])
    platformGroup = pygame.sprite.Group()
    for plat in env.activePlatforms:
        platformGroup.add(plat)

    spawn_locations = env.getSpawnLocations()
    numSpawns = len(spawn_locations) - 1

    # First thing to do is spawn enemies. We will spawn 1 enemy every X frames until we reach the appropriate
    # number of enemies for the current wave. After all of the enemies have been spawned, we check if the number
    # of enemies remaining hits 0, after which the function will return.
    enemySpawns = waveSpawns[wave - 1]
    
    numberOfEnemies = len(enemySpawns)
    numSpawned = 0

    counter = FPS

    playerLostMount = False
    playerStartingLives = player.lives
    while True:
        screen.fill(BLACK)

        # Input handling below this line
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_SPACE):
                    player.flap()
                if (ev.key == K_ESCAPE):
                    return -1
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed() # Store player inputs

        if (numSpawned < numberOfEnemies):
            counter += 1
            if (counter > (FPS * 3)):
                # Spawn enemy
                eType = enemySpawns[numSpawned]
                spawnPos = spawn_locations[random.randint(0, numSpawns)]
                env.addEnemy(eType, spawnPos)
                numSpawned += 1
                counter = 0
        else:
            # If no more enemies/eggs then the wave is over and we exit this function
            if (len(eggGroup) + len(enemyGroup) == 0):
                if playerLostMount == False:
                    player.points += 3000
                return 0

        # Updates go below this line
        updateFrame(env, platformGroup, pressed)

        if player.lives < playerStartingLives:
            playerLostMount = True

        # Rendering goes below this line
        renderFrame(env, platformGroup)

        pygame.display.update()
        clock.tick(FPS)
    return None


def eggWave(env, wave):
    """ The eggWave() function specifies the behavior of the game loop for the
        egg wave. 

        An egg wave starts with several eggs spawning randomly throughout each of
        the platforms. The player must hurry to destroy each of the eggs before they
        hatch, after which the jouster can re-mount the bird. The wave ends after all
        eggs are destroyed and no enemy jousters remain. 
    """
    screen, clock, player, enemyGroup, eggGroup, pointManager, mainDisplay = env.get()
    pointManager.reset()

    displayCurrentWave(env, wave)

    env.updatePlatforms(platforms[wave - 1])
    platformGroup = pygame.sprite.Group()
    for plat in env.activePlatforms:
        platformGroup.add(plat)

    spawn_locations = env.getSpawnLocations()
    numSpawns = len(spawn_locations) - 1

    numEggs = min(12, 10 + (wave // 5)) # Number of eggs spawned is determined by this line

    for i in range(numEggs):
        loc = random.randint(0, 7)
        xpos, ypos = getRandomLocationOnPlatform(env.activePlatforms[loc])
        
        e = EBJ((xpos, ypos), Vector2(), 0, platformGroup)
        while (e.collideAny(eggGroup)): # This loop makes sure none of the eggs are on top of each other
            loc = random.randint(0, 7)
            xpos, ypos = getRandomLocationOnPlatform(env.activePlatforms[loc])
            e = EBJ((xpos, ypos), Vector2(), 0, platformGroup)
        eggGroup.add(e)

    while True:
        screen.fill(BLACK)

        # Input handling below this line
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_SPACE):
                    player.flap()
                if (ev.key == K_ESCAPE):
                    return -1
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed() # Store player inputs

        # Updates go below this line
        # If no more enemies/eggs then the wave is over and we exit this function
        if (len(eggGroup) + len(enemyGroup) == 0):
            return 0
        
        updateFrame(env, platformGroup, pressed)

        # Rendering goes below this line
        renderFrame(env, platformGroup)

        pygame.display.update()
        clock.tick(FPS)


def gameLoop(screen, clock):
    """ This function manages the structure of the game by calling the appropriate
        function for each wave. gameLoop() iterates through the different types
        of waves until either the player has died, or the wave limit has been reached. 
    """
    screen.fill(BLACK) # Clear the previous screen display

    Plat1 = Platform((SCREEN_SIZE[0] // 2 - 40, 200), (160, 8), PLATFORM1) # Top middle plat
    Plat2 = Platform((SCREEN_SIZE[0] - 20, 190), (110, 8), PLATFORM23) # Top right plat
    Plat3 = Platform((-40, 190), (80, 8), PLATFORM23) # Top left plat
    Plat4 = Platform((20, SCREEN_SIZE[1] //2 + 30), (120, 8), PLATFORM4) # Bottom left plat
    Plat5 = Platform((SCREEN_SIZE[0] // 2 - 30, SCREEN_SIZE[1] //2 + 80), (120, 8), PLATFORM5) # Bottom middle plat
    Plat6 = Platform((SCREEN_SIZE[0] - 35, SCREEN_SIZE[1] //2 + 28), (80, 8), PLATFORM6) # Right connect plat
    Plat7 = Platform((SCREEN_SIZE[0] - 125, SCREEN_SIZE[1] //2 + 18), (90, 8), PLATFORM7) # Left connected plat
    Plat8 = Platform((SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 96), (640, 8)) # Bottom plat #1
    Plat9 = Platform((SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 50), (320, 100), PLATFORM8) # Bottom plat #2

    # Initialize spawn positions on platforms
    Plat9.setSpawn((288, 479))
    Plat7.setSpawn((490, 288))
    Plat4.setSpawn((25, 304))
    Plat1.setSpawn((234, 175))

    listOfPlatforms = [Plat1, Plat2, Plat3, Plat4, Plat5, Plat6, Plat7, Plat8, Plat9]

    player = Player() # Create player

    env = Env(listOfPlatforms, player, screen, clock)
    
    wave = 1
    
    # Survival waves: 2, 7, 12, 17...
    # Egg waves: 5, 10, 15, 20...
    # Pteradactyl waves: 8, 13, 18, 23...
    # Normal wave: Anything in between
    while True:
        env.wave = wave
        if (wave % 5 == 0):
            # Egg wave
            if (eggWave(env, wave) == -1):
                return None
        elif ((wave - 2) % 5 == 0):
            # survival wave
            if survivalWave(env, wave) == -1:
                return None
        elif ((wave > 7) and(wave - 3) % 5 == 0):
            # pteradactyl wave
            pass
        else:
            # generic wave
            if genericWave(env, wave) == -1:
                return None

        if (wave > 20):
            return None
        wave += 1

    return None
