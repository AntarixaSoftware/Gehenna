import pygame
from configuration import *
import global_vars

class Gate(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += global_vars.screen_scroll