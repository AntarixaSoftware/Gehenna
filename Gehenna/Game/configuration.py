import pygame
import os
import csv
from button import Button

pygame.init()
pygame.mixer.init()

current_track = "intro"
pygame.mixer.music.load('Game/Sound Assets/bg_music/intro_3.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.3)  # Pastikan volume terdengar

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
TILE_TYPES = 18
RETURN_BUTTON = pygame.USEREVENT + 1

screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False
show_story = False  # Variable to control the story display
story_index = 0
text_index = 0
text_timer = 0
text_speed = 30  # Milliseconds per character
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
    "A knight, who's swore to be the best Knight",
    "Is now on his mission to accomplish his ambition",
    "The road ahead is unkwown",
    "Only him and him only can go down this road"
]

ending_story_texts = [
    "The journey may not be the one",
    "The start might not be the same",
    "The end has to be this way",
    "He accomplish what he swore",
    "But at what cost"
]

credits_text = [
    "ANTARIXA",
    " ",
    "KETUA",
    "Yohannes Christian Panjaitan",
    " ",
    "ANGGOTA",
    "Muhammad Zahran Albara",
    "Roy Sebastian Surbakti",
    "Muhammad Sabda Arif",
    "Yossi Afridho",
    "Dimas Dharma Wicaksono",
    " ",
    "GEHENNA",
    " ",
    "THANKS FOR PLAYING!!!"
]

credits_scroll = 0

attack_sound = pygame.mixer.Sound('Game/Sound Assets/sfx/mixkit-sword-cutting-flesh-2788.wav')
jump_sound = pygame.mixer.Sound('Game/Sound Assets/sfx/mixkit-quick-jump-arcade-game-239.wav')
death_sound = pygame.mixer.Sound('Game/Sound Assets/sfx/mixkit-ominous-drums-227.wav')
heal_sound = pygame.mixer.Sound('Game/Sound Assets/sfx/mixkit-player-boost-recharging-2040.wav')

moving_left = False
moving_right = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GEHENNA')
logo_img = pygame.image.load('Game/img/Logoo.png').convert_alpha()

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


start_button = Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2, start_btn, start_click, 1)
exit_button = Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT - 200, exit_btn, exit_click, 1)
restart_button = Button(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT - 350, restart_btn,restart_click, 1)



