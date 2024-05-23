import pygame
import os
from configuration import *
from healthbar import HealthBar
import global_vars


class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, speed, world, gates):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.death_played = False
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
        self.attack_count = 0
        self.update_time = pygame.time.get_ticks()
        self.world = world
        self.gates = gates

        animation_types = ['idle', 'run', 'jump', 'death', 'attack']
        for animation in animation_types:
            temp_list = []
            # count num of files in folder
            num_of_frames = len(os.listdir(f'Game/assets/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Game/assets/{char_type}/{animation}/{i}.png').convert_alpha()
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    
    def update(self, enemies):
        self.update_animation()
        self.check_alive()
        
        if pygame.sprite.spritecollide(self, enemies, False):
            self.health -= 1
            if self.health == 0:
                self.alive = False

        if self.attacked and self.index == len(self.animation_list[self.action]) - 1:
            attack_sound.stop()  # Menghentikan suara lompat sebelum memainkan yang baru
            attack_sound.play()
            self.attacked = False
            self.update_action(0)

        if pygame.sprite.spritecollide(self, enemies, False) and self.attacked:
            self.attack_count += 1
            self.attacked = False  # Hanya satu serangan setiap kali menyentuh musuh
            if self.attack_count >= 3:
                for enemy in enemies:
                    if pygame.sprite.collide_rect(self, enemy):
                        enemies.remove(enemy)
                        self.attack_count = 0  # Setel ulang jumlah serangan setelah musuh terbunuh
                        break

    def move(self, moving_left, moving_right):
        global_vars.screen_scroll = 0
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

        for tile in self.world.obstacle_list:
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
        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0
            self.alive = False
        
        level_complete = False
        if pygame.sprite.spritecollide(self, self.gates, False):
            level_complete = True

        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and global_vars.bg_scroll < (self.world.level_length * TILE_SIZE) - SCREEN_WIDTH):
            self.rect.x -= dx
            global_vars.screen_scroll = -dx
        elif (self.rect.left < SCROLL_THRESH and global_vars.bg_scroll > abs(dx)):
            self.rect.x -= dx
            global_vars.screen_scroll = -dx

        return global_vars.screen_scroll, level_complete

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:  # if death animation
                self.index = len(self.animation_list[self.action]) - 1
                self.death_played = True
            if self.action == 4:  # attack animation finished
                self.attacked = False
                self.update_action(0)
            else:
                self.index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            if not self.death_played:
                self.update_action(3)
                death_sound.stop()
                death_sound.play()
                

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)