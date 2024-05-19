import pygame
import os
import pygame.locals
from pygame.sprite import Group
import random
import csv
import button
import cv2

pygame.init()

clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

GRAVITY = 1
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 10
screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False

moving_left = False
moving_right = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GEHENNA')
logo_img = pygame.image.load('Game/img/logo.png').convert_alpha()
start_btn = pygame.image.load('Game/img/start.png').convert_alpha()
start_btn = pygame.transform.scale(start_btn, (250, 80)).convert_alpha()
exit_btn = pygame.image.load('Game/img/exit.png').convert_alpha()
exit_btn = pygame.transform.scale(exit_btn, (200, 80)).convert_alpha()
backgrounds = {
    0: pygame.transform.scale(pygame.image.load('Game/img/Background/level1_bg.png').convert_alpha(), (1140, 640)),
    1: pygame.transform.scale(pygame.image.load('Game/img/Background/level2_bg.png').convert_alpha(), (1140, 640)),
    2: pygame.transform.scale(pygame.image.load('Game/img/Background/level3_bg.png').convert_alpha(), (1140, 640))
}
# define colors
BG = (20, 230, 250)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Game/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

def draw_bg():
    screen.fill(BG)
    width = backgrounds[level].get_width()
    for i in range(SCREEN_WIDTH // width + 3):
        screen.blit(backgrounds[level], (i * width - bg_scroll * 0.5, 0))

def reset_level():
    enemies.empty()
    potions.empty()
    gates.empty()
    decorations.empty()

    data = []
    for row in range(ROWS):
	    r = [-1] * COLS
	    data.append(r)

    return data

class Player(pygame.sprite.Sprite):
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
        self.attacked = False
        self.update_time = pygame.time.get_ticks()

        animation_types = ['idle', 'run', 'jump']
        for animation in animation_types:
            temp_list = []
            # count num of files in folder
            num_of_frames = len(os.listdir(f'Game/assets/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Game/assets/{char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (50, 100))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self, enemies):
        if pygame.sprite.spritecollide(self, enemies, False) and not self.attacked:
            self.health -= 1
            if self.health == 0:
                self.attacked = True
        self.attacked = False

    def move(self, moving_left, moving_right):
        screen_scroll = 0
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

        if self.jump and not self.in_air:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0
        
        level_complete = False
        if pygame.sprite.spritecollide(self, gates, False):
            level_complete = True

        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
            or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll, level_complete

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

class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <=3:
                        self.obstacle_list.append(tile_data) 
                    elif tile >= 4 and tile <= 5:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decorations.add(decoration)
                    elif tile == 6:
                        player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 7:
                        enemy = Enemy('enemy', x * TILE_SIZE, y * TILE_SIZE, 2, 100)
                        enemies.add(enemy)
                    elif tile == 8:
                        potion = Potion(img,x * TILE_SIZE, y * TILE_SIZE)
                        potions.add(potion)
                    elif tile == 9:
                        gate = Gate(img, x * TILE_SIZE, y * TILE_SIZE)
                        gates.add(gate)
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
    
class Enemy(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, speed, move_range):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = -1
        self.flip = False
        self.move_counter = 0
        self.move_range = move_range
        self.start_x = x
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.attacked = False
        self.update_time = pygame.time.get_ticks()

        animation_types = ['idle', 'run', 'attack']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'Game/assets/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Game/assets/{char_type}/{animation}/{i}.png').convert_alpha()
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self):
        self.rect.x += self.direction * self.speed
        self.move_counter += self.speed

        if abs(self.move_counter) >= self.move_range:
            self.direction *= -1
            self.move_counter *= -1
            self.flip = not self.flip

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            self.index = 0
        
        self.rect.x += screen_scroll

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
        pygame.draw.rect(screen, (0,0,0), (self.x - 5, self.y - 5, 160, 30))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Potion(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            player.health += 25
            if player.health >= player.max_health:
                player.health = player.max_health
            self.kill()
        self.rect.x += screen_scroll

class Gate(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Decoration(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

start_button = button.Button(SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2, start_btn, 1)
exit_button = button.Button(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT - 200, exit_btn, 1)

enemies = pygame.sprite.Group()
potions = pygame.sprite.Group()
gates = pygame.sprite.Group()
decorations = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

def play_intro_video(video_path, fps=60):
    cap = cv2.VideoCapture(video_path)
    clock = pygame.time.Clock()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frame = frame.swapaxes(0, 1)
        pygame.surfarray.blit_array(screen, frame)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cap.release()
                    return
        clock.tick(fps)
    cap.release()

run = True

play_intro_video('Game/intro_3.mp4')

while run:
    clock.tick(60)

    if start_game == False:
        screen.fill(BG)
        screen.blit(backgrounds[0],(0, 0))
        screen.blit(logo_img, (150, 30))
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        health_bar.draw(player.health)
        player.update_animation()
        player.draw()
        enemies.draw(screen)
        potions.draw(screen)
        potions.update()
        decorations.draw(screen)
        decorations.update()
        gates.draw(screen)
        gates.update()

        if player.alive:
            if player.in_air:
                player.update_action(2)  # jump
            elif moving_left or moving_right:
                player.update_action(1)  # run
            else:
                player.update_action(0)  # idle

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            for enemy in enemies:
                enemy.update_animation()
                if player.rect.colliderect(enemy.rect):
                    enemy.update_action(2)  # attack
                else:
                    enemy.update_action(1)  # run

            player.update(enemies)
            for enemy in enemies:
                enemy.move()

            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= 2:
                    with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            bg_scroll = 0
            world_data = reset_level()
            with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)

            world = World()
            player, health_bar = world.process_data(world_data)

    # Draw the rect of player and enemies for debugging
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
