import pygame 
RETURN_BUTTON = pygame.USEREVENT + 1
#button class
class Button():
    def __init__(self, x, y, image_before, image_after, scale):
        width = image_before.get_width()
        height = image_before.get_height()
        self.image_before = pygame.transform.scale(image_before, (int(width * scale), int(height * scale)))
        self.image_after = pygame.transform.scale(image_after, (int(width * scale), int(height * scale)))
        self.image = self.image_before
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.button_clicked = False

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                self.button_clicked = True
    
                pygame.time.set_timer(RETURN_BUTTON, 200)

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Update button image based on click status
        if self.button_clicked:
            self.image = self.image_after
        else:
            self.image = self.image_before

        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action