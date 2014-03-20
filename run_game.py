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


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCE_PATH, filename))


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)


class Game:
    def __init__(self):
        self.buffer_size = None
        self.map_buffer = None
        self.running = False
        self.actors = {}

        self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])

        self.tmx_data = load_map('level.tmx')
        map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.buffer_size)

        geometry = []
        for obj in self.tmx_data.objectgroups[0]:
            bbox = (0, obj.x, obj.y, 0, obj.width, obj.height)
            geometry.append(bbox)

        self.physicsgroup = physics.PlatformerPhysicsGroup(1, 1/60., 9.8, [], geometry)

        self.new_hero()

    def new_hero(self):
        hero = Hero()
        obj = self.tmx_data.get_object_by_name('hero')
        hero.body.bbox.move(0, obj.x, obj.y)
        self.add_actor(hero)

    def add_actor(self, actor):
        self.actors[actor.name] = actor
        self.physicsgroup.bodies.append(actor.body)

    def init_buffer(self, size):
        self.map_buffer = pygame.Surface(size)
        self.buffer_size = self.map_buffer.get_size()

    def draw(self, surface):
        self.map_layer.draw(self.map_buffer, surface.get_rect())
        bx, by = self.map_buffer.get_size()
        cx_, cy_, cz_ = self.actors['hero'].body.bbox.topcenter
        cx = cy_
        cy = cz_
        for actor in self.actors.values():
            rect = self.physicsgroup.toRect(actor.body.bbox)
            x, y = rect.topleft
            x = x - cx + (bx / 2)
            y = y - cy + (by / 2)
            self.map_buffer.blit(actor.image, (x, y))

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
        x, y, z = self.actors['hero'].body.bbox.topcenter
        self.map_layer.center((y, z))
        self.physicsgroup.update(dt)
        for actor in self.actors.values():
            actor.update(dt)

    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        try:
            while self.running:
                td = clock.tick(60)
                self.handle_input()
                self.update(td)
                self.draw(screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


class Hero(pygame.sprite.Sprite):
    sprite_sheet = 'elisa-spritesheet1.png'
    name = 'hero'

    def __init__(self):
        bbox = physics.BBox((0, 0, 0, 32, 54, 54))
        self.body = physics.Body3(bbox, (0, 0), (0, 0), 0)

        s = load_image(self.sprite_sheet)
        self.image = pygame.Surface((54, 54))
        self.image.blit(s, (0, 0), (4, 4, 54, 54))
        self.image.set_colorkey(self.image.get_at((0, 0)))

    def handle_input(self, event):
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.body.acc = physics.Vector3(0, 0, -4)
            elif event.key == K_DOWN:
                pass
            elif event.key == K_LEFT:
                self.body.acc = physics.Vector3(0, -2, 0)
            elif event.key == K_RIGHT:
                self.body.acc = physics.Vector3(0, 2, 0)


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

