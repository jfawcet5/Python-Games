""" Space invader clone

"""

import pygame
import sys
import random

from pygame.locals import (
    RLEACCEL, 
    K_UP,
    K_DOWN,
    KEYUP,
    KEYDOWN, 
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    K_RETURN,
    QUIT,
)

pygame.init()

SCREEN_SIZE = (600, 600)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 10, 10)

FPS = 60

PLAYER = "Art/Tank.png"

E1 = "Art/Ghost.png"
E2 = "Art/enemy2.png"
E3 = "Art/enemy3.png"

""" ================================================================ Enemy Class ======================================== """
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, position, projectiles, canshoot, score):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load(image).convert()
        self.surf.set_colorkey(BLACK, RLEACCEL) # Enemy sprites have black background
        self.rect = self.surf.get_rect(center=(position))
        self.shootchance = 12
        self.timer = random.randint(0, FPS)
        self.projectiles = projectiles
        self.canshoot = canshoot
        self.dead = False
        self.score = score

    def death(self):
        # Change sprite to enemy death sprite
        self.surf = pygame.image.load("Art/enemy_death.png").convert()

    def shoot(self):
        # Shoots a missile at the player if the enemy is able to shoot
        if (self.canshoot):
            bullet = Projectile("Art/Missile.png", (self.rect.centerx, self.rect.centery), 7, 1)
            self.projectiles.add(bullet)

    def update(self):
        # randomly fire
        # Every 1 second, the enemy will have a 12% chance to shoot
        if (self.timer == 0):
            rng = random.randint(0, 100)
            if (rng <= self.shootchance):
                self.shoot()
        self.timer = (self.timer + 1) % FPS

""" ============================================================ Barrier Class ================================================ """
class Barrier(pygame.sprite.Sprite):
    def __init__(self, position):
        super(Barrier, self).__init__()
        self.surf = pygame.image.load("Art/Barrier.png").convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=(position))

        self.leftcollider = pygame.Rect(0, 6, 12, 56)

        self.midleftcollider = pygame.Rect(12, 2, 10, 58)

        self.midcollider = pygame.Rect(22, 2, 20, 48)

        self.midrightcollider = pygame.Rect(42, 2, 10, 58)

        self.rightcollider = pygame.Rect(52, 6, 12, 56)

        x = self.leftcollider.left
        y = self.leftcollider.top

        colors = [(255, 180, 180), (0, 0, 255), (255, 150, 10), (0, 255, 255), (255, 0, 255)]

        i = 0

        self.allcolliders = []

        # Split the rect regions
        cells = [self.leftcollider, self.midleftcollider, self.midcollider, self.midrightcollider, self.rightcollider]

        # Split regions into cells. Create rects to represent breakable pieces of the barrier
        j = 0
        for c in cells:
            x = c.left
            y = c.top
            while y <= c.bottom:
                if (not((y +4) > c.bottom)):
                    while x < c.right:
                        tempRect = pygame.Rect(x, y, 4, 4)
                        self.allcolliders.append(tempRect)
                        i = (i + 1) % 5
                        x += 4
                y += 4
                x= c.left
            j += 1

    def collision(self, proj):
        # Get position of projectile relative to barrier
        relativeleft = proj.rect.left - self.rect.left - 2
        
        # Create a rect encapsulating all possible cells to be hit
        if (proj.y_velocity < 0):
            r_coords = pygame.Rect(relativeleft - 2, 0, proj.rect.width + 4, self.rect.height)
        else:
            r_coords = pygame.Rect(relativeleft - 2, 0, proj.rect.width + 4, proj.rect.bottom - self.rect.top + proj.rect.height)

        # List of cells hit
        hitlist = []


        # Determine the top most/bottom most cells that can be hit by the projectile
        minmax = [SCREEN_SIZE[1], 0]

        for cell in self.allcolliders:
            if (cell.colliderect(r_coords)):
                hitlist.append(cell)
                minmax[0] = min(minmax[0], cell.top)
                minmax[1] = max(minmax[1], cell.bottom)

        minmax[0] = minmax[0] + proj.rect.height
        minmax[1] = minmax[1] - proj.rect.height

        if (proj.y_velocity > 0):
            # bullet traveling down, break top of barrier
            index = 0
            compareFN = lambda a, b: a <= b
            pass
        else:
            # bullet traveling up, break bottom of barrier
            index = 1
            compareFN = lambda a, b: a >= b
            pass

        # Destroy the affected cells
        for c in hitlist:
            if compareFN(c.bottom, minmax[index]):
                # Remove cell from colliders
                self.allcolliders.remove(c)
                # Draw a black rectangle where the cell used to be
                pygame.draw.rect(self.surf, BLACK, c)
        
        return len(hitlist)
""" ====================================================== Projectile Class ==================================================== """
class Projectile(pygame.sprite.Sprite):
    def __init__(self, image_file, position, y_velocity, projectile_type):
        super(Projectile, self).__init__()
        self.surf = pygame.image.load(image_file).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=(position[0], position[1]))
        self.y_velocity = y_velocity
        self.type = projectile_type

    def update(self):
        # Move the projectile up/down
        self.rect.move_ip(0, self.y_velocity)

""" ============================================================= Player Class ============================================= """
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load(PLAYER).convert()
        self.surf.set_colorkey(WHITE, RLEACCEL)
        self.rect = self.surf.get_rect(center=(SCREEN_SIZE[0] //2, SCREEN_SIZE[1] - 80))

        self.save = self.surf

        self.lives = 3

        # Shot timer: How many frames player must wait between shots
        self.shot_timer = FPS

        self.anim_timer = 0

        self.death_anim = ["Art/Player_death1.png", "Art/Player_death2.png",
                           "Art/Player_death3.png"]

    def reset(self):
        # Reset player surface to default tank picture
        self.surf = self.save

    def death(self, screen, index):
        # draw player death animation onto the screen
        if (self.anim_timer == 0):
            self.surf = pygame.image.load(self.death_anim[index])
            self.surf.set_colorkey(WHITE, RLEACCEL)
            screen.blit(self.surf, self.rect)
            index = (index + 1) % len(self.death_anim)
        self.anim_timer = (self.anim_timer + 1) % (FPS // 8)
        return index

    def update(self, pressed):
        # Update player position based on keyboard inputs
        if (pressed[K_RIGHT]):
            self.rect.move_ip(3, 0)
        if (pressed[K_LEFT]):
            self.rect.move_ip(-3, 0)

        # Limit position to keep player on screen
        if (self.rect.left <= 0):
            self.rect.left = 0
        if (self.rect.right >= SCREEN_SIZE[0]):
            self.rect.right = SCREEN_SIZE[0]

        # Update shot timer
        if (self.shot_timer <= FPS):
            self.shot_timer += 1

    def fire(self, proj_group):
        # Fire a projectile if allowed
        if (self.shot_timer >= (FPS // 2)):
            bullet = Projectile("Art/Player_Projectile.png", (self.rect.centerx, self.rect.centery), -22, 0)
            proj_group.add(bullet)
            self.shot_timer = 0

""" ====================================================== Enemy Grid Class =================================================== """
# Maintains the grid of enemies that move simultaneously
class enemyGrid():
    def __init__(self, proj_group):
        self.enemies = []
        self.proj_group = proj_group
        
        xpos = 66
        ypos = 60

        types = [E1, E2, E2, E3, E3] # Types of enemies in each row
        scores = [30, 20, 20, 10, 10] # Points awarded for killing types of enemies

        self.rows = len(types)
        self.cols = 11

        # Populate the grid with enemies
        enemycanshoot = False
        for i in range(len(types)):
            if (i == 4):
                enemycanshoot = True
            for j in range(11):
                tempEnemy = Enemy(types[i], (xpos, ypos), self.proj_group, enemycanshoot, scores[i])
                self.enemies.append(tempEnemy)
                xpos += 45
            ypos += 45
            xpos = 66

        self.timer = 1
        self.updatetime = (FPS // 6) # update every 1/6 of a second
        self.x_velocity = 5
        self.hasMovedDown = False

        self.right_edge = self.enemies[-1].rect.right # Right most edge of grid
        self.left_edge = self.enemies[0].rect.left # Left most edge of grid

        self.index = self.rows - 1

        self.count = self.rows * self.cols # Number of enemies that are alive
        self.kills_to_speedup = self.count // 2 # Number of enemy deaths before next grid speedup

    def move_down(self):
        # Move all enemies down
        for e in self.enemies:
            e.rect.move_ip(0, 16)

    def move(self, index):
        # Move enemies in specified row (index) right/left
        offset = index * self.cols
        for i in range(self.cols):
            self.enemies[offset + i].rect.move_ip(self.x_velocity, 0)

    def updateEdges(self):
        mincol = self.cols # leftmost column with an enemy that is still alive
        maxcol = 0 # Rightmost column with an enemy that is still alive

        # Iterate through each column in the grid
        for i in range(self.cols):
            for j in range(self.rows): # Iterate through each row in the current column
                if (self.enemies[i + (j*self.cols)].dead == False): # If current enemy is alive
                    if (i < mincol): # Update mincol as necessary
                        mincol = i
                    elif (i > maxcol): # Update maxol as necessary
                        maxcol = i
                    break
        # Error cases
        if (maxcol < mincol):
            maxcol = mincol
        elif (mincol > maxcol):
            mincol = maxcol
        # Update the right and left coordinates of the edge of the grid
        self.right_edge = self.enemies[maxcol].rect.right
        self.left_edge = self.enemies[mincol].rect.left
        return (maxcol, mincol)

    def updateEnemies(self):
        # Iterate through the rows bottom up to update which enemies can shoot. Only the bottom most
        # enemy in each column should have the ability to shoot
        offset = (self.rows - 1)
        for i in range(self.cols):
            if (self.enemies[offset * self.cols + i].dead == False):
                self.enemies[offset * self.cols + i].canshoot = True
                continue
            else:
                for j in range(offset, -1, -1):
                    if (self.enemies[j*self.cols + i].dead == False):
                        self.enemies[j*self.cols + i].canshoot = True
                        break
        # Count the number of enemies still alive
        count = 0
        for i in range(len(self.enemies)):
            if (self.enemies[i].dead == False):
                count += 1
        if (count < self.count):
            self.count = count

        # Update speed of grid movements based on number of enemies alive
        if (self.count <= self.kills_to_speedup):
            if (self.updatetime >= 5):
                if self.updatetime > 2:
                    self.updatetime -= 2
                    self.timer -= 2
            self.kills_to_speedup = self.count // 2

            if (self.count == 1):
                self.updatetime = 1
                self.x_velocity *= 3

    def update(self):
        # check timer if ready to move
        if (self.timer == 0):
            # Update the edges of the grid to find rightmost and leftmost enemies
            self.updateEdges()
            # check if the enemies are colliding with the right side of the wall
            right_barrier = (SCREEN_SIZE[0] - 10) - abs(self.x_velocity)
            left_barrier = 10 + abs(self.x_velocity)
            if (self.right_edge >= right_barrier and (not self.hasMovedDown) and self.index == self.rows - 1):
                self.move_down() # Move grid down and change direction
                self.x_velocity *= -1
                self.hasMovedDown = True
            # Check if the enemies are colliding with the left side of the wall
            elif (self.left_edge <= left_barrier and (not self.hasMovedDown and self.index == self.rows - 1)):
                self.move_down() # Move grid down and change direction
                self.x_velocity *= -1
                self.hasMovedDown = True
            # Move the enemies right/left row by row
            else:
                self.move(self.index)
                self.index = (self.index - 1) % self.rows
                self.hasMovedDown = False
        self.updateEnemies()
        self.timer = (self.timer + 1) % self.updatetime

""" ========================================================= Check Collisions Function ========================================= """
def check_collisions(proj_group, player, barriers, enemies, screen, clock):
    retval = 0
    enemies_hitlist = []
    # Check collisions between projectiles and barriers
    for b in barriers:
        hit_list = pygame.sprite.spritecollide(b, proj_group, False)

        for hit in hit_list:
            if (b.collision(hit) > 0):
                proj_group.remove(hit)

    # Check collisions between projectiles and enemies
    for e in enemies:
        hit_list = pygame.sprite.spritecollide(e, proj_group, False)

        for hit in hit_list:
            if (hit.type == 0):
                e.dead = True
                enemies.remove(e)
                proj_group.remove(hit)
                retval = 2
                enemies_hitlist.append(e)

    # Check collisions between projectiles and other projectiles
    for p in proj_group:
        if (p.type == 0):
            hit_list = pygame.sprite.spritecollide(p, proj_group, False)

            for hit in hit_list:
                if hit is not p:
                    randint = random.randint(0, 100)
                    if (randint > 40):
                        proj_group.remove(hit)
            if (len(hit_list)) > 1:
                proj_group.remove(p)

    # Check collisions between projectiles and player
    hit_list = pygame.sprite.spritecollide(player, proj_group, False)
    for hit in hit_list:
        if (hit.type == 1):
            print("player is hit")
            player.lives -= 1
            proj_group.remove(hit)
            retval = 1
    return retval, enemies_hitlist
""" ========================================================= Game Over Function =============================================== """
def game_over(screen, clock):
    # This function displays the game over screen
    
    title_font = pygame.font.SysFont("Corbel", 48)
    prompt_font = pygame.font.SysFont("Corbel", 32)

    title_text = title_font.render("Game Over", False, RED)
    title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 25))

    title_text1 = title_font.render("Game Over", False, WHITE)
    title_rect1 = title_text.get_rect(center=((SCREEN_SIZE[0] // 2) + 2, 25 + 2))

    prompt_text = prompt_font.render("Hit enter to play", False, WHITE)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_SIZE[0] // 2, 250))

    while True:
        screen.blit(title_text1, title_rect1)
        screen.blit(title_text, title_rect)
        screen.blit(prompt_text, prompt_rect)
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_RETURN):
                    level_1(screen, clock)
                if (ev.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            elif ev.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        clock.tick(FPS)
    return

""" ===================================================== Enemy Hit function =========================================== """
def enemy_hit(screen, clock, enemy):
    # Pauses the game for a fraction of a second and displays the enemy death animation
    timer = 0
    duration = FPS // 8

    enemy.death()

    screen.blit(enemy.surf, enemy.rect)
    pygame.display.update()

    while True:
        timer = (timer + 1) % duration

        if (timer == 0):
            return

        clock.tick(FPS)
    return

""" ======================================================== Player Hit function ============================================ """
def player_hit(screen, clock, player):
    # Pause the game and play player death animation for 1 second
    timer = 0
    one_second = FPS

    index = 0

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == KEYUP:
                if (ev.key == K_ESCAPE):
                    main_menu(screen, clock)
                    return
            elif ev.type == QUIT:
                pygame.quit()
                sys.exit()

        # draw hit animation for player
        index = player.death(screen, index)
        
        timer = (timer + 1) % one_second
        if (timer == 0):
            player.reset()
            return
        pygame.display.update()
        clock.tick(FPS)
        

""" ========================================================== Level 1 Function ================================================ """
def level_1(screen, clock):
    score = 0

    # Pygame sprite group to store all projectiles
    projectiles = pygame.sprite.Group()

    # Create player
    player = Player()

    # Variables used to display information on screen
    lives_font = pygame.font.SysFont("Corbel", 30)
    temp_surf = lives_font.render("3", False, GREEN)
    lives_rect = temp_surf.get_rect()

    score_surf = lives_font.render("{:04}".format(score), False, GREEN)
    score_rect = temp_surf.get_rect()

    # Initialize barriers
    tempvalue = SCREEN_SIZE[0] // 8
    barrier1 = Barrier((tempvalue, SCREEN_SIZE[1] - 140))
    barrier2 = Barrier((tempvalue * 3, SCREEN_SIZE[1] - 140))
    barrier3 = Barrier((tempvalue * 5, SCREEN_SIZE[1] - 140))
    barrier4 = Barrier((tempvalue * 7, SCREEN_SIZE[1] - 140))

    barriers = pygame.sprite.Group()
    barriers.add(barrier1)
    barriers.add(barrier2)
    barriers.add(barrier3)
    barriers.add(barrier4)

    # Initialize enemy grid
    e_grid = enemyGrid(projectiles)

    # Create sprite group for all enemies
    enemies = pygame.sprite.Group()

    for e in e_grid.enemies:
        enemies.add(e)

    # Currently unused
    difficulty = 1

    running = True
    while running:
        # Reset the screen to all black for next frame
        screen.fill(BLACK)

        # Draw green line between playing area and display area at bottom of screen
        pygame.draw.line(screen, (0, 255, 0), (0, SCREEN_SIZE[1] - 50), (SCREEN_SIZE[0], SCREEN_SIZE[1] - 50), 3)

        # Event handling
        for ev in pygame.event.get():
            if ev.type == KEYUP:
                if (ev.key == K_SPACE):
                    player.fire(projectiles)
                if (ev.key == K_ESCAPE):
                    main_menu(screen, clock)
                    return
            elif ev.type == QUIT:
                pygame.quit()
                sys.exit()

        # Player destroyed all enemies => start next wave
        if (e_grid.count <= 0):
            e_grid = enemyGrid(projectiles)
            enemies = pygame.sprite.Group()
            barriers = pygame.sprite.Group()

            barrier1 = Barrier((tempvalue, SCREEN_SIZE[1] - 140))
            barrier2 = Barrier((tempvalue * 3, SCREEN_SIZE[1] - 140))
            barrier3 = Barrier((tempvalue * 5, SCREEN_SIZE[1] - 140))
            barrier4 = Barrier((tempvalue * 7, SCREEN_SIZE[1] - 140))

            barriers.add(barrier1)
            barriers.add(barrier2)
            barriers.add(barrier3)
            barriers.add(barrier4)

            for e in e_grid.enemies:
                enemies.add(e)
                e.shootchance += (difficulty * 8)
            e_grid.x_velocity += difficulty
            difficulty += 1

        # Get keyboard inputs
        pressed_keys = pygame.key.get_pressed()

        # Update player
        player.update(pressed_keys)

        # Update projectiles
        projectiles.update()

        # Update enemies
        enemies.update()

        # Update enemy grid
        e_grid.update()

        # Draw barriers to the screen
        for b in barriers:
            screen.blit(b.surf, b.rect)

        # Draw projectiles to the screen
        for p in projectiles:
            screen.blit(p.surf, p.rect)

            if (p.rect.bottom <= 0):
                projectiles.remove(p)
            elif (p.rect.bottom >= (SCREEN_SIZE[1] - 50)):
                projectiles.remove(p)

        # Collision check for all objects
        sprite_was_hit, hit_enemies = check_collisions(projectiles, player, barriers, enemies, screen, clock)

        if (player.lives == 0): # Game over
            game_over(screen, clock)
            return

        for e in hit_enemies: # Update player score based on destroyed enemies
            score += e.score

        # draw player life indicators
        xpos = 40
        for i in range(player.lives - 1):
            screen.blit(player.surf, (xpos, SCREEN_SIZE[1] - player.rect.height - 10))
            xpos += 35

        # Write number of player lives 
        lives_text = lives_font.render(str(player.lives), False, GREEN)
        screen.blit(lives_text, (lives_rect.width, SCREEN_SIZE[1] - (lives_rect.height) - 10))

        # Write Score
        score_text = lives_font.render("Score: {:04}".format(score), False, GREEN)
        screen.blit(score_text, (400, SCREEN_SIZE[1] - (score_rect.height) - 10))

        # Draw player (tank) on the screen
        screen.blit(player.surf, player.rect)

        # Draw all enemies on the screen
        for e in enemies:
            screen.blit(e.surf, e.rect)

        # Player was hit by a projectile
        if (sprite_was_hit == 1):
            player_hit(screen, clock, player)
            for p in projectiles:
                projectiles.remove(p)

        # An enemy was hit by a projectile
        elif (sprite_was_hit == 2):
            for enemy in hit_enemies:
                enemy_hit(screen, clock, enemy)
            
        pygame.display.update()
        clock.tick(FPS)
    return

""" ========================================================== Main Menu Function =============================================== """
def main_menu(screen, clock):
    # This function displays the main menu
    screen.fill(BLACK)
    title_font = pygame.font.SysFont("Corbel", 48)
    prompt_font = pygame.font.SysFont("Corbel", 32)

    title_text = title_font.render("Space Invader", False, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 100))

    prompt_text = prompt_font.render("Hit enter to play", False, WHITE)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_SIZE[0] // 2, 250))

    while True:
        screen.blit(title_text, title_rect)
        screen.blit(prompt_text, prompt_rect)
        for ev in pygame.event.get():
            if ev.type == KEYDOWN:
                if (ev.key == K_RETURN):
                    level_1(screen, clock)
                if (ev.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            elif ev.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        clock.tick(FPS)
    return

""" ================================================ Main ============================================== """
def main():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    
    main_menu(screen, clock)
    return

if __name__ == "__main__":
    main()
