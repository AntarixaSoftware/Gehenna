import pygame
import random
import os
from configuration import *
import global_vars


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
        self.idle = False
        self.idle_timer = pygame.time.get_ticks()
        self.idle_duration = random.randint(1000, 3000)  # Idle duration between 1 to 3 seconds
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
        if not self.idle:
            self.rect.x += self.direction * self.speed
            self.move_counter += self.speed

            if abs(self.move_counter) >= self.move_range:
                self.direction *= -1
                self.move_counter *= -1
                self.flip = True
                self.idle = True
                self.idle_timer = pygame.time.get_ticks()
        else:
            if pygame.time.get_ticks() - self.idle_timer > self.idle_duration:
                self.idle = False
                self.idle_duration = random.randint(1000, 3000)  # New idle duration

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

        if self.index >= len(self.animation_list[self.action]):
            self.index = 0
        
        self.rect.x += global_vars.screen_scroll

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        if self.idle:
            self.update_action(0)  # Idle action
        else:
            self.update_action(1)  # Run action
        self.update_animation()


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)