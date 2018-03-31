# Init
import pygame, math, random, sys
from pygame.locals import *
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image)
        self.direction = 0
        self.position = position

        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
    def update(self, deltat):
        # Runs every game tick
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

class ScreenWrapObject(GameObject):
    def __init__(self, image, position, screenWidth, screenHeight):
        GameObject.__init__(self, image, position)
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.screenBorder = 120
    def update(self, deltat, x, y):
        if x < -self.screenBorder:
            x += self.screenWidth + self.screenBorder*2
        if y < -self.screenBorder:
            y += self.screenHeight + self.screenBorder*2
        if x > self.screenWidth + self.screenBorder:
            x -= self.screenWidth + self.screenBorder*2
        if y > self.screenHeight + self.screenBorder:
            y -= self.screenHeight + self.screenBorder*2
        self.position = (x, y)

        GameObject.update(self, deltat)

class FloatingObject(ScreenWrapObject):
    def __init__(self, image, position, direction, speed, life, screenWidth, screenHeight):
        ScreenWrapObject.__init__(self, image, position, screenWidth, screenHeight)
        self.direction = direction
        self.speed = speed
        self.life = life
    def update(self, deltat):
        if self.life == 0:
            self.kill()
        else:
            self.life -= 1
            x, y = self.position
            rad = self.direction * math.pi / 180
            x -= math.sin(rad)*self.speed
            y -= math.cos(rad)*self.speed

            ScreenWrapObject.update(self, deltat, x, y)

class Effect(GameObject):
    def __init__(self, image, position, offsetX, offsetY):
        GameObject.__init__(self, image, position)
        self.offsetY = offsetY
        self.offsetX = offsetX
    def update(self, deltat, position, direction):
        self.position = position
        self.direction = direction
        rad = self.direction * math.pi / 180
        offsetX = position[0] + math.sin(rad)*self.offsetY - math.cos(rad)*self.offsetX
        offsetY = position[1] + math.cos(rad)*self.offsetY + math.sin(rad)*self.offsetX
        self.position = (offsetX, offsetY)
        GameObject.update(self, deltat)

class PlayerSprite(ScreenWrapObject):
    MAX_FORWARD_SPEED = 15
    ACCELERATION = 2
    DECCELERATION = 0.95
    TURN_SPEED = 5

    def __init__(self, image, position, screenWidth, screenHeight):
        ScreenWrapObject.__init__(self, image, position, screenWidth, screenHeight)
        self.speedX = self.speedY = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
    def update(self, deltat):
        self.direction += (self.k_right + self.k_left)
        rad = self.direction * math.pi / 180

        self.speedX *= self.DECCELERATION
        self.speedY *= self.DECCELERATION

        self.speedX += math.sin(rad)*(self.k_up + self.k_down)
        self.speedY += math.cos(rad)*(self.k_up + self.k_down)
        if self.speedX**2 + self.speedY**2 > self.MAX_FORWARD_SPEED**2:
            self.speedX *= self.MAX_FORWARD_SPEED/math.sqrt(self.speedX**2 + self.speedY**2)
            self.speedY *= self.MAX_FORWARD_SPEED/math.sqrt(self.speedX**2 + self.speedY**2)

        x, y = self.position
        x += -self.speedX
        y += -self.speedY

        ScreenWrapObject.update(self, deltat, x, y)

# Initialize the game and run
rect = screen.get_rect()
player = PlayerSprite('PNG/playerShip1_blue.png', rect.center, WIDTH, HEIGHT)
player_group = pygame.sprite.RenderPlain(player)
engineFire = Effect('PNG/Effects/fire09.png', rect.center, 0, 55)
engineFire_group = pygame.sprite.RenderPlain(engineFire)
asteroid = list()
FloatingObject('PNG/Meteors/meteorBrown_big1.png', (100,100), 45, 2, -1, WIDTH, HEIGHT)
asteroid_group = pygame.sprite.RenderPlain(asteroid)
for x in range(0, 15):
    asteroid_group.add(FloatingObject('PNG/Meteors/meteorBrown_big1.png', (random.randint(0, WIDTH) + player.position[0], -120), random.randint(0,360), 2, -1, WIDTH, HEIGHT))
lasers = list()
laser_group = pygame.sprite.RenderPlain(lasers)
while 1:
    # Player Input
    deltat = clock.tick(30)
    for event in pygame.event.get():
        if not hasattr(event, 'key'): continue
        down = event.type == KEYDOWN
        if event.key == K_RIGHT and player.alive(): player.k_right = down * -5
        elif event.key == K_LEFT and player.alive(): player.k_left = down * 5
        elif event.key == K_UP and player.alive(): player.k_up = down * 2
        elif event.key == K_SPACE and player.alive() and down > 0:
            playerSpeed = math.sqrt(player.speedX**2 + player.speedY**2)
            laser_group.add(FloatingObject('PNG/Lasers/laserBlue01.png', player.position, player.direction, 30+playerSpeed, 15, WIDTH, HEIGHT))
        elif event.key == K_ESCAPE: sys.exit(0)
    # Update objects and draw
    screen.fill((0,0,0))

    asteroidCollisions = pygame.sprite.spritecollide(player, asteroid_group, False)
    if len(asteroidCollisions) > 0 and player.alive():
        laser_group.add(FloatingObject('PNG/Damage/playerShip1_damage1.png', player.position, random.randint(0,360), 1, -1, WIDTH, HEIGHT))
        laser_group.add(FloatingObject('PNG/Damage/playerShip1_damage2.png', player.position, random.randint(0,360), 1, -1, WIDTH, HEIGHT))
        laser_group.add(FloatingObject('PNG/Damage/playerShip1_damage3.png', player.position, random.randint(0,360), 1, -1, WIDTH, HEIGHT))
        player.k_up = 0
        player.kill()

    laserCollisions = pygame.sprite.groupcollide(laser_group, asteroid_group, True, True, None)

    for x in laserCollisions:
        asteroid_group.add(FloatingObject('PNG/Meteors/meteorBrown_big1.png', (random.randint(0, WIDTH) + player.position[0], -120), random.randint(0,360), 2, -1, WIDTH, HEIGHT))

    player_group.update(deltat)
    player_group.draw(screen)
    engineFire_group.update(deltat, player.position, player.direction)
    if player.k_up > 0: engineFire_group.draw(screen)
    asteroid_group.update(deltat)
    asteroid_group.draw(screen)
    laser_group.update(deltat)
    laser_group.draw(screen)
    pygame.display.flip()
