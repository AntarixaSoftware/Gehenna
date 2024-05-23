import pygame
import csv
from configuration import *
from potion import Potion
from decoration import Decoration
from enemy import Enemy
from player import Player
from healthbar import HealthBar
from gate import Gate
import global_vars

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Game/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

enemies = pygame.sprite.Group()
potions = pygame.sprite.Group()
gates = pygame.sprite.Group()
decorations = pygame.sprite.Group()

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
                    if tile >= 0 and tile <=3 or tile >= 15 and tile <= 16:
                        self.obstacle_list.append(tile_data) 
                    elif tile >= 4 and tile <= 5 or tile >= 12 and tile <= 14 or tile == 17 :
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decorations.add(decoration)
                    elif tile == 6:
                        global_vars.player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 5, self, gates)
                        health_bar = HealthBar(10, 10, global_vars.player.health, global_vars.player.health)
                    elif tile == 7:
                        enemy = Enemy('enemy', x * TILE_SIZE, y * TILE_SIZE, 2, 100)
                        enemies.add(enemy)
                    elif tile == 8:
                        enemy = Enemy('enemy2', x * TILE_SIZE, y * TILE_SIZE, 2, 100)
                        enemies.add(enemy)
                    elif tile == 9:
                        enemy = Enemy('enemy3', x * TILE_SIZE, y * TILE_SIZE, 2, 100)
                        enemies.add(enemy)                                         
                    elif tile == 10:
                        potion = Potion(img,x * TILE_SIZE, y * TILE_SIZE)
                        potions.add(potion)
                    elif tile == 11:
                        gate = Gate(img, x * TILE_SIZE, y * TILE_SIZE)
                        gates.add(gate)
        return global_vars.player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += global_vars.screen_scroll
            screen.blit(tile[0], tile[1])

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