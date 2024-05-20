import pygame
import os
from pygame.sprite import Group
import random
import csv
import button
import cv2
import pygame.mixer

pygame.init()
pygame.mixer.init()

def change_background_music(level):
    pygame.mixer.music.stop()  # Stop current music
    if level == 0:
        pygame.mixer.music.load('Game/ingame.mp3')
    elif level == 1:
        pygame.mixer.music.load('Game/lvl1.mp3')
    elif level == 2:
        pygame.mixer.music.load('Game/lvl2.mp3')
    pygame.mixer.music.play(-1)  # Play the new music in loop

current_track = "intro"
pygame.mixer.music.load('Game/intro_3.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(1.0)  # Pastikan volume terdengar

music_end_event = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(music_end_event)

clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

GRAVITY = 1
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 12
RETURN_BUTTON = pygame.USEREVENT + 1
screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False
show_story = False  # Variable to control the story display
story_index = 0
text_index = 0
text_timer = 0
text_speed = 10  # Milliseconds per character
waiting_for_click = False
printed_text = ""
story_texts_displayed = []
show_ending_story = False
ending_story_index = 0
ending_text_index = 0
ending_text_timer = 0
ending_waiting_for_click = False
ending_printed_text = ""
ending_story_texts_displayed = []

story_texts = [
    "Pada suatu hari hiduplah seorang pemuda yang sangat tampan.",
    "pemuda tersebut bernama Zahran.",
    "Setiap hari, dia dicari oleh gadis gadis cantik di seluruh desa."
]

ending_story_texts = [
    "Akhirnya, Zahran berhasil mengalahkan semua musuhnya.",
    "Dia kembali ke desanya sebagai pahlawan.",
    "Desanya kembali damai dan Zahran hidup bahagia selamanya."
]

credits_text = [
    "Credits",
    "",
    "Game Developer:",
    "Nama Developer 1",
    "Nama Developer 2",
    "",
    "Art & Design:",
    "Nama Designer 1",
    "Nama Designer 2",
    "",
    "Music & Sound:",
    "Nama Musician 1",
    "Nama Musician 2",
    "",
    "Special Thanks:",
    "Nama Orang 1",
    "Nama Orang 2",
    "",
    "Thank you for playing!"
]

credits_scroll = 0

story_texts = [
    "Pada suatu hari hiduplah seorang pemuda yang sangat tampan.",
    "pemuda tersebut bernama Zahran.",
    "Setiap hari, dia dicari oleh gadis gadis cantik di seluruh desa."
]

moving_left = False
moving_right = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GEHENNA')
logo_img = pygame.image.load('Game/img/logo.png').convert_alpha()
logo_img = pygame.transform.scale(logo_img, (300, 300))
start_btn = pygame.image.load('Game/img/start.png').convert_alpha()
start_click = pygame.image.load('Game/img/start-click.png').convert_alpha()
exit_btn = pygame.image.load('Game/img/exit.png').convert_alpha()
exit_click = pygame.image.load('Game/img/exit-click.png').convert_alpha()
restart_btn = pygame.image.load('Game/img/restart.png').convert_alpha()
restart_click = pygame.image.load('Game/img/restart-click.png').convert_alpha()
waiting_icon = pygame.image.load('Game/img/waiting_icon.png').convert_alpha()
waiting_icon = pygame.transform.scale(waiting_icon, (50, 50))
backgrounds = {
    0: pygame.transform.scale(pygame.image.load('Game/img/Background/level1_bg.png').convert_alpha(), (1140, 640)),
    1: pygame.transform.scale(pygame.image.load('Game/img/Background/level2_bg.png').convert_alpha(), (1140, 640)),
    2: pygame.transform.scale(pygame.image.load('Game/img/Background/level3_bg.png').convert_alpha(), (1140, 640))
}
# define colors
BG = (20, 230, 250)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

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

        animation_types = ['idle', 'run', 'jump', 'death', 'attack']
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
        self.update_animation()
        self.check_alive()
        
        if pygame.sprite.spritecollide(self, enemies, False):
            self.health -= 1
            if self.health == 0:
                self.alive = False

        if self.attacked and self.index == len(self.animation_list[self.action]) - 1:
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
        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0
            self.alive = False
        
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
                self.flip = not self.flip
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
        
        self.rect.x += screen_scroll

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

start_button = button.Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2, start_btn, start_click, 1)
exit_button = button.Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT - 200, exit_btn, exit_click, 1)
restart_button = button.Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT - 350, restart_btn,restart_click, 1)

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

def draw_textbox():
    global story_index, text_index, text_timer, waiting_for_click, printed_text, story_texts_displayed
    
    pygame.draw.rect(screen, GRAY, (50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 100))
    pygame.draw.rect(screen, BLACK, (50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 100), 2)

    if story_index < len(story_texts):
        # Jika belum selesai menampilkan teks
        if not waiting_for_click:
            # Jika belum selesai menampilkan satu baris teks
            if text_index < len(story_texts[story_index]):
                # Tambahkan satu karakter ke printed_text setiap waktu text_speed
                if pygame.time.get_ticks() - text_timer > text_speed:
                    printed_text += story_texts[story_index][text_index]
                    text_index += 1
                    text_timer = pygame.time.get_ticks()
        
            # Gambar teks yang sudah dicetak
            font = pygame.font.SysFont('Arial', 24)
            text_surface = font.render(printed_text, True, (255, 255, 255))
            screen.blit(text_surface, (60, SCREEN_HEIGHT - 130))

            # Jika sudah mencapai akhir teks, tunggu klik
            if text_index >= len(story_texts[story_index]):
                waiting_for_click = True
                story_texts_displayed.append(printed_text)  # Save the printed text to the list
                printed_text = ""  # Reset printed_text for the next line

        # Jika menunggu klik
        else:
            screen.blit(waiting_icon, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120))
            # Jika mendapatkan klik kiri, lanjut ke baris teks berikutnya
            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]:
                story_index += 1
                text_index = 0
                text_timer = pygame.time.get_ticks()  # Kosongkan teks yang sudah tercetak
                waiting_for_click = False
                printed_text = ""
                story_texts_displayed = []  # Clear the list of displayed texts

    # Jika sudah mencapai akhir story, hentikan menampilkan story
    else:
        global show_story
        show_story = False

    # Display previous lines of story
    for i, line in enumerate(story_texts_displayed):
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (60, SCREEN_HEIGHT - 130 - (i+1)*30))  # Adjust the y position for each line

def draw_ending_textbox():
    global ending_story_index, ending_text_index, ending_text_timer, ending_waiting_for_click, ending_printed_text, ending_story_texts_displayed

    pygame.draw.rect(screen, GRAY, (50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 100))
    pygame.draw.rect(screen, BLACK, (50, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 100, 100), 2)

    if ending_story_index < len(ending_story_texts):
        if not ending_waiting_for_click:
            if ending_text_index < len(ending_story_texts[ending_story_index]):
                if pygame.time.get_ticks() - ending_text_timer > text_speed:
                    ending_printed_text += ending_story_texts[ending_story_index][ending_text_index]
                    ending_text_index += 1
                    ending_text_timer = pygame.time.get_ticks()

            font = pygame.font.SysFont('Arial', 24)
            text_surface = font.render(ending_printed_text, True, (255, 255, 255))
            screen.blit(text_surface, (60, SCREEN_HEIGHT - 130))

            if ending_text_index >= len(ending_story_texts[ending_story_index]):
                ending_waiting_for_click = True
                ending_story_texts_displayed.append(ending_printed_text)
                ending_printed_text = ""

        else:
            screen.blit(waiting_icon, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120))
            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]:
                ending_story_index += 1
                ending_text_index = 0
                ending_text_timer = pygame.time.get_ticks()
                ending_waiting_for_click = False
                ending_printed_text = ""
                ending_story_texts_displayed = []

    else:
        show_ending_story = False
        draw_credits()

    for i, line in enumerate(ending_story_texts_displayed):
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (60, SCREEN_HEIGHT - 130 - (i+1)*30))

def draw_credits():
    global credits_scroll, run, start_game, level
    screen.fill(BLACK)
    
    font = pygame.font.SysFont('Arial', 30)
    y = SCREEN_HEIGHT + credits_scroll
    for line in credits_text:
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(text_surface, text_rect)
        y += 40

    credits_scroll -= 1

    if y < -100: # Add this condition to close the game after credits finish
        start_game = False

def play_next_track(current_track):
    if current_track == "intro":
        pygame.mixer.music.load('Game/ingame.mp3')
        pygame.mixer.music.play()
        return "main_menu"
    elif current_track == "main_menu":
        pygame.mixer.music.load('Game/sound2.mp3')
        pygame.mixer.music.play(-1)  # Looping musik game
        return "ingame"
    return "none"

run = True

play_intro_video('Game/intro_3.mp4')

while run:
    clock.tick(60)
    if start_game == False:
        screen.fill(BG)
        screen.blit(backgrounds[0],(0, 0))
        screen.blit(logo_img, (260, 30))
        if start_button.draw(screen):
            start_game = True
            show_story = True
            level = 0
            bg_scroll = 0
            world_data = reset_level()
            with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)

            world = World()
            player, health_bar = world.process_data(world_data)
            change_background_music(level)  # Set initial background music
        if exit_button.draw(screen):
                run = False
    elif show_ending_story:
        draw_ending_textbox()
    else:
        if show_story:
            draw_textbox()
        else:       
            draw_bg()
            world.draw()
            potions.draw(screen)
            potions.update()
            decorations.draw(screen)
            decorations.update()
            gates.draw(screen)
            gates.update()
            health_bar.draw(player.health)
            player.update(enemies)
            player.draw()
            enemies.draw(screen)

            if player.alive:
                
                if player.in_air:
                    player.update_action(2)  # jump
                elif player.attacked:
                    player.update_action(4)
                elif moving_left or moving_right:
                    player.update_action(1)  # run
                else:
                    player.update_action(0)  # idle

                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll

                for enemy in enemies:
                    enemy.update()

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
                        change_background_music(level)  # Change the music based on the new level
                    else:
                        show_ending_story = True

            else:
                screen_scroll = 0
                if restart_button.draw(screen):
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                    change_background_music(level)  # Reset music if restarting the level

    # Draw the rect of player and enemies for debugging
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == music_end_event:
            current_track = play_next_track(current_track)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_SPACE:
                player.attacked = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

        if event.type == RETURN_BUTTON:
            start_button.button_clicked = False
            exit_button.button_clicked = False
            restart_button.button_clicked = False

            pygame.time.set_timer(RETURN_BUTTON, 0)

    pygame.display.update()

pygame.quit()
