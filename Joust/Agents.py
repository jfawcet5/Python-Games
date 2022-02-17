""" Class definitions for Joust """
import pygame
import sys
import random

from Misc import *

GRAVITY = 0.049
FRICTION = .15

# Linear interpolation
def lerp(a, b, f):
    return (1-f)*a + (f*b)

# ============================================================================================================= #
# ====================================================== physics Object ================================================ #
# Physics object base class for all moving objects.
# Defines basic behavior for movement and collisions
class physicsObject(pygame.sprite.Sprite):
    def __init__(self):
        super(physicsObject, self).__init__()
        self.surf = pygame.Surface((10, 10))
        self.rect = self.surf.get_rect()

        self.velocity = Vector2()
        self.grounded = True

    def collidePlatform(self, other):
        # Change object velocity based on collision with platform
        leftline = pygame.Rect(other.rect.left, other.rect.top - 1, 1, other.rect.height - 1)
        rightline = pygame.Rect(other.rect.right - 1, other.rect.top, 1, other.rect.height)
        bottomline = pygame.Rect(other.rect.left, other.rect.bottom + 1, other.rect.width, 1)

        collideleft = leftline.colliderect(self.rect)
        collideright = rightline.colliderect(self.rect)
        collidebottom = bottomline.colliderect(self.rect)

        magnitude = (abs(self.velocity.x) / 3)
        offset = random.randint(1, 4)

        if (collideleft):
            d = Vector2(-1 * magnitude - offset, 0)
            self.rect.right = other.rect.left
        elif (collideright):
            d = Vector2(magnitude + offset, 0)
            self.rect.left = other.rect.right
        elif (collidebottom):
            d = Vector2(self.velocity.x, 1)
            self.rect.top = other.rect.bottom
        else:
            d = self.velocity
                
        self.velocity = d

    def groundCheck(self, platforms):
        # Check if object is standing on platform or is in the air
        
        groundcheck = pygame.Rect(self.rect.centerx, self.rect.bottom, 1, 3)

        surfaces = []
        for p in platforms:
            surfaces.append(p.rect)
        surfaces.append(pygame.Rect(0, SCREEN_SIZE[0], SCREEN_SIZE[0], 100))

        ind = groundcheck.collidelist(surfaces)
        if (ind != -1):
            self.velocity.y = 0
            if (self.rect.bottom >= surfaces[ind].top):
                self.rect.bottom = surfaces[ind].top - 1
            self.grounded = True
        else:
            self.grounded = False
        
    def collisionCheck(self, platforms):
        """ Use this function to check collisions against the platforms
            - If on top of platform, object will be grounded
            - If object collides with any other side of the platform, it will 'bounce'
        """
        for p in platforms:
            if (self.rect.colliderect(p)):
                # Determine type of collision and modify velocity accordingly
                self.collidePlatform(p)

        # A collision with the top of the screen (rect.top <= 0) will cause the object to
        # 'bounce' off the top with a magnitude that is relative to the speed at which the object
        # was traveling prior to the collision
        if (self.rect.top <= 0):
            bounce = (abs(self.velocity.y) / 3) + 1
            self.rect.top = 0
            self.velocity = Vector2(self.velocity.x, bounce)

        # Check if the object is on the ground or in the air
        self.groundCheck(platforms)
        return

# ============================================================================================================= #
# ====================================================== Enemy ================================================ #
# Enemy base class
# Defines most of the basic behavior shared by the enemies
class Enemy(physicsObject):
    def __init__(self, position, eType):
        super(Enemy, self).__init__()
        if (eType == 0): # Bounder
            self.groundImage = BOUNDER_IDLE_G
            self.airImage = BOUNDER_IDLE_A
            self.flapImage = BOUNDER_FLAP
        elif (eType == 1): # Hunter
            self.groundImage = HUNTER_IDLE_G
            self.airImage = HUNTER_IDLE_A
            self.flapImage = HUNTER_FLAP
        elif (eType == 2): # Shadow Lord
            self.groundImage = SHADOWLORD_IDLE_G
            self.airImage = SHADOWLORD_IDLE_A
            self.flapImage = SHADOWLORD_FLAP
        elif (eType == 3): # Pterodactyl
            self.groundImage = SHADOWLORD_IDLE_G
            self.airImage = SHADOWLORD_IDLE_A
            self.flapImage = SHADOWLORD_FLAP
        elif (eType == 4): # Bird
            self.groundImage = BIRD_IDLE_G
            self.airImage = BIRD_IDLE_A
            self.flapImage = BIRD_FLAP
        self.surf = pygame.image.load(self.groundImage).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=position)

        self.type = eType

        direction = random.choice([-1, 1])
        self.velocity = Vector2(direction * 2, 0)

        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = Vector2(0, random.randint(30, 470))

        self.state = 0
        self.flapCounter = 1

        self.flapChance = random.randint(8, 16)

        self.alive = 1

        self.counter = 0

        self.facing = direction # 1 = facing right, -1 = facing left
        if (self.facing == -1):
            self.surf = pygame.transform.flip(self.surf, True, False)

    def flap(self):
        # Determines how enemies flap
        if (self.rect.centery > SCREEN_SIZE[1] - 50):
            self.velocity.y = 0
        if (self.flapCounter == 0):
            if (self.rect.centery > self.target.y):
                self.rect.centery -= 1
                self.velocity.y -= 0.72
                self.surf = pygame.image.load(self.flapImage).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                self.state = 2
                if (self.facing == -1):
                    self.surf = pygame.transform.flip(self.surf, True, False)
                self.counter = 0
                self.flapChance = random.randint(8, 16)
                
        self.flapCounter = (self.flapCounter + 1) % self.flapChance # Evaluate flap every 'flapChance' frames

    def die(self):
        # Enemy death
        self.alive = 0
        return Egg(self.rect.center, Vector2(self.facing * 2, 0), self.type)

    def animate(self):
        # Animate the enemy based on current state
        if (self.grounded):
            self.surf = pygame.image.load(self.groundImage).convert()
            self.surf.set_colorkey(WHITE, RLEACCEL)
            if (self.facing == -1):
                self.surf = pygame.transform.flip(self.surf, True, False)
        else:
            if (self.state == 1):
                self.surf = pygame.image.load(self.airImage).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                if (self.facing == -1):
                    self.surf = pygame.transform.flip(self.surf, True, False)
            else:
                if (self.counter == (self.flapChance // 2)):
                    self.state = 1
                    self.counter = 0
                self.counter += 1

        if (self.velocity.x < 0 and self.facing == 1):
            self.surf = pygame.transform.flip(self.surf, True, False)
            self.facing = -1
        if (self.velocity.x > 0 and self.facing == -1):
            self.surf = pygame.transform.flip(self.surf, True, False)
            self.facing = 1

    def collide(self, other):
        # Override parent collide function. Change enemy velocity based on collision with platform
        leftline = pygame.Rect(other.rect.left, other.rect.top - 1, 1, other.rect.height - 1)
        rightline = pygame.Rect(other.rect.right - 1, other.rect.top, 1, other.rect.height)
        bottomline = pygame.Rect(other.rect.left, other.rect.bottom + 1, other.rect.width, 1)

        collideleft = leftline.colliderect(self.rect)
        collideright = rightline.colliderect(self.rect)
        collidebottom = bottomline.colliderect(self.rect)

        magnitude = (abs(self.velocity.x) / 3)
        offset = random.randint(1, 4)

        if (collideleft):
            d = Vector2(-1 * self.velocity.x, 0)
            self.rect.right = other.rect.left
        elif (collideright):
            d = Vector2(-1 * self.velocity.x, 0)
            self.rect.left = other.rect.right
        elif (collidebottom):
            d = Vector2(self.velocity.x, 1)
            self.rect.top = other.rect.bottom
        else:
            d = self.velocity
                
        self.velocity = d

    def groundCheck(self, platforms):
        # Overwriting parent groundCheck() function. Enemies hitbox is updated based on whether
        # they are in the air or on the ground, so the groundcheck must account for this change
        if (self.grounded):
            bottom = self.rect.bottom
        else:
            bottom = self.rect.bottom + 12
        
        groundcheck = pygame.Rect(self.rect.centerx, bottom, 1, 3)

        surfaces = []
        for p in platforms:
            surfaces.append(p.rect)
        surfaces.append(pygame.Rect(0, SCREEN_SIZE[0], SCREEN_SIZE[0], 100))

        ind = groundcheck.collidelist(surfaces)
        if (ind != -1):
            self.velocity.y = 0
            if (not self.grounded):
                self.rect.height += 12
            if (self.rect.bottom >= surfaces[ind].top):
                self.rect.bottom = surfaces[ind].top - 1
            self.grounded = True
        else:
            if (self.grounded):
                self.rect.height -= 12
            self.grounded = False

    def update(self, platforms, player):
        # Update the enemy
        self.__move__()
        self.animate()
        self.collisionCheck(platforms)
        return None

def findPath(actor, target, platformGroup):
    # Very crude pathfinding for birds
    if (actor.facing == 1):
        left = actor.rect.centerx
    else:
        left = actor.rect.centerx - (2 * actor.rect.width)
    rectH = pygame.Rect(left, actor.rect.top, 2 * actor.rect.width, actor.rect.height)

    rectH.normalize()

    for plat in platformGroup:
        if (plat.rect.colliderect(rectH)):
            if (plat.rect.centery > target.y):
                ypos = plat.rect.top - actor.rect.height + 1
            else:
                ypos = plat.rect.bottom + actor.rect.height - 1
            if (actor.facing == 1):
                xpos = plat.rect.left - actor.rect.width
            else:
                xpos = plat.rect.right + actor.rect.width
            return Vector2(xpos, ypos)

    return target

# ============================================================================================================= #
# ====================================================== Bird ================================================ #
''' Class for birds that fly on screen for enemy jouster to mount. 
'''
class Bird(Enemy):
    def __init__(self, platformGroup, egg):
        super(Bird, self).__init__((10, 100), 4)
        self.target = Vector2(egg.rect.centerx, egg.rect.centery)
        if (self.target.x > SCREEN_SIZE[1] // 2):
            x_spawn = 0
            self.velocity.x = 1
        else:
            x_spawn = SCREEN_SIZE[1]
            self.velocity.x = 0

        # Spawn the bird on the opposite side of the screen and 50 pixels above the egg
        self.rect.center = (x_spawn, self.target.y - 50)

        # Store target egg
        self.egg = egg

        # Set initial target near egg
        self.__setInitialTarget__(platformGroup, egg.rect)

        # Set initial height, based on nearby platforms
        for plat in platformGroup:
            if (plat.rect.colliderect(self.rect)):
                self.rect.centery += (self.rect.height + 1)

        # Initialize current target with very simple pathfinding
        self.curTarget = findPath(self, self.target, platformGroup)
        self.flapChance = 8

        self.canFlap = True
        self.speed = 2

        self.mount = False
        self.reachedInitialTarget = False

        self.timer = 1

    def __setInitialTarget__(self, platformGroup, eggRect):
        platform = None
        for plat in platformGroup: # Iterate through the platforms
            if (self.egg.rect.centerx > plat.rect.left and self.egg.rect.centerx < plat.rect.right):
                if (abs(self.egg.rect.centery - plat.rect.top) < 20):
                    # If the egg is on the current platform, then save the platform in 'platform'
                    platform = plat
                    break
        
        # randNum is used to set the target 10-30 pixels away from the egg
        randNum = random.randint(10,30)
        if (eggRect.centerx > platform.rect.centerx): # If egg is on right side of platform
            # Set x coordinate of the target to the left of the egg
            x_target = self.egg.rect.centerx - randNum
            if (x_target < 0): # If target goes past the left side of screen
                x_target = 10 # Move it back onto the screen

        else: # Egg is on left side of platform
            # Set the x coordinate of the target to the right of the egg
            x_target = self.egg.rect.centerx + randNum
            if (x_target > SCREEN_SIZE[0]): # If target goes past the right side of screen
                x_target = SCREEN_SIZE[0] - 10 # Move it back onto the screen

        self.target.x = x_target
        return None

    def flyOffScreen(self):
        # When the egg is destroyed the bird will fly off the screen

        if (self.facing == -1):
            # New target will be off the left screen
            self.target.x = -20
        else:
            # New target will be off the right screen
            self.target.x = SCREEN_SIZE[0] + 20
        self.speed = 4
        return None

    def doFlap(self):
        # Flap
        self.rect.centery -= 1
        self.velocity.y -= 0.72
        self.surf = pygame.image.load(self.flapImage).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.state = 2
        if (self.facing == -1):
            self.surf = pygame.transform.flip(self.surf, True, False)

    def flap(self):
        # Attempt to flap
        if (self.rect.centery > SCREEN_SIZE[1] - 50):
            self.velocity.y = 0

        if (self.flapCounter == 0):
            # Check position relative to target
            #   If greater than target
            #       Check velocity
            #   If less than target
            #       Flap
            if (self.rect.centery < self.curTarget.y):
                # higher than target
                if (self.velocity.y > 2): # Moving downwards at a rate of 2 pixels per frame
                    self.doFlap()
                else:
                    if (random.randint(1, 10) < 2):
                        self.doFlap()
            else:
                self.doFlap()
                
        self.flapCounter = (self.flapCounter + 1) % self.flapChance # Evaluate flap every 'flapChance' frames

    def __move__(self, platforms):
        # Move the bird based on the target position
        if (self.canFlap):
            self.flap()

        # Find a path to the current target
        self.curTarget = findPath(self, self.target, platforms)

        distX = self.curTarget.x - self.rect.centerx
        if (abs(distX) > 2): # Set direction and speed based on relative target position
            if (distX > 0):
                self.velocity.x = self.speed
            else:
                self.velocity.x = -1 * self.speed
        else: # If bird is near target
            self.velocity.x = 0 
            if (self.grounded): # Update target to the egg, walk
                self.target = Vector2(self.egg.rect.centerx, self.egg.rect.centery)
                self.speed = 1
                self.canFlap = False
                self.reachedInitialTarget = True

        distX = self.egg.rect.centerx - self.rect.centerx

        # Jouster mount bird if bird close enough and can be mounted
        if (abs(distX) < 5 and self.canFlap == False):
            self.mount = True

        # Apply gravity if not grounded
        if (not self.grounded):
            self.velocity.y += GRAVITY

        self.rect.move_ip(self.velocity.x, self.velocity.y)
        
        if (self.rect.right < 0):
            self.rect.left = SCREEN_SIZE[0]
        if (self.rect.left > SCREEN_SIZE[0]):
            self.rect.right = 0
        return None

    def update(self, platforms, player):
        # Update the bird
        self.__move__(platforms)
        super(Bird, self).animate()
        super(Bird, self).collisionCheck(platforms)

        if (self.mount):
            return 1
        elif (self.reachedInitialTarget):
            return 2
        return 0

# Container to display little jouster guys that hatch from an egg 
class Jouster(pygame.sprite.Sprite):
    def __init__(self, position, jType):
        super(Jouster, self).__init__()
        if jType == 0:
            image = RED_JOUSTER
        elif jType == 1:
            image = GREY_JOUSTER
        elif jType == 2:
            image = BLUE_JOUSTER
        self.surf = pygame.image.load(image).convert()
        self.rect = self.surf.get_rect(center=position)
        self.type = jType

    def update(self):
        return

# Class for eggs that spawn when an enemy is defeated
class Egg(physicsObject):
    def __init__(self, position, velocity, eType):
        super(Egg, self).__init__()
        self.surf = pygame.image.load(EGG).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=position)

        self.type = eType

        self.velocity = Vector2(velocity.x, 0)
        self.grounded = False

        self.timer = 0
        self.hatchTime = FPS * random.randint(12,16)

        randNum = random.randint(7, 12)
        self.birdSpawn = randNum * FPS 

    def __move__(self):
        # Move the egg
        if (not self.grounded):
            self.velocity.y += GRAVITY
        else:
            if (self.velocity.x != 0):
                if (self.velocity.x < 0):
                    self.velocity.x += 0.24
                else:
                    self.velocity.x -= 0.24
        if (abs(self.velocity.x) < 0.24):
            self.velocity.x = 0

        self.rect.move_ip(self.velocity.x, self.velocity.y)

        if (self.rect.right < 0):
            self.rect.left = SCREEN_SIZE[0]
        if (self.rect.left > SCREEN_SIZE[0]):
            self.rect.right = 0

    def update(self, platforms):
        # Update the egg

        # Move the egg based on its velocity
        self.__move__()
        # Check for collision with platform
        self.collisionCheck(platforms)
        # Update timer
        if (self.timer >= self.hatchTime): # Return 1 on hatch
            return 1
        elif (self.timer == self.birdSpawn): # return 2 on bird appearance.
            self.timer += 1
            return 2
        self.timer += 1
        return 0

# ==================================================================== EBJ ===============================================================
""" Egg/Bird/Jouster class. Holds the instances for the egg, bird, and jouster since they
    are all related (i.e. Egg hatches into jouster, bird targets egg, jouster mounts bird).
    This class handles all of the updates, state changes, and rendering for the egg/bird/jouster.
    Note: This implementation is somewhat messy and could probably be cleaned up, but works for now
"""
class EBJ(pygame.sprite.Sprite):
    def __init__(self, position, velocity, enemyType, platformGroup):
        super(EBJ, self).__init__()
        self.egg = Egg(position, velocity, enemyType)
        self.jouster = None
        # We cannot create the bird instance here because it could cause the bird to target the
        # position of the egg when it was first created. This is an issue because the egg can
        # move (if the egg was created in the air and drops to the ground, the bird will target
        # the eggs position when it was in the air)
        self.bird = None
        self.type = enemyType
        # Save the platformGroup for when we need to create the bird instance
        self.__platforms = platformGroup

        self.renderList = [self.egg]

        """ Current state of the Egg/Bird/Jouster:
                0: Only egg is active
                1: Egg and Bird are active
                2: Bird and Jouster are active
                3: Only bird is active

                4: Destroy egg, bird not spawned yet
                5: Egg destroyed, waiting for bird to exit screen
        """
        self.state = 0


    def spawn(self):
        # Spawn an enemy based on the egg type
        if (self.type == 0):
            return Bounder((self.egg.rect.centerx, self.egg.rect.centery - 3))
        elif (self.type == 1):
            return Hunter((self.egg.rect.centerx, self.egg.rect.centery - 3))
        elif (self.type == 2):
            return ShadowLord((self.egg.rect.centerx, self.egg.rect.centery - 3))

    def collideAny(self, group):
        # Check if there is a collision between the egg and any object in a sprite group
        for obj in group:
            if self.egg.rect.colliderect(obj.egg.rect):
                return True
        return False

    def destroy(self):
        # This function is called when player makes contact with egg/jouster

        # Start by removing the egg and jouster from render/update calls

        # If bird is none then we destroy the EBJ instance
        if (self.bird is None):
            self.state = 4
        else:# If bird is not none then we wait for bird to exit screen before destroying instance
            if (self.egg in self.renderList):
                self.renderList.remove(self.egg)
            if (self.jouster in self.renderList):
                self.renderList.remove(self.jouster)
            self.bird.flyOffScreen()
            self.state = 5
        return None

    def render(self, screen):
        # Render appropriate object based on state
        for item in self.renderList:
            screen.blit(item.surf, item.rect)

        return None

    def update(self, platforms, player):
        if (self.state == 0): # Only egg is active
            ret = self.egg.update(platforms) # Update egg and save return value
            if (ret == 2): # If egg update returned 2
                self.state = 1 # Change state to 1: Bird and egg are active
                if (self.bird is None): # If bird is None
                    self.bird = Bird(platforms, self.egg) # Create bird instance
                self.renderList.append(self.bird)
                    
            elif (ret == 1): # If egg update returned 1
                self.state = 2 # Change state to 2: Bird and jouster are active
                if (self.jouster is None): # If jouster is None
                    self.jouster = Jouster((self.egg.rect.centerx, self.egg.rect.centery - 2), self.type) # Create jouster instance
                self.renderList.remove(self.egg)
                self.renderList.append(self.jouster)
                    
        elif (self.state == 1): # Bird and Egg are active
            ret1 = self.bird.update(platforms, player) # Update the bird
            if (ret1 == 2):
                self.state = 2 # Change state to 2: Bird and jouster are active
                if (self.jouster is None): # If jouster is None
                    self.jouster = Jouster(self.egg.rect.center, self.type) # Create jouster instance
                self.renderList.remove(self.egg)
                self.renderList.append(self.jouster)
            
            ret2 = self.egg.update(platforms) # Update the egg and save return value
            if (ret2 == 1): # If egg update returned 1
                self.state = 2 # Change state to 2: Bird and jouster are active
                if (self.jouster is None): # If jouster is None
                    self.jouster = Jouster(self.egg.rect.center, self.type) # Create jouster instance
                self.renderList.remove(self.egg)
                self.renderList.append(self.jouster)
                    
        elif (self.state == 2): # Bird and Jouster are active
            if (self.bird is not None):
                ret = self.bird.update(platforms, player) # Update bird and save return value
                if (ret == 1): # If bird update returned 1
                    # This means the jouster mounted the bird and we need to create a bounder/hunter/shadow lord
                    # in this position
                    return 1

        elif (self.state == 4): # Egg destroyed, and bird is not on screen
            return 2

        elif (self.state == 5): # Egg destroyed, bird is on screen
            self.bird.update(platforms, player)
            if (self.bird.rect.centerx > SCREEN_SIZE[0] or self.bird.rect.centerx < 0):
                return 2
        
        return 0

# Shadow Lord - Fly quickly and closer to the top. Fly higher when close to player - 1500 points
class ShadowLord(Enemy):
    def __init__(self, position):
        super(ShadowLord, self).__init__(position, 2)

        direction = random.choice([-1, 1])

        # Set initial velocity with random x direction
        self.velocity = Vector2(direction * 2, 0)

        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = Vector2(0, random.randint(30, 470))

        self.flapChance = 10

    def __move__(self, player):
        # Not implemented yet
        return None

    def update(self, platforms, player):
        self.__move__(player)
        super(ShadowLord, self).animate()
        super(ShadowLord, self).collisionCheck(platforms)
        return None

# Hunter - Seeks player in effort to collide - 750 points
class Hunter(Enemy):
    def __init__(self, position):
        super(Hunter, self).__init__(position, 1)

        direction = random.choice([-1, 1])

        # Set initial velocity with random x direction
        self.velocity = Vector2(direction * 2, 0)

        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = Vector2(0, random.randint(30, 470))

        self.flapChance = 10

    def __move__(self, player):
        # Update position based on speed, player position, and gravity
        self.target.x = player.rect.centerx
        self.target.y = player.rect.centery
        
        self.flap()

        if (not self.grounded):
            self.velocity.y += GRAVITY

        self.rect.move_ip(self.velocity.x, self.velocity.y)
        
        if (self.rect.right < 0):
            self.rect.left = SCREEN_SIZE[0]
        if (self.rect.left > SCREEN_SIZE[0]):
            self.rect.right = 0
        return None

    def update(self, platforms, player):
        self.__move__(player)
        super(Hunter, self).animate()
        super(Hunter, self).collisionCheck(platforms)
        return None

# Bounder - Fly around environment randomly, ocassionally reacting to player - 500 points
class Bounder(Enemy):
    def __init__(self, position):
        super(Bounder, self).__init__(position, 0)

        direction = random.choice([-1, 1])

        # Set initial velocity with random x direction
        self.velocity = Vector2(direction * 2, 0)

        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = Vector2(0, random.randint(30, 470))

    def __move__(self):
        # Update position based on speed and gravity
        self.flap()

        if (not self.grounded):
            self.velocity.y += GRAVITY

        self.rect.move_ip(self.velocity.x, self.velocity.y)

        if (self.rect.right < 0):
            self.rect.left = SCREEN_SIZE[0]
        if (self.rect.left > SCREEN_SIZE[0]):
            self.rect.right = 0
        return None

# ============================================================================================================= #
# ====================================================== Player =============================================== #
class Player(physicsObject):
    def __init__(self):
        super(Player, self).__init__()
        # overwrite parent self.surf and self.rect
        # Default animation state
        self.idleGroundAnim = PLAYER_IDLE_GROUND

        self.surf = pygame.image.load(self.idleGroundAnim).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)

        self.rect = self.surf.get_rect(center=(SCREEN_SIZE[0]//2, 354))

        # self.velocity and self.grounded included in parent class
        self.max_x = 6
        self.state = 0
        self.accelerating = False
        self.invincible = False
        self.facing = 0 # 0 for right, 1 for left

        self.counter = 0 # general counter/timer
        self.animct = 0 # animation counter

        self.lives = 4
        self.points = 0

        # Default animations:
        self.idleAirAnim = PLAYER_IDLE_AIR
        self.flapAnim = PLAYER_FLAP
        self.slideAnim = PLAYER_SLIDE
        self.walkAnim = PLAYER_WALK
        self.respawnAnim = PLAYER_RESPAWN

    def flap(self):
        # Prevent player from moving for the first (1/4) second after death
        # to prevent accidental movements
        if (self.state == 5 and self.counter < (FPS / 4)):
            return None
        if (self.grounded): # Taking off the ground
            self.velocity.y -= 1.5
        else: # Flapping in the air
            self.velocity.y -= 0.9
            self.state = 4
            self.counter = 0
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        return None

    def __move__(self, inputs):
        """ Moves the player based on the player input
            - Updates the x component of velocity
            - Applies gravity
            - Applies friction
        """
        # Prevent player from moving for the first (1/4) second after death
        # to prevent accidental movements
        if (self.state == 5 and self.counter < (FPS / 4)):
            return None
        moving = False
        if (inputs[K_RIGHT]): # Moving to the right
            if (self.velocity.x < self.max_x):
                self.velocity.x += 0.24
            if (self.facing == 1):
                self.facing = 0
            moving = True
        if (inputs[K_LEFT]): # Moving to the left
            if (self.velocity.x > (-1 * self.max_x)):
                self.velocity.x -= 0.24
            if (self.facing == 0):
                self.facing = 1
            moving = True
        if (self.grounded): # Player is on a platform
            if (self.velocity.x != 0 and (not moving)): # Sliding
                if (self.velocity.x > 0):
                    self.velocity.x -= FRICTION
                else:
                    self.velocity.x += FRICTION
            if (moving): # Used to determine player state
                self.accelerating = True
            else:
                self.accelerating = False
        if (not self.grounded): # Increase y velocity (down) based on acceleration due to gravity
            self.velocity.y += GRAVITY
        if (abs(self.velocity.x) < 0.2):
            self.velocity.x = 0
        self.rect.move_ip(self.velocity.x, self.velocity.y)

    def respawn(self, locations):
        # Respawn the player on a random spawning platform and start respawn animation
        self.invincible = True
        self.state = 5
        numlocations = len(locations) - 1
        loc = random.randint(0, numlocations)
        self.rect.center = locations[loc]
        self.counter = 0
        self.animct = 0
        return None

    def die(self, locs):
        # Player death
        self.lives = self.lives - 1
        self.points += 50
        self.velocity.x = 0
        self.velocity.y = 0
        self.respawn(locs)
        return None

    def getState(self):
        """ Determine the state of the player using previous state and current inputs.
            More states can be added as needed (such as respawning, death, etc)
            - 0 for idle (standing)
            - 1 for walking/running (on ground)
            - 2 for sliding (on ground)
            - 3 for idle (in air)
            - 4 for flapping
            - 5 for respawning
        """
        curState = -1
        if (self.grounded): # On the ground
            if (abs(self.velocity.x) >= 1): # Moving
                if (self.accelerating):
                    curState = 1 # Walking/Running
                    if (self.state != 1):
                        self.counter = 0
                        self.animct = 3
                else:
                    curState = 2 # Sliding
            else: # Not moving
                if (self.state == 5): # Respawning takes precedent over idle ground
                    curState = 5 # Respawning
                else:
                    curState = 0 # Idle Ground
        else: # In the air
            if (self.state != 4): # if not flapping
                curState = 3 # Idle air
            else:
                curState = 4
        return curState

    def __animate__(self):
        # Play the appropriate animation based on state
        state = self.getState()

        self.state = state
        if (state == 0): # Idle Ground
            self.surf = pygame.image.load(self.idleGroundAnim).convert()
            self.surf.set_colorkey(WHITE, RLEACCEL)
        elif (state == 1): # Running
            # Update speed determines the speed of the transition. It is based on the
            # speed at which the player is moving
            updateSpeed = lerp(16, 4, abs(self.velocity.x) // self.max_x)
            updateSpeed = int(updateSpeed)
            if (self.counter % updateSpeed == 0): # Update current image
                self.animct = (self.animct + 1) % 4
                self.surf = pygame.image.load(self.walkAnim[self.animct]).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
            else:
                self.surf = pygame.image.load(self.walkAnim[self.animct]).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
            self.counter += 1
        elif (state == 2): # Sliding
            self.surf = pygame.image.load(self.slideAnim).convert()
            self.surf.set_colorkey(WHITE, RLEACCEL)
        elif (state == 3): # Idle Air
            self.surf = pygame.image.load(self.idleAirAnim).convert()
            self.surf.set_colorkey(WHITE, RLEACCEL)
        elif (state == 4): # Flapping
            if (self.counter == 5): # Flapping is over = Transition to idle air
                self.state = 3
                self.surf = pygame.image.load(self.idleAirAnim).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                self.counter = 0
            else: # Display flap image
                self.surf = pygame.image.load(self.flapAnim).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                self.counter += 1
        elif (state == 5): # Respawning
            if (self.counter <= (FPS * 5)): # Respawn state lasts for 5 seconds
                # update current image and counter
                self.surf = pygame.image.load(self.respawnAnim[self.animct]).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                if (self.counter % 10 == 0):
                    self.animct = (self.animct + 1) % 3
            else: # After 5 seconds, return to idle ground image
                self.state = 0
                self.surf = pygame.image.load(self.idleGroundAnim).convert()
                self.surf.set_colorkey(WHITE, RLEACCEL)
                self.counter = 0
                self.invincible = False
            self.counter += 1

        # Flip image based on the direction the player is facing
        if (self.facing == 1):
            self.surf = pygame.transform.flip(self.surf, True, False)
        return None

    def groundCheck(self, platforms):
        # Overwriting parent groundCheck() function. Player's hitbox is updated based on whether
        # the player is in the air or on the ground, so the groundcheck must account for this change
        if (self.grounded):
            bottom = self.rect.bottom
        else:
            bottom = self.rect.bottom + 12
        
        groundcheck = pygame.Rect(self.rect.centerx, bottom, 1, 3)

        surfaces = []
        for p in platforms:
            surfaces.append(p.rect)
        surfaces.append(pygame.Rect(0, SCREEN_SIZE[0], SCREEN_SIZE[0], 100))

        ind = groundcheck.collidelist(surfaces)
        if (ind != -1):
            self.velocity.y = 0
            if (not self.grounded):
                self.rect.height += 12
            if (self.rect.bottom >= surfaces[ind].top):
                self.rect.bottom = surfaces[ind].top - 1
            self.grounded = True
        else:
            if (self.grounded):
                self.rect.height -= 12
            self.grounded = False

    def update(self, pressed, platforms):
        # Update the player

        # Move based on inputs
        self.__move__(pressed)

        # Check collisions with platforms
        self.collisionCheck(platforms)

        # Animate
        self.__animate__()

        if (self.rect.right < 0):
            self.rect.left = SCREEN_SIZE[0]
        if (self.rect.left > SCREEN_SIZE[0]):
            self.rect.right = 0
        return None
