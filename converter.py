from PIL import Image
import numpy as np
from scipy.spatial import KDTree
import random
import cv2

COLORS = {
    "woda": (147, 215, 236),
    "las": (195, 241, 213),
    "pole": (210, 248, 22),
    "budynki": (245, 243, 244),
}

FOREST = (51, 204, 51)
WATER = (153, 204, 255)
GROUND = (153, 255, 153)
BUILDINGS = (230, 230, 230)

WHITE = (255, 255, 255)


def map_key_to_color(key):
    if "las" in key:
        return FOREST
    elif "woda" in key:
        return WATER
    elif "pole" in key:
        return GROUND
    elif "budynki" in key:
        return BUILDINGS
    else:
        return WHITE


def find_nearest_color(color, color_tree, color_keys):
    _, idx = color_tree.query(color)
    key = color_keys[idx]
    return map_key_to_color(key)


def convert_image(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)

    color_values = np.array(list(COLORS.values()))
    color_keys = list(COLORS.keys())
    color_tree = KDTree(color_values)

    height, width, _ = pixels.shape
    for y in range(height):
        for x in range(width):
            original_color = pixels[y, x]
            nearest_color = find_nearest_color(original_color, color_tree, color_keys)
            pixels[y, x] = nearest_color

    return Image.fromarray(pixels)

def main():

    map_path = 'maps/map1.jpg'
    image = cv2.imread(map_path)
    kernel = np.ones((2, 2), np.uint8)
    eroded_image = cv2.erode(image, kernel, iterations=1)
    converted_image = convert_image('maps/map1.jpg')
    converted_image.save(f"maps/map1_converted.png")


if __name__ == '__main__':
    main()