import pygame
import os
from pygame.sprite import Group


pygame.init()

clock = pygame.time.Clock()

SCREEN_WIDTH = 800 
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

GRAVITY = 1

moving_left = False
moving_right = False

mount_img = pygame.image.load('Game/mount.png')
tree_img = pygame.image.load('Game/TreeBG.png')

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('GEHENNA')

#define colors
BG = (20, 230,250)
RED = (255, 255, 0)
GREEN = (0, 255 , 0)

def draw_bg():
    screen.fill(BG)

class Knight(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.vel_y = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ['idle', 'run', 'jump']
        for animation in animation_types:
            temp_list = []
            #count num of files in folder
            num_of_frames = len(os.listdir(f'Game/assets/{char_type}/{animation}'))
            for i in range(num_of_frames):
                self.img = pygame.image.load(f'Game/assets/{char_type}/{animation}/{i}.png')
                temp_list.append(self.img) 
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx -= self.speed
            self.direction = -1
            self.flip = True
        if moving_right:
            dx += self.speed
            self.direction = 1
            self.flip = False

        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        #gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        if self.rect.bottom + dy >600 :
            dy = 600 - self.rect.bottom
            self.in_air = False
        
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            self.index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health 
        self.max_health = max_health
        
    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
player = Knight('player', 100, 500, 5)
health_bar = HealthBar(10, 10, player.health, player.health)
x = 100
y = 500

run = True

while run :
    clock.tick(60)
    draw_bg()
    health_bar.draw(player.health)
    screen.blit(mount_img, (0,0))
    screen.blit(tree_img, (0,0))
    player.update_animation()
    player.draw()

    if player.alive:
        if player.in_air:
            player.update_action(2)#jump
        if moving_left or moving_right:
            player.update_action(1)#run
        else:
            player.update_action(0)#idle
    
        player.move(moving_left, moving_right)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_w and player.alive:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
    pygame.display.update()

pygame.quit()
