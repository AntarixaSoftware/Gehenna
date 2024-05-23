import pygame
from configuration import *
import global_vars

class Potion(pygame.sprite.Sprite):
    def __init__(self,img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, global_vars.player):
            global_vars.player.health += 25
            heal_sound.stop()
            heal_sound.play()
            if global_vars.player.health >= global_vars.player.max_health:
                global_vars.player.health = global_vars.player.max_health
            self.kill()
        self.rect.x += global_vars.screen_scroll