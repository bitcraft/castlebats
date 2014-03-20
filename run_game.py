__author__ = 'leif'

import os
import pytmx
import pygame
import physics
from pygame.locals import *
import pyscroll


RESOURCE_PATH = 'resources'


def load_map(filename):
    return pytmx.load_pygame(os.path.join(RESOURCE_PATH, filename))


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)


class Game:
    def __init__(self):
        self.buffer_size = None
        self.map_buffer = None
        self.running = False
        self.physicsgroup = physics.PhysicsGroup(1, 1/60., 9.8, [], [])
        self.actors = {}

        self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])

        self.tmx_data = load_map('level.tmx')
        map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.buffer_size)

        self.new_hero()

    def new_hero(self):
        hero = Hero()
        obj = self.tmx_data.get_object_by_name('hero')
        hero.rect.move_ip((obj.x, obj.y))
        self.actors['hero'] = hero

    def init_buffer(self, size):
        self.map_buffer = pygame.Surface(size)
        self.buffer_size = self.map_buffer.get_size()

    def draw(self, surface):
        self.map_layer.draw(self.map_buffer, surface.get_rect())
        pygame.transform.scale(self.map_buffer, surface.get_size(), surface)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break

            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])
                self.map_layer.set_size(self.buffer_size)

            self.actors['hero'].handle_input(event)

    def update(self, dt):
        self.map_layer.center(self.actors['hero'].rect.topleft)
        self.physicsgroup.update(dt)
        for actor in self.actors.values():
            actor.update(dt)

    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        try:
            while self.running:
                td = clock.tick(60) / 1000.0
                self.handle_input()
                self.update(td)
                self.draw(screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


class Hero(pygame.sprite.Sprite):
    sprite_sheet = ""

    def __init__(self):
        self.bbox = physics.BBox((0, 0, 0, 32, 32, 64))
        self.rect = pygame.Rect(0, 0, 32, 64)
        self.body = physics.Body2(self.bbox, (0, 0), (0, 0), 0)

    def handle_input(self, event):
        if event.type == KEYDOWN:
            if event.key == K_UP:
                pass
            elif event.key == K_DOWN:
                pass
            elif event.key == K_LEFT:
                pass
            elif event.key == K_RIGHT:
                pass


class Level:
    def __init__(self):
        pass


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = init_screen(700, 700)
    pygame.display.set_caption('Castle Bats')

    game = Game()
    try:
        game.run()
    except:
        pygame.quit()
        raise

