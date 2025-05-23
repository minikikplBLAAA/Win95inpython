# apps/paint.py
import sys
import pygame
import os
import io
from PIL import Image, ImageDraw, ImageFont # Pillow do generowania ikon Pygame

# Definicje kolorów (standardowe kolory Win95)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY_WIN95 = (192, 192, 192)
DARK_GRAY_WIN95 = (128, 128, 128)
LIGHT_GRAY_WIN95 = (223, 223, 223)
BLUE_WIN95 = (0, 0, 128)

# Rozmiary okna Paint
WIDTH, HEIGHT = 640, 480

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bez tytułu - Paint")

# --- Generowanie prostej ikony dla okna Pygame ---
def generate_pygame_icon(text, bg_color, text_color, size=32):
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.6))
    except IOError:
        font = ImageFont.load_default()

    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) / 2
    text_y = (size - text_height) / 2 - 2

    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Konwersja PIL Image do formatu Pygame Surface
    raw_str = img.tobytes("raw", "RGBA")
    return pygame.image.fromstring(raw_str, img.size, "RGBA")

try:
    # Generujemy prostą ikonę dla okna Paint Pygame
    pygame_icon_surface = generate_pygame_icon("Art", (255, 150, 150), (0,0,0), 32)
    pygame.display.set_icon(pygame_icon_surface)
except Exception as e:
    print(f"Nie można załadować ikony Pygame: {e}")

# Płótno do rysowania
drawing_surface = pygame.Surface((WIDTH, HEIGHT - 50))
drawing_surface.fill(WHITE)

# Narzędzia do rysowania
drawing = False
last_pos = None
draw_color = BLACK
brush_size = 2

# Funkcje rysujące elementy GUI Pygame (bez zmian, używają tylko kolorów i tekstu)
def draw_button(surface, rect, text, is_pressed=False):
    if is_pressed:
        pygame.draw.rect(surface, DARK_GRAY_WIN95, rect, 0)
        pygame.draw.line(surface, BLACK, rect.topleft, rect.bottomleft)
        pygame.draw.line(surface, BLACK, rect.topleft, rect.topright)
        pygame.draw.line(surface, WHITE, rect.topright, rect.bottomright)
        pygame.draw.line(surface, WHITE, rect.bottomleft, rect.bottomright)
    else:
        pygame.draw.rect(surface, GRAY_WIN95, rect, 0)
        pygame.draw.line(surface, WHITE, rect.topleft, rect.bottomleft)
        pygame.draw.line(surface, WHITE, rect.topleft, rect.topright)
        pygame.draw.line(surface, DARK_GRAY_WIN95, rect.topright, rect.bottomright)
        pygame.draw.line(surface, DARK_GRAY_WIN95, rect.bottomleft, rect.bottomright)

    font = pygame.font.Font(None, 20)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def draw_color_box(surface, rect, color, is_selected=False):
    pygame.draw.rect(surface, color, rect)
    if is_selected:
        pygame.draw.rect(surface, BLACK, rect, 2)

# Pasek narzędzi Pygame
toolbar_rect = pygame.Rect(0, 0, WIDTH, 50)
toolbar_buttons = {
    "Czysty": pygame.Rect(10, 10, 80, 30),
    "Cofnij": pygame.Rect(100, 10, 80, 30),
    "Zapisz": pygame.Rect(190, 10, 80, 30)
}
color_palette = [
    (BLACK, pygame.Rect(WIDTH - 100, 10, 15, 15)),
    (BLUE_WIN95, pygame.Rect(WIDTH - 80, 10, 15, 15)),
    ((0, 128, 0), pygame.Rect(WIDTH - 60, 10, 15, 15)),
    ((255, 0, 0), pygame.Rect(WIDTH - 40, 10, 15, 15)),
    ((255, 255, 0), pygame.Rect(WIDTH - 100, 30, 15, 15)),
    ((255, 165, 0), pygame.Rect(WIDTH - 80, 30, 15, 15)),
    ((128, 0, 128), pygame.Rect(WIDTH - 60, 30, 15, 15)),
    (WHITE, pygame.Rect(WIDTH - 40, 30, 15, 15)),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if toolbar_rect.collidepoint(event.pos):
                    for text, rect in toolbar_buttons.items():
                        if rect.collidepoint(event.pos):
                            if text == "Czysty":
                                drawing_surface.fill(WHITE)
                            elif text == "Zapisz":
                                try:
                                    pygame.image.save(drawing_surface, "my_paint_drawing.png")
                                    print("Zapisano rysunek jako my_paint_drawing.png")
                                except Exception as e:
                                    print(f"Błąd zapisu: {e}")
                else:
                    drawing = True
                    last_pos = event.pos[0], event.pos[1] - 50
                for color, rect in color_palette:
                    if rect.collidepoint(event.pos):
                        draw_color = color
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                last_pos = None
        if event.type == pygame.MOUSEMOTION:
            if drawing and last_pos:
                current_pos = event.pos[0], event.pos[1] - 50
                pygame.draw.line(drawing_surface, draw_color, last_pos, current_pos, brush_size)
                last_pos = current_pos

    screen.fill(GRAY_WIN95)

    pygame.draw.rect(screen, GRAY_WIN95, toolbar_rect, 0)
    pygame.draw.line(screen, WHITE, toolbar_rect.topleft, toolbar_rect.bottomleft)
    pygame.draw.line(screen, WHITE, toolbar_rect.topleft, toolbar_rect.topright)
    pygame.draw.line(screen, DARK_GRAY_WIN95, toolbar_rect.topright, toolbar_rect.bottomright)
    pygame.draw.line(screen, DARK_GRAY_WIN95, toolbar_rect.bottomleft, toolbar_rect.bottomright)

    for text, rect in toolbar_buttons.items():
        draw_button(screen, rect, text)

    for color, rect in color_palette:
        is_selected = (color == draw_color)
        draw_color_box(screen, rect, color, is_selected)

    screen.blit(drawing_surface, (0, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()