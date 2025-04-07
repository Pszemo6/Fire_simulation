import pygame
from PIL import Image
import numpy as np
from scipy.spatial import KDTree
import random
import cv2

pygame.init()

FOREST = (51, 204, 51)
WATER = (153, 204, 255)
GROUND = (153, 255, 153)
BUILDINGS = (230, 230, 230)

WHITE = (255, 255, 255)

FIRE1 = (254, 48, 35)
FIRE2 = (72, 0, 4)

WIDTH, HEIGHT = 1500, 750
TILE_SIZE = 3
GRID_WIDTH = WIDTH // TILE_SIZE  # 500
GRID_HEIGHT = HEIGHT // TILE_SIZE  # 250
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

font = pygame.font.SysFont("Lato", 16)

#wind_direction = (0, 0)
#wind_strength = 0

def draw_grid(points, wind_direction):
    for point, (color, duration) in points.items():
        col, row = point
        pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    panel_x = GRID_WIDTH * TILE_SIZE
    panel_width = WIDTH - panel_x
    pygame.draw.rect(screen, (30, 30, 30), (panel_x, 0, panel_width, HEIGHT))

    instructions = [
        "INSTRUKCJE:",
        "",
        "MYSZKA:",
        "  LPM - Dodaj ogień",
        "  PPM - Dodaj wodę",
        "",
        "KLAWIATURA:",
        "  SPACE - Start/Pauza",
        "  UP - Zwiększ FPS",
        "  DOWN - Zmniejsz FPS",
        "  R - Reset planszy",
        "  W - Wiatr na północ",
        "  A - Wiatr na zachód",
        "  S - Wiatr na południe",
        "  D - Wiatr na wschód",
        "  X - Anulacja wiatru",
        "  ESC - Wyjście",
        "",
        "Dane wiatru:",
    ]

    y_offset = 10
    for line in instructions:
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (panel_x + 10, y_offset))
        y_offset += 20

    if wind_direction[0] == 0:
        if wind_direction[1] == 0:
            wind_text = "Nie wieje"
        elif wind_direction[1] == 1:
            wind_text = "Wieje na południe"
        elif wind_direction[1] == -1:
            wind_text = "Wieje na północ"
    elif wind_direction[0] == 1:
        if wind_direction[1] == 0:
            wind_text = "Wieje na wschód"
    elif wind_direction[0] == -1:
        if wind_direction[1] == 0:
            wind_text = "Wieje na zachód"
    wind_surface = font.render(wind_text, True, WHITE)
    screen.blit(wind_surface, (panel_x + 10, y_offset))


def update_grid(points, wind_direction):
    new_points = {}

    for point, (color, duration) in points.items():
        duration += 1
        if color == FIRE1 and duration >= 50:
            if (duration < 75 and random.random() < 0.01) or (duration < 100 and random.random() < 0.05) or (duration < 125 and random.random() < 0.15) or (random.random() < 0.3):
                new_points[point] = (FIRE2, 0)
            else:
                new_points[point] = (color, duration)
        else:
            new_points[point] = (color, duration)

    new_points_updated = new_points.copy()
    for point, (color, duration) in points.items():
        if color in {FIRE1, FIRE2}:
            neighbors = get_neighbors(point, points, wind_direction)
            for neighbor_pos, neighbor_color in neighbors:
                if (neighbor_pos in new_points and new_points[neighbor_pos][0] not in {FIRE2}):
                    neighbor_state = new_points[neighbor_pos][0]

                    "wind_factor = 0.01 * wind_strength"

                    if neighbor_state == FOREST and random.random() < 0.2:
                        new_points_updated[neighbor_pos] = (FIRE1, 0)
                    elif neighbor_state == GROUND and random.random() < 0.1:
                        new_points_updated[neighbor_pos] = (FIRE1, 0)
                    elif neighbor_state == BUILDINGS and random.random() < 0.02:
                        new_points_updated[neighbor_pos] = (FIRE1, 0)
                    elif neighbor_state == WATER and random.random() < 0.008:
                        new_points_updated[neighbor_pos] = (FIRE1, 0)

    return new_points_updated


def get_neighbors(point, points, wind_direction):
    x, y = point
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            nx, ny = x + dx + wind_direction[0], y + dy + wind_direction[1]

            if nx < 0:
                nx = -nx
            elif nx >= GRID_WIDTH:
                nx = GRID_WIDTH - (GRID_HEIGHT - nx)

            if ny < 0:
                ny = -ny
            elif ny >= GRID_HEIGHT:
                ny = GRID_HEIGHT - (GRID_HEIGHT - ny)

            neighbor_pos = (nx, ny)
            neighbor_color = points.get(neighbor_pos, None)
            neighbors.append((neighbor_pos, neighbor_color))

    return neighbors

def main():
    global FPS
    wind_direction = (0, 0)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    image_path = "maps/map1_converted.png"
    image = Image.open(image_path).convert('RGB')
    background_image = pygame.image.fromstring(
        image.tobytes(), image.size, image.mode
    )

    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    screen.blit(background_image, (0, 0))

    running = True
    playing = False
    f = 10

    points = {}

    for col in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            color = background_image.get_at((x, y))[:3]
            if color == FOREST:
                points[(col, row)] = (FOREST, 0)
            elif color == WATER:
                points[(col, row)] = (WATER, 0)
            elif color == GROUND:
                points[(col, row)] = (GROUND, 0)
            elif color == BUILDINGS:
                points[(col, row)] = (BUILDINGS, 0)

    iteration = 0

    while running:
        clock.tick(FPS)
        if playing:
            iteration = iteration + 1
            points = update_grid(points, wind_direction)

        pygame.display.set_caption("Playing" if playing else "Paused")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or (
                    event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]):
                x, y = pygame.mouse.get_pos()
                col = x // TILE_SIZE
                row = y // TILE_SIZE
                pos = (col, row)

                points[pos] = (FIRE1, 0)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 or (
                    event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[2]):
                x, y = pygame.mouse.get_pos()
                col = x // TILE_SIZE
                row = y // TILE_SIZE

                for dx in range(-3, 5):
                    for dy in range(-3, 5):
                        new_col = col + dx
                        new_row = row + dy
                        pos = (new_col, new_row)
                        points[pos] = (WATER, 0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE:
                    if playing:
                        playing = False
                        f = FPS
                        FPS = 60
                    else:
                        playing = True
                        FPS = f

                if event.key == pygame.K_UP:
                    FPS = min(FPS + 1, 60)

                if event.key == pygame.K_DOWN:
                    FPS = max(FPS - 1, 1)

                if event.key== pygame.K_r:
                    for col in range(GRID_WIDTH):
                        for row in range(GRID_HEIGHT):
                            x, y = col * TILE_SIZE, row * TILE_SIZE
                            color = background_image.get_at((x, y))[:3]
                            if color == FOREST:
                                points[(col, row)] = (FOREST, 0)
                            elif color == WATER:
                                points[(col, row)] = (WATER, 0)
                            elif color == GROUND:
                                points[(col, row)] = (GROUND, 0)
                            elif color == BUILDINGS:
                                points[(col, row)] = (BUILDINGS, 0)

                if event.key == pygame.K_w:
                    wind_direction = (0, -1)
                    #wind_strength = 0.2
                elif event.key == pygame.K_a:
                    wind_direction = (-1, 0)
                    #wind_strength = 0.2
                elif event.key == pygame.K_s:
                    wind_direction = (0, 1)
                    #wind_strength = 0.2
                elif event.key == pygame.K_d:
                    wind_direction = (1, 0)
                    #wind_strength = 0.2
                elif event.key == pygame.K_x:
                    wind_direction = (0, 0)
                    #wind_strength = 0.2

        draw_grid(points, wind_direction)

        fps = font.render(f"{FPS} FPS", True, WHITE)
        screen.blit(fps, (3, 3))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    WIDTH += 200
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    main()