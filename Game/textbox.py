import pygame
import sys

# Inisialisasi Pygame
pygame.init()

# Set ukuran layar
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Set warna dan font
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 24)

# Story yang akan ditampilkan
story = [
    "Baris pertama dari cerita ini.",
    "Baris kedua dari cerita ini.",
    "Baris ketiga dari cerita ini.",
    "Baris keempat dari cerita ini.",
    # Tambahkan baris-baris lainnya disini
]

# Variabel untuk menyimpan baris yang sedang ditampilkan
current_line = 0

# Fungsi untuk mencetak textbox
def print_textbox(text, x, y):
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x, y))

# Loop utama
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Klik kiri
                current_line += 1
                if current_line >= len(story):
                    current_line = 0  # Kembali ke awal jika sudah mencapai akhir cerita

    # Bersihkan layar
    screen.fill(WHITE)

    # Cetak textbox untuk setiap baris cerita
    y = 100
    for i in range(current_line + 1):
        print_textbox(story[i], 100, y)
        y += 30  # Jarak antar baris

    # Update layar
    pygame.display.flip()
    pygame.time.Clock().tick(60)