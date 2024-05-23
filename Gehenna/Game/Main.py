import pygame
import os
from pygame.sprite import Group
import random
import csv
import button
from button import Button
import cv2
import pygame.mixer
from configuration import *
from world import *
import global_vars

pygame.init()
pygame.mixer.init()

def change_background_music(level):
    pygame.mixer.music.stop()  # Stop current music
    if level == 0:
        pygame.mixer.music.load('Game/Sound Assets/bg_music/ingame.mp3')
    elif level == 1:
        pygame.mixer.music.load('Game/Sound Assets/bg_music/lvl1.mp3')
    elif level == 2:
        pygame.mixer.music.load('Game/Sound Assets/bg_music/lvl2.mp3')
    pygame.mixer.music.play(-1)  # Play the new music in loop

def draw_bg():
    screen.fill(BG)
    width = backgrounds[level].get_width()
    for i in range(SCREEN_WIDTH // width + 3):
        screen.blit(backgrounds[level], (i * width - global_vars.bg_scroll * 0.5, 0))

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
    global credits_scroll, run

    # Event handling untuk mengontrol percepatan scroll menggunakan spasi atau klik mouse
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    if keys[pygame.K_SPACE] or mouse_buttons[0]:  # Tombol spasi atau klik kiri mouse ditekan
        credits_scroll -= 5  # Meningkatkan percepatan scroll
    else:
        credits_scroll -= 1  # Scroll normal

    screen.fill(BLACK)

    font = pygame.font.SysFont('Arial', 30)
    y = SCREEN_HEIGHT + credits_scroll
    for line in credits_text:
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(text_surface, text_rect)
        y += 40

    # Menutup game setelah kredit selesai
    if y < -100:
        run = False

def play_next_track(current_track):
    if current_track == "intro":
        pygame.mixer.music.load('Game/Sound Assets/bg_music/ingame.mp3')
        pygame.mixer.music.play()
        return "main_menu"
    elif current_track == "main_menu":
        pygame.mixer.music.load('Game/Sound Assets/bg_music/sound2.mp3')
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
        screen.blit(logo_img, (160, 30))
        if start_button.draw(screen):
            start_game = True
            show_story = True
            level = 0
            global_vars.bg_scroll = 0
            world_data = reset_level()
            with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)

            world = World()
            global_vars.player, health_bar = world.process_data(world_data)
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
            health_bar.draw(global_vars.player.health)
            global_vars.player.update(enemies)
            global_vars.player.draw(screen)
            enemies.draw(screen)

            if global_vars.player.alive:
                
                if global_vars.player.in_air:
                    global_vars.player.update_action(2)  # jump
                elif global_vars.player.attacked:
                    global_vars.player.update_action(4)
                elif moving_left or moving_right:
                    global_vars.player.update_action(1)  # run
                else:
                    global_vars.player.update_action(0)  # idle

                global_vars.screen_scroll, level_complete = global_vars.player.move(moving_left, moving_right)
                global_vars.bg_scroll -= global_vars.screen_scroll

                for enemy in enemies:
                    enemy.update()

                for enemy in enemies:
                    enemy.move()
 
                if level_complete:
                    level += 1
                    global_vars.bg_scroll = 0
                    world_data = reset_level()
                    if level <= 2:
                        with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        world = World()
                        global_vars.player, health_bar = world.process_data(world_data)
                        change_background_music(level)  # Change the music based on the new level
                    else:
                        show_ending_story = True

            else:
               
                screen_scroll = 0
                if restart_button.draw(screen):
                    global_vars.bg_scroll = 0
                    world_data = reset_level()
                    with open(f'Game/levels/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    global_vars.player, health_bar = world.process_data(world_data)
                    change_background_music(level)  # Reset music if restarting the level

    # Draw the player and enemies for debugging
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
            if event.key == pygame.K_w and global_vars.player.alive:
                global_vars.player.jump = True
                jump_sound.stop()  # Menghentikan suara lompat sebelum memainkan yang baru
                jump_sound.play()
            if event.key == pygame.K_SPACE:
                global_vars.player.attacked = True


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
