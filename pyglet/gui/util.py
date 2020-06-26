import pyglet
from functools import lru_cache


@lru_cache()
def make_rect(width, height, color=(255, 255, 255, 255)):
    return pyglet.image.SolidColorImagePattern(color).create_image(width, height)
